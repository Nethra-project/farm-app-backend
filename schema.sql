CREATE TABLE farmer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    village VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    crops_grown TEXT,
    upi_id VARCHAR(50),
    bank_account_no VARCHAR(30),
    ifsc_code VARCHAR(20),
    fpo_id INT NULL,
    profile_photo_url VARCHAR(255),

    CONSTRAINT fk_farmer_profiles_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT uq_farmer_profiles_user
        UNIQUE (user_id)
);
