"""
Script pour importer la base de données vers Railway MySQL
"""
import mysql.connector
import os
import sys

# Configuration Railway MySQL (PUBLIC URL)
DB_CONFIG = {
    'host': 'metro.proxy.rlwy.net',
    'port': 43906,
    'user': 'root',
    'password': 'aMjJRaAdhsDrzGiLngGanPULJqGpmUiZ',
    'database': 'railway',
    'charset': 'utf8mb4',
    'autocommit': True,
}

def read_sql_file(filepath):
    """Lit un fichier SQL"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('\ufeff'):
        content = content[1:]
    return content

def split_statements(content):
    """Sépare le contenu SQL en instructions"""
    statements = []
    current = []
    
    for line in content.split('\n'):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('--'):
            continue
        if stripped.upper().startswith('DELIMITER'):
            continue
            
        current.append(stripped)
        
        if stripped.endswith(';'):
            stmt = ' '.join(current).strip()
            if stmt:
                statements.append(stmt[:-1])
            current = []
    
    if current:
        stmt = ' '.join(current).strip()
        if stmt:
            statements.append(stmt.rstrip(';'))
    
    return statements

def execute_statement(cursor, stmt):
    """Exécute une instruction SQL"""
    upper = stmt.upper().strip()
    
    # Ignorer certaines commandes
    if upper.startswith('DROP DATABASE') or upper.startswith('CREATE DATABASE'):
        return True, None
    if upper.startswith('USE '):
        return True, None
    if upper.startswith('ANALYZE '):
        return True, None
    
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

def import_file(cursor, filepath, show_tables=False):
    """Importe un fichier SQL"""
    filename = os.path.basename(filepath)
    print(f"\n{'='*55}")
    print(f"📄 {filename}")
    print('='*55)
    
    if not os.path.exists(filepath):
        print(f"  ⚠️  Fichier ignoré (non trouvé)")
        return 0, 0
    
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
            if show_tables and 'CREATE TABLE' in stmt.upper():
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
    print("█  IMPORT VERS RAILWAY MYSQL (USA)")
    print("█" * 60)
    
    # Connexion
    print("\n🔗 Connexion à Railway MySQL...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        print("✅ Connecté!")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    # Fichiers à importer
    base = os.path.dirname(os.path.abspath(__file__))
    db = os.path.join(base, 'database')
    
    files = [
        ('schema.sql', True),
        ('auth_tables.sql', True),
        ('add_indexes.sql', False),
        ('stored_procedures.sql', False),
    ]
    
    total_ok = 0
    total_err = 0
    
    for fname, show in files:
        path = os.path.join(db, fname)
        s, e = import_file(cursor, path, show)
        total_ok += s
        total_err += e
    
    # Vérification
    print("\n" + "█" * 60)
    print("█  VÉRIFICATION")
    print("█" * 60)
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\n📊 {len(tables)} tables/vues créées:")
    
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
        print("   2. Mettre à jour Streamlit Secrets avec Railway")
        print("   3. git push")
    else:
        print("\n⚠️  Vérifiez les erreurs")

if __name__ == "__main__":
    main()
