"""
Script de benchmarking des performances
Mesure les temps d'exécution des requêtes et de l'optimisation
"""
import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import execute_query, get_cursor
from services.optimization import ExamScheduler


def benchmark_query(name: str, query: str, params: tuple = None) -> dict:
    """Mesure le temps d'exécution d'une requête"""
    start = time.time()
    result = execute_query(query, params)
    end = time.time()
    
    return {
        'name': name,
        'execution_time_ms': round((end - start) * 1000, 2),
        'rows_returned': len(result) if result else 0
    }


def run_benchmarks():
    """Exécute tous les benchmarks"""
    print("\n" + "="*60)
    print("📊 BENCHMARKS DE PERFORMANCE")
    print("="*60 + "\n")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'benchmarks': []
    }
    
    # 1. Requêtes de comptage simples
    print("📌 Tests de comptage...")
    
    benchmarks = [
        ("Comptage étudiants", "SELECT COUNT(*) FROM etudiants", None),
        ("Comptage inscriptions", "SELECT COUNT(*) FROM inscriptions", None),
        ("Comptage modules", "SELECT COUNT(*) FROM modules", None),
    ]
    
    for name, query, params in benchmarks:
        result = benchmark_query(name, query, params)
        results['benchmarks'].append(result)
        print(f"  ✓ {name}: {result['execution_time_ms']}ms")
    
    # 2. Requêtes avec jointures
    print("\n📌 Tests de jointures...")
    
    join_benchmarks = [
        ("Stats département", """
            SELECT d.nom, COUNT(e.id) as nb_etudiants
            FROM departements d
            LEFT JOIN formations f ON f.dept_id = d.id
            LEFT JOIN etudiants e ON e.formation_id = f.id
            GROUP BY d.id
        """, None),
        ("Planning examens", """
            SELECT e.*, m.nom, l.nom, ch.libelle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            LIMIT 100
        """, None),
    ]
    
    for name, query, params in join_benchmarks:
        result = benchmark_query(name, query, params)
        results['benchmarks'].append(result)
        print(f"  ✓ {name}: {result['execution_time_ms']}ms ({result['rows_returned']} rows)")
    
    # 3. Test d'optimisation
    print("\n📌 Test d'optimisation EDT...")
    
    try:
        session_id = 1
        
        # Nettoyer les examens précédents
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM examens WHERE session_id = %s", (session_id,))
        
        start = time.time()
        scheduler = ExamScheduler(session_id)
        scheduled, conflicts, exec_time = scheduler.schedule()
        scheduler.save_to_database()
        total_time = time.time() - start
        
        opt_result = {
            'name': 'Génération EDT complète',
            'execution_time_ms': round(total_time * 1000, 2),
            'examens_planifies': scheduled,
            'conflits': conflicts,
            'objectif_45s': total_time <= 45
        }
        results['benchmarks'].append(opt_result)
        
        status = "✅" if total_time <= 45 else "⚠️"
        print(f"  {status} Génération EDT: {total_time:.2f}s ({scheduled} examens, {conflicts} conflits)")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Résumé
    print("\n" + "="*60)
    print("📋 RÉSUMÉ")
    print("="*60)
    
    for b in results['benchmarks']:
        print(f"  • {b['name']}: {b.get('execution_time_ms', 'N/A')}ms")
    
    # Sauvegarder
    output_file = os.path.join(os.path.dirname(__file__), 'results', 'benchmark_results.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés: {output_file}")
    
    return results


if __name__ == "__main__":
    run_benchmarks()
