-- Script pour TiDB Cloud (utilise la base 'test')
-- Exécuter ce script dans TiDB SQL Editor

-- TABLE: departements
CREATE TABLE IF NOT EXISTS departements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    chef_dept_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- TABLE: formations
CREATE TABLE IF NOT EXISTS formations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    dept_id INT NOT NULL,
    nb_modules INT NOT NULL DEFAULT 6,
    niveau ENUM('L1', 'L2', 'L3', 'M1', 'M2') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departements(id) ON DELETE RESTRICT,
    INDEX idx_dept (dept_id),
    INDEX idx_niveau (niveau)
);

-- TABLE: etudiants
CREATE TABLE IF NOT EXISTS etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricule VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    formation_id INT NOT NULL,
    promo INT NOT NULL,
    groupe VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (formation_id) REFERENCES formations(id) ON DELETE RESTRICT,
    INDEX idx_formation (formation_id),
    INDEX idx_promo (promo),
    INDEX idx_nom_prenom (nom, prenom)
);

-- TABLE: modules
CREATE TABLE IF NOT EXISTS modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(150) NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    formation_id INT NOT NULL,
    semestre ENUM('S1', 'S2') NOT NULL,
    coefficient DECIMAL(3,1) DEFAULT 1.0,
    pre_req_id INT NULL,
    duree_examen_minutes INT NOT NULL DEFAULT 90,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (formation_id) REFERENCES formations(id) ON DELETE CASCADE,
    INDEX idx_formation (formation_id),
    INDEX idx_semestre (semestre)
);

-- TABLE: lieu_examen
CREATE TABLE IF NOT EXISTS lieu_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    capacite INT NOT NULL,
    type ENUM('AMPHI', 'SALLE', 'LABO') NOT NULL,
    batiment VARCHAR(50) NOT NULL,
    etage INT DEFAULT 0,
    equipements TEXT,
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_capacite (capacite)
);

-- TABLE: professeurs
CREATE TABLE IF NOT EXISTS professeurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricule VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    dept_id INT NOT NULL,
    specialite VARCHAR(150),
    grade ENUM('MAA', 'MAB', 'MCA', 'MCB', 'PR') NOT NULL DEFAULT 'MAB',
    max_surveillances_jour INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departements(id) ON DELETE RESTRICT,
    INDEX idx_dept (dept_id)
);

-- TABLE: inscriptions
CREATE TABLE IF NOT EXISTS inscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    module_id INT NOT NULL,
    annee_universitaire VARCHAR(9) NOT NULL DEFAULT '2025/2026',
    note DECIMAL(4,2) NULL,
    statut ENUM('INSCRIT', 'VALIDE', 'AJOURNE', 'ABSENT') DEFAULT 'INSCRIT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    UNIQUE KEY uk_inscription (etudiant_id, module_id, annee_universitaire),
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_module (module_id)
);

-- TABLE: sessions_examen
CREATE TABLE IF NOT EXISTS sessions_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type_session ENUM('NORMALE', 'RATTRAPAGE') NOT NULL DEFAULT 'NORMALE',
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    annee_universitaire VARCHAR(9) NOT NULL DEFAULT '2025/2026',
    statut ENUM('PLANIFICATION', 'EN_COURS', 'TERMINEE', 'VALIDEE') DEFAULT 'PLANIFICATION',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_dates (date_debut, date_fin),
    INDEX idx_statut (statut)
);

-- TABLE: creneaux_horaires
CREATE TABLE IF NOT EXISTS creneaux_horaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    ordre INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_creneau (heure_debut, heure_fin)
);

-- Insertion créneaux
INSERT IGNORE INTO creneaux_horaires (libelle, heure_debut, heure_fin, ordre) VALUES
('Matin 1', '08:00:00', '09:30:00', 1),
('Matin 2', '09:45:00', '11:15:00', 2),
('Matin 3', '11:30:00', '13:00:00', 3),
('Après-midi 1', '13:45:00', '15:15:00', 4),
('Après-midi 2', '15:30:00', '17:00:00', 5);

-- TABLE: examens
CREATE TABLE IF NOT EXISTS examens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    session_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_examen DATE NOT NULL,
    creneau_id INT NOT NULL,
    duree_minutes INT NOT NULL DEFAULT 90,
    nb_etudiants_prevus INT DEFAULT 0,
    groupe VARCHAR(20) NULL,
    statut ENUM('PLANIFIE', 'EN_COURS', 'TERMINE', 'ANNULE') DEFAULT 'PLANIFIE',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions_examen(id) ON DELETE CASCADE,
    FOREIGN KEY (salle_id) REFERENCES lieu_examen(id) ON DELETE RESTRICT,
    FOREIGN KEY (creneau_id) REFERENCES creneaux_horaires(id) ON DELETE RESTRICT,
    INDEX idx_module (module_id),
    INDEX idx_session (session_id),
    INDEX idx_date (date_examen)
);

-- TABLE: surveillances
CREATE TABLE IF NOT EXISTS surveillances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    examen_id INT NOT NULL,
    professeur_id INT NOT NULL,
    role ENUM('SURVEILLANT') NOT NULL DEFAULT 'SURVEILLANT',
    present BOOLEAN DEFAULT NULL,
    remarques TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (examen_id) REFERENCES examens(id) ON DELETE CASCADE,
    FOREIGN KEY (professeur_id) REFERENCES professeurs(id) ON DELETE CASCADE,
    UNIQUE KEY uk_surveillance (examen_id, professeur_id),
    INDEX idx_examen (examen_id),
    INDEX idx_professeur (professeur_id)
);

