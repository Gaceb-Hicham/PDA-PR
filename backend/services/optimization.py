"""
Algorithme d'optimisation pour la génération des emplois du temps d'examens
VERSION CORRIGÉE v5.2:
- Même examen pour tous les groupes d'une formation = même date/heure
- Salle DIFFÉRENTE pour chaque groupe
- Surveillant DIFFÉRENT pour chaque salle (UN prof = UNE salle)
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
    groupe: str
    nb_etudiants: int
    duree_minutes: int
    priority_score: float = 0.0


@dataclass
class ScheduledExam:
    """Représente un examen planifié - UN prof par salle"""
    module_id: int
    salle_id: int
    slot: ExamSlot
    nb_etudiants: int
    groupe: str = None
    prof_id: int = None  # Surveillant de CETTE salle uniquement


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
# SCHEDULER CLASS - AVEC SURVEILLANCE CORRECTE
# ============================================================================

class ExamScheduler:
    """
    Planificateur d'examens - Version corrigée
    
    RÈGLE CRITIQUE: Un professeur ne peut surveiller qu'UNE salle à la fois!
    Donc si un module a 3 groupes dans 3 salles différentes, il faut 3 surveillants.
    """
    
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.session_info = self._load_session()
        self.exams_by_module: Dict[int, List[GroupExam]] = defaultdict(list)
        self.scheduled_exams: List[ScheduledExam] = []
        self.conflicts: List[Conflict] = []
        
        # Contraintes
        self.room_schedule: Dict[int, Dict[ExamSlot, int]] = defaultdict(dict)
        self.student_schedule: Dict[int, Set[date]] = defaultdict(set)
        
        # CRITIQUE: Suivi des profs par créneau PRÉCIS (pas juste par jour)
        self.prof_slot_busy: Dict[Tuple[int, ExamSlot], bool] = {}  # (prof_id, slot) -> busy
        self.prof_daily_count: Dict[int, Dict[date, int]] = defaultdict(lambda: defaultdict(int))
        
        # Données
        self.rooms: List[Dict] = []
        self.professors: List[Dict] = []
        self.professors_by_dept: Dict[int, List[Dict]] = defaultdict(list)
        self.slots: List[ExamSlot] = []
        
        # Distribution équitable
        self.prof_total_supervisions: Dict[int, int] = defaultdict(int)
    
    def _load_session(self) -> Dict:
        result = execute_query(
            "SELECT * FROM sessions_examen WHERE id = %s",
            (self.session_id,), fetch='one'
        )
        if not result:
            raise ValueError(f"Session {self.session_id} non trouvée")
        return result
    
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
        """Charge TOUS les professeurs"""
        result = execute_query("SELECT id, nom, prenom, dept_id FROM professeurs") or []
        self.professors = list(result)
        
        for prof in self.professors:
            dept_id = prof.get('dept_id')
            if dept_id:
                self.professors_by_dept[dept_id].append(prof)
        
        print(f"👨‍🏫 {len(self.professors)} professeurs disponibles")
    
    def _generate_slots(self):
        """Génère les créneaux d'examen"""
        creneaux = execute_query("SELECT * FROM creneaux_horaires ORDER BY ordre") or []
        
        current_date = self.session_info['date_debut']
        end_date = self.session_info['date_fin']
        
        while current_date <= end_date:
            # Exclure weekends (samedi=5, dimanche=6) et vendredi=4 si nécessaire
            if current_date.weekday() < 5:  # Lundi à vendredi
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
        """Charge les examens PAR GROUPE"""
        annee = self.session_info.get('annee_universitaire', '2024-2025')
        
        group_data = execute_query("""
            SELECT 
                m.id AS module_id,
                m.code AS module_code,
                m.nom AS module_nom,
                m.formation_id,
                f.dept_id,
                COALESCE(e.groupe, 'G01') AS groupe,
                COUNT(DISTINCT i.etudiant_id) AS nb_etudiants,
                COALESCE(m.duree_examen_minutes, 90) AS duree_minutes
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            LEFT JOIN inscriptions i ON i.module_id = m.id
            LEFT JOIN etudiants e ON i.etudiant_id = e.id
            WHERE m.semestre = 'S1'
            GROUP BY m.id, m.code, m.nom, m.formation_id, f.dept_id, e.groupe
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
                groupe=row['groupe'],
                nb_etudiants=row['nb_etudiants'],
                duree_minutes=row['duree_minutes'],
                priority_score=row['nb_etudiants']
            )
            self.exams_by_module[row['module_id']].append(exam)
        
        total_groups = sum(len(groups) for groups in self.exams_by_module.values())
        print(f"📝 {len(self.exams_by_module)} modules ({total_groups} groupes)")
    
    def _is_prof_available_for_slot(self, prof_id: int, slot: ExamSlot) -> bool:
        """
        CRITIQUE: Vérifie si un prof est disponible à ce créneau PRÉCIS
        Un prof ne peut PAS être dans deux salles au même moment!
        """
        # Déjà occupé à ce créneau?
        if self.prof_slot_busy.get((prof_id, slot), False):
            return False
        
        # Limite quotidienne?
        max_per_day = OPTIMIZATION_CONFIG.get('max_exam_per_professor_per_day', 3)
        if self.prof_daily_count[prof_id][slot.date] >= max_per_day:
            return False
        
        return True
    
    def _find_supervisor(self, dept_id: int, slot: ExamSlot, excluded_profs: Set[int]) -> Optional[int]:
        """
        Trouve UN surveillant disponible pour UN créneau
        
        Args:
            dept_id: Département prioritaire
            slot: Créneau horaire
            excluded_profs: Profs déjà assignés à ce même créneau (pour d'autres salles)
        
        Returns:
            ID du prof ou None
        """
        # Trier par nombre total de surveillances (distribution équitable)
        sorted_profs = sorted(
            self.professors,
            key=lambda p: self.prof_total_supervisions[p['id']]
        )
        
        # D'abord chercher dans le département
        for prof in sorted_profs:
            if prof.get('dept_id') != dept_id:
                continue
            if prof['id'] in excluded_profs:
                continue
            if self._is_prof_available_for_slot(prof['id'], slot):
                return prof['id']
        
        # Ensuite dans les autres départements
        for prof in sorted_profs:
            if prof.get('dept_id') == dept_id:
                continue
            if prof['id'] in excluded_profs:
                continue
            if self._is_prof_available_for_slot(prof['id'], slot):
                return prof['id']
        
        return None
    
    def _check_student_availability(self, module_id: int, slot: ExamSlot) -> bool:
        """Vérifie qu'aucun étudiant n'a déjà un examen ce jour"""
        students = execute_query("""
            SELECT DISTINCT etudiant_id FROM inscriptions WHERE module_id = %s
        """, (module_id,)) or []
        
        for s in students:
            if slot.date in self.student_schedule[s['etudiant_id']]:
                return False
        return True
    
    def _find_rooms_and_supervisors(
        self, 
        group_exams: List[GroupExam], 
        slot: ExamSlot
    ) -> Optional[List[Tuple[GroupExam, Dict, int]]]:
        """
        FONCTION CRITIQUE: Trouve salles ET surveillants pour TOUS les groupes
        
        Retourne: Liste de (group_exam, room, prof_id) où chaque prof est DIFFÉRENT
        """
        total_students = sum(g.nb_etudiants for g in group_exams)
        dept_id = group_exams[0].dept_id
        
        # ═══════════════════════════════════════════════════════════════
        # OPTION 1: Une seule grande salle pour tous les groupes
        # CRITIQUE: Créer une entrée pour CHAQUE groupe (même salle, même créneau)
        # ═══════════════════════════════════════════════════════════════
        for room in self.rooms:
            if room['capacite'] >= total_students:
                if slot not in self.room_schedule[room['id']]:
                    # Trouver UN surveillant
                    prof_id = self._find_supervisor(dept_id, slot, set())
                    if prof_id:
                        # CORRECTION: Retourner TOUS les groupes, pas juste le premier!
                        # Chaque groupe aura son propre enregistrement avec la même salle
                        return [(group, room, prof_id) for group in group_exams]
        
        # ═══════════════════════════════════════════════════════════════
        # OPTION 2: Salles séparées avec surveillants DIFFÉRENTS
        # ═══════════════════════════════════════════════════════════════
        assignments = []
        used_rooms = set()
        used_profs = set()  # CRITIQUE: Suivre les profs déjà utilisés!
        
        # Trier par nombre d'étudiants décroissant
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
                return None  # Pas assez de salles
            
            # CRITIQUE: Trouver un surveillant DIFFÉRENT
            prof_id = self._find_supervisor(dept_id, slot, used_profs)
            if not prof_id:
                return None  # Pas assez de surveillants disponibles
            
            assignments.append((group, room_found, prof_id))
            used_rooms.add(room_found['id'])
            used_profs.add(prof_id)  # Marquer comme utilisé!
        
        return assignments
    
    def _commit_assignments(
        self, 
        module_id: int, 
        assignments: List[Tuple[GroupExam, Dict, int]], 
        slot: ExamSlot
    ):
        """Enregistre les assignations et met à jour les contraintes"""
        for group, room, prof_id in assignments:
            # Créer l'examen planifié
            self.scheduled_exams.append(ScheduledExam(
                module_id=module_id,
                salle_id=room['id'],
                slot=slot,
                nb_etudiants=group.nb_etudiants,
                groupe=group.groupe,
                prof_id=prof_id
            ))
            
            # Marquer salle occupée
            self.room_schedule[room['id']][slot] = module_id
            
            # CRITIQUE: Marquer le prof comme occupé à ce créneau
            self.prof_slot_busy[(prof_id, slot)] = True
            self.prof_daily_count[prof_id][slot.date] += 1
            self.prof_total_supervisions[prof_id] += 1
        
        # Marquer les étudiants du module
        students = execute_query("""
            SELECT DISTINCT etudiant_id FROM inscriptions WHERE module_id = %s
        """, (module_id,)) or []
        
        for s in students:
            self.student_schedule[s['etudiant_id']].add(slot.date)
    
    def schedule(self, progress_callback=None) -> Tuple[int, int, float]:
        """Exécute l'algorithme de planification"""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("🚀 OPTIMISATION v5.2 - Surveillants différents par salle")
        print("="*60)
        
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
        
        if not self.professors:
            print("⚠️ Aucun professeur disponible")
            return 0, 0, time.time() - start_time
        
        # Trier les modules par nombre total d'étudiants
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
            
            for slot in self.slots:
                # Vérifier disponibilité étudiants
                if not self._check_student_availability(module_id, slot):
                    continue
                
                # Trouver salles ET surveillants (différents!)
                assignments = self._find_rooms_and_supervisors(group_exams, slot)
                if not assignments:
                    continue
                
                # Valider!
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
                    description=f"Impossible: {first_group.module_code} - {first_group.module_nom}",
                    severite='CRITIQUE'
                ))
                conflict_count += 1
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ Planification terminée en {execution_time:.2f}s")
        print(f"   - Examens planifiés: {scheduled_count}")
        print(f"   - Modules non planifiés: {conflict_count}")
        
        # Stats surveillances
        if self.prof_total_supervisions:
            values = list(self.prof_total_supervisions.values())
            if values:
                print(f"   - Surveillances/prof: min={min(values)}, max={max(values)}, moy={sum(values)/len(values):.1f}")
        
        return scheduled_count, conflict_count, execution_time
    
    def save_to_database(self):
        """Sauvegarde les examens planifiés"""
        if not self.scheduled_exams:
            print("⚠️ Aucun examen à sauvegarder")
            return
        
        print("\n💾 Sauvegarde des examens...")
        
        with get_cursor() as cursor:
            # Nettoyer anciens examens
            cursor.execute("""
                DELETE FROM surveillances WHERE examen_id IN 
                (SELECT id FROM examens WHERE session_id = %s)
            """, (self.session_id,))
            cursor.execute("DELETE FROM examens WHERE session_id = %s", (self.session_id,))
            
            # Vérifier si la colonne groupe existe, sinon la créer
            try:
                cursor.execute("SELECT groupe FROM examens LIMIT 1")
            except:
                cursor.execute("ALTER TABLE examens ADD COLUMN groupe VARCHAR(20) DEFAULT NULL")
                print("   ➕ Colonne 'groupe' ajoutée")
            
            for se in self.scheduled_exams:
                # Insérer l'examen AVEC le groupe pour permettre les PDFs par groupe
                cursor.execute("""
                    INSERT INTO examens (module_id, session_id, salle_id, date_examen, creneau_id, nb_etudiants_prevus, groupe)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
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


def run_optimization(session_id: int) -> Dict:
    """Fonction principale pour lancer l'optimisation"""
    try:
        scheduler = ExamScheduler(session_id)
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
