"""
Script de génération de données réalistes pour la plateforme EDT Examens
Génère environ 13,000 étudiants et 130,000 inscriptions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
from datetime import datetime, timedelta, date
from tqdm import tqdm
import bcrypt
from typing import List, Dict, Tuple

from config import DB_CONFIG, DEPARTEMENTS

# Initialisation de Faker pour données françaises
fake = Faker('fr_FR')
Faker.seed(42)
random.seed(42)

# ============================================================================
# CONFIGURATION DE LA GÉNÉRATION
# ============================================================================

GENERATION_CONFIG = {
    'nb_departements': 7,
    'formations_par_dept': 30,  # ~210 formations total
    'modules_par_formation': (6, 9),  # Entre 6 et 9 modules
    'etudiants_par_formation': 65,  # ~13,650 étudiants total
    'nb_professeurs_par_dept': 25,  # ~175 professeurs total
    'nb_amphis': 15,
    'nb_salles': 40,
    'annee_universitaire': '2025/2026',
    'session_debut': date(2026, 1, 6),
    'session_fin': date(2026, 1, 24)
}

# Spécialités par département
SPECIALITES = {
    'INFO': ['Génie Logiciel', 'Intelligence Artificielle', 'Réseaux', 'Sécurité Informatique', 
             'Bases de Données', 'Systèmes Embarqués', 'Cloud Computing', 'DevOps'],
    'MATH': ['Algèbre', 'Analyse', 'Probabilités', 'Statistiques', 'Optimisation', 
             'Mathématiques Appliquées', 'Cryptographie'],
    'PHYS': ['Physique Quantique', 'Optique', 'Mécanique', 'Thermodynamique', 
             'Électromagnétisme', 'Physique des Matériaux'],
    'CHIM': ['Chimie Organique', 'Chimie Inorganique', 'Biochimie', 'Chimie Analytique',
             'Chimie Industrielle', 'Chimie Verte'],
    'BIO': ['Biologie Moléculaire', 'Génétique', 'Microbiologie', 'Écologie',
            'Biotechnologie', 'Bioinformatique'],
    'GEO': ['Géologie Structurale', 'Hydrogéologie', 'Géophysique', 'Pétrologie',
            'Cartographie', 'Géologie Marine'],
    'ELEC': ['Électronique Numérique', 'Électronique de Puissance', 'Automatique',
             'Télécommunications', 'Microélectronique', 'Robotique']
}

# Noms de formations
FORMATIONS_NOMS = {
    'INFO': [
        ('GL', 'Génie Logiciel'),
        ('IA', 'Intelligence Artificielle'),
        ('RSI', 'Réseaux et Systèmes Informatiques'),
        ('SI', 'Systèmes d\'Information'),
        ('SIW', 'Systèmes Informatiques et Web'),
        ('ISI', 'Ingénierie des Systèmes Informatiques')
    ],
    'MATH': [
        ('MA', 'Mathématiques Appliquées'),
        ('MADS', 'Mathématiques et Analyse de Données'),
        ('RO', 'Recherche Opérationnelle'),
        ('STAT', 'Statistiques'),
        ('ALG', 'Algèbre et Géométrie')
    ],
    'PHYS': [
        ('PE', 'Physique Énergétique'),
        ('PM', 'Physique des Matériaux'),
        ('PQ', 'Physique Quantique'),
        ('OP', 'Optique et Photonique'),
        ('MEC', 'Mécanique')
    ],
    'CHIM': [
        ('CO', 'Chimie Organique'),
        ('CA', 'Chimie Analytique'),
        ('CI', 'Chimie Industrielle'),
        ('BC', 'Biochimie'),
        ('GP', 'Génie des Procédés')
    ],
    'BIO': [
        ('BM', 'Biologie Moléculaire'),
        ('GEN', 'Génétique'),
        ('ECO', 'Écologie'),
        ('MB', 'Microbiologie'),
        ('BT', 'Biotechnologie')
    ],
    'GEO': [
        ('GS', 'Géologie Structurale'),
        ('HG', 'Hydrogéologie'),
        ('GP', 'Géophysique'),
        ('RS', 'Ressources du Sol'),
        ('GE', 'Génie de l\'Environnement')
    ],
    'ELEC': [
        ('EN', 'Électronique Numérique'),
        ('AUT', 'Automatique'),
        ('TEL', 'Télécommunications'),
        ('EEA', 'Électronique, Électrotechnique, Automatique'),
        ('ROB', 'Robotique')
    ]
}

# Modules types par spécialité
MODULES_TYPES = {
    'INFO': [
        'Programmation Avancée', 'Algorithmes et Structures de Données', 'Bases de Données',
        'Réseaux Informatiques', 'Systèmes d\'Exploitation', 'Génie Logiciel',
        'Intelligence Artificielle', 'Machine Learning', 'Deep Learning',
        'Sécurité Informatique', 'Cloud Computing', 'DevOps', 'Architecture Logicielle',
        'Conception Orientée Objet', 'Développement Web', 'Développement Mobile',
        'Big Data', 'IoT', 'Compilation', 'Théorie des Langages'
    ],
    'MATH': [
        'Algèbre Linéaire', 'Analyse Réelle', 'Analyse Complexe', 'Probabilités',
        'Statistiques', 'Optimisation', 'Équations Différentielles', 'Topologie',
        'Théorie des Graphes', 'Analyse Numérique', 'Calcul Scientifique',
        'Mathématiques Financières', 'Cryptographie', 'Théorie des Nombres'
    ],
    'PHYS': [
        'Mécanique Classique', 'Mécanique Quantique', 'Électromagnétisme',
        'Thermodynamique', 'Optique', 'Physique Statistique', 'Relativité',
        'Physique du Solide', 'Physique Nucléaire', 'Astrophysique', 'Acoustique'
    ],
    'CHIM': [
        'Chimie Générale', 'Chimie Organique', 'Chimie Inorganique', 'Thermochimie',
        'Électrochimie', 'Spectroscopie', 'Chimie Analytique', 'Chimie des Polymères',
        'Chimie Industrielle', 'Catalyse', 'Chimie Verte'
    ],
    'BIO': [
        'Biologie Cellulaire', 'Biologie Moléculaire', 'Génétique', 'Microbiologie',
        'Biochimie', 'Immunologie', 'Écologie', 'Physiologie', 'Évolution',
        'Biotechnologie', 'Bioinformatique', 'Neurosciences'
    ],
    'GEO': [
        'Géologie Générale', 'Pétrologie', 'Stratigraphie', 'Tectonique',
        'Hydrogéologie', 'Géophysique', 'Paléontologie', 'Géomorphologie',
        'Cartographie', 'SIG', 'Géologie Marine', 'Ressources Minérales'
    ],
    'ELEC': [
        'Électronique Analogique', 'Électronique Numérique', 'Automatique',
        'Traitement du Signal', 'Télécommunications', 'Microprocesseurs',
        'Électrotechnique', 'Électronique de Puissance', 'Capteurs',
        'Systèmes Embarqués', 'Robotique', 'Contrôle Industriel'
    ]
}

BATIMENTS = ['Bloc A', 'Bloc B', 'Bloc C', 'Bloc D', 'Bloc E', 'Nouveau Bloc']
NIVEAUX = ['L1', 'L2', 'L3', 'M1', 'M2']

# ============================================================================
# FONCTIONS DE GÉNÉRATION
# ============================================================================

def get_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Erreur de connexion: {e}")
        raise


def clear_tables(cursor):
    """Vide les tables dans le bon ordre (respect des FK)"""
    tables = [
        'logs_systeme', 'conflits', 'surveillances', 'examens', 
        'inscriptions', 'utilisateurs', 'sessions_examen',
        'modules', 'etudiants', 'professeurs', 'formations',
        'lieu_examen', 'departements'
    ]
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table}")
        except:
            pass
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("🗑️ Tables vidées")


def generate_departements(cursor) -> List[int]:
    """Génère les 7 départements"""
    dept_ids = []
    for dept in DEPARTEMENTS:
        cursor.execute(
            "INSERT INTO departements (nom, code) VALUES (%s, %s)",
            (dept['nom'], dept['code'])
        )
        dept_ids.append(cursor.lastrowid)
    print(f"✅ {len(dept_ids)} départements créés")
    return dept_ids


def generate_lieu_examen(cursor) -> Dict[str, List[int]]:
    """Génère les salles d'examen et amphithéâtres"""
    lieux = {'AMPHI': [], 'SALLE': [], 'LABO': []}
    
    # Amphithéâtres (grande capacité: 100-300)
    for i in range(1, GENERATION_CONFIG['nb_amphis'] + 1):
        batiment = random.choice(BATIMENTS[:3])
        capacite = random.choice([100, 150, 200, 250, 300])
        cursor.execute("""
            INSERT INTO lieu_examen (nom, code, capacite, type, batiment, etage)
            VALUES (%s, %s, %s, 'AMPHI', %s, %s)
        """, (f"Amphithéâtre {i}", f"AMP{i:02d}", capacite, batiment, 0))
        lieux['AMPHI'].append(cursor.lastrowid)
    
    # Salles (capacité moyenne: 20-60)
    for i in range(1, GENERATION_CONFIG['nb_salles'] + 1):
        batiment = random.choice(BATIMENTS)
        capacite = random.choice([20, 25, 30, 35, 40, 45, 50, 60])
        etage = random.randint(0, 3)
        cursor.execute("""
            INSERT INTO lieu_examen (nom, code, capacite, type, batiment, etage)
            VALUES (%s, %s, %s, 'SALLE', %s, %s)
        """, (f"Salle {i:02d}", f"S{i:03d}", capacite, batiment, etage))
        lieux['SALLE'].append(cursor.lastrowid)
    
    # Laboratoires (pour examens pratiques)
    for i in range(1, 11):
        batiment = random.choice(BATIMENTS[3:])
        cursor.execute("""
            INSERT INTO lieu_examen (nom, code, capacite, type, batiment, etage)
            VALUES (%s, %s, %s, 'LABO', %s, %s)
        """, (f"Laboratoire {i}", f"LAB{i:02d}", random.randint(15, 25), batiment, random.randint(0, 2)))
        lieux['LABO'].append(cursor.lastrowid)
    
    total = sum(len(v) for v in lieux.values())
    print(f"✅ {total} lieux d'examen créés (Amphis: {len(lieux['AMPHI'])}, Salles: {len(lieux['SALLE'])}, Labs: {len(lieux['LABO'])})")
    return lieux


