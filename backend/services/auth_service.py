"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SERVICE D'AUTHENTIFICATION                                                   ║
║  Gestion des connexions, sessions et permissions                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import execute_query, get_cursor


# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

# Définition des niveaux d'accès par rôle
ROLE_LEVELS = {
    'ETUDIANT': 1,
    'PROFESSEUR': 2,
    'CHEF_DEPT': 3,
    'ADMIN': 4,
    'VICE_DOYEN': 5
}

# Pages accessibles par rôle (fallback si la table permissions_role n'existe pas)
ROLE_PAGES = {
    'ETUDIANT': ['dashboard', 'plannings'],
    'PROFESSEUR': ['dashboard', 'plannings', 'export'],
    'CHEF_DEPT': ['dashboard', 'plannings', 'export', 'validation_dept'],
    'ADMIN': ['dashboard', 'configuration', 'donnees', 'generation', 'plannings', 'export', 'validation_dept', 'benchmarks'],
    'VICE_DOYEN': ['dashboard', 'configuration', 'donnees', 'generation', 'plannings', 'export', 'validation_dept', 'kpis_vicedoyen', 'benchmarks']
}

# Mapping des noms de pages UI vers les clés de permission
PAGE_KEYS = {
    '🏠 Dashboard': 'dashboard',
    '⚙️ Configuration': 'configuration',
    '📝 Données': 'donnees',
    '🚀 Génération': 'generation',
    '📊 Plannings': 'plannings',
    '📄 Export': 'export',
    '📈 KPIs Vice-doyen': 'kpis_vicedoyen',
    '✅ Validation Dept': 'validation_dept',
    '⏱️ Benchmarks': 'benchmarks'
}


# ════════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE HASHAGE
# ════════════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie si un mot de passe correspond au hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE CONNEXION
# ════════════════════════════════════════════════════════════════════════════════

