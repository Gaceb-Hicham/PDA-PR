-- OPTIMISATION PDA EXAMENS: Index et Vues
-- Note: Les procédures stockées ont été converties en fonctions Python pour compatibilité cloud

-- INDEX POUR PERFORMANCE

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

-- Index sur le statut des examens
CREATE INDEX IF NOT EXISTS idx_examens_statut 
ON examens(statut);


-- VUES POUR STATISTIQUES

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


-- Vue: Statistiques par département
CREATE OR REPLACE VIEW v_stats_departement AS
SELECT 
    d.id AS dept_id,
    d.nom AS departement,
    d.code,
    COUNT(DISTINCT f.id) AS nb_formations,
    COUNT(DISTINCT m.id) AS nb_modules,
    COUNT(DISTINCT et.id) AS nb_etudiants,
    COUNT(DISTINCT p.id) AS nb_professeurs
FROM departements d
LEFT JOIN formations f ON f.dept_id = d.id
LEFT JOIN modules m ON m.formation_id = f.id
LEFT JOIN etudiants et ON et.formation_id = f.id
LEFT JOIN professeurs p ON p.dept_id = d.id
GROUP BY d.id;


-- Vue: Planning des examens
CREATE OR REPLACE VIEW v_planning_examens AS
SELECT 
    e.id AS examen_id,
    e.date_examen,
    c.libelle AS creneau,
    c.heure_debut,
    c.heure_fin,
    m.code AS module_code,
    m.nom AS module_nom,
    f.nom AS formation,
    f.niveau,
    d.nom AS departement,
    l.nom AS salle,
    l.capacite,
    e.nb_etudiants_prevus,
    e.groupe,
    e.statut
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
JOIN lieu_examen l ON e.salle_id = l.id
JOIN creneaux_horaires c ON e.creneau_id = c.id
ORDER BY e.date_examen, c.ordre;


-- Vue: Charge de surveillance (compatible avec l'app)
CREATE OR REPLACE VIEW v_charge_surveillance AS
SELECT 
    p.id AS professeur_id,
    p.nom,
    p.prenom,
    p.grade,
    d.nom AS departement,
    d.code AS dept_code,
    COUNT(s.id) AS nb_surveillances,
    p.max_surveillances_jour
FROM professeurs p
JOIN departements d ON p.dept_id = d.id
LEFT JOIN surveillances s ON s.professeur_id = p.id
GROUP BY p.id;
