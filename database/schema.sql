-- ============================================================================
-- PLATEFORME D'OPTIMISATION DES EMPLOIS DU TEMPS D'EXAMENS UNIVERSITAIRES
-- Base de données: MySQL
-- Université M'Hamed Bougara - Faculté des Sciences
-- ============================================================================

-- Création de la base de données
DROP DATABASE IF EXISTS pda_examens;
CREATE DATABASE pda_examens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pda_examens;

-- ============================================================================
-- TABLE: departements
-- Description: Les 7 départements de la faculté
-- ============================================================================
CREATE TABLE departements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    chef_dept_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: formations
-- Description: Les programmes de formation (200+ formations, 6-9 modules chacune)
-- ============================================================================
CREATE TABLE formations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    dept_id INT NOT NULL,
    nb_modules INT NOT NULL DEFAULT 6 CHECK (nb_modules BETWEEN 6 AND 9),
    niveau ENUM('L1', 'L2', 'L3', 'M1', 'M2') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departements(id) ON DELETE RESTRICT,
    INDEX idx_dept (dept_id),
    INDEX idx_niveau (niveau)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: etudiants
-- Description: Les étudiants (13,000+ étudiants)
-- ============================================================================
CREATE TABLE etudiants (
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
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: modules
-- Description: Les modules de cours (6-9 par formation)
-- ============================================================================
CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(150) NOT NULL,
    credits INT NOT NULL DEFAULT 3 CHECK (credits BETWEEN 1 AND 10),
    formation_id INT NOT NULL,
    semestre ENUM('S1', 'S2') NOT NULL,
    coefficient DECIMAL(3,1) DEFAULT 1.0,
    pre_req_id INT NULL,
    duree_examen_minutes INT NOT NULL DEFAULT 90,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (formation_id) REFERENCES formations(id) ON DELETE CASCADE,
    FOREIGN KEY (pre_req_id) REFERENCES modules(id) ON DELETE SET NULL,
    INDEX idx_formation (formation_id),
    INDEX idx_semestre (semestre)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: lieu_examen
-- Description: Salles d'examen et amphithéâtres
-- ============================================================================
CREATE TABLE lieu_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    capacite INT NOT NULL CHECK (capacite > 0),
    type ENUM('AMPHI', 'SALLE', 'LABO') NOT NULL,
    batiment VARCHAR(50) NOT NULL,
    etage INT DEFAULT 0,
    equipements TEXT,
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_capacite (capacite),
    INDEX idx_batiment (batiment)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: professeurs
-- Description: Corps enseignant
-- ============================================================================
CREATE TABLE professeurs (
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
    INDEX idx_dept (dept_id),
    INDEX idx_nom_prenom (nom, prenom)
) ENGINE=InnoDB;

-- Mise à jour de la référence chef_dept dans departements
ALTER TABLE departements 
ADD FOREIGN KEY (chef_dept_id) REFERENCES professeurs(id) ON DELETE SET NULL;

-- ============================================================================
-- TABLE: inscriptions
-- Description: Inscriptions des étudiants aux modules (~130,000 inscriptions)
-- ============================================================================
CREATE TABLE inscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    module_id INT NOT NULL,
    annee_universitaire VARCHAR(9) NOT NULL DEFAULT '2025/2026',
    note DECIMAL(4,2) NULL CHECK (note IS NULL OR (note >= 0 AND note <= 20)),
    statut ENUM('INSCRIT', 'VALIDE', 'AJOURNE', 'ABSENT') DEFAULT 'INSCRIT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    UNIQUE KEY uk_inscription (etudiant_id, module_id, annee_universitaire),
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_module (module_id),
    INDEX idx_annee (annee_universitaire)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: sessions_examen
-- Description: Sessions/périodes d'examens
-- ============================================================================
CREATE TABLE sessions_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type_session ENUM('NORMALE', 'RATTRAPAGE') NOT NULL DEFAULT 'NORMALE',
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    annee_universitaire VARCHAR(9) NOT NULL DEFAULT '2025/2026',
    statut ENUM('PLANIFICATION', 'EN_COURS', 'TERMINEE', 'VALIDEE') DEFAULT 'PLANIFICATION',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (date_fin >= date_debut),
    INDEX idx_dates (date_debut, date_fin),
    INDEX idx_statut (statut)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: creneaux_horaires
-- Description: Créneaux horaires disponibles pour les examens
-- ============================================================================
CREATE TABLE creneaux_horaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    ordre INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (heure_fin > heure_debut),
    UNIQUE KEY uk_creneau (heure_debut, heure_fin)
) ENGINE=InnoDB;

