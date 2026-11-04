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