def login_student(nom: str, num_inscription: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Connexion pour les étudiants (nom + numéro d'inscription)
    Retourne: (success, user_data, message)
    """
    if not nom or not num_inscription:
        return False, None, "Veuillez remplir tous les champs"
    
    # Rechercher l'étudiant
    etudiant = execute_query("""
        SELECT id, nom, prenom, matricule 
        FROM etudiants 
        WHERE LOWER(nom) = LOWER(%s) AND matricule = %s
    """, (nom.strip(), num_inscription.strip()), fetch='one')
    
    if not etudiant:
        _log_action(None, 'LOGIN_FAILED', f"Étudiant non trouvé: {nom} / {num_inscription}")
        return False, None, "Étudiant non trouvé. Vérifiez votre nom et numéro d'inscription."
    
    # Chercher ou créer l'utilisateur
    user = execute_query("""
        SELECT * FROM utilisateurs WHERE etudiant_id = %s
    """, (etudiant['id'],), fetch='one')
    
    if not user:
        # Créer automatiquement le compte utilisateur
        user = _create_student_user(etudiant)
    
    if not user or not user.get('actif', True):
        return False, None, "Compte désactivé. Contactez l'administration."
    
    # Mettre à jour last_login
    _update_last_login(user['id'])
    _log_action(user['id'], 'LOGIN', f"Connexion étudiant réussie")
    
    return True, {
        'id': user['id'],
        'nom': etudiant['nom'],
        'prenom': etudiant['prenom'],
        'role': 'ETUDIANT',
        'niveau_acces': 1,
        'etudiant_id': etudiant['id']
    }, "Connexion réussie"


def login_user(email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Connexion pour les professeurs, chefs de département, admins et vice-doyen
    Retourne: (success, user_data, message)
    """
    if not email or not password:
        return False, None, "Veuillez remplir tous les champs"
    
    # Rechercher l'utilisateur
    user = execute_query("""
        SELECT u.*, p.nom as prof_nom, p.prenom as prof_prenom, d.nom as dept_nom
        FROM utilisateurs u
        LEFT JOIN professeurs p ON u.professeur_id = p.id
        LEFT JOIN departements d ON u.dept_id = d.id
        WHERE u.email = %s
    """, (email.strip().lower(),), fetch='one')
    
    if not user:
        _log_action(None, 'LOGIN_FAILED', f"Email non trouvé: {email}")
        return False, None, "Email ou mot de passe incorrect"
    
    if not user.get('actif', True):
        return False, None, "Compte désactivé. Contactez l'administration."
    
    # Vérifier le mot de passe
    if not verify_password(password, user.get('password_hash', '')):
        _log_action(user['id'], 'LOGIN_FAILED', "Mot de passe incorrect")
        return False, None, "Email ou mot de passe incorrect"
    
    # Mettre à jour last_login
    _update_last_login(user['id'])
    _log_action(user['id'], 'LOGIN', f"Connexion réussie - Rôle: {user['role']}")
    
    return True, {
        'id': user['id'],
        'nom': user.get('prof_nom') or user['nom'],
        'prenom': user.get('prof_prenom') or user.get('prenom', ''),
        'email': user['email'],
        'role': user['role'],
        'niveau_acces': ROLE_LEVELS.get(user['role'], 1),
        'professeur_id': user.get('professeur_id'),
        'dept_id': user.get('dept_id'),
        'dept_nom': user.get('dept_nom'),
        'premiere_connexion': user.get('premiere_connexion', False)
    }, "Connexion réussie"


def logout(user_id: int) -> bool:
    """Déconnexion d'un utilisateur"""
    _log_action(user_id, 'LOGOUT', "Déconnexion")
    return True


# ════════════════════════════════════════════════════════════════════════════════
# GESTION DES PERMISSIONS
# ════════════════════════════════════════════════════════════════════════════════

def get_user_permissions(role: str) -> List[str]:
    """Retourne la liste des pages accessibles pour un rôle"""
    # Essayer de charger depuis la base de données
    try:
        perms = execute_query("""
            SELECT page_key FROM permissions_role 
            WHERE role = %s AND peut_voir = TRUE
        """, (role,))
        if perms:
            return [p['page_key'] for p in perms]
    except Exception:
        pass
    
    # Fallback sur la configuration statique
    return ROLE_PAGES.get(role, ['dashboard'])


def get_allowed_pages(role: str) -> List[str]:
    """Retourne les noms de pages UI accessibles pour un rôle"""
    allowed_keys = get_user_permissions(role)
    return [page_name for page_name, key in PAGE_KEYS.items() if key in allowed_keys]


def can_access_page(role: str, page_name: str) -> bool:
    """Vérifie si un rôle peut accéder à une page"""
    page_key = PAGE_KEYS.get(page_name, '')
    allowed_keys = get_user_permissions(role)
    return page_key in allowed_keys


def can_modify(role: str, page_name: str) -> bool:
    """Vérifie si un rôle peut modifier sur une page"""
    page_key = PAGE_KEYS.get(page_name, '')
    try:
        perm = execute_query("""
            SELECT peut_modifier FROM permissions_role 
            WHERE role = %s AND page_key = %s
        """, (role, page_key), fetch='one')
        return perm.get('peut_modifier', False) if perm else False
    except Exception:
        return role in ['ADMIN', 'VICE_DOYEN']


# ════════════════════════════════════════════════════════════════════════════════
# CRÉATION D'UTILISATEURS
# ════════════════════════════════════════════════════════════════════════════════

def create_user(
    email: str,
    password: str,
    role: str,
    nom: str,
    prenom: str = '',
    professeur_id: int = None,
    etudiant_id: int = None,
    dept_id: int = None
) -> Optional[int]:
    """Crée un nouvel utilisateur"""
    try:
        password_hash = hash_password(password)
        niveau = ROLE_LEVELS.get(role, 1)
        
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateurs 
                (email, password_hash, role, niveau_acces, nom, prenom, 
                 professeur_id, etudiant_id, dept_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (email.lower() if email else None, password_hash, role, niveau, 
                  nom, prenom, professeur_id, etudiant_id, dept_id))
            return cursor.lastrowid
    except Exception as e:
        print(f"Erreur création utilisateur: {e}")
        return None


def change_password(user_id: int, new_password: str) -> bool:
    """Change le mot de passe d'un utilisateur"""
    try:
        password_hash = hash_password(new_password)
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE utilisateurs 
                SET password_hash = %s, premiere_connexion = FALSE
                WHERE id = %s
            """, (password_hash, user_id))
        _log_action(user_id, 'PASSWORD_CHANGE', "Mot de passe modifié")
        return True
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES PRIVÉES
# ════════════════════════════════════════════════════════════════════════════════

def _create_student_user(etudiant: Dict) -> Optional[Dict]:
    """Crée un utilisateur pour un étudiant (sans mot de passe, login par num_inscription)"""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateurs 
                (role, niveau_acces, nom, prenom, etudiant_id, actif)
                VALUES ('ETUDIANT', 1, %s, %s, %s, TRUE)
            """, (etudiant['nom'], etudiant['prenom'], etudiant['id']))
            user_id = cursor.lastrowid
            
        return execute_query("SELECT * FROM utilisateurs WHERE id = %s", (user_id,), fetch='one')
    except Exception as e:
        print(f"Erreur création utilisateur étudiant: {e}")
        return None


def _update_last_login(user_id: int):
    """Met à jour la date de dernière connexion"""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE utilisateurs SET last_login = NOW() WHERE id = %s
            """, (user_id,))
    except Exception:
        pass


def _log_action(user_id: Optional[int], action: str, details: str = ''):
    """Enregistre une action dans les logs"""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO logs_connexion (utilisateur_id, action, details)
                VALUES (%s, %s, %s)
            """, (user_id, action, details))
    except Exception:
        pass  # Ne pas bloquer si le log échoue


# ════════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE VÉRIFICATION
# ════════════════════════════════════════════════════════════════════════════════

def validate_password_strength(password: str, role: str) -> Tuple[bool, str]:
    """
    Valide la force du mot de passe selon le rôle
    Rôles élevés = exigences plus strictes
    """
    min_length = {
        'ETUDIANT': 0,  # Pas de mot de passe requis
        'PROFESSEUR': 6,
        'CHEF_DEPT': 8,
        'ADMIN': 10,
        'VICE_DOYEN': 10
    }.get(role, 6)
    
    if len(password) < min_length:
        return False, f"Le mot de passe doit contenir au moins {min_length} caractères"
    
    if role in ['ADMIN', 'VICE_DOYEN', 'CHEF_DEPT']:
        if not any(c.isupper() for c in password):
            return False, "Le mot de passe doit contenir au moins une majuscule"
        if not any(c.isdigit() for c in password):
            return False, "Le mot de passe doit contenir au moins un chiffre"
        if not any(c in '!@#$%^&*()_+-=' for c in password):
            return False, "Le mot de passe doit contenir au moins un caractère spécial"
    
    return True, "Mot de passe valide"


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Récupère un utilisateur par son ID"""
    return execute_query("""
        SELECT u.*, p.nom as prof_nom, p.prenom as prof_prenom
        FROM utilisateurs u
        LEFT JOIN professeurs p ON u.professeur_id = p.id
        WHERE u.id = %s
    """, (user_id,), fetch='one')