-- Insertion des créneaux horaires standards
INSERT INTO creneaux_horaires (libelle, heure_debut, heure_fin, ordre) VALUES
('Matin 1', '08:00:00', '09:30:00', 1),
('Matin 2', '09:45:00', '11:15:00', 2),
('Matin 3', '11:30:00', '13:00:00', 3),
('Après-midi 1', '13:45:00', '15:15:00', 4),
('Après-midi 2', '15:30:00', '17:00:00', 5);

-- ============================================================================
-- TABLE: examens
-- Description: Planification des examens
-- ============================================================================
CREATE TABLE examens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    session_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_examen DATE NOT NULL,
    creneau_id INT NOT NULL,
    duree_minutes INT NOT NULL DEFAULT 90,
    nb_etudiants_prevus INT DEFAULT 0,
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
    INDEX idx_date (date_examen),
    INDEX idx_salle_date (salle_id, date_examen),
    INDEX idx_statut (statut)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: surveillances
-- Description: Affectation des surveillants aux examens
-- ============================================================================
CREATE TABLE surveillances (
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
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: utilisateurs
-- Description: Gestion des utilisateurs du système
-- ============================================================================
CREATE TABLE utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role ENUM('ADMIN', 'DOYEN', 'VICE_DOYEN', 'CHEF_DEPT', 'PROFESSEUR', 'ETUDIANT') NOT NULL,
    professeur_id INT NULL,
    etudiant_id INT NULL,
    dept_id INT NULL,
    actif BOOLEAN DEFAULT TRUE,
    derniere_connexion TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (professeur_id) REFERENCES professeurs(id) ON DELETE SET NULL,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE SET NULL,
    FOREIGN KEY (dept_id) REFERENCES departements(id) ON DELETE SET NULL,
    INDEX idx_role (role),
    INDEX idx_actif (actif)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: conflits
-- Description: Gestion des conflits détectés
-- ============================================================================
CREATE TABLE conflits (
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
    FOREIGN KEY (examen1_id) REFERENCES examens(id) ON DELETE CASCADE,
    FOREIGN KEY (examen2_id) REFERENCES examens(id) ON DELETE CASCADE,
    INDEX idx_type (type_conflit),
    INDEX idx_resolu (resolu),
    INDEX idx_severite (severite)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: logs_systeme
-- Description: Journalisation des actions système
-- ============================================================================
CREATE TABLE logs_systeme (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NULL,
    action VARCHAR(100) NOT NULL,
    table_cible VARCHAR(50),
    enregistrement_id INT,
    details JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_action (action),
    INDEX idx_date (created_at),
    INDEX idx_utilisateur (utilisateur_id)
) ENGINE=InnoDB;

-- ============================================================================
-- VUES UTILES
-- ============================================================================

-- Vue: Statistiques par département
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

-- Vue: Planning des examens avec détails
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

-- Vue: Charge de surveillance par professeur
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

-- ============================================================================
-- PROCÉDURES STOCKÉES
-- ============================================================================

DELIMITER //

-- Procédure: Vérifier les conflits étudiants (max 1 examen/jour)
CREATE PROCEDURE sp_check_conflits_etudiants(IN p_session_id INT)
BEGIN
    INSERT INTO conflits (type_conflit, examen1_id, examen2_id, entite_id, description, severite)
    SELECT 
        'ETUDIANT_DOUBLE',
        e1.id,
        e2.id,
        i1.etudiant_id,
        CONCAT('Étudiant ', et.nom, ' ', et.prenom, ' a 2 examens le ', e1.date_examen),
        'CRITIQUE'
    FROM examens e1
    JOIN examens e2 ON e1.date_examen = e2.date_examen 
        AND e1.id < e2.id 
        AND e1.session_id = e2.session_id
    JOIN inscriptions i1 ON i1.module_id = e1.module_id
    JOIN inscriptions i2 ON i2.module_id = e2.module_id AND i1.etudiant_id = i2.etudiant_id
    JOIN etudiants et ON et.id = i1.etudiant_id
    WHERE e1.session_id = p_session_id
        AND NOT EXISTS (
            SELECT 1 FROM conflits c 
            WHERE c.examen1_id = e1.id AND c.examen2_id = e2.id AND c.resolu = FALSE
        );
END //

-- Procédure: Vérifier les conflits professeurs (max 3 examens/jour)
CREATE PROCEDURE sp_check_conflits_professeurs(IN p_session_id INT)
BEGIN
    INSERT INTO conflits (type_conflit, examen1_id, entite_id, description, severite)
    SELECT 
        'PROF_SURCHARGE',
        MIN(e.id),
        p.id,
        CONCAT('Professeur ', p.nom, ' ', p.prenom, ' a ', COUNT(*), ' surveillances le ', e.date_examen),
        'MAJEUR'
    FROM surveillances s
    JOIN examens e ON s.examen_id = e.id
    JOIN professeurs p ON s.professeur_id = p.id
    WHERE e.session_id = p_session_id
    GROUP BY p.id, e.date_examen, p.nom, p.prenom
    HAVING COUNT(*) > 3;
END //

-- Procédure: Calculer les KPIs globaux
CREATE PROCEDURE sp_get_kpis_globaux(IN p_session_id INT)
BEGIN
    -- Taux d'occupation des salles
    SELECT 
        'Taux occupation salles' AS kpi,
        ROUND(
            (SELECT COUNT(DISTINCT salle_id, date_examen, creneau_id) FROM examens WHERE session_id = p_session_id) * 100.0 /
            (SELECT COUNT(*) * DATEDIFF(
                (SELECT date_fin FROM sessions_examen WHERE id = p_session_id),
                (SELECT date_debut FROM sessions_examen WHERE id = p_session_id)
            ) * 5 FROM lieu_examen WHERE disponible = TRUE), 2
        ) AS valeur,
        '%' AS unite
    UNION ALL
    -- Nombre total d'examens
    SELECT 'Nombre examens', COUNT(*), 'examens' 
    FROM examens WHERE session_id = p_session_id
    UNION ALL
    -- Nombre de conflits non résolus
    SELECT 'Conflits non résolus', COUNT(*), 'conflits'
    FROM conflits c
    JOIN examens e ON c.examen1_id = e.id
    WHERE e.session_id = p_session_id AND c.resolu = FALSE
    UNION ALL
    -- Moyenne surveillances par professeur
    SELECT 'Moyenne surveillances/prof', ROUND(AVG(nb_surv), 2), 'surveillances'
    FROM (
        SELECT COUNT(*) AS nb_surv
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        WHERE e.session_id = p_session_id
        GROUP BY s.professeur_id
    ) AS sub;
END //

DELIMITER ;

-- ============================================================================
-- INDEX POUR OPTIMISATION
-- ============================================================================

-- Index pour les examens (statut inclus pour filtrage rapide)
CREATE INDEX idx_examens_planifies ON examens(statut, date_examen, creneau_id);

-- Index pour les conflits (resolu inclus pour filtrage rapide)
CREATE INDEX idx_conflits_actifs ON conflits(resolu, type_conflit, severite);

-- Index pour les utilisateurs (actif inclus pour filtrage rapide)
CREATE INDEX idx_utilisateurs_actifs ON utilisateurs(actif, role, dept_id);

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

SELECT 'Base de données pda_examens créée avec succès!' AS message;
