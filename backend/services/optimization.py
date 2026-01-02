"""
Algorithme d'optimisation pour la génération des emplois du temps d'examens
Utilise une approche de satisfaction de contraintes avec optimisation gloutonne
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import random
import time
from tqdm import tqdm

from database import (
    execute_query, execute_many, get_cursor,
    get_all_modules, get_all_salles, get_all_professeurs
)
from config import OPTIMIZATION_CONFIG

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ExamSlot:
    """Représente un créneau d'examen"""
    date: date
    creneau_id: int
    heure_debut: str
    heure_fin: str
    
    def __hash__(self):
        return hash((self.date, self.creneau_id))
    
    def __eq__(self, other):
        return self.date == other.date and self.creneau_id == other.creneau_id


@dataclass
class ExamToSchedule:
    """Représente un examen à planifier"""
    module_id: int
    module_code: str
    module_nom: str
    formation_id: int
    dept_id: int
    nb_etudiants: int
    duree_minutes: int
    priority_score: float = 0.0


@dataclass
class ScheduledExam:
    """Représente un examen planifié"""
    module_id: int
    salle_id: int
    slot: ExamSlot
    nb_etudiants: int
    prof_id: int = None  # Surveillant assigné


@dataclass
class Conflict:
    """Représente un conflit détecté"""
    type: str
    examen1_id: int
    examen2_id: Optional[int]
    entite_id: Optional[int]
    description: str
    severite: str


# ============================================================================
# SCHEDULER CLASS
# ============================================================================

