CREATE DATABASE IF NOT EXISTS main_db;
USE main_db;


CREATE TABLE tbl_users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL);

CREATE TABLE tbl_gw2_accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gw2_player_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES tbl_users(user_id)
)

CREATE TABLE tbl_gw2_item (
    item_id INT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    item_rarity VARCHAR(50) NOT NULL,
    item_level INT NOT NULL,
    item_description VARCHAR(255) NOT NULL,
    vendor_value INT NOT NULL,
    icon_url VARCHAR(255) NOT NULL,
)