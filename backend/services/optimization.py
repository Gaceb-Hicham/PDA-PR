"""
Algorithme d'optimisation pour la génération des emplois du temps d'examens
VERSION 6.0 - AVEC TOUS LES PARAMÈTRES AVANCÉS:
- Jours de repos entre examens
- Division par département (alternance des jours)
- Division par niveau
- Surveillants multiples par salle (selon capacité)
- Chaque groupe = Sa propre salle + Ses propres surveillants
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
    niveau: str  # L1, L2, L3, M1, M2
    groupe: str
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
    groupe: str = None
    prof_ids: List[int] = field(default_factory=list)  # Plusieurs surveillants possibles


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
# SCHEDULER CLASS - VERSION 6.0 AVEC PARAMÈTRES AVANCÉS
# ============================================================================

class ExamScheduler:
    """
    Planificateur d'examens avec support complet des paramètres:
    - rest_days: Jours de repos entre examens
    - division_by_dept: Alternance départements par jour
    - division_by_level: Séparation par niveau
    - multi-supervisors: Plusieurs surveillants selon capacité salle
    """
    
    def __init__(self, session_id: int, config: Dict = None):
        self.session_id = session_id
        self.config = config or {}
        self.session_info = self._load_session()
        
        self.exams_by_module: Dict[int, List[GroupExam]] = defaultdict(list)
        self.scheduled_exams: List[ScheduledExam] = []
        self.conflicts: List[Conflict] = []
        
        # Contraintes
        self.room_schedule: Dict[int, Dict[ExamSlot, int]] = defaultdict(dict)
        self.student_schedule: Dict[int, Set[date]] = defaultdict(set)
        self.prof_slot_busy: Dict[Tuple[int, ExamSlot], bool] = {}
        self.prof_daily_count: Dict[int, Dict[date, int]] = defaultdict(lambda: defaultdict(int))
        
        # Ressources
        self.rooms: List[Dict] = []
        self.professors: List[Dict] = []
        self.professors_by_dept: Dict[int, List[Dict]] = defaultdict(list)
        self.slots: List[ExamSlot] = []
        self.slots_by_dept: Dict[int, List[ExamSlot]] = {}  # Pour division par département
        
        # Distribution équitable
        self.prof_total_supervisions: Dict[int, int] = defaultdict(int)
        
        # Départements
        self.departments: List[Dict] = []
    
    def _load_session(self) -> Dict:
        result = execute_query(
            "SELECT * FROM sessions_examen WHERE id = %s",
            (self.session_id,), fetch='one'
        )
        if not result:
            raise ValueError(f"Session {self.session_id} non trouvée")
        return result
    
    def _load_departments(self):
        """Charge tous les départements"""
        self.departments = execute_query("SELECT id, nom, code FROM departements") or []
        print(f"🏛️ {len(self.departments)} départements")
    
    def _load_rooms(self):
        """Charge les salles disponibles"""
        self.rooms = execute_query("""
            SELECT id, code, nom, capacite, type 
            FROM lieu_examen 
            WHERE disponible = TRUE 
            ORDER BY capacite DESC
        """) or []
        print(f"📍 {len(self.rooms)} salles disponibles")
    
    def _load_professors(self):
        """Charge tous les professeurs"""
        result = execute_query("SELECT id, nom, prenom, dept_id FROM professeurs") or []
        self.professors = list(result)
        
        for prof in self.professors:
            dept_id = prof.get('dept_id')
            if dept_id:
                self.professors_by_dept[dept_id].append(prof)
        
        print(f"👨‍🏫 {len(self.professors)} professeurs disponibles")
    
    def _generate_slots(self):
        """Génère les créneaux avec support jours de repos et division département"""
        creneaux = execute_query("SELECT * FROM creneaux_horaires ORDER BY ordre") or []
        
        start_date = self.session_info['date_debut']
        end_date = self.session_info['date_fin']
        rest_days = self.config.get('rest_days', 0)
        dept_splitting = self.config.get('dept_splitting', False)
        
        # Générer tous les jours ouvrables
        work_days = []
        current = start_date
        while current <= end_date:
            # Exclure weekends (samedi=5, dimanche=6)
            if current.weekday() < 5:
                work_days.append(current)
            current += timedelta(days=1)
        
        # Appliquer les jours de repos
        if rest_days > 0:
            exam_days = []
            i = 0
            while i < len(work_days):
                exam_days.append(work_days[i])
                i += 1 + rest_days  # Sauter les jours de repos
            work_days = exam_days
        
        # Générer les créneaux
        for day in work_days:
            for c in creneaux:
                self.slots.append(ExamSlot(
                    date=day,
                    creneau_id=c['id'],
                    heure_debut=str(c['heure_debut']),
                    heure_fin=str(c['heure_fin'])
                ))
        
        # Division par département basée sur les groupes A et B
        # Groupe A: jours 1, 3, 5... / Groupe B: jours 2, 4, 6...
        if dept_splitting:
            dept_group_a = self.config.get('dept_group_a', [])
            dept_group_b = self.config.get('dept_group_b', [])
            
            unique_days = sorted(set(s.date for s in self.slots))
            odd_days = [d for i, d in enumerate(unique_days) if i % 2 == 0]  # Jours 1, 3, 5...
            even_days = [d for i, d in enumerate(unique_days) if i % 2 == 1]  # Jours 2, 4, 6...
            
            odd_slots = [s for s in self.slots if s.date in odd_days]
            even_slots = [s for s in self.slots if s.date in even_days]
            
            # Assigner les créneaux selon le groupe
            for dept_id in dept_group_a:
                self.slots_by_dept[dept_id] = odd_slots  # Groupe A = jours impairs
            
            for dept_id in dept_group_b:
                self.slots_by_dept[dept_id] = even_slots  # Groupe B = jours pairs
            
            print(f"📅 Alternance départements: Groupe A ({len(dept_group_a)} depts) → {len(odd_days)} jours")
            print(f"📅 Alternance départements: Groupe B ({len(dept_group_b)} depts) → {len(even_days)} jours")
        
        print(f"📅 {len(self.slots)} créneaux générés (repos: {rest_days} jour(s))")
    
    def _load_exams_by_group(self):
        """Charge les examens PAR GROUPE avec filtrage par niveau"""
        selected_levels = self.config.get('selected_levels', ['L1', 'L2', 'L3', 'M1', 'M2'])
        levels_str = "','".join(selected_levels)
        
        group_data = execute_query(f"""
            SELECT 
                m.id AS module_id,
                m.code AS module_code,
                m.nom AS module_nom,
                m.formation_id,
                f.dept_id,
                f.niveau,
                COALESCE(e.groupe, 'G01') AS groupe,
                COUNT(DISTINCT i.etudiant_id) AS nb_etudiants,
                COALESCE(m.duree_examen_minutes, 90) AS duree_minutes
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            LEFT JOIN inscriptions i ON i.module_id = m.id
            LEFT JOIN etudiants e ON i.etudiant_id = e.id
            WHERE m.semestre = 'S1' AND f.niveau IN ('{levels_str}')
            GROUP BY m.id, m.code, m.nom, m.formation_id, f.dept_id, f.niveau, e.groupe
            HAVING nb_etudiants > 0
            ORDER BY nb_etudiants DESC, m.id, groupe
        """) or []
        
        for row in group_data:
            exam = GroupExam(
                module_id=row['module_id'],
                module_code=row['module_code'],
                module_nom=row['module_nom'],
                formation_id=row['formation_id'],
                dept_id=row['dept_id'],
                niveau=row['niveau'],
                groupe=row['groupe'],
                nb_etudiants=row['nb_etudiants'],
                duree_minutes=row['duree_minutes'],
                priority_score=row['nb_etudiants']
            )
            self.exams_by_module[row['module_id']].append(exam)
        
        total_groups = sum(len(groups) for groups in self.exams_by_module.values())
        print(f"📝 {len(self.exams_by_module)} modules ({total_groups} groupes) - Niveaux: {selected_levels}")
    
    def _get_required_supervisors(self, room: Dict) -> int:
        """Calcule le nombre de surveillants requis selon la capacité"""
        capacity = room.get('capacite', 0)
        if capacity > 100:  # Amphithéâtre
            return self.config.get('supervisors_amphi', 2)
        else:  # Petite salle
            return self.config.get('supervisors_small_room', 1)
    
    def _is_prof_available_for_slot(self, prof_id: int, slot: ExamSlot) -> bool:
        """Vérifie si un prof est disponible à ce créneau"""
        if self.prof_slot_busy.get((prof_id, slot), False):
            return False
        max_per_day = self.config.get('max_exam_per_professor_per_day', 3)
        if self.prof_daily_count[prof_id][slot.date] >= max_per_day:
            return False
        return True
    
    def _find_supervisors(self, dept_id: int, slot: ExamSlot, count: int, excluded: Set[int]) -> List[int]:
        """Trouve plusieurs surveillants disponibles"""
        supervisors = []
        
        # Trier par nombre total de surveillances
        sorted_profs = sorted(
            self.professors,
            key=lambda p: self.prof_total_supervisions[p['id']]
        )
        
        dept_priority = self.config.get('dept_priority', True)
        
        # D'abord département si priorité activée
        if dept_priority:
            for prof in sorted_profs:
                if len(supervisors) >= count:
                    break
                if prof.get('dept_id') != dept_id:
                    continue
                if prof['id'] in excluded:
                    continue
                if self._is_prof_available_for_slot(prof['id'], slot):
                    supervisors.append(prof['id'])
        
        # Ensuite autres
        for prof in sorted_profs:
            if len(supervisors) >= count:
                break
            if prof['id'] in excluded or prof['id'] in supervisors:
                continue
            if self._is_prof_available_for_slot(prof['id'], slot):
                supervisors.append(prof['id'])
        
        return supervisors if len(supervisors) == count else []
    
    def _get_slots_for_dept(self, dept_id: int, module_id: int = None) -> List[ExamSlot]:
        """Retourne les créneaux pour un département selon son groupe"""
        if self.config.get('dept_splitting', False) and dept_id in self.slots_by_dept:
            # Retourner directement les créneaux assignés à ce département
            return self.slots_by_dept[dept_id]
        return self.slots
    
    def _check_student_availability(self, module_id: int, slot: ExamSlot) -> bool:
        """Vérifie qu'aucun étudiant n'a déjà un examen ce jour"""
        max_exams = self.config.get('max_exam_per_student_per_day', 1)
        
        students = execute_query("""
            SELECT DISTINCT etudiant_id FROM inscriptions WHERE module_id = %s
        """, (module_id,)) or []
        
        for s in students:
            # Compter les examens de cet étudiant ce jour
            student_day_exams = sum(1 for d in self.student_schedule.get(s['etudiant_id'], set()) if d == slot.date)
            if student_day_exams >= max_exams:
                return False
        return True
    
    def _find_rooms_and_supervisors(
        self, 
        group_exams: List[GroupExam], 
        slot: ExamSlot
    ) -> Optional[List[Tuple[GroupExam, Dict, List[int]]]]:
        """
        RÈGLE STRICTE: 
        - Chaque groupe = Sa propre salle + Ses propres surveillants
        - Nombre de surveillants selon capacité salle
        """
        dept_id = group_exams[0].dept_id
        
        assignments = []
        used_rooms = set()
        used_profs = set()
        
        sorted_groups = sorted(group_exams, key=lambda x: x.nb_etudiants, reverse=True)
        
        for group in sorted_groups:
            # Trouver une salle libre
            room_found = None
            for room in self.rooms:
                if room['id'] in used_rooms:
                    continue
                if slot in self.room_schedule[room['id']]:
                    continue
                if room['capacite'] < group.nb_etudiants:
                    continue
                room_found = room
                break
            
            if not room_found:
                return None
            
            # Trouver les surveillants requis
            required = self._get_required_supervisors(room_found)
            supervisors = self._find_supervisors(dept_id, slot, required, used_profs)
            
            if len(supervisors) < required:
                return None
            
            assignments.append((group, room_found, supervisors))
            used_rooms.add(room_found['id'])
            used_profs.update(supervisors)
        
        return assignments
    
    def _commit_assignments(
        self, 
        module_id: int, 
        assignments: List[Tuple[GroupExam, Dict, List[int]]], 
        slot: ExamSlot
    ):
        """Enregistre les assignations"""
        for group, room, prof_ids in assignments:
            self.scheduled_exams.append(ScheduledExam(
                module_id=module_id,
                salle_id=room['id'],
                slot=slot,
                nb_etudiants=group.nb_etudiants,
                groupe=group.groupe,
                prof_ids=prof_ids
            ))
            
            self.room_schedule[room['id']][slot] = module_id
            
            for prof_id in prof_ids:
                self.prof_slot_busy[(prof_id, slot)] = True
                self.prof_daily_count[prof_id][slot.date] += 1
                self.prof_total_supervisions[prof_id] += 1
        
        # Marquer les étudiants
        students = execute_query("""
            SELECT DISTINCT etudiant_id FROM inscriptions WHERE module_id = %s
        """, (module_id,)) or []
        
        for s in students:
            self.student_schedule[s['etudiant_id']].add(slot.date)
    
    def schedule(self, progress_callback=None) -> Tuple[int, int, float]:
        """Exécute l'algorithme de planification"""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("🚀 OPTIMISATION v6.0 - Paramètres Avancés")
        print("="*60)
        print(f"   - Rest days: {self.config.get('rest_days', 0)}")
        print(f"   - Division par dept: {self.config.get('division_by_dept', False)}")
        print(f"   - Surveillants amphi: {self.config.get('supervisors_amphi', 2)}")
        
        self._load_departments()
        self._load_rooms()
        self._load_professors()
        self._generate_slots()
        self._load_exams_by_group()
        
        if not self.exams_by_module:
            print("⚠️ Aucun examen à planifier")
            return 0, 0, time.time() - start_time
        
        if not self.rooms:
            print("⚠️ Aucune salle disponible")
            return 0, 0, time.time() - start_time
        
        sorted_modules = sorted(
            self.exams_by_module.items(),
            key=lambda x: sum(g.nb_etudiants for g in x[1]),
            reverse=True
        )
        
        scheduled_count = 0
        conflict_count = 0
        total = len(sorted_modules)
        
        print(f"\n⏳ Planification de {total} modules...")
        
        for idx, (module_id, group_exams) in enumerate(sorted_modules):
            if progress_callback and idx % 50 == 0:
                progress_callback(idx / total)
            
            first_group = group_exams[0]
            scheduled = False
            
            # Obtenir les créneaux pour ce département (avec division si activée)
            available_slots = self._get_slots_for_dept(first_group.dept_id, module_id)
            
            for slot in available_slots:
                if not self._check_student_availability(module_id, slot):
                    continue
                
                assignments = self._find_rooms_and_supervisors(group_exams, slot)
                if not assignments:
                    continue
                
                self._commit_assignments(module_id, assignments, slot)
                scheduled_count += len(assignments)
                scheduled = True
                break
            
            if not scheduled:
                self.conflicts.append(Conflict(
                    type='PLANIFICATION_IMPOSSIBLE',
                    examen1_id=module_id,
                    examen2_id=None,
                    entite_id=None,
                    description=f"Impossible: {first_group.module_code} ({first_group.niveau})",
                    severite='CRITIQUE'
                ))
                conflict_count += 1
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ Planification terminée en {execution_time:.2f}s")
        print(f"   - Examens planifiés: {scheduled_count}")
        print(f"   - Modules non planifiés: {conflict_count}")
        
        return scheduled_count, conflict_count, execution_time
    
    def save_to_database(self):
        """Sauvegarde les examens planifiés"""
        if not self.scheduled_exams:
            print("⚠️ Aucun examen à sauvegarder")
            return
        
        print("\n💾 Sauvegarde des examens...")
        
        with get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM surveillances WHERE examen_id IN 
                (SELECT id FROM examens WHERE session_id = %s)
            """, (self.session_id,))
            cursor.execute("DELETE FROM examens WHERE session_id = %s", (self.session_id,))
            
            try:
                cursor.execute("SELECT groupe FROM examens LIMIT 1")
            except:
                cursor.execute("ALTER TABLE examens ADD COLUMN groupe VARCHAR(20) DEFAULT NULL")
            
            for se in self.scheduled_exams:
                cursor.execute("""
                    INSERT INTO examens (module_id, session_id, salle_id, date_examen, creneau_id, nb_etudiants_prevus, groupe)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    se.module_id, self.session_id, se.salle_id,
                    se.slot.date, se.slot.creneau_id, se.nb_etudiants, se.groupe
                ))
                exam_id = cursor.lastrowid
                
                # Insérer TOUS les surveillants
                for idx, prof_id in enumerate(se.prof_ids):
                    role = 'RESPONSABLE' if idx == 0 else 'SURVEILLANT'
                    cursor.execute("""
                        INSERT INTO surveillances (examen_id, professeur_id, role)
                        VALUES (%s, %s, %s)
                    """, (exam_id, prof_id, role))
        
        print(f"✅ {len(self.scheduled_exams)} examens sauvegardés")
    
    def save_conflicts_to_database(self):
        """Sauvegarde les conflits"""
        if not self.conflicts:
            return
        
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM conflits WHERE session_id = %s", (self.session_id,))
            
            for conflict in self.conflicts:
                cursor.execute("""
                    INSERT INTO conflits (session_id, examen1_id, examen2_id, type_conflit, description, severite)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    self.session_id,
                    conflict.examen1_id, conflict.examen2_id,
                    conflict.type, conflict.description, conflict.severite
                ))


def run_optimization(session_id: int, config: Dict = None) -> Dict:
    """Fonction principale pour lancer l'optimisation"""
    try:
        scheduler = ExamScheduler(session_id, config)
        scheduled, conflicts, exec_time = scheduler.schedule()
        
        if scheduled > 0:
            scheduler.save_to_database()
        
        if conflicts > 0:
            scheduler.save_conflicts_to_database()
        
        total_modules = len(scheduler.exams_by_module)
        
        return {
            'success': True,
            'scheduled': scheduled,
            'conflicts': conflicts,
            'execution_time': exec_time,
            'success_rate': ((total_modules - conflicts) / max(total_modules, 1)) * 100,
            'modules_planifies': total_modules - conflicts,
            'total_modules': total_modules
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}