-- TABLE: utilisateurs
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('ETUDIANT', 'PROFESSEUR', 'CHEF_DEPT', 'ADMIN', 'VICE_DOYEN') NOT NULL,
    niveau_acces INT DEFAULT 1,
    etudiant_id INT DEFAULT NULL,
    professeur_id INT DEFAULT NULL,
    dept_id INT DEFAULT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    actif BOOLEAN DEFAULT TRUE,
    premiere_connexion BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    INDEX idx_role (role),
    INDEX idx_email (email)
);

-- TABLE: conflits
CREATE TABLE IF NOT EXISTS conflits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_conflit ENUM('ETUDIANT_DOUBLE', 'PROF_SURCHARGE', 'SALLE_PLEINE', 'HORAIRE_OVERLAP') NOT NULL,
    examen1_id INT NOT NULL,
    examen2_id INT NULL,
    entite_id INT NULL,
    description TEXT NOT NULL,
    severite ENUM('CRITIQUE', 'MAJEUR', 'MINEUR') NOT NULL DEFAULT 'MAJEUR',
    resolu BOOLEAN DEFAULT FALSE,
    date_resolution TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type_conflit),
    INDEX idx_resolu (resolu)
);

-- TABLE: logs
CREATE TABLE IF NOT EXISTS logs_connexion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT,
    action ENUM('LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_CHANGE') NOT NULL,
    ip_address VARCHAR(45),
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (utilisateur_id),
    INDEX idx_action (action)
);

-- TABLE: permissions
CREATE TABLE IF NOT EXISTS permissions_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('ETUDIANT', 'PROFESSEUR', 'CHEF_DEPT', 'ADMIN', 'VICE_DOYEN') NOT NULL,
    page_key VARCHAR(50) NOT NULL,
    peut_voir BOOLEAN DEFAULT FALSE,
    peut_modifier BOOLEAN DEFAULT FALSE,
    UNIQUE KEY unique_role_page (role, page_key)
);

-- Permissions par défaut
INSERT IGNORE INTO permissions_role (role, page_key, peut_voir, peut_modifier) VALUES
('ETUDIANT', 'dashboard', TRUE, FALSE),
('ETUDIANT', 'export', TRUE, FALSE),
('PROFESSEUR', 'dashboard', TRUE, FALSE),
('PROFESSEUR', 'export', TRUE, FALSE),
('CHEF_DEPT', 'dashboard', TRUE, FALSE),
('CHEF_DEPT', 'plannings', TRUE, FALSE),
('CHEF_DEPT', 'export', TRUE, FALSE),
('CHEF_DEPT', 'validation_dept', TRUE, TRUE),
('ADMIN', 'dashboard', TRUE, TRUE),
('ADMIN', 'configuration', TRUE, TRUE),
('ADMIN', 'donnees', TRUE, TRUE),
('ADMIN', 'generation', TRUE, TRUE),
('ADMIN', 'plannings', TRUE, TRUE),
('ADMIN', 'export', TRUE, TRUE),
('ADMIN', 'validation_dept', TRUE, TRUE),
('ADMIN', 'benchmarks', TRUE, TRUE),
('VICE_DOYEN', 'dashboard', TRUE, TRUE),
('VICE_DOYEN', 'configuration', TRUE, TRUE),
('VICE_DOYEN', 'donnees', TRUE, TRUE),
('VICE_DOYEN', 'generation', TRUE, TRUE),
('VICE_DOYEN', 'plannings', TRUE, TRUE),
('VICE_DOYEN', 'export', TRUE, TRUE),
('VICE_DOYEN', 'validation_dept', TRUE, TRUE),
('VICE_DOYEN', 'kpis_vicedoyen', TRUE, TRUE),
('VICE_DOYEN', 'benchmarks', TRUE, TRUE);

-- Vue: Stats département
CREATE OR REPLACE VIEW v_stats_departement AS
SELECT 
    d.id AS dept_id,
    d.nom AS departement,
    d.code,
    COUNT(DISTINCT f.id) AS nb_formations,
    COUNT(DISTINCT e.id) AS nb_etudiants,
    COUNT(DISTINCT p.id) AS nb_professeurs,
    COUNT(DISTINCT m.id) AS nb_modules
FROM departements d
LEFT JOIN formations f ON f.dept_id = d.id
LEFT JOIN etudiants e ON e.formation_id = f.id
LEFT JOIN professeurs p ON p.dept_id = d.id
LEFT JOIN modules m ON m.formation_id = f.id
GROUP BY d.id, d.nom, d.code;

-- Vue: Planning examens
CREATE OR REPLACE VIEW v_planning_examens AS
SELECT 
    ex.id AS examen_id,
    ex.date_examen,
    ch.libelle AS creneau,
    ch.heure_debut,
    ch.heure_fin,
    m.code AS module_code,
    m.nom AS module_nom,
    f.code AS formation_code,
    f.nom AS formation_nom,
    d.nom AS departement,
    l.nom AS salle,
    l.capacite AS capacite_salle,
    ex.nb_etudiants_prevus,
    ex.statut,
    se.nom AS session_nom
FROM examens ex
JOIN modules m ON ex.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
JOIN lieu_examen l ON ex.salle_id = l.id
JOIN creneaux_horaires ch ON ex.creneau_id = ch.id
JOIN sessions_examen se ON ex.session_id = se.id
ORDER BY ex.date_examen, ch.ordre;

-- Vue: Charge surveillance
CREATE OR REPLACE VIEW v_charge_surveillance AS
SELECT 
    p.id AS professeur_id,
    p.nom,
    p.prenom,
    d.nom AS departement,
    COUNT(s.id) AS nb_surveillances
FROM professeurs p
JOIN departements d ON p.dept_id = d.id
LEFT JOIN surveillances s ON s.professeur_id = p.id
GROUP BY p.id, p.nom, p.prenom, d.nom
ORDER BY nb_surveillances DESC;
