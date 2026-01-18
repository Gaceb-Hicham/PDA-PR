-- ════════════════════════════════════════════════════════════════════════════════
-- PROCÉDURES STOCKÉES ET INDEX - Optimisation PDA Examens
-- Conformément aux exigences: "Optimisation: Procédures PL/pgSQL + index partiels"
-- ════════════════════════════════════════════════════════════════════════════════

-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  INDEX PARTIELS POUR PERFORMANCE                                              ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

-- Index sur les examens par session et date (requêtes fréquentes)
CREATE INDEX IF NOT EXISTS idx_examens_session_date 
ON examens(session_id, date_examen);

-- Index sur les surveillances par examen
CREATE INDEX IF NOT EXISTS idx_surveillances_examen 
ON surveillances(examen_id);

-- Index sur les inscriptions par module (jointures fréquentes)
CREATE INDEX IF NOT EXISTS idx_inscriptions_module 
ON inscriptions(module_id);

-- Index sur les inscriptions par étudiant
CREATE INDEX IF NOT EXISTS idx_inscriptions_etudiant 
ON inscriptions(etudiant_id);

-- Index sur les modules par formation et semestre
CREATE INDEX IF NOT EXISTS idx_modules_formation_semestre 
ON modules(formation_id, semestre);

-- Index sur les formations par département
CREATE INDEX IF NOT EXISTS idx_formations_dept 
ON formations(dept_id);

-- Index sur les professeurs par département
CREATE INDEX IF NOT EXISTS idx_professeurs_dept 
ON professeurs(dept_id);

-- Index sur les conflits non résolus
CREATE INDEX IF NOT EXISTS idx_conflits_non_resolus 
ON conflits(resolu, type_conflit);


-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  PROCÉDURES STOCKÉES                                                          ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

DELIMITER //

-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: Détection des conflits étudiants (plus d'un examen par jour)
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_detect_student_conflicts//
CREATE PROCEDURE sp_detect_student_conflicts(IN p_session_id INT)
BEGIN
    SELECT 
        e.id AS etudiant_id, 
        e.nom, 
        e.prenom, 
        ex1.date_examen,
        m1.code AS module1, 
        m2.code AS module2,
        COUNT(*) AS nb_conflits
    FROM inscriptions i1
    JOIN inscriptions i2 ON i1.etudiant_id = i2.etudiant_id AND i1.module_id < i2.module_id
    JOIN examens ex1 ON ex1.module_id = i1.module_id AND ex1.session_id = p_session_id
    JOIN examens ex2 ON ex2.module_id = i2.module_id AND ex2.session_id = p_session_id
    JOIN modules m1 ON i1.module_id = m1.id
    JOIN modules m2 ON i2.module_id = m2.id
    JOIN etudiants e ON i1.etudiant_id = e.id
    WHERE ex1.date_examen = ex2.date_examen
    GROUP BY e.id, ex1.date_examen
    LIMIT 100;
END//


-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: Statistiques globales optimisées
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_get_global_stats//
CREATE PROCEDURE sp_get_global_stats()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM etudiants) AS total_etudiants,
        (SELECT COUNT(*) FROM professeurs) AS total_professeurs,
        (SELECT COUNT(*) FROM formations) AS total_formations,
        (SELECT COUNT(*) FROM modules) AS total_modules,
        (SELECT COUNT(*) FROM inscriptions) AS total_inscriptions,
        (SELECT COUNT(*) FROM lieu_examen WHERE disponible = TRUE) AS total_salles,
        (SELECT COUNT(*) FROM departements) AS total_departements;
END//


