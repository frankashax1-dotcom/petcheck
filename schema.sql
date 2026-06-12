-- PetCheck Database Schema
-- Run this in MySQL before starting the app

CREATE DATABASE IF NOT EXISTS petcheck;
USE petcheck;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('pet_owner', 'vet') DEFAULT 'pet_owner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pets table
CREATE TABLE IF NOT EXISTS pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    species ENUM('dog', 'cat') NOT NULL,
    breed VARCHAR(100),
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Diagnoses table
CREATE TABLE IF NOT EXISTS diagnoses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    pet_id INT,
    image_path VARCHAR(255),
    predicted_disease VARCHAR(200),
    confidence FLOAT,
    advice TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL
);

-- Vets / Clinics table
CREATE TABLE IF NOT EXISTS vets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    clinic_name VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(150),
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    specialization VARCHAR(200),
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample vet data for Entebbe area
INSERT INTO vets (name, clinic_name, phone, location, latitude, longitude, specialization) VALUES
('Dr. Ssali James', 'Entebbe Veterinary Clinic', '+256 700 123456', 'Division A, Entebbe', 0.0512, 32.4637, 'Dogs & Cats'),
('Dr. Nakato Sarah', 'PetCare Entebbe', '+256 782 654321', 'Division B, Entebbe', 0.0598, 32.4701, 'Small Animals'),
('Dr. Mukasa David', 'Animal Health Center', '+256 755 987654', 'Kampala Rd, Entebbe', 0.0476, 32.4589, 'General Veterinary');

-- Health articles table
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample articles
INSERT INTO articles (title, content, category) VALUES
('How to Spot Mange in Dogs Early', '<p>Mange is a common skin disease caused by mites...</p>', 'dogs'),
('Eye Infections in Cats: Causes & Treatment', '<p>Conjunctivitis is one of the most common conditions in cats...</p>', 'cats'),
('Feeding Your Dog the Right Diet in Uganda', '<p>Many pet owners feed their dogs table scraps...</p>', 'nutrition');

-- Forum posts table (no updated_at column to avoid errors)
CREATE TABLE IF NOT EXISTS forum_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Forum replies table
CREATE TABLE IF NOT EXISTS forum_replies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert sample forum posts
INSERT INTO forum_posts (user_id, title, body) VALUES
(1, 'Welcome to the PetCheck Forum!', 'This is a place where pet owners can share experiences and ask questions. Feel free to introduce yourself and your furry friends!'),
(1, 'My dog has a skin rash - what should I do?', 'I noticed my dog scratching a lot and saw red patches on his belly. Has anyone experienced this before?');

-- Insert sample replies
INSERT INTO forum_replies (post_id, user_id, body) VALUES
(2, 1, 'It could be allergies or a skin infection. I recommend taking your dog to a vet for proper diagnosis. In the meantime, keep the area clean and prevent scratching.');