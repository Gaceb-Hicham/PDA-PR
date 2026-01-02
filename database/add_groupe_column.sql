-- Ajouter la colonne 'groupe' à la table examens pour la gestion des groupes
-- Chaque groupe d'une formation peut avoir sa propre salle pour le même examen

ALTER TABLE examens ADD COLUMN groupe VARCHAR(20) DEFAULT NULL AFTER nb_etudiants_prevus;

-- Ajouter un index pour améliorer les recherches par groupe
CREATE INDEX idx_examens_groupe ON examens(groupe);

-- Mettre à jour le schéma pour permettre plusieurs examens par module (un par groupe)
-- Note: le même module peut avoir plusieurs lignes (une par groupe) avec la même date/créneau mais des salles différentes

ANALYZE TABLE examens;