def generate_professeurs(cursor, dept_ids: List[int]) -> Dict[int, List[int]]:
    """Génère les professeurs par département"""
    profs_by_dept = {dept_id: [] for dept_id in dept_ids}
    grades = ['MAA', 'MAB', 'MCA', 'MCB', 'PR']
    
    for idx, dept_id in enumerate(dept_ids):
        dept_code = DEPARTEMENTS[idx]['code']
        specialites = SPECIALITES.get(dept_code, ['Général'])
        
        for i in range(GENERATION_CONFIG['nb_professeurs_par_dept']):
            nom = fake.last_name()
            prenom = fake.first_name()
            matricule = f"P{dept_code}{i+1:03d}"
            email = f"{prenom.lower()}.{nom.lower()}@univ-boumerdes.dz"
            specialite = random.choice(specialites)
            grade = random.choices(grades, weights=[20, 30, 25, 15, 10])[0]
            
            cursor.execute("""
                INSERT INTO professeurs (matricule, nom, prenom, email, dept_id, specialite, grade)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (matricule, nom, prenom, email, dept_id, specialite, grade))
            profs_by_dept[dept_id].append(cursor.lastrowid)
    
    total = sum(len(v) for v in profs_by_dept.values())
    print(f"✅ {total} professeurs créés")
    return profs_by_dept


def generate_formations(cursor, dept_ids: List[int]) -> Dict[int, List[Tuple[int, str, int]]]:
    """Génère les formations (~210 formations)"""
    formations_by_dept = {dept_id: [] for dept_id in dept_ids}
    
    for idx, dept_id in enumerate(dept_ids):
        dept_code = DEPARTEMENTS[idx]['code']
        formation_types = FORMATIONS_NOMS.get(dept_code, [('GEN', 'Formation Générale')])
        
        for niveau in NIVEAUX:
            for code_base, nom_base in formation_types:
                nb_modules = random.randint(*GENERATION_CONFIG['modules_par_formation'])
                code = f"{niveau}_{dept_code}_{code_base}"
                nom = f"{niveau} - {nom_base}"
                
                cursor.execute("""
                    INSERT INTO formations (nom, code, dept_id, nb_modules, niveau)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nom, code, dept_id, nb_modules, niveau))
                formations_by_dept[dept_id].append((cursor.lastrowid, niveau, nb_modules))
    
    total = sum(len(v) for v in formations_by_dept.values())
    print(f"✅ {total} formations créées")
    return formations_by_dept


