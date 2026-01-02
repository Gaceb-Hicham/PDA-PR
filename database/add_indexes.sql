-- Script pour ajouter des index critiques pour la performance
-- Ces indexes accélèrent les requêtes de jointure fréquentes

-- Index composés pour les requêtes de planning
CREATE INDEX IF NOT EXISTS idx_examens_session_date ON examens(session_id, date_examen);
CREATE INDEX IF NOT EXISTS idx_examens_date_creneau ON examens(date_examen, creneau_id);

-- Index pour accélérer les jointures modules->formations
CREATE INDEX IF NOT EXISTS idx_modules_formation ON modules(formation_id);
CREATE INDEX IF NOT EXISTS idx_modules_semestre ON modules(semestre);

-- Index pour les jointures formations->departements
CREATE INDEX IF NOT EXISTS idx_formations_dept ON formations(dept_id);
CREATE INDEX IF NOT EXISTS idx_formations_niveau ON formations(niveau);

-- Index pour les jointures etudiants->formations
CREATE INDEX IF NOT EXISTS idx_etudiants_formation ON etudiants(formation_id);

-- Index pour les jointures professeurs->departements
CREATE INDEX IF NOT EXISTS idx_professeurs_dept ON professeurs(dept_id);

-- Index composite pour les surveillances avec jointure
CREATE INDEX IF NOT EXISTS idx_surveillances_exam_prof ON surveillances(examen_id, professeur_id);

-- Optimiser le tri des créneaux horaires
CREATE INDEX IF NOT EXISTS idx_creneaux_ordre ON creneaux_horaires(ordre);

-- Index pour les salles
CREATE INDEX IF NOT EXISTS idx_salles_disponible ON lieu_examen(disponible);
CREATE INDEX IF NOT EXISTS idx_salles_type_capacite ON lieu_examen(type, capacite);

ANALYZE TABLE departements, formations, modules, etudiants, professeurs, inscriptions, examens, surveillances, lieu_examen, creneaux_horaires;
