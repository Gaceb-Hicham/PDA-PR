-- ════════════════════════════════════════════════════════════════════════════════
-- TABLE D'AUTHENTIFICATION ET CONTRÔLE D'ACCÈS
-- Système de gestion des utilisateurs avec rôles hiérarchiques
-- ════════════════════════════════════════════════════════════════════════════════

-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  TABLE PRINCIPALE DES UTILISATEURS                                            ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Identifiants de connexion
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    
    -- Rôle et niveau d'accès
    role ENUM('ETUDIANT', 'PROFESSEUR', 'CHEF_DEPT', 'ADMIN', 'VICE_DOYEN') NOT NULL,
    niveau_acces INT DEFAULT 1,
    
    -- Liens vers les entités (selon le type d'utilisateur)
    etudiant_id INT DEFAULT NULL,
    professeur_id INT DEFAULT NULL,
    dept_id INT DEFAULT NULL,
    
    -- Informations personnelles
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    
    -- État du compte
    actif BOOLEAN DEFAULT TRUE,
    premiere_connexion BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    
    -- Contraintes
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE SET NULL,
    FOREIGN KEY (professeur_id) REFERENCES professeurs(id) ON DELETE SET NULL,
    FOREIGN KEY (dept_id) REFERENCES departements(id) ON DELETE SET NULL,
    
    -- Index pour recherche rapide
    INDEX idx_utilisateurs_role (role),
    INDEX idx_utilisateurs_email (email),
    INDEX idx_utilisateurs_etudiant (etudiant_id),
    INDEX idx_utilisateurs_professeur (professeur_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  TABLE DES SESSIONS DE CONNEXION                                              ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

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


-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  TABLE DES LOGS D'ACTIVITÉ                                                    ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

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


-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  DÉFINITION DES PERMISSIONS PAR RÔLE                                          ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS permissions_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('ETUDIANT', 'PROFESSEUR', 'CHEF_DEPT', 'ADMIN', 'VICE_DOYEN') NOT NULL,
    page_key VARCHAR(50) NOT NULL,
    peut_voir BOOLEAN DEFAULT FALSE,
    peut_modifier BOOLEAN DEFAULT FALSE,
    
    UNIQUE KEY unique_role_page (role, page_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertion des permissions par défaut
INSERT INTO permissions_role (role, page_key, peut_voir, peut_modifier) VALUES
-- Étudiant: accès limité
('ETUDIANT', 'dashboard', TRUE, FALSE),
('ETUDIANT', 'plannings', TRUE, FALSE),

-- Professeur: accès lecture + export
('PROFESSEUR', 'dashboard', TRUE, FALSE),
('PROFESSEUR', 'plannings', TRUE, FALSE),
('PROFESSEUR', 'export', TRUE, FALSE),

-- Chef de département: + validation
('CHEF_DEPT', 'dashboard', TRUE, FALSE),
('CHEF_DEPT', 'plannings', TRUE, FALSE),
('CHEF_DEPT', 'export', TRUE, FALSE),
('CHEF_DEPT', 'validation_dept', TRUE, TRUE),

-- Admin: accès complet sauf KPIs Vice-doyen
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
('VICE_DOYEN', 'benchmarks', TRUE, TRUE)
ON DUPLICATE KEY UPDATE peut_voir = VALUES(peut_voir), peut_modifier = VALUES(peut_modifier);


-- ════════════════════════════════════════════════════════════════════════════════
-- FIN DU SCRIPT
-- Exécuter avec: mysql -u root -p pda_examens < auth_tables.sql
-- ════════════════════════════════════════════════════════════════════════════════