def generate_modules(cursor, formations_by_dept: Dict, dept_ids: List[int]) -> Dict[int, List[int]]:
    """Génère les modules pour chaque formation"""
    modules_by_formation = {}
    
    for idx, dept_id in enumerate(dept_ids):
        dept_code = DEPARTEMENTS[idx]['code']
        module_names = MODULES_TYPES.get(dept_code, ['Module Général'])
        
        for formation_id, niveau, nb_modules in formations_by_dept[dept_id]:
            modules_by_formation[formation_id] = []
            used_names = set()
            
            for i in range(nb_modules):
                # Répartition entre S1 et S2
                semestre = 'S1' if i < nb_modules // 2 else 'S2'
                
                # Choix du nom de module
                available_names = [n for n in module_names if n not in used_names]
                if not available_names:
                    available_names = module_names
                module_nom = random.choice(available_names)
                used_names.add(module_nom)
                
                code_module = f"M{formation_id:03d}{i+1:02d}"
                credits = random.choice([2, 3, 4, 5, 6])
                coef = credits / 2.0
                duree = random.choice([60, 90, 120, 150])
                
                cursor.execute("""
                    INSERT INTO modules (code, nom, credits, formation_id, semestre, coefficient, duree_examen_minutes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (code_module, module_nom, credits, formation_id, semestre, coef, duree))
                modules_by_formation[formation_id].append(cursor.lastrowid)
    
    total = sum(len(v) for v in modules_by_formation.values())
    print(f"✅ {total} modules créés")
    return modules_by_formation


def generate_etudiants(cursor, formations_by_dept: Dict) -> Dict[int, List[int]]:
    """Génère les étudiants (~13,000)"""
    etudiants_by_formation = {}
    total = 0
    
    all_formations = []
    for formations in formations_by_dept.values():
        all_formations.extend(formations)
    
    print("⏳ Génération des étudiants...")
    for formation_id, niveau, _ in tqdm(all_formations, desc="Étudiants"):
        etudiants_by_formation[formation_id] = []
        
        # Nombre d'étudiants variable selon le niveau
        if niveau in ['L1', 'L2']:
            nb_etudiants = random.randint(80, 120)
        elif niveau == 'L3':
            nb_etudiants = random.randint(60, 90)
        else:  # M1, M2
            nb_etudiants = random.randint(30, 50)
        
        # Répartition en groupes
        nb_groupes = (nb_etudiants // 25) + 1
        
        for i in range(nb_etudiants):
            nom = fake.last_name()
            prenom = fake.first_name()
            matricule = f"E{formation_id:04d}{i+1:04d}"
            annee_promo = 2025 if niveau in ['L1', 'M1'] else (2024 if niveau in ['L2'] else 2023)
            groupe = f"G{(i % nb_groupes) + 1:02d}"
            
            cursor.execute("""
                INSERT INTO etudiants (matricule, nom, prenom, formation_id, promo, groupe)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (matricule, nom, prenom, formation_id, annee_promo, groupe))
            etudiants_by_formation[formation_id].append(cursor.lastrowid)
            total += 1
    
    print(f"✅ {total} étudiants créés")
    return etudiants_by_formation


