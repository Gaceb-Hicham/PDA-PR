"""
Services de statistiques et KPIs pour le tableau de bord
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from datetime import date
from database import execute_query


def get_global_stats() -> Dict[str, Any]:
    """Récupère les statistiques globales du système"""
    stats = {}
    
    # Nombre total d'étudiants
    result = execute_query("SELECT COUNT(*) as total FROM etudiants", fetch='one')
    stats['total_etudiants'] = result['total'] if result else 0
    
    # Nombre total de professeurs
    result = execute_query("SELECT COUNT(*) as total FROM professeurs", fetch='one')
    stats['total_professeurs'] = result['total'] if result else 0
    
    # Nombre de formations
    result = execute_query("SELECT COUNT(*) as total FROM formations", fetch='one')
    stats['total_formations'] = result['total'] if result else 0
    
    # Nombre de modules
    result = execute_query("SELECT COUNT(*) as total FROM modules", fetch='one')
    stats['total_modules'] = result['total'] if result else 0
    
    # Nombre d'inscriptions
    result = execute_query("SELECT COUNT(*) as total FROM inscriptions", fetch='one')
    stats['total_inscriptions'] = result['total'] if result else 0
    
    # Nombre de salles
    result = execute_query("SELECT COUNT(*) as total FROM lieu_examen WHERE disponible = TRUE", fetch='one')
    stats['total_salles'] = result['total'] if result else 0
    
    return stats


def get_session_stats(session_id: int) -> Dict[str, Any]:
    """Récupère les statistiques d'une session d'examen"""
    stats = {}
    
    # Nombre d'examens planifiés
    result = execute_query(
        "SELECT COUNT(*) as total FROM examens WHERE session_id = %s",
        (session_id,), fetch='one'
    )
    stats['examens_planifies'] = result['total'] if result else 0
    
    # Examens par statut
    statuts = execute_query("""
        SELECT statut, COUNT(*) as count 
        FROM examens 
        WHERE session_id = %s 
        GROUP BY statut
    """, (session_id,))
    stats['examens_par_statut'] = {s['statut']: s['count'] for s in statuts}
    
    # Conflits non résolus
    result = execute_query("""
        SELECT COUNT(*) as total 
        FROM conflits c
        JOIN examens e ON c.examen1_id = e.id
        WHERE e.session_id = %s AND c.resolu = FALSE
    """, (session_id,), fetch='one')
    stats['conflits_non_resolus'] = result['total'] if result else 0
    
    # Taux d'occupation des salles
    occupation = execute_query("""
        SELECT 
            l.id,
            l.nom,
            l.capacite,
            COUNT(DISTINCT CONCAT(e.date_examen, '-', e.creneau_id)) as nb_creneaux_occupes
        FROM lieu_examen l
        LEFT JOIN examens e ON e.salle_id = l.id AND e.session_id = %s
        WHERE l.disponible = TRUE
        GROUP BY l.id, l.nom, l.capacite
    """, (session_id,))
    stats['occupation_salles'] = occupation
    
    return stats


def get_department_stats(dept_id: int = None) -> List[Dict]:
    """Récupère les statistiques par département"""
    query = """
        SELECT 
            d.id,
            d.nom AS departement,
            d.code,
            COUNT(DISTINCT f.id) AS nb_formations,
            COUNT(DISTINCT e.id) AS nb_etudiants,
            COUNT(DISTINCT p.id) AS nb_professeurs,
            COUNT(DISTINCT m.id) AS nb_modules,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM inscriptions i WHERE i.module_id = m.id)
            ), 0) AS nb_inscriptions
        FROM departements d
        LEFT JOIN formations f ON f.dept_id = d.id
        LEFT JOIN etudiants e ON e.formation_id = f.id
        LEFT JOIN professeurs p ON p.dept_id = d.id
        LEFT JOIN modules m ON m.formation_id = f.id
    """
    
    if dept_id:
        query += " WHERE d.id = %s"
        query += " GROUP BY d.id, d.nom, d.code"
        return execute_query(query, (dept_id,))
    
    query += " GROUP BY d.id, d.nom, d.code ORDER BY d.nom"
    return execute_query(query)


def get_room_utilization(session_id: int) -> List[Dict]:
    """Calcule le taux d'utilisation des salles"""
    # Calculer le nombre total de créneaux disponibles
    session = execute_query(
        "SELECT date_debut, date_fin FROM sessions_examen WHERE id = %s",
        (session_id,), fetch='one'
    )
    
    if not session:
        return []
    
    # Nombre de jours * 5 créneaux
    from datetime import timedelta
    nb_jours = (session['date_fin'] - session['date_debut']).days + 1
    # Enlever les vendredis (approximatif)
    nb_jours_exam = nb_jours - (nb_jours // 7)
    total_creneaux = nb_jours_exam * 5
    
    utilization = execute_query("""
        SELECT 
            l.id,
            l.nom,
            l.code,
            l.type,
            l.capacite,
            l.batiment,
            COUNT(e.id) AS nb_examens,
            ROUND(COUNT(e.id) * 100.0 / %s, 2) AS taux_utilisation
        FROM lieu_examen l
        LEFT JOIN examens e ON e.salle_id = l.id AND e.session_id = %s
        WHERE l.disponible = TRUE
        GROUP BY l.id, l.nom, l.code, l.type, l.capacite, l.batiment
        ORDER BY nb_examens DESC
    """, (max(total_creneaux, 1), session_id))
    
    return utilization


def get_professor_workload(session_id: int = None) -> List[Dict]:
    """Calcule la charge de travail des professeurs"""
    query = """
        SELECT 
            p.id,
            p.nom,
            p.prenom,
            d.nom AS departement,
            p.grade,
            COUNT(DISTINCT s.examen_id) AS nb_surveillances,
            SUM(CASE WHEN s.role = 'RESPONSABLE' THEN 1 ELSE 0 END) AS nb_responsable,
            SUM(CASE WHEN s.role = 'SURVEILLANT' THEN 1 ELSE 0 END) AS nb_surveillant
        FROM professeurs p
        JOIN departements d ON p.dept_id = d.id
        LEFT JOIN surveillances s ON s.professeur_id = p.id
    """
    
    if session_id:
        query += """
        LEFT JOIN examens e ON s.examen_id = e.id AND e.session_id = %s
        """
        query += """
        GROUP BY p.id, p.nom, p.prenom, d.nom, p.grade
        ORDER BY nb_surveillances DESC
        """
        return execute_query(query, (session_id,))
    
    query += """
        GROUP BY p.id, p.nom, p.prenom, d.nom, p.grade
        ORDER BY nb_surveillances DESC
    """
    return execute_query(query)


def get_daily_exam_distribution(session_id: int) -> List[Dict]:
    """Distribution des examens par jour"""
    return execute_query("""
        SELECT 
            e.date_examen,
            COUNT(*) AS nb_examens,
            SUM(e.nb_etudiants_prevus) AS total_etudiants,
            COUNT(DISTINCT e.salle_id) AS nb_salles_utilisees
        FROM examens e
        WHERE e.session_id = %s
        GROUP BY e.date_examen
        ORDER BY e.date_examen
    """, (session_id,))


def get_formation_exam_progress(session_id: int, dept_id: int = None) -> List[Dict]:
    """Progression de la planification par formation"""
    query = """
        SELECT 
            f.id,
            f.nom AS formation,
            f.niveau,
            d.nom AS departement,
            COUNT(DISTINCT m.id) AS total_modules,
            COUNT(DISTINCT e.module_id) AS modules_planifies,
            ROUND(COUNT(DISTINCT e.module_id) * 100.0 / NULLIF(COUNT(DISTINCT m.id), 0), 2) AS taux_planification
        FROM formations f
        JOIN departements d ON f.dept_id = d.id
        LEFT JOIN modules m ON m.formation_id = f.id AND m.semestre = 'S1'
        LEFT JOIN examens e ON e.module_id = m.id AND e.session_id = %s
    """
    
    if dept_id:
        query += " WHERE f.dept_id = %s"
        query += " GROUP BY f.id, f.nom, f.niveau, d.nom ORDER BY d.nom, f.niveau, f.nom"
        return execute_query(query, (session_id, dept_id))
    
    query += " GROUP BY f.id, f.nom, f.niveau, d.nom ORDER BY d.nom, f.niveau, f.nom"
    return execute_query(query, (session_id,))


def get_conflicts_summary(session_id: int) -> Dict:
    """Résumé des conflits par type"""
    conflicts = execute_query("""
        SELECT 
            c.type_conflit,
            c.severite,
            COUNT(*) AS count
        FROM conflits c
        JOIN examens e ON c.examen1_id = e.id
        WHERE e.session_id = %s AND c.resolu = FALSE
        GROUP BY c.type_conflit, c.severite
        ORDER BY 
            FIELD(c.severite, 'CRITIQUE', 'MAJEUR', 'MINEUR'),
            count DESC
    """, (session_id,))
    
    return {
        'by_type': {c['type_conflit']: c['count'] for c in conflicts},
        'by_severity': {},
        'total': sum(c['count'] for c in conflicts)
    }


def get_kpis_dashboard(session_id: int) -> Dict[str, Any]:
    """KPIs principaux pour le tableau de bord"""
    kpis = {}
    
    # Stats globales
    global_stats = get_global_stats()
    kpis.update(global_stats)
    
    # Stats session
    session_stats = get_session_stats(session_id)
    kpis.update(session_stats)
    
    # Taux de planification global
    if global_stats['total_modules'] > 0:
        kpis['taux_planification'] = round(
            session_stats['examens_planifies'] / global_stats['total_modules'] * 100, 2
        )
    else:
        kpis['taux_planification'] = 0
    
    # Charge moyenne par prof
    workload = get_professor_workload(session_id)
    if workload:
        total_surv = sum(w['nb_surveillances'] or 0 for w in workload)
        kpis['charge_moyenne_prof'] = round(total_surv / len(workload), 2)
    else:
        kpis['charge_moyenne_prof'] = 0
    
    return kpis