class ExamScheduler:
    """Classe principale pour l'optimisation des emplois du temps"""
    
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.session_info = self._load_session()
        self.exams_to_schedule: List[ExamToSchedule] = []
        self.scheduled_exams: List[ScheduledExam] = []
        self.conflicts: List[Conflict] = []
        
        # Contraintes
        self.room_schedule: Dict[int, Dict[ExamSlot, int]] = defaultdict(dict)  # salle_id -> slot -> exam
        self.student_schedule: Dict[int, Set[date]] = defaultdict(set)  # etudiant_id -> dates avec examen
        self.prof_schedule: Dict[int, Dict[date, int]] = defaultdict(lambda: defaultdict(int))  # prof_id -> date -> count
        
        # Chargement des données
        self.rooms: List[Dict] = []
        self.professors: Dict[int, List[Dict]] = {}  # dept_id -> list of profs
        self.slots: List[ExamSlot] = []
        
    def _load_session(self) -> Dict:
        """Charge les informations de la session"""
        result = execute_query(
            "SELECT * FROM sessions_examen WHERE id = %s",
            (self.session_id,),
            fetch='one'
        )
        if not result:
            raise ValueError(f"Session {self.session_id} non trouvée")
        return result
    
    def _load_rooms(self):
        """Charge les salles disponibles"""
        self.rooms = execute_query("""
            SELECT * FROM lieu_examen 
            WHERE disponible = TRUE 
            ORDER BY capacite DESC
        """)
        print(f"📍 {len(self.rooms)} salles chargées")
    
    def _load_professors(self):
        """Charge les professeurs par département"""
        all_profs = execute_query("SELECT * FROM professeurs")
        for prof in all_profs:
            dept_id = prof['dept_id']
            if dept_id not in self.professors:
                self.professors[dept_id] = []
            self.professors[dept_id].append(prof)
        print(f"👨‍🏫 {len(all_profs)} professeurs chargés")
    
    def _generate_slots(self):
        """Génère tous les créneaux disponibles pour la session"""
        creneaux = execute_query("SELECT * FROM creneaux_horaires ORDER BY ordre")
        
        current_date = self.session_info['date_debut']
        end_date = self.session_info['date_fin']
        
        while current_date <= end_date:
            # Exclure les vendredis (ou dimanches selon la culture)
            if current_date.weekday() != 4:  # 4 = vendredi
                for creneau in creneaux:
                    self.slots.append(ExamSlot(
                        date=current_date,
                        creneau_id=creneau['id'],
                        heure_debut=str(creneau['heure_debut']),
                        heure_fin=str(creneau['heure_fin'])
                    ))
            current_date += timedelta(days=1)
        
        print(f"📅 {len(self.slots)} créneaux générés ({self.session_info['date_debut']} à {self.session_info['date_fin']})")
    
    def _load_exams_to_schedule(self):
        """Charge les examens à planifier depuis les modules"""
        # Récupérer tous les modules avec le nombre d'inscrits
        modules = execute_query("""
            SELECT 
                m.id AS module_id,
                m.code AS module_code,
                m.nom AS module_nom,
                m.formation_id,
                m.duree_examen_minutes,
                f.dept_id,
                COUNT(i.id) AS nb_etudiants
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            LEFT JOIN inscriptions i ON i.module_id = m.id 
                AND i.annee_universitaire = %s
            WHERE m.semestre = 'S1'
            GROUP BY m.id, m.code, m.nom, m.formation_id, m.duree_examen_minutes, f.dept_id
            HAVING nb_etudiants > 0
            ORDER BY nb_etudiants DESC
        """, (self.session_info['annee_universitaire'],))
        
        for m in modules:
            exam = ExamToSchedule(
                module_id=m['module_id'],
                module_code=m['module_code'],
                module_nom=m['module_nom'],
                formation_id=m['formation_id'],
                dept_id=m['dept_id'],
                nb_etudiants=m['nb_etudiants'],
                duree_minutes=m['duree_examen_minutes'] or 90
            )
            # Score de priorité: exams avec plus d'étudiants = plus prioritaires
            exam.priority_score = exam.nb_etudiants
            self.exams_to_schedule.append(exam)
        
        # Trier par priorité décroissante
        self.exams_to_schedule.sort(key=lambda x: x.priority_score, reverse=True)
        print(f"📝 {len(self.exams_to_schedule)} examens à planifier")
    
    def _find_best_room(self, exam: ExamToSchedule, slot: ExamSlot) -> Optional[Dict]:
        """Trouve la meilleure salle pour un examen dans un créneau"""
        for room in self.rooms:
            # Vérifier la capacité
            if room['capacite'] < exam.nb_etudiants:
                continue
            
            # Vérifier la disponibilité
            if slot in self.room_schedule[room['id']]:
                continue
            
            # Salle trouvée!
            return room
        
        return None
    
    def _check_student_constraint(self, exam: ExamToSchedule, slot: ExamSlot) -> bool:
        """Vérifie la contrainte: max 1 examen par jour par étudiant"""
        # Récupérer les étudiants inscrits à ce module
        students = execute_query("""
            SELECT etudiant_id FROM inscriptions 
            WHERE module_id = %s AND annee_universitaire = %s
        """, (exam.module_id, self.session_info['annee_universitaire']))
        
        for student in students:
            if slot.date in self.student_schedule[student['etudiant_id']]:
                return False
        
        return True
    
    def _assign_supervisor(self, exam: ExamToSchedule, slot: ExamSlot) -> Optional[int]:
        """Assigne un surveillant en respectant les contraintes"""
        # Priorité: professeurs du même département
        dept_profs = self.professors.get(exam.dept_id, [])
        
        # Mélanger pour équilibrer
        random.shuffle(dept_profs)
        
        for prof in dept_profs:
            # Vérifier: max 3 surveillances par jour
            if self.prof_schedule[prof['id']][slot.date] >= OPTIMIZATION_CONFIG['max_exam_per_professor_per_day']:
                continue
            return prof['id']
        
        # Si pas de prof du département disponible, chercher ailleurs
        for dept_id, profs in self.professors.items():
            if dept_id == exam.dept_id:
                continue
            random.shuffle(profs)
            for prof in profs:
                if self.prof_schedule[prof['id']][slot.date] >= OPTIMIZATION_CONFIG['max_exam_per_professor_per_day']:
                    continue
                return prof['id']
        
        return None
    
    def _update_constraints(self, exam: ExamToSchedule, scheduled: ScheduledExam, prof_id: int):
        """Met à jour les contraintes après planification d'un examen"""
        # Marquer la salle comme occupée
        self.room_schedule[scheduled.salle_id][scheduled.slot] = exam.module_id
        
        # Marquer les étudiants comme ayant un examen ce jour
        students = execute_query("""
            SELECT etudiant_id FROM inscriptions 
            WHERE module_id = %s AND annee_universitaire = %s
        """, (exam.module_id, self.session_info['annee_universitaire']))
        
        for student in students:
            self.student_schedule[student['etudiant_id']].add(scheduled.slot.date)
        
        # Incrémenter le compteur de surveillances du prof
        self.prof_schedule[prof_id][scheduled.slot.date] += 1
    
    def schedule(self, progress_callback=None) -> Tuple[int, int, float]:
        """
        Exécute l'algorithme de planification
        
        Returns:
            Tuple (nb_scheduled, nb_conflicts, execution_time)
        """
        start_time = time.time()
        
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE DE L'OPTIMISATION")
        print("="*60)
        
        # Chargement des données
        self._load_rooms()
        self._load_professors()
        self._generate_slots()
        self._load_exams_to_schedule()
        
        if not self.exams_to_schedule:
            print("⚠️ Aucun examen à planifier")
            return 0, 0, time.time() - start_time
        
        scheduled_count = 0
        conflict_count = 0
        
        print(f"\n⏳ Planification de {len(self.exams_to_schedule)} examens...")
        
        for exam in tqdm(self.exams_to_schedule, desc="Planification"):
            scheduled = False
            
            # Essayer chaque créneau
            for slot in self.slots:
                # Vérifier la contrainte étudiant (max 1 exam/jour)
                if not self._check_student_constraint(exam, slot):
                    continue
                
                # Trouver une salle
                room = self._find_best_room(exam, slot)
                if not room:
                    continue
                
                # Assigner un surveillant
                prof_id = self._assign_supervisor(exam, slot)
                if not prof_id:
                    continue
                
                # Planifier l'examen avec le surveillant
                scheduled_exam = ScheduledExam(
                    module_id=exam.module_id,
                    salle_id=room['id'],
                    slot=slot,
                    nb_etudiants=exam.nb_etudiants,
                    prof_id=prof_id  # IMPORTANT: Stocker le surveillant
                )
                
                self.scheduled_exams.append(scheduled_exam)
                self._update_constraints(exam, scheduled_exam, prof_id)
                scheduled_count += 1
                scheduled = True
                break
            
            if not scheduled:
                # Conflit non résolu
                self.conflicts.append(Conflict(
                    type='PLANIFICATION_IMPOSSIBLE',
                    examen1_id=exam.module_id,
                    examen2_id=None,
                    entite_id=None,
                    description=f"Impossible de planifier: {exam.module_code} - {exam.module_nom}",
                    severite='CRITIQUE'
                ))
                conflict_count += 1
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ Planification terminée en {execution_time:.2f}s")
        print(f"   - Examens planifiés: {scheduled_count}/{len(self.exams_to_schedule)}")
        print(f"   - Conflits: {conflict_count}")
        
        return scheduled_count, conflict_count, execution_time
    
    def save_to_database(self):
        """Sauvegarde les examens planifiés ET les surveillances dans la base de données"""
        if not self.scheduled_exams:
            print("⚠️ Aucun examen à sauvegarder")
            return
        
        print("\n💾 Sauvegarde des examens et surveillances...")
        
        surveillance_count = 0
        
        with get_cursor() as cursor:
            for se in self.scheduled_exams:
                # Insérer l'examen
                cursor.execute("""
                    INSERT INTO examens (module_id, session_id, salle_id, date_examen, creneau_id, 
                                        duree_minutes, nb_etudiants_prevus, statut)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    se.module_id,
                    self.session_id,
                    se.salle_id,
                    se.slot.date,
                    se.slot.creneau_id,
                    90,
                    se.nb_etudiants,
                    'PLANIFIE'
                ))
                
                # Récupérer l'ID de l'examen inséré
                exam_id = cursor.lastrowid
                
                # IMPORTANT: Sauvegarder la surveillance du professeur
                if se.prof_id and exam_id:
                    cursor.execute("""
                        INSERT INTO surveillances (examen_id, professeur_id, role)
                        VALUES (%s, %s, 'RESPONSABLE')
                    """, (exam_id, se.prof_id))
                    surveillance_count += 1
        
        print(f"✅ {len(self.scheduled_exams)} examens sauvegardés")
        print(f"✅ {surveillance_count} surveillances assignées")
        
        # Sauvegarder les conflits
        if self.conflicts:
            print(f"\n⚠️ {len(self.conflicts)} conflits détectés")
    
    def generate_report(self) -> Dict:
        """Génère un rapport de la planification"""
        return {
            'total_exams': len(self.exams_to_schedule),
            'scheduled': len(self.scheduled_exams),
            'conflicts': len(self.conflicts),
            'success_rate': (len(self.scheduled_exams) / len(self.exams_to_schedule) * 100) if self.exams_to_schedule else 0,
            'rooms_used': len(set(se.salle_id for se in self.scheduled_exams)),
            'dates_used': len(set(se.slot.date for se in self.scheduled_exams))
        }


# ============================================================================
# CONFLICT DETECTION FUNCTIONS
# ============================================================================

def detect_student_conflicts(session_id: int) -> List[Dict]:
    """Détecte les conflits étudiants (plus d'un examen par jour)"""
    conflicts = execute_query("""
        SELECT 
            e.nom AS etudiant_nom,
            e.prenom AS etudiant_prenom,
            ex1.date_examen,
            m1.nom AS module1,
            m2.nom AS module2
        FROM inscriptions i1
        JOIN inscriptions i2 ON i1.etudiant_id = i2.etudiant_id AND i1.module_id < i2.module_id
        JOIN examens ex1 ON ex1.module_id = i1.module_id AND ex1.session_id = %s
        JOIN examens ex2 ON ex2.module_id = i2.module_id AND ex2.session_id = %s
        JOIN modules m1 ON i1.module_id = m1.id
        JOIN modules m2 ON i2.module_id = m2.id
        JOIN etudiants e ON i1.etudiant_id = e.id
        WHERE ex1.date_examen = ex2.date_examen
        LIMIT 100
    """, (session_id, session_id))
    
    return conflicts


def detect_room_conflicts(session_id: int) -> List[Dict]:
    """Détecte les conflits de salles (double réservation)"""
    conflicts = execute_query("""
        SELECT 
            l.nom AS salle,
            ex1.date_examen,
            CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) AS horaire,
            m1.nom AS module1,
            m2.nom AS module2
        FROM examens ex1
        JOIN examens ex2 ON ex1.salle_id = ex2.salle_id 
            AND ex1.date_examen = ex2.date_examen 
            AND ex1.creneau_id = ex2.creneau_id
            AND ex1.id < ex2.id
        JOIN lieu_examen l ON ex1.salle_id = l.id
        JOIN creneaux_horaires ch ON ex1.creneau_id = ch.id
        JOIN modules m1 ON ex1.module_id = m1.id
        JOIN modules m2 ON ex2.module_id = m2.id
        WHERE ex1.session_id = %s
    """, (session_id,))
    
    return conflicts


def detect_prof_overload(session_id: int) -> List[Dict]:
    """Détecte les surcharges de professeurs (plus de 3 surveillances par jour)"""
    overloads = execute_query("""
        SELECT 
            p.nom,
            p.prenom,
            e.date_examen,
            COUNT(*) AS nb_surveillances
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        JOIN professeurs p ON s.professeur_id = p.id
        WHERE e.session_id = %s
        GROUP BY p.id, e.date_examen
        HAVING nb_surveillances > 3
    """, (session_id,))
    
    return overloads


# ============================================================================
# MAIN / TEST
# ============================================================================

def run_optimization(session_id: int = 1) -> Dict:
    """
    Fonction principale pour lancer l'optimisation
    
    Args:
        session_id: ID de la session d'examen
        
    Returns:
        Rapport de planification
    """
    scheduler = ExamScheduler(session_id)
    
    scheduled, conflicts, exec_time = scheduler.schedule()
    
    # Sauvegarder les résultats
    scheduler.save_to_database()
    
    # Générer le rapport
    report = scheduler.generate_report()
    report['execution_time'] = exec_time
    
    # Vérifier si on respecte la contrainte de 45 secondes
    if exec_time > OPTIMIZATION_CONFIG['optimization_timeout_seconds']:
        print(f"⚠️ Temps d'exécution ({exec_time:.2f}s) dépasse la limite de 45s")
    else:
        print(f"✅ Temps d'exécution ({exec_time:.2f}s) dans les limites")
    
    return report


if __name__ == "__main__":
    report = run_optimization()
    print("\n📊 RAPPORT FINAL:")
    for key, value in report.items():
        print(f"   {key}: {value}")
