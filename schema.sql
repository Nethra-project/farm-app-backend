-- Database Schema for Farm Platform

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'fpo', 'buyer', 'driver', 'admin') NOT NULL,
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS farmer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fpo_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    fpo_name VARCHAR(150) NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    bank_account_no VARCHAR(30),
    ifsc_code VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS buyer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    buyer_type ENUM('consumer', 'bulk_buyer') NOT NULL,
    full_name_or_contact VARCHAR(100) NOT NULL,
    business_name VARCHAR(150) NULL,
    business_type ENUM('hotel', 'restaurant', 'mess', 'retailer', 'processor', 'other') NULL,
    gstin VARCHAR(15) NULL,
    preferred_language VARCHAR(20) DEFAULT 'English',
    crops_needed TEXT NULL,
    monthly_quantity_approx VARCHAR(50) NULL,
    business_proof_url VARCHAR(255) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS buyer_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    address_line TEXT NOT NULL,
    landmark VARCHAR(100) NULL,
    city VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS driver_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    pincodes_served TEXT NOT NULL,
    vehicle_type ENUM('bike', 'tempo', 'pickup_truck', 'mini_truck') NOT NULL,
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    load_capacity_kg DECIMAL(10,2) NOT NULL,
    licence_photo_url VARCHAR(255) NULL,
    upi_id VARCHAR(50) NULL,
    bank_account_no VARCHAR(30) NULL,
    ifsc_code VARCHAR(20) NULL,
    is_online BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    price_per_unit DECIMAL(10,2) NOT NULL,
    district VARCHAR(100) NOT NULL,
    description TEXT,
    status ENUM('active', 'sold_out', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id INT NOT NULL,
    farmer_id INT NOT NULL,
    buyer_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    farmer_price_total DECIMAL(10,2) NOT NULL,
    payment_method ENUM('COD', 'UPI') DEFAULT 'COD',
    payment_status ENUM('pending', 'paid') DEFAULT 'pending',
    status ENUM('new', 'accepted', 'in_progress', 'out_for_delivery', 'delivered', 'cancelled') DEFAULT 'new',
    buyer_address_id INT NULL,
    delivery_date DATE NULL,
    transport_fee DECIMAL(10,2) DEFAULT 0.00,
    platform_fee DECIMAL(10,2) DEFAULT 0.00,
    driver_name VARCHAR(100) NULL,
    driver_phone VARCHAR(15) NULL,
    delivery_code VARCHAR(6) NULL,
    issue_report TEXT NULL,
    farmer_rating INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS delivery_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    driver_id INT NULL,
    pickup_village VARCHAR(100) NOT NULL,
    pickup_district VARCHAR(100) NOT NULL,
    drop_city VARCHAR(100) NOT NULL,
    drop_pincode VARCHAR(10) NOT NULL,
    total_weight_kg DECIMAL(10,2) NOT NULL,
    distance_km DECIMAL(6,2) DEFAULT 0.00,
    driver_pay DECIMAL(10,2) NOT NULL,
    farmer_pickup_code VARCHAR(6) NOT NULL,
    buyer_delivery_code VARCHAR(6) NOT NULL,
    pickup_photo_url VARCHAR(255) NULL,
    cash_collected DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('open', 'accepted', 'picked_up', 'delivered', 'failed', 'cancelled') DEFAULT 'open',
    failure_reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS driver_earnings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_id INT NOT NULL,
    job_id INT NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('pending', 'paid') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES delivery_jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS rfqs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    quality_grade VARCHAR(20) NULL,
    needed_by_date DATE NOT NULL,
    target_price_per_unit DECIMAL(10,2) NULL,
    delivery_district VARCHAR(100) NOT NULL,
    min_order_amount DECIMAL(10,2) NULL,
    status ENUM('open', 'fulfilled', 'closed') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS rfq_quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfq_id INT NOT NULL,
    farmer_id INT NOT NULL,
    offered_price_per_unit DECIMAL(10,2) NOT NULL,
    supply_quantity DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rfq_id) REFERENCES rfqs(id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS mandi_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    mandi_price_per_unit DECIMAL(10,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    updated_at DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS admin_invites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invite_code VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    admin_level ENUM('super_admin', 'moderator') NOT NULL DEFAULT 'moderator',
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    target_entity VARCHAR(50) NOT NULL,
    target_id INT NULL,
    details TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS system_settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO system_settings (setting_key, setting_value) VALUES 
('platform_fee_percent', '2.0'),
('transport_rate_per_km', '10.0'),
('served_districts', '["District A", "District B", "District C"]'),
('crop_grades', '["A+", "A", "B", "C"]')
ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value);