def generate_inscriptions(cursor, etudiants_by_formation: Dict, modules_by_formation: Dict):
    """Génère les inscriptions (~130,000)"""
    total = 0
    batch_size = 1000
    inscriptions_batch = []
    
    print("⏳ Génération des inscriptions...")
    for formation_id, etudiants in tqdm(etudiants_by_formation.items(), desc="Inscriptions"):
        if formation_id not in modules_by_formation:
            continue
            
        modules = modules_by_formation[formation_id]
        
        for etudiant_id in etudiants:
            for module_id in modules:
                # Génération optionnelle de note (rattrapages, etc.)
                note = None
                statut = 'INSCRIT'
                
                inscriptions_batch.append((
                    etudiant_id, module_id, GENERATION_CONFIG['annee_universitaire'], note, statut
                ))
                total += 1
                
                if len(inscriptions_batch) >= batch_size:
                    cursor.executemany("""
                        INSERT INTO inscriptions (etudiant_id, module_id, annee_universitaire, note, statut)
                        VALUES (%s, %s, %s, %s, %s)
                    """, inscriptions_batch)
                    inscriptions_batch = []
    
    # Insertion du reste
    if inscriptions_batch:
        cursor.executemany("""
            INSERT INTO inscriptions (etudiant_id, module_id, annee_universitaire, note, statut)
            VALUES (%s, %s, %s, %s, %s)
        """, inscriptions_batch)
    
    print(f"✅ {total} inscriptions créées")


