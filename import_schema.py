"""
Script COMPLET pour importer la base de données vers MariaDB Cloud
Version 3 - Lecture directe et exécution fiable
"""
import mysql.connector
import os
import sys

# Configuration MariaDB Cloud
DB_CONFIG = {
    'host': 'serverless-europe-west2.sysp0000.db2.skysql.com',
    'port': 4057,
    'user': 'dbpgf25031469',
    'password': '9bx6PXBZ/b320{6XLMvs',
    'charset': 'utf8mb4',
    'autocommit': True,
    'ssl_disabled': False
}

def read_sql_file(filepath):
    """Lit un fichier SQL et retourne les instructions"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Supprimer BOM
    if content.startswith('\ufeff'):
        content = content[1:]
    
    return content

def split_statements(content):
    """Sépare le contenu SQL en instructions individuelles"""
    statements = []
    current = []
    in_procedure = False
    
    lines = content.split('\n')
    
    for line in lines:
        stripped = line.strip()
        
        # Ignorer les lignes vides et commentaires seuls
        if not stripped or stripped.startswith('--'):
            continue
        
        # Détecter DELIMITER
        if stripped.upper().startswith('DELIMITER'):
            if '//' in stripped:
                in_procedure = True
            else:
                in_procedure = False
            continue
        
        # Dans une procédure, chercher la fin //
        if in_procedure:
            if stripped.endswith('//'):
                current.append(stripped[:-2])  # Sans //
                stmt = '\n'.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(stripped)
            continue
        
        # Ajouter la ligne
        current.append(stripped)
        
        # Si la ligne se termine par ;, c'est la fin d'une instruction
        if stripped.endswith(';'):
            stmt = ' '.join(current).strip()
            if stmt:
                statements.append(stmt[:-1])  # Sans le ;
            current = []
    
    # Reste
    if current:
        stmt = ' '.join(current).strip()
        if stmt and stmt.endswith(';'):
            statements.append(stmt[:-1])
        elif stmt:
            statements.append(stmt)
    
    return statements

def execute_statement(cursor, stmt):
    """Exécute une instruction SQL"""
    # Ignorer certaines commandes
    upper = stmt.upper().strip()
    
    if upper.startswith('DROP DATABASE'):
        return True, "Ignoré"
    if upper.startswith('CREATE DATABASE') and 'pda_examens' in stmt.lower():
        return True, "Ignoré"
    if upper.startswith('USE ') and 'pda_examens' in stmt.lower():
        return True, "Ignoré"
    if upper.startswith('ANALYZE '):
        return True, "Ignoré"
    
    try:
        cursor.execute(stmt)
        try:
            cursor.fetchall()
        except:
            pass
        return True, None
    except mysql.connector.Error as e:
        err = str(e).lower()
        if 'already exists' in err or 'duplicate' in err:
            return True, None
        return False, str(e)[:80]

def import_file(cursor, filepath, show_success=False):
    """Importe un fichier SQL"""
    filename = os.path.basename(filepath)
    print(f"\n{'='*55}")
    print(f"📄 {filename}")
    print('='*55)
    
    if not os.path.exists(filepath):
        print(f"  ❌ Fichier non trouvé: {filepath}")
        return 0, 1
    
    content = read_sql_file(filepath)
    statements = split_statements(content)
    
    success = 0
    errors = 0
    
    for stmt in statements:
        if not stmt.strip():
            continue
            
        ok, err = execute_statement(cursor, stmt)
        if ok:
            success += 1
            if show_success and 'CREATE TABLE' in stmt.upper():
                # Extraire le nom de la table
                import re
                match = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?(\w+)`?', stmt, re.IGNORECASE)
                if match:
                    print(f"  ✅ Table: {match.group(1)}")
        else:
            errors += 1
            print(f"  ⚠️  {err}")
    
    print(f"  📊 {success} OK, {errors} erreurs")
    return success, errors

def main():
    print("\n" + "█" * 60)
    print("█  IMPORT COMPLET VERS MARIADB CLOUD - V3")
    print("█" * 60)
    
    # Connexion
    print("\n🔗 Connexion à MariaDB Cloud...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        print("✅ Connecté!")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    # Créer la base
    print("\n📦 Création de pda_examens...")
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS pda_examens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE pda_examens")
        print("✅ Base prête")
    except Exception as e:
        print(f"⚠️  {e}")
        cursor.execute("USE pda_examens")
    
    # Fichiers à importer
    base = os.path.dirname(os.path.abspath(__file__))
    db = os.path.join(base, 'database')
    
    files = [
        ('schema.sql', True),           # Tables principales
        ('auth_tables.sql', True),      # Auth
        ('add_groupe_column.sql', False), # Colonne groupe
        ('add_indexes.sql', False),     # Index
        ('stored_procedures.sql', False), # Procédures (optionnel)
    ]
    
    total_ok = 0
    total_err = 0
    
    for fname, show in files:
        path = os.path.join(db, fname)
        if os.path.exists(path):
            s, e = import_file(cursor, path, show)
            total_ok += s
            total_err += e
    
    # Vérification
    print("\n" + "█" * 60)
    print("█  VÉRIFICATION")
    print("█" * 60)
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\n📊 {len(tables)} tables/vues:")
    
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{t[0]}`")
            n = cursor.fetchone()[0]
            print(f"   ✅ {t[0]} ({n} lignes)")
        except:
            print(f"   ✅ {t[0]}")
    
    # Résumé
    print("\n" + "█" * 60)
    print(f"█  TOTAL: {total_ok} OK, {total_err} erreurs")
    print("█" * 60)
    
    cursor.close()
    conn.close()
    
    if len(tables) >= 10:
        print("\n🎉 IMPORT RÉUSSI!")
        print("\n📋 Prochaines étapes:")
        print("   1. Exécuter: python backend/seed_data.py")
        print("   2. Mettre à jour Streamlit Secrets")
        print("   3. git push pour redéployer")
    else:
        print("\n⚠️  Moins de 10 tables créées. Vérifiez les erreurs.")

if __name__ == "__main__":
    main()
