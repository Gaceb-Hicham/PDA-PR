"""
Fonctions de données avec cache Streamlit
Réduction de la latence réseau via mise en cache
"""
import streamlit as st
from typing import List, Dict, Optional, Any

# Import database functions
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import execute_query


# Cache pour les données statiques (changent rarement)
@st.cache_data(ttl=300)  # 5 minutes
def get_departements_cached() -> List[Dict]:
    """Récupère les départements avec cache"""
    return execute_query("SELECT * FROM departements ORDER BY nom") or []


@st.cache_data(ttl=300)
def get_formations_cached(dept_id: Optional[int] = None) -> List[Dict]:
    """Récupère les formations avec cache"""
    if dept_id:
        return execute_query(
            "SELECT * FROM formations WHERE dept_id = %s ORDER BY niveau, nom",
            (dept_id,)
        ) or []
    return execute_query("SELECT * FROM formations ORDER BY dept_id, niveau, nom") or []


@st.cache_data(ttl=300)
def get_modules_cached(formation_id: Optional[int] = None, semestre: Optional[str] = None) -> List[Dict]:
    """Récupère les modules avec cache"""
    if formation_id and semestre:
        return execute_query(
            "SELECT * FROM modules WHERE formation_id = %s AND semestre = %s ORDER BY nom",
            (formation_id, semestre)
        ) or []
    if formation_id:
        return execute_query(
            "SELECT * FROM modules WHERE formation_id = %s ORDER BY semestre, nom",
            (formation_id,)
        ) or []
    return execute_query("SELECT * FROM modules ORDER BY formation_id, semestre, nom LIMIT 1000") or []


@st.cache_data(ttl=300)
def get_professeurs_cached(dept_id: Optional[int] = None) -> List[Dict]:
    """Récupère les professeurs avec cache"""
    if dept_id:
        return execute_query(
            "SELECT * FROM professeurs WHERE dept_id = %s ORDER BY nom, prenom",
            (dept_id,)
        ) or []
    return execute_query("SELECT * FROM professeurs ORDER BY dept_id, nom, prenom") or []


@st.cache_data(ttl=300)
def get_salles_cached() -> List[Dict]:
    """Récupère les salles avec cache"""
    return execute_query("SELECT * FROM lieu_examen WHERE disponible = TRUE ORDER BY capacite DESC") or []


@st.cache_data(ttl=300)
def get_creneaux_cached() -> List[Dict]:
    """Récupère les créneaux horaires avec cache"""
    return execute_query("SELECT * FROM creneaux_horaires ORDER BY ordre") or []


# Cache pour les statistiques (TTL plus court)
@st.cache_data(ttl=60)  # 1 minute
def get_stats_globales_cached() -> Dict[str, int]:
    """Récupère les statistiques globales avec cache"""
    result = execute_query("""
        SELECT 
            (SELECT COUNT(*) FROM departements) AS departements,
            (SELECT COUNT(*) FROM formations) AS formations,
            (SELECT COUNT(*) FROM modules) AS modules,
            (SELECT COUNT(*) FROM etudiants) AS etudiants,
            (SELECT COUNT(*) FROM professeurs) AS professeurs,
            (SELECT COUNT(*) FROM inscriptions) AS inscriptions,
            (SELECT COUNT(*) FROM lieu_examen WHERE disponible = TRUE) AS salles
    """, fetch='one')
    return result or {}


@st.cache_data(ttl=60)
def get_stats_departement_cached(dept_id: int) -> Dict:
    """Récupère les stats d'un département avec cache"""
    result = execute_query("""
        SELECT 
            d.nom AS departement,
            d.code,
            (SELECT COUNT(*) FROM formations WHERE dept_id = d.id) AS formations,
            (SELECT COUNT(*) FROM modules m JOIN formations f ON m.formation_id = f.id WHERE f.dept_id = d.id) AS modules,
            (SELECT COUNT(*) FROM etudiants e JOIN formations f ON e.formation_id = f.id WHERE f.dept_id = d.id) AS etudiants,
            (SELECT COUNT(*) FROM professeurs WHERE dept_id = d.id) AS professeurs
        FROM departements d
        WHERE d.id = %s
    """, (dept_id,), fetch='one')
    return result or {}


# Cache pour les sessions d'examens
@st.cache_data(ttl=60)
def get_sessions_examen_cached() -> List[Dict]:
    """Récupère les sessions d'examen avec cache"""
    return execute_query("""
        SELECT * FROM sessions_examen 
        ORDER BY date_debut DESC 
        LIMIT 10
    """) or []


# Fonction pour vider le cache manuellement
def clear_all_caches():
    """Vide tous les caches (après modification de données)"""
    get_departements_cached.clear()
    get_formations_cached.clear()
    get_modules_cached.clear()
    get_professeurs_cached.clear()
    get_salles_cached.clear()
    get_creneaux_cached.clear()
    get_stats_globales_cached.clear()
    get_stats_departement_cached.clear()
    get_sessions_examen_cached.clear()
