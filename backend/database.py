"""
Module de connexion et gestion de la base de données MySQL
"""
import mysql.connector
from mysql.connector import Error
import logging
from typing import Optional, List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """Crée une nouvelle connexion à la base de données"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        logger.error(f"Erreur de connexion: {e}")
        raise


def execute_query(query: str, params: tuple = None, fetch: str = 'all') -> Any:
    """
    Exécute une requête SQL et retourne les résultats
    
    Args:
        query: Requête SQL
        params: Paramètres de la requête
        fetch: 'all', 'one', 'none' pour le type de fetch
    
    Returns:
        Résultats de la requête
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch == 'all':
            result = cursor.fetchall()
        elif fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'none':
            conn.commit()
            result = cursor.lastrowid
        else:
            result = None
        
        return result
    except Error as e:
        logger.error(f"Erreur SQL: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_many(query: str, params_list: List[tuple]) -> int:
    """Exécute une requête pour plusieurs ensembles de paramètres"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    except Error as e:
        logger.error(f"Erreur SQL: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


class get_cursor:
    """Context manager pour obtenir un curseur avec fermeture automatique"""
    def __init__(self, dictionary: bool = True):
        self.dictionary = dictionary
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=self.dictionary)
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
        return False


# ============================================================================
# Fonctions utilitaires pour les requêtes courantes
# ============================================================================

def get_all_departements() -> List[Dict]:
    """Récupère tous les départements"""
    return execute_query("SELECT * FROM departements ORDER BY nom")


def get_all_formations(dept_id: int = None) -> List[Dict]:
    """Récupère toutes les formations"""
    if dept_id:
        return execute_query(
            "SELECT * FROM formations WHERE dept_id = %s ORDER BY niveau, nom",
            (dept_id,)
        )
    return execute_query("SELECT * FROM formations ORDER BY dept_id, niveau, nom")


def get_all_modules(formation_id: int = None) -> List[Dict]:
    """Récupère tous les modules"""
    if formation_id:
        return execute_query(
            "SELECT * FROM modules WHERE formation_id = %s ORDER BY semestre, nom",
            (formation_id,)
        )
    return execute_query("SELECT * FROM modules ORDER BY formation_id, semestre, nom")


def get_all_professeurs(dept_id: int = None) -> List[Dict]:
    """Récupère tous les professeurs"""
    if dept_id:
        return execute_query(
            "SELECT * FROM professeurs WHERE dept_id = %s ORDER BY nom, prenom",
            (dept_id,)
        )
    return execute_query("SELECT * FROM professeurs ORDER BY dept_id, nom, prenom")


def get_all_salles(type_salle: str = None) -> List[Dict]:
    """Récupère toutes les salles"""
    if type_salle:
        return execute_query(
            "SELECT * FROM lieu_examen WHERE type = %s AND disponible = TRUE ORDER BY capacite DESC",
            (type_salle,)
        )
    return execute_query(
        "SELECT * FROM lieu_examen WHERE disponible = TRUE ORDER BY type, capacite DESC"
    )


def get_stats_departement() -> List[Dict]:
    """Récupère les statistiques par département"""
    return execute_query("SELECT * FROM v_stats_departement ORDER BY departement")


def get_conflits_actifs(session_id: int = None) -> List[Dict]:
    """Récupère les conflits non résolus"""
    query = """
        SELECT c.*, e1.date_examen, m1.nom AS module1_nom
        FROM conflits c
        JOIN examens e1 ON c.examen1_id = e1.id
        JOIN modules m1 ON e1.module_id = m1.id
        WHERE c.resolu = FALSE
    """
    if session_id:
        query += " AND e1.session_id = %s"
        return execute_query(query + " ORDER BY c.severite, c.created_at DESC", (session_id,))
    return execute_query(query + " ORDER BY c.severite, c.created_at DESC")


# ============================================================================
# Test de connexion
# ============================================================================

def test_connection() -> bool:
    """Teste la connexion à la base de données"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Connexion à la base de données réussie!")
        return True
    except Error as e:
        logger.error(f"Échec de la connexion: {e}")
        return False


if __name__ == "__main__":
    if test_connection():
        print("✅ Connexion réussie!")
        depts = get_all_departements()
        print(f"📊 Nombre de départements: {len(depts)}")
    else:
        print("❌ Échec de la connexion")
