# Made a mistake and now i found an easier way to do this. 
# I will be now instead of storing static data into the sql database,
# i will store the static data into a json file and then read from that json file when needed. 
# This will make it easier to update the static data in the future and its alot more efficient.

import json
import time # have a rest time between requests to avoid rate limiting
import sys
import argparse
import re
import requests # to make http requests to the API
from pathlib import Path # build files and folders

API = "https://api.guildwars2.com"
PAGE_SIZE = 200 # The maximum page size for the API is 300, so we will use that to minimize the number of requests we need to make
                # The refill rate for tokens is 5 tokens per second, 300 per minute


# Endpoints in which data is not static and needs to be updated frequently or on a seasonal basis.
DYNAMIC_ENDPOINTS = [
    "commerce/",
    "wvw/matches/",
    "wvw/guilds",
    "wvw/timers",
    "achievements/daily",
    "events-state",
    "wizardsvault",
]

# Endpoint flags -
# a - needs a auth key
# d - disabled for now
# l - You can pass a specific language ID using the query parameter ?lang=<langId> at the end of the API URL
#   includ: en, de, es, fr, zh

ALWAYS_SKIP_FLAGS = {"a", "d"}

# The following endpoints awlays require a auth key
AUTH_PREFIXES = (
    "account",
    "characters"
)

# Never Fetch these endpoints, they are not needed for our use case and can be gotten from other endpoints.
NEVER_FETCH = {
    "guild/search",
    "recipes/search",
    "home",
    "mounts",
    "pvp",
}


session = requests.Session()
session.headers["X-Schema-Version"] = "latest" # Get the latest version

def get(path, **params):
    url = f"{API}/{path}"

    for attempts in range(6):
        try:
            output = session.get(url, params=params, timeout=60)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching ({e}), retrying...", file=sys.stderr)
            time.sleep(2 ** attempts)  # Exponential backoff
            
            continue
        if output.status_code == 429:
            wait = int(output.headers.get("Retry-After", 15))
            print(f"Rate limited, waiting {wait}, seconds...")
            time.sleep(wait)
            
            continue

        if output.status_code >= 500:
            print(f"Serever error ({output.status_code}), retrying...", file=sys.stderr)
            time.sleep(2 ** attempts)

            continue
        time.sleep(0.2) # Sleep for 200ms to avoid rate limiting
        return output.status_code, output
    return 0, None

def fetch(path, **params):
    status, output = get(path, **params)
    if output is None:
        return status,None, {}
    try:
        return status, output.json(), output.headers
    except ValueError:
        return status, None, output.headers

def list_endpoint(): # Discovers and lists all available enpoints
    
    status, output = get("v2")

    if status != 200 or output is None: #Check if request was successful.
        sys.exit(f"Could not fetch endpoint list, status code: {status}")

    seen, endpoints = set(), [] # seen tracks enpoints visited, enpoints stores the endpoints and their flags
    in_list = False 

    for line in output.text.splitlines():
        if "paths are exposed" in line:
            in_list = True
            continue

        if not in_list:
            continue

        if line.startswith("Key:"):
            break

        m = re.match(r"\s*/v2/(\S+)(?:\s+\[([a-z,]+)\])?\s*$", line)
        if not m:
            continue

        path = m.group(1)
        flags = {f.strip() for f in m.group(2).split(",")} if m.group(2) else set()

        if path not in seen:
            seen.add(path)
            endpoints.append((path, flags))

    return endpoints

def fetch_all(path, ids, lang):
    status, body, headers = fetch(path, page=0, page_size=PAGE_SIZE, lang = lang)

    if status == 200 and isinstance(body, list) and "X-Page-Total" in headers:
        results = list(body)
        total_pages = int(headers["X-Page-Total"])

        for page in range(1, total_pages):
            status, body, headers = fetch(path, page=page, page_size=PAGE_SIZE, lang = lang)

            if status != 200 or not isinstance(body, list):
                print(f"Error fetching page {page} of {path}, status code: {status}", file=sys.stderr)
                break

            results.extend(body)
        return results

    results = []

    for i in range (0, len(ids), PAGE_SIZE):
        chunk = ids[i:i + PAGE_SIZE]
        status, body, headers = fetch(path, ids=",".join(map(str, chunk)), lang = lang)

        if status == 200 and isinstance(body, list):
            results.extend(body)

        else:
            return ids
    return results

# Build Path
def out_file(folder, name):
    return folder / f"{name.replace('/', '__')}.json"

# Save data to json file and stores them 
def save(folder, name, data):
    out_file(folder, name).write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )

def download(name, folder, lang):
    if out_file(folder, name).exists():
        print(f" = {name}: already downloaded")
        return False

    status, body, _ = fetch(f"/v2/{name}", lang=lang)
    if status != 200 or body is None:
        print(f"    - {name}: skipped (status {status})")
        return False

    if isinstance(body, list) and body:
        body = fetch_all(f"/v2/{name}", body, lang)

    save(folder, name, body)
    count = len(body) if isinstance(body,(list, dict)) else 1
    print(f" + {name}: saved ({count} entries)")
    
    return True

