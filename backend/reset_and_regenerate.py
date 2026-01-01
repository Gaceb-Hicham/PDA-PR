"""
Script pour réinitialiser et régénérer les données
Efface les examens et surveillances existants, puis régénère le planning
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import execute_query, get_cursor

def reset_and_regenerate():
    """Réinitialise et régénère toutes les données"""
    
    print("🗑️ Suppression des anciennes données...")
    
    with get_cursor() as cursor:
        # Supprimer les surveillances
        cursor.execute("DELETE FROM surveillances")
        print("  ✓ Surveillances supprimées")
        
        # Supprimer les conflits
        cursor.execute("DELETE FROM conflits")
        print("  ✓ Conflits supprimés")
        
        # Supprimer les examens
        cursor.execute("DELETE FROM examens")
        print("  ✓ Examens supprimés")
    
    print("\n🚀 Régénération du planning...")
    
    from services.optimization import run_optimization
    report = run_optimization(1)
    
    print("\n" + "="*50)
    print("📊 RAPPORT:")
    print(f"   Examens planifiés: {report.get('scheduled', 0)}")
    print(f"   Conflits: {report.get('conflicts', 0)}")
    print(f"   Temps: {report.get('execution_time', 0):.2f}s")
    print("="*50)
    
    # Vérifier les surveillances
    result = execute_query("SELECT COUNT(*) as c FROM surveillances", fetch='one')
    print(f"\n✅ Surveillances enregistrées: {result['c'] if result else 0}")
    
    return report

if __name__ == "__main__":
    reset_and_regenerate()
