import math
import json
from pathlib import Path
from benchmark_logger import BenchmarkLogger

logger = BenchmarkLogger()  

REPORT_DIR = Path(__file__).parent / "reports"

def calculate_pass_at_k(n, c, k) -> dict:
    """
    Berechnet die Pass@K-Metrik basierend auf der Anzahl der generierten Code-Samples (n), der Anzahl der korrekten Samples (c) und der Anzahl der betrachteten Samples (k).
    und gibt die Wahrscheinlichkeit zurück, dass mindestens eines der k betrachteten Samples korrekt ist.
    
    Parameter:
    n: Anzahl der gesamten Versuche bzw. generierten Code-Samples (unterschiedliche Varianten) (z.B. 10)
    c: Anzahl der korrekten Versuche, die den Unittests bestehen (z.B. 3)
    k: Anzahl der betrachteten Versuche, die gemessen werden sollen (z.B. 5)
    """
    if n - c < k:
        return f"Die Wahrscheinlichkeit für Pass@{k} mit n={n}, c={c}, k={k} = 100% (Alle korrekten Versuche passen in die Top-{k})"
    
    # Kombinatorik: 1 - (n-c über k) / (n über k)
    def combinations(n, k):
        return math.comb(n, k)
    
    pass_at = 1.0 - (combinations(n - c, k) / combinations(n, k))

    return {
        "n": n,
        "c": c,
        "k": k,
        "pass_at_k": f"{pass_at * 100:.2f}%"
    }

def pass_at_k(k: int, testdata: dict) -> dict:
    """ Berechnet Pass@K für jedes Endpoint basierend auf den Testdaten und speichert die Ergebnisse in JSON-Dateien.
    
    Parameter:
    k: Anzahl der betrachteten Versuche, die gemessen werden sollen (z.B. 5)
    testdata: Ein Dictionary, das die Anzahl der bestandenen, fehlgeschlagenen und übersprungenen Tests für jedes Endpoint enthält.
    """
    for key, value in testdata.items():
        
        pass_at_k = calculate_pass_at_k(n=value["passed"] + value["failures"]  + value["skipped"], c=value["passed"], k=k)

        try:
            endpoint_report_dir = REPORT_DIR / key
            endpoint_report_dir.mkdir(parents=True, exist_ok=True)
            with open(endpoint_report_dir / f"{key}_report.json", "w") as f:
                json.dump({
                    "endpoint": key,
                    "n": pass_at_k["n"],
                    "c": pass_at_k["c"],
                    "k": pass_at_k["k"],
                    "pass_at_k": pass_at_k["pass_at_k"]
                }, f)
            logger.success(f"Erfolgreich in {key}_report.json gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Pass@{k} Ergebnisse für {key}: {e}")
    return pass_at_k

# Beispiel
if __name__ == "__main__":
    p_at_5 = calculate_pass_at_k(10, 3, 5)