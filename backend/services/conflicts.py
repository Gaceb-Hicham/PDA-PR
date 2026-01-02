"""
Service de détection des conflits - VERSION OPTIMISÉE
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
from database import execute_query


def detect_student_conflicts(session_id: int) -> List[Dict]:
    """Détecte les étudiants avec plus d'un examen le même jour - LIMITÉ"""
    return execute_query("""
        SELECT e.id AS etudiant_id, e.nom, e.prenom, ex1.date_examen,
               m1.code AS module1, m2.code AS module2
        FROM inscriptions i1
        JOIN inscriptions i2 ON i1.etudiant_id = i2.etudiant_id AND i1.module_id < i2.module_id
        JOIN examens ex1 ON ex1.module_id = i1.module_id AND ex1.session_id = %s
        JOIN examens ex2 ON ex2.module_id = i2.module_id AND ex2.session_id = %s
        JOIN modules m1 ON i1.module_id = m1.id
        JOIN modules m2 ON i2.module_id = m2.id
        JOIN etudiants e ON i1.etudiant_id = e.id
        WHERE ex1.date_examen = ex2.date_examen
        LIMIT 50
    """, (session_id, session_id)) or []


def detect_room_conflicts(session_id: int) -> List[Dict]:
    """Détecte les doubles réservations de salles - LIMITÉ"""
    return execute_query("""
        SELECT l.nom AS salle, ex1.date_examen, 
               CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) AS horaire,
               m1.code AS module1, m2.code AS module2
        FROM examens ex1
        JOIN examens ex2 ON ex1.salle_id = ex2.salle_id 
            AND ex1.date_examen = ex2.date_examen 
            AND ex1.creneau_id = ex2.creneau_id AND ex1.id < ex2.id
        JOIN lieu_examen l ON ex1.salle_id = l.id
        JOIN creneaux_horaires ch ON ex1.creneau_id = ch.id
        JOIN modules m1 ON ex1.module_id = m1.id
        JOIN modules m2 ON ex2.module_id = m2.id
        WHERE ex1.session_id = %s
        LIMIT 50
    """, (session_id,)) or []


def detect_professor_overload(session_id: int) -> List[Dict]:
    """Détecte les professeurs avec plus de 3 surveillances par jour - LIMITÉ"""
    return execute_query("""
        SELECT p.nom, p.prenom, e.date_examen, COUNT(*) AS nb_surveillances
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        JOIN professeurs p ON s.professeur_id = p.id
        WHERE e.session_id = %s
        GROUP BY p.id, e.date_examen 
        HAVING nb_surveillances > 3
        LIMIT 50
    """, (session_id,)) or []


def detect_capacity_overflow(session_id: int) -> List[Dict]:
    """Détecte les dépassements de capacité - LIMITÉ"""
    return execute_query("""
        SELECT e.id, m.code, l.nom AS salle, l.capacite, e.nb_etudiants_prevus
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN lieu_examen l ON e.salle_id = l.id
        WHERE e.session_id = %s AND e.nb_etudiants_prevus > l.capacite
        LIMIT 50
    """, (session_id,)) or []


def detect_all_conflicts(session_id: int) -> Dict[str, List]:
    """Détecte tous les conflits - avec limites"""
    return {
        'student': detect_student_conflicts(session_id),
        'room': detect_room_conflicts(session_id),
        'professor': detect_professor_overload(session_id),
        'capacity': detect_capacity_overflow(session_id)
    }


def get_conflict_stats(session_id: int) -> Dict:
    """Statistiques des conflits - optimisé"""
    result = execute_query("""
        SELECT type_conflit, COUNT(*) as count
        FROM conflits c JOIN examens e ON c.examen1_id = e.id
        WHERE e.session_id = %s AND c.resolu = FALSE
        GROUP BY type_conflit
        LIMIT 10
    """, (session_id,)) or []
    return {r['type_conflit']: r['count'] for r in result}
