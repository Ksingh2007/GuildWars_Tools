CREATE DATABASE IF NOT EXISTS main_db;
USE main_db;


CREATE TABLE tbl_users (
    user_id INT AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    PRIMARY KEY (user_id)
);

-- Store GW2 Account Information
CREATE TABLE tbl_gw2_accounts (
    account_id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gw2_player_name VARCHAR(100) NOT NULL,

    PRIMARY KEY (account_id),
    FOREIGN KEY (user_id) REFERENCES tbl_users(user_id)
);

-- Store Static GW2 Item data to prevent excessive API calls and to allow for more complex queries and filtering.
CREATE TABLE tbl_gw2_item (
    item_id INT,
    item_name VARCHAR(100) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    item_rarity VARCHAR(50) NOT NULL,
    item_level INT DEFAULT 0,
    item_description TEXT NULL,
    item_vendor_value INT DEFAULT 0,
    item_default_skin INT DEFAULT 0,
    item_game_type VARCHAR(255) NULL,
    item_restriction VARCHAR(50) NULL,
    item_chat_link VARCHAR(255) NULL,
    item_flags VARCHAR(255) NULL,
    item_icon_url VARCHAR(255) NULL,

    PRIMARY KEY (item_id)
);

-- Child Table for tbl_gw2_item to store additional details about items that have them such as armor and weapons.
CREATE TABLE tbl_item_details (
    item_id INT,
    item_sub_type VARCHAR(50) NULL,
    item_weight_class VARCHAR(50) NULL,
    item_defense int DEFAULT 0,
    item_infusion_slots VARCHAR(255) NULL,
    item_attribute_adjustments VARCHAR(255) NULL,
    item_infix_upgrade JSON NULL,
    secondary_suffix_item_id JSON NULL, -- Read warning above about inserting raw empty strings into JSON columns

    PRIMARY KEY (item_id),
    FOREIGN KEY (item_id) REFERENCES tbl_gw2_item(item_id) ON DELETE CASCADE
);

-- WARNING: Do not insert raw empty strings ("") 
-- from the API directly into MySQL JSON columns, 
-- or it will trigger a database syntax error. 
-- Ensure empty values are converted to null first.

-- Store Static GW2 Currency data
CREATE TABLE tbl_gw2_currency (
    currency_id INT,
    currency_name VARCHAR(100) NULL,
    currency_description TEXT NULL,
    currency_order INT NULL,
    currency_icon_url VARCHAR(255) NULL,

    PRIMARY KEY (currency_id)
)