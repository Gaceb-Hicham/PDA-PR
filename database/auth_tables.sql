-- Tables d'authentification supplémentaires
-- Note: La table 'utilisateurs' est définie dans schema.sql

-- Table des sessions de connexion
CREATE TABLE IF NOT EXISTS sessions_utilisateur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_sessions_token (token),
    INDEX idx_sessions_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table des logs de connexion
CREATE TABLE IF NOT EXISTS logs_connexion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT,
    action ENUM('LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_CHANGE') NOT NULL,
    ip_address VARCHAR(45),
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_logs_user (utilisateur_id),
    INDEX idx_logs_action (action),
    INDEX idx_logs_date (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Définition des permissions par rôle
CREATE TABLE IF NOT EXISTS permissions_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('ETUDIANT', 'PROFESSEUR', 'CHEF_DEPT', 'ADMIN', 'VICE_DOYEN', 'DOYEN') NOT NULL,
    page_key VARCHAR(50) NOT NULL,
    peut_voir BOOLEAN DEFAULT FALSE,
    peut_modifier BOOLEAN DEFAULT FALSE,
    
    UNIQUE KEY unique_role_page (role, page_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertion des permissions par défaut
INSERT INTO permissions_role (role, page_key, peut_voir, peut_modifier) VALUES
-- Étudiant: accès limité
('ETUDIANT', 'dashboard', TRUE, FALSE),
('ETUDIANT', 'export', TRUE, FALSE),

-- Professeur: accès lecture + export
('PROFESSEUR', 'dashboard', TRUE, FALSE),
('PROFESSEUR', 'plannings', TRUE, FALSE),
('PROFESSEUR', 'export', TRUE, FALSE),

-- Chef de département: + validation
('CHEF_DEPT', 'dashboard', TRUE, FALSE),
('CHEF_DEPT', 'plannings', TRUE, FALSE),
('CHEF_DEPT', 'export', TRUE, FALSE),
('CHEF_DEPT', 'validation_dept', TRUE, TRUE),

-- Admin: accès complet
('ADMIN', 'dashboard', TRUE, TRUE),
('ADMIN', 'configuration', TRUE, TRUE),
('ADMIN', 'donnees', TRUE, TRUE),
('ADMIN', 'generation', TRUE, TRUE),
('ADMIN', 'plannings', TRUE, TRUE),
('ADMIN', 'export', TRUE, TRUE),
('ADMIN', 'validation_dept', TRUE, TRUE),
('ADMIN', 'benchmarks', TRUE, TRUE),

-- Vice-doyen: accès total
('VICE_DOYEN', 'dashboard', TRUE, TRUE),
('VICE_DOYEN', 'configuration', TRUE, TRUE),
('VICE_DOYEN', 'donnees', TRUE, TRUE),
('VICE_DOYEN', 'generation', TRUE, TRUE),
('VICE_DOYEN', 'plannings', TRUE, TRUE),
('VICE_DOYEN', 'export', TRUE, TRUE),
('VICE_DOYEN', 'validation_dept', TRUE, TRUE),
('VICE_DOYEN', 'kpis_vicedoyen', TRUE, TRUE),
('VICE_DOYEN', 'benchmarks', TRUE, TRUE),

-- Doyen: accès total
('DOYEN', 'dashboard', TRUE, TRUE),
('DOYEN', 'configuration', TRUE, TRUE),
('DOYEN', 'donnees', TRUE, TRUE),
('DOYEN', 'generation', TRUE, TRUE),
('DOYEN', 'plannings', TRUE, TRUE),
('DOYEN', 'export', TRUE, TRUE),
('DOYEN', 'validation_dept', TRUE, TRUE),
('DOYEN', 'kpis_vicedoyen', TRUE, TRUE),
('DOYEN', 'benchmarks', TRUE, TRUE)
ON DUPLICATE KEY UPDATE peut_voir = VALUES(peut_voir), peut_modifier = VALUES(peut_modifier);