def generate_session_examen(cursor) -> int:
    """Crée la session d'examen"""
    cursor.execute("""
        INSERT INTO sessions_examen (nom, type_session, date_debut, date_fin, annee_universitaire, statut)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        "Session Normale S1 2025/2026",
        "NORMALE",
        GENERATION_CONFIG['session_debut'],
        GENERATION_CONFIG['session_fin'],
        GENERATION_CONFIG['annee_universitaire'],
        "PLANIFICATION"
    ))
    session_id = cursor.lastrowid
    print(f"✅ Session d'examen créée (ID: {session_id})")
    return session_id


def generate_utilisateurs(cursor, dept_ids: List[int], profs_by_dept: Dict):
    """
    Génère les utilisateurs du système avec rôles hiérarchiques:
    - 1 Vice-Doyen
    - 1 Admin
    - 7 Chefs de département (liés aux professeurs)
    - Tous les professeurs
    """
    
    # Mots de passe par défaut (hashés)
    pwd_admin = bcrypt.hashpw("Admin2026!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    pwd_vicedoyen = bcrypt.hashpw("ViceDoyen2026!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    pwd_chef = bcrypt.hashpw("Chef2026!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    pwd_prof = bcrypt.hashpw("Prof2026!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_count = 0
    
    # 1. Vice-Doyen
    cursor.execute("""
        INSERT INTO utilisateurs (email, password_hash, role, niveau_acces, nom, prenom, actif)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, ("vicedoyen@univ-boumerdes.dz", pwd_vicedoyen, "VICE_DOYEN", 5, "Bensalem", "Mohamed", True))
    user_count += 1
    
    # 2. Admin
    cursor.execute("""
        INSERT INTO utilisateurs (email, password_hash, role, niveau_acces, nom, prenom, actif)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, ("admin@univ-boumerdes.dz", pwd_admin, "ADMIN", 4, "Administrateur", "Système", True))
    user_count += 1
    
    # 3. Chefs de département (premier professeur de chaque département)
    for idx, dept_id in enumerate(dept_ids):
        dept_code = DEPARTEMENTS[idx]['code'].lower()
        dept_nom = DEPARTEMENTS[idx]['nom']
        
        if profs_by_dept.get(dept_id):
            chef_prof_id = profs_by_dept[dept_id][0]  # Premier prof = chef
            
            # Récupérer les infos du professeur
            cursor.execute("SELECT nom, prenom FROM professeurs WHERE id = %s", (chef_prof_id,))
            prof_info = cursor.fetchone()
            if prof_info:
                cursor.execute("""
                    INSERT INTO utilisateurs 
                    (email, password_hash, role, niveau_acces, nom, prenom, professeur_id, dept_id, actif)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"chef.{dept_code}@univ-boumerdes.dz", 
                    pwd_chef, 
                    "CHEF_DEPT", 
                    3,
                    prof_info[0],  # nom
                    prof_info[1],  # prenom
                    chef_prof_id,
                    dept_id,
                    True
                ))
                user_count += 1
    
    # 4. Tous les professeurs (sauf ceux déjà créés comme chefs)
    chef_ids = {profs_by_dept[d][0] for d in dept_ids if profs_by_dept.get(d)}
    
    for dept_id, prof_ids in profs_by_dept.items():
        for prof_id in prof_ids:
            if prof_id in chef_ids:
                continue  # Déjà créé comme chef
            
            cursor.execute("SELECT nom, prenom FROM professeurs WHERE id = %s", (prof_id,))
            prof_info = cursor.fetchone()
            if prof_info:
                # Générer email unique
                email = f"{prof_info[1].lower()}.{prof_info[0].lower()}@univ-boumerdes.dz"
                email = email.replace(" ", "").replace("'", "")[:100]
                
                try:
                    cursor.execute("""
                        INSERT INTO utilisateurs 
                        (email, password_hash, role, niveau_acces, nom, prenom, professeur_id, dept_id, actif)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        email,
                        pwd_prof,
                        "PROFESSEUR",
                        2,
                        prof_info[0],
                        prof_info[1],
                        prof_id,
                        dept_id,
                        True
                    ))
                    user_count += 1
                except Exception:
                    pass  # Ignorer les doublons d'email
    
    print(f"✅ {user_count} utilisateurs créés (1 Vice-Doyen, 1 Admin, {len(dept_ids)} Chefs, {user_count - 2 - len(dept_ids)} Professeurs)")


def update_chef_departements(cursor, dept_ids: List[int], profs_by_dept: Dict):
    """Met à jour les chefs de département"""
    for dept_id in dept_ids:
        if profs_by_dept[dept_id]:
            chef_id = profs_by_dept[dept_id][0]  # Premier professeur comme chef
            cursor.execute(
                "UPDATE departements SET chef_dept_id = %s WHERE id = %s",
                (chef_id, dept_id)
            )


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Fonction principale de génération des données"""
    print("\n" + "="*60)
    print("🎓 GÉNÉRATION DES DONNÉES - PLATEFORME EDT EXAMENS")
    print("="*60 + "\n")
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Désactiver l'autocommit pour une meilleure performance
        conn.autocommit = False
        
        # 1. Vider les tables
        clear_tables(cursor)
        conn.commit()
        
        # 2. Générer les départements
        dept_ids = generate_departements(cursor)
        conn.commit()
        
        # 3. Générer les lieux d'examen
        lieux = generate_lieu_examen(cursor)
        conn.commit()
        
        # 4. Générer les professeurs
        profs_by_dept = generate_professeurs(cursor, dept_ids)
        conn.commit()
        
        # 5. Générer les formations
        formations_by_dept = generate_formations(cursor, dept_ids)
        conn.commit()
        
        # 6. Générer les modules
        modules_by_formation = generate_modules(cursor, formations_by_dept, dept_ids)
        conn.commit()
        
        # 7. Générer les étudiants
        etudiants_by_formation = generate_etudiants(cursor, formations_by_dept)
        conn.commit()
        
        # 8. Générer les inscriptions
        generate_inscriptions(cursor, etudiants_by_formation, modules_by_formation)
        conn.commit()
        
        # 9. Créer la session d'examen
        session_id = generate_session_examen(cursor)
        conn.commit()
        
        # 10. Générer les utilisateurs
        generate_utilisateurs(cursor, dept_ids, profs_by_dept)
        conn.commit()
        
        # 11. Mettre à jour les chefs de département
        update_chef_departements(cursor, dept_ids, profs_by_dept)
        conn.commit()
        
        # Résumé final
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE LA GÉNÉRATION")
        print("="*60)
        
        cursor.execute("SELECT COUNT(*) FROM departements")
        print(f"   Départements: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM formations")
        print(f"   Formations: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM modules")
        print(f"   Modules: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM professeurs")
        print(f"   Professeurs: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM etudiants")
        print(f"   Étudiants: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM inscriptions")
        print(f"   Inscriptions: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM lieu_examen")
        print(f"   Lieux d'examen: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM utilisateurs")
        print(f"   Utilisateurs: {cursor.fetchone()[0]}")
        
        print("\n✅ Génération terminée avec succès!")
        print("="*60 + "\n")
        
    except Error as e:
        print(f"\n❌ Erreur: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    main()