-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: KPIs par département
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_get_department_kpis//
CREATE PROCEDURE sp_get_department_kpis(IN p_session_id INT)
BEGIN
    SELECT 
        d.id AS dept_id,
        d.nom AS departement,
        d.code,
        COUNT(DISTINCT e.id) AS nb_examens,
        COUNT(DISTINCT s.professeur_id) AS nb_surveillants_actifs,
        COUNT(s.id) AS total_surveillances,
        ROUND(COUNT(s.id) / NULLIF(COUNT(DISTINCT s.professeur_id), 0), 2) AS moyenne_surv_par_prof,
        (SELECT COUNT(*) FROM conflits c 
         JOIN examens ex ON c.examen1_id = ex.id 
         JOIN modules m ON ex.module_id = m.id
         JOIN formations f ON m.formation_id = f.id
         WHERE f.dept_id = d.id AND ex.session_id = p_session_id AND c.resolu = FALSE
        ) AS nb_conflits
    FROM departements d
    LEFT JOIN formations f ON f.dept_id = d.id
    LEFT JOIN modules m ON m.formation_id = f.id
    LEFT JOIN examens e ON e.module_id = m.id AND e.session_id = p_session_id
    LEFT JOIN surveillances s ON s.examen_id = e.id
    GROUP BY d.id
    ORDER BY d.nom;
END//


-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: Taux d'utilisation des salles
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_get_room_utilization//
CREATE PROCEDURE sp_get_room_utilization(IN p_session_id INT)
BEGIN
    DECLARE v_total_slots INT;
    DECLARE v_session_days INT;
    DECLARE v_creneaux_per_day INT;
    
    -- Calculer le nombre total de créneaux disponibles
    SELECT COUNT(*) INTO v_creneaux_per_day FROM creneaux_horaires;
    
    SELECT DATEDIFF(date_fin, date_debut) + 1 INTO v_session_days
    FROM sessions_examen WHERE id = p_session_id;
    
    SET v_total_slots = v_session_days * v_creneaux_per_day;
    
    SELECT 
        l.id,
        l.nom,
        l.code,
        l.type,
        l.capacite,
        COUNT(e.id) AS nb_examens,
        ROUND((COUNT(e.id) / v_total_slots) * 100, 2) AS taux_utilisation
    FROM lieu_examen l
    LEFT JOIN examens e ON e.salle_id = l.id AND e.session_id = p_session_id
    WHERE l.disponible = TRUE
    GROUP BY l.id
    ORDER BY taux_utilisation DESC;
END//


-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: Charge de travail des professeurs
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_get_professor_workload//
CREATE PROCEDURE sp_get_professor_workload(IN p_session_id INT)
BEGIN
    SELECT 
        p.id,
        p.nom,
        p.prenom,
        p.grade,
        d.nom AS departement,
        COUNT(s.id) AS total_surveillances,
        COUNT(DISTINCT e.date_examen) AS nb_jours_travail,
        ROUND(COUNT(s.id) * 1.5, 2) AS heures_totales,
        MAX(daily_count.surv_par_jour) AS max_surv_jour
    FROM professeurs p
    JOIN departements d ON p.dept_id = d.id
    LEFT JOIN surveillances s ON s.professeur_id = p.id
    LEFT JOIN examens e ON s.examen_id = e.id AND e.session_id = p_session_id
    LEFT JOIN (
        SELECT s2.professeur_id, e2.date_examen, COUNT(*) AS surv_par_jour
        FROM surveillances s2
        JOIN examens e2 ON s2.examen_id = e2.id
        WHERE e2.session_id = p_session_id
        GROUP BY s2.professeur_id, e2.date_examen
    ) daily_count ON daily_count.professeur_id = p.id
    GROUP BY p.id
    ORDER BY total_surveillances DESC;
END//


-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: Validation du planning (pour chef de département)
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_validate_department_schedule//
CREATE PROCEDURE sp_validate_department_schedule(
    IN p_session_id INT,
    IN p_dept_id INT,
    IN p_validated_by INT,
    IN p_comments TEXT
)
BEGIN
    -- Mettre à jour le statut de validation pour tous les examens du département
    UPDATE examens e
    JOIN modules m ON e.module_id = m.id
    JOIN formations f ON m.formation_id = f.id
    SET e.statut = 'VALIDE',
        e.validated_by = p_validated_by,
        e.validated_at = NOW(),
        e.validation_comments = p_comments
    WHERE e.session_id = p_session_id AND f.dept_id = p_dept_id;
    
    SELECT ROW_COUNT() AS examens_valides;
