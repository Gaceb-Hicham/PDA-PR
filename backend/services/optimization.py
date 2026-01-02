"""
Algorithme d'optimisation pour la génération des emplois du temps d'examens
VERSION AVEC GESTION DES GROUPES:
- Même examen pour tous les groupes d'une formation
- Même date et heure
- Salle DIFFÉRENTE pour chaque groupe (ou une grande salle si possible)
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

from database import execute_query, get_cursor
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
class GroupExam:
    """Représente un examen pour UN groupe spécifique"""
    module_id: int
    module_code: str
    module_nom: str
    formation_id: int
    dept_id: int
    groupe: str  # Le groupe (G01, G02, etc.)
    nb_etudiants: int  # Étudiants de CE groupe uniquement
    duree_minutes: int
    priority_score: float = 0.0


@dataclass
class ScheduledExam:
    """Représente un examen planifié"""
    module_id: int
    salle_id: int
    slot: ExamSlot
    nb_etudiants: int
    groupe: str = None
    prof_id: int = None


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
# SCHEDULER CLASS - AVEC GESTION DES GROUPES
# ============================================================================

class ExamScheduler:
    """Classe principale pour l'optimisation des emplois du temps"""
    
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.session_info = self._load_session()
        self.exams_by_module: Dict[int, List[GroupExam]] = defaultdict(list)  # module_id -> list of group exams
        self.scheduled_exams: List[ScheduledExam] = []
        self.conflicts: List[Conflict] = []
        
        # Contraintes
        self.room_schedule: Dict[int, Dict[ExamSlot, int]] = defaultdict(dict)
        self.student_schedule: Dict[int, Set[date]] = defaultdict(set)
        self.prof_schedule: Dict[int, Dict[date, int]] = defaultdict(lambda: defaultdict(int))
        
        # Données
        self.rooms: List[Dict] = []
        self.professors: Dict[int, List[Dict]] = {}
        self.slots: List[ExamSlot] = []
        
    def _load_session(self) -> Dict:
        result = execute_query(
            "SELECT * FROM sessions_examen WHERE id = %s",
            (self.session_id,), fetch='one'
        )
        if not result:
            raise ValueError(f"Session {self.session_id} non trouvée")
        return result
    
    def _load_rooms(self):
        """Charge les salles, triées par capacité décroissante"""
        self.rooms = execute_query("""
            SELECT * FROM lieu_examen 
            WHERE disponible = TRUE 
            ORDER BY capacite DESC
        """) or []
        print(f"📍 {len(self.rooms)} salles chargées")
    
    def _load_professors(self):
        all_profs = execute_query("SELECT * FROM professeurs") or []
        for prof in all_profs:
            dept_id = prof['dept_id']
            if dept_id not in self.professors:
                self.professors[dept_id] = []
            self.professors[dept_id].append(prof)
        print(f"👨‍🏫 {len(all_profs)} professeurs chargés")
    
    def _generate_slots(self):
        creneaux = execute_query("SELECT * FROM creneaux_horaires ORDER BY ordre") or []
        
        current_date = self.session_info['date_debut']
        end_date = self.session_info['date_fin']
        
        while current_date <= end_date:
            if current_date.weekday() != 4:  # Exclure vendredi
                for creneau in creneaux:
                    self.slots.append(ExamSlot(
                        date=current_date,
                        creneau_id=creneau['id'],
                        heure_debut=str(creneau['heure_debut']),
                        heure_fin=str(creneau['heure_fin'])
                    ))
            current_date += timedelta(days=1)
        
        print(f"📅 {len(self.slots)} créneaux générés")
    
    def _load_exams_by_group(self):
        """
        Charge les examens PAR GROUPE:
        - Pour chaque module, on récupère les groupes distincts
        - Chaque groupe devient un "examen" séparé qui aura sa propre salle
        """
        # Récupérer tous les modules avec les groupes et le nombre d'étudiants par groupe
        group_data = execute_query("""
            SELECT 
                m.id AS module_id,
                m.code AS module_code,
                m.nom AS module_nom,
                m.formation_id,
                m.duree_examen_minutes,
                f.dept_id,
                COALESCE(e.groupe, 'G01') AS groupe,
                COUNT(DISTINCT i.etudiant_id) AS nb_etudiants
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            LEFT JOIN inscriptions i ON i.module_id = m.id 
                AND i.annee_universitaire = %s
            LEFT JOIN etudiants e ON i.etudiant_id = e.id
            WHERE m.semestre = 'S1'
            GROUP BY m.id, m.code, m.nom, m.formation_id, m.duree_examen_minutes, f.dept_id, e.groupe
            HAVING nb_etudiants > 0
            ORDER BY m.formation_id, m.id, groupe
        """, (self.session_info['annee_universitaire'],)) or []
        
        # Organiser par module
        for row in group_data:
            exam = GroupExam(
                module_id=row['module_id'],
                module_code=row['module_code'],
                module_nom=row['module_nom'],
                formation_id=row['formation_id'],
                dept_id=row['dept_id'],
                groupe=row['groupe'],
                nb_etudiants=row['nb_etudiants'],
                duree_minutes=row['duree_examen_minutes'] or 90,
                priority_score=row['nb_etudiants']
            )
            self.exams_by_module[row['module_id']].append(exam)
        
        total_groups = sum(len(groups) for groups in self.exams_by_module.values())
        print(f"📝 {len(self.exams_by_module)} modules avec {total_groups} groupes à planifier")
    
    def _find_rooms_for_groups(self, group_exams: List[GroupExam], slot: ExamSlot) -> Optional[List[Tuple[GroupExam, Dict]]]:
        """
        Trouve des salles pour TOUS les groupes d'un module au même créneau.
        Retourne None si impossible, sinon liste de (group_exam, room)
        """
        total_students = sum(g.nb_etudiants for g in group_exams)
        
        # Option 1: Une seule grande salle pour tous les groupes
        for room in self.rooms:
            if room['capacite'] >= total_students and slot not in self.room_schedule[room['id']]:
                # Une seule salle suffit!
                return [(group_exams[0], room)]  # On utilise le premier groupe comme référence
        
        # Option 2: Une salle séparée par groupe
        assignments = []
        used_rooms = set()
        
        # Trier les groupes par taille décroissante
        sorted_groups = sorted(group_exams, key=lambda x: x.nb_etudiants, reverse=True)
        
        for group in sorted_groups:
            room_found = False
            for room in self.rooms:
                if room['id'] in used_rooms:
                    continue
                if room['capacite'] < group.nb_etudiants:
                    continue
                if slot in self.room_schedule[room['id']]:
                    continue
                
                assignments.append((group, room))
                used_rooms.add(room['id'])
                room_found = True
                break
            
            if not room_found:
                return None  # Impossible de trouver une salle pour ce groupe
        
        return assignments
    
    def _check_student_constraint_for_module(self, module_id: int, slot: ExamSlot) -> bool:
        """Vérifie la contrainte étudiant pour un module entier"""
        students = execute_query("""
            SELECT DISTINCT etudiant_id FROM inscriptions 
            WHERE module_id = %s AND annee_universitaire = %s
        """, (module_id, self.session_info['annee_universitaire'])) or []
        
        for student in students:
            if slot.date in self.student_schedule[student['etudiant_id']]:
                return False
        return True
    
    def _assign_supervisor(self, dept_id: int, slot: ExamSlot) -> Optional[int]:
        """Assigne un surveillant"""
        dept_profs = self.professors.get(dept_id, [])
        random.shuffle(dept_profs)
        
        for prof in dept_profs:
            if self.prof_schedule[prof['id']][slot.date] >= OPTIMIZATION_CONFIG.get('max_exam_per_professor_per_day', 3):
                continue
            return prof['id']
        
        # Chercher dans autres départements
        for did, profs in self.professors.items():
            if did == dept_id:
                continue
            random.shuffle(profs)
            for prof in profs:
                if self.prof_schedule[prof['id']][slot.date] >= OPTIMIZATION_CONFIG.get('max_exam_per_professor_per_day', 3):
                    continue
                return prof['id']
        
        return None
    
    def _update_constraints_for_module(self, module_id: int, assignments: List[Tuple[GroupExam, Dict]], slot: ExamSlot, prof_id: int):
        """Met à jour les contraintes après planification"""
        # Marquer les salles comme occupées
        for group_exam, room in assignments:
            self.room_schedule[room['id']][slot] = module_id
        
        # Marquer les étudiants
        students = execute_query("""
            SELECT DISTINCT etudiant_id FROM inscriptions 
            WHERE module_id = %s AND annee_universitaire = %s
        """, (module_id, self.session_info['annee_universitaire'])) or []
        
        for student in students:
            self.student_schedule[student['etudiant_id']].add(slot.date)
        
        # Prof
        self.prof_schedule[prof_id][slot.date] += 1
    
    def schedule(self, progress_callback=None) -> Tuple[int, int, float]:
        """Exécute l'algorithme de planification avec gestion des groupes"""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE DE L'OPTIMISATION (AVEC GROUPES)")
        print("="*60)
        
        self._load_rooms()
        self._load_professors()
        self._generate_slots()
        self._load_exams_by_group()
        
        if not self.exams_by_module:
            print("⚠️ Aucun examen à planifier")
            return 0, 0, time.time() - start_time
        
        scheduled_count = 0
        conflict_count = 0
        
        print(f"\n⏳ Planification de {len(self.exams_by_module)} modules...")
        
        # Trier les modules par nombre total d'étudiants (priorité)
        sorted_modules = sorted(
            self.exams_by_module.items(),
            key=lambda x: sum(g.nb_etudiants for g in x[1]),
            reverse=True
        )
        
        for module_id, group_exams in sorted_modules:
            scheduled = False
            first_group = group_exams[0]  # Pour les infos communes
            
            # Essayer chaque créneau
            for slot in self.slots:
                # Vérifier contrainte étudiants
                if not self._check_student_constraint_for_module(module_id, slot):
                    continue
                
                # Trouver des salles pour TOUS les groupes
                assignments = self._find_rooms_for_groups(group_exams, slot)
                if not assignments:
                    continue
                
                # Assigner un surveillant
                prof_id = self._assign_supervisor(first_group.dept_id, slot)
                if not prof_id:
                    continue
                
                # Planifier! Créer un examen par groupe/salle
                for group_exam, room in assignments:
                    se = ScheduledExam(
                        module_id=module_id,
                        salle_id=room['id'],
                        slot=slot,
                        nb_etudiants=group_exam.nb_etudiants,
                        groupe=group_exam.groupe,
                        prof_id=prof_id
                    )
                    self.scheduled_exams.append(se)
                    scheduled_count += 1
                
                self._update_constraints_for_module(module_id, assignments, slot, prof_id)
                scheduled = True
                break
            
            if not scheduled:
                self.conflicts.append(Conflict(
                    type='PLANIFICATION_IMPOSSIBLE',
                    examen1_id=module_id,
                    examen2_id=None,
                    entite_id=None,
                    description=f"Impossible de planifier: {first_group.module_code} - {first_group.module_nom}",
                    severite='CRITIQUE'
                ))
                conflict_count += 1
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ Planification terminée en {execution_time:.2f}s")
        print(f"   - Examens créés: {scheduled_count} (avec salles séparées par groupe)")
        print(f"   - Modules non planifiés: {conflict_count}")
        
        return scheduled_count, conflict_count, execution_time
    
    def save_to_database(self):
        """Sauvegarde les examens planifiés dans la base de données"""
        if not self.scheduled_exams:
            print("⚠️ Aucun examen à sauvegarder")
            return
        
        print("\n💾 Sauvegarde des examens et surveillances...")
        
        with get_cursor() as cursor:
            for se in self.scheduled_exams:
                # Insérer l'examen
                cursor.execute("""
                    INSERT INTO examens (module_id, session_id, salle_id, date_examen, creneau_id, 
                                        nb_etudiants_prevus, statut, groupe)
                    VALUES (%s, %s, %s, %s, %s, %s, 'PLANIFIE', %s)
                """, (
                    se.module_id, self.session_id, se.salle_id,
                    se.slot.date, se.slot.creneau_id, se.nb_etudiants, se.groupe
                ))
                exam_id = cursor.lastrowid
                
                # Insérer la surveillance
                if se.prof_id:
                    cursor.execute("""
                        INSERT INTO surveillances (examen_id, professeur_id, role)
                        VALUES (%s, %s, 'RESPONSABLE')
                    """, (exam_id, se.prof_id))
        
        print(f"✅ {len(self.scheduled_exams)} examens sauvegardés")
    
    def save_conflicts_to_database(self):
        """Sauvegarde les conflits"""
        if not self.conflicts:
            return
        
        with get_cursor() as cursor:
            for conflict in self.conflicts:
                cursor.execute("""
                    INSERT INTO conflits (examen1_id, examen2_id, type_conflit, description, severite)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    conflict.examen1_id, conflict.examen2_id,
                    conflict.type, conflict.description, conflict.severite
                ))


def run_optimization(session_id: int) -> Dict:
    """Fonction principale pour lancer l'optimisation"""
    scheduler = ExamScheduler(session_id)
    
    scheduled, conflicts, exec_time = scheduler.schedule()
    
    if scheduled > 0:
        scheduler.save_to_database()
    
    if conflicts > 0:
        scheduler.save_conflicts_to_database()
    
    total_modules = len(scheduler.exams_by_module)
    
    return {
        'scheduled': scheduled,
        'conflicts': conflicts,
        'execution_time': exec_time,
        'success_rate': (total_modules - conflicts) / max(total_modules, 1) * 100 if total_modules > 0 else 0,
        'modules_planifies': total_modules - conflicts,
        'total_modules': total_modules
    }
