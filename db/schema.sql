CREATE DATABASE IF NOT EXISTS jobhub_db;
USE jobhub_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    role VARCHAR(10),
    name VARCHAR(100),
    phone VARCHAR(15),
    password VARCHAR(255),
    email VARCHAR(100),
    city VARCHAR(100),
    gender VARCHAR(10),
    experience VARCHAR(50),
    availability_status VARCHAR(20),
    expected_salary INT,
    job_types JSON,             
    availability JSON,          
    languages JSON,             
    education VARCHAR(100),     
    company_name VARCHAR(100),
    company_type VARCHAR(50),
    company_address VARCHAR(255),
    designation VARCHAR(100),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    business_description TEXT,
    address VARCHAR(255),
    state VARCHAR(50),
    pincode VARCHAR(20),
    website VARCHAR(100),
    aadhaar VARCHAR(20),
    age INT,
    profile_completed TINYINT(1),
    created_at DATETIME,
    updated_at DATETIME,
    emergency_contact VARCHAR(15),
    emergency_name VARCHAR(100),
    bio TEXT
);

CREATE TABLE IF NOT EXISTS job_postings (
    id INT AUTO_INCREMENT PRIMARY KEY,  
    user_id INT,
    title VARCHAR(100),
    location VARCHAR(100),
    salary INT,
    job_type VARCHAR(100),
    experience VARCHAR(50),
    working_hours VARCHAR(50),
    urgency VARCHAR(50),
    contract_type VARCHAR(50),
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    posted_date DATETIME,
    status VARCHAR(20),
    applications_count INT,
    required_candidates INT,
    hired_count INT,
    is_closed TINYINT(1),
    auto_closed TINYINT(1),
    closed_date DATETIME,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,  
    job_id INT,
    job_title VARCHAR(100),
    employer_id VARCHAR(100),
    employer_name VARCHAR(100),
    applicant_id INT,
    applicant_name VARCHAR(100),
    applicant_phone VARCHAR(15),
    applicant_email VARCHAR(100),
    applicant_skills TEXT,
    applicant_experience VARCHAR(50),
    expected_salary INT,
    applied_date DATETIME,
    status VARCHAR(20),
    response_date DATETIME,
    response_message TEXT,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,  
    job_id INT,
    job_title VARCHAR(100),
    employer_id VARCHAR(100),
    employer_name VARCHAR(100),
    applicant_id INT,
    applicant_name VARCHAR(100),
    applicant_phone VARCHAR(15),
    applicant_email VARCHAR(100),
    applicant_skills TEXT,
    applicant_experience VARCHAR(50),
    expected_salary INT,
    offered_date DATETIME,
    status VARCHAR(20),
    expires_at DATETIME,
    response_date DATETIME,
    response_message TEXT,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS congratulations_dismissed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    application_id INT NOT NULL,
    dismissed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_dismissal (user_id, job_id, application_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