END//


-- ────────────────────────────────────────────────────────────────────────────────
-- Procédure: Benchmark de performance
-- ────────────────────────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_run_benchmark//
CREATE PROCEDURE sp_run_benchmark()
BEGIN
    DECLARE v_start DATETIME(6);
    DECLARE v_end DATETIME(6);
    DECLARE v_duration_ms DECIMAL(10,3);
    
    -- Test 1: Count inscriptions
    SET v_start = NOW(6);
    SELECT COUNT(*) INTO @cnt FROM inscriptions;
    SET v_end = NOW(6);
    SET v_duration_ms = TIMESTAMPDIFF(MICROSECOND, v_start, v_end) / 1000;
    SELECT 'COUNT inscriptions' AS test, @cnt AS result, v_duration_ms AS duration_ms;
    
    -- Test 2: Join complexe
    SET v_start = NOW(6);
    SELECT COUNT(*) INTO @cnt 
    FROM inscriptions i 
    JOIN etudiants e ON i.etudiant_id = e.id
    JOIN modules m ON i.module_id = m.id
    JOIN formations f ON m.formation_id = f.id;
    SET v_end = NOW(6);
    SET v_duration_ms = TIMESTAMPDIFF(MICROSECOND, v_start, v_end) / 1000;
    SELECT 'JOIN 4 tables' AS test, @cnt AS result, v_duration_ms AS duration_ms;
END//

DELIMITER ;


-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  COLONNES ADDITIONNELLES POUR VALIDATION                                      ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

-- Ajouter colonnes de validation à la table examens (si elles n'existent pas)
ALTER TABLE examens 
ADD COLUMN IF NOT EXISTS statut ENUM('PLANIFIE', 'VALIDE', 'ANNULE') DEFAULT 'PLANIFIE',
ADD COLUMN IF NOT EXISTS validated_by INT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS validated_at DATETIME DEFAULT NULL,
ADD COLUMN IF NOT EXISTS validation_comments TEXT DEFAULT NULL;

-- Index sur le statut
CREATE INDEX IF NOT EXISTS idx_examens_statut ON examens(statut);


-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  VUES OPTIMISÉES                                                              ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝

-- Vue: Résumé des examens par département
CREATE OR REPLACE VIEW v_exams_by_department AS
SELECT 
    d.id AS dept_id,
    d.nom AS departement,
    d.code AS dept_code,
    e.session_id,
    COUNT(DISTINCT e.id) AS total_examens,
    COUNT(DISTINCT e.module_id) AS modules_planifies,
    SUM(e.nb_etudiants_prevus) AS total_etudiants,
    COUNT(DISTINCT e.salle_id) AS salles_utilisees
FROM departements d
LEFT JOIN formations f ON f.dept_id = d.id
LEFT JOIN modules m ON m.formation_id = f.id
LEFT JOIN examens e ON e.module_id = m.id
GROUP BY d.id, e.session_id;


-- Vue: Charge de surveillance par professeur
CREATE OR REPLACE VIEW v_professor_surveillance_load AS
SELECT 
    p.id AS prof_id,
    p.nom,
    p.prenom,
    p.grade,
    d.nom AS departement,
    COUNT(s.id) AS total_surveillances,
    COUNT(DISTINCT e.date_examen) AS jours_travail
FROM professeurs p
JOIN departements d ON p.dept_id = d.id
LEFT JOIN surveillances s ON s.professeur_id = p.id
LEFT JOIN examens e ON s.examen_id = e.id
GROUP BY p.id;


-- ════════════════════════════════════════════════════════════════════════════════
-- FIN DU SCRIPT - Exécuter avec: mysql -u root -p pda_examens < stored_procedures.sql
-- ════════════════════════════════════════════════════════════════════════════════
