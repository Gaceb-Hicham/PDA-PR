-- Script sécurisé pour ajouter la colonne groupe
-- Note: La colonne groupe est maintenant incluse dans schema.sql
-- Ce script existe pour compatibilité avec les anciennes bases

-- Ajouter la colonne si elle n'existe pas (pour migration)
-- MariaDB/MySQL ne supporte pas IF NOT EXISTS pour ADD COLUMN
-- Donc ce script peut générer une erreur si la colonne existe déjà

-- Si vous exécutez ce script sur une nouvelle base, ignorez les erreurs
-- ALTER TABLE examens ADD COLUMN groupe VARCHAR(20) DEFAULT NULL AFTER nb_etudiants_prevus;
-- CREATE INDEX IF NOT EXISTS idx_examens_groupe ON examens(groupe);
