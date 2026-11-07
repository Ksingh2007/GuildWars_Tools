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

