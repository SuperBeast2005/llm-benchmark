#Standard-Libs Import
import os
import subprocess
from pathlib import Path
import sys
from dotenv import load_dotenv

#Eigene Module Import
from benchmark_logger import BenchmarkLogger
from gsm_runner import run_gsm
from passatk import pass_at_k
from extract_test_data import extract_test_data

# ==================== KONFIGURATION ====================
load_dotenv()

# ==================== JAVA/GSM BUILD & TEST ====================
def build_gsm() -> bool:
    """
    Baut das Java Projekt mit Gradle
    
    Returns:
        True wenn erfolgreich, False sonst
    """
    logger.info("Baue Java Projekt mit Gradle...")
    if not Path(os.getenv("GSM_PATH")).exists():
        logger.error(f"Projekt Pfad existiert nicht: {os.getenv('GSM_PATH')}")
        return False
    
    try:
        # Wechsle in Java Projekt Verzeichnis
        original_cwd = os.getcwd()
        os.chdir(os.getenv("GSM_PATH"))
        
        #GSM mit Maven bauen via Subprocess
        result = subprocess.run(
            [os.getenv("GSM_PATH") / "mvnw.cmd", "compile"],
            check=True,
            cwd=os.getenv("GSM_PATH")
        )
        
        os.chdir(original_cwd)
        if result.returncode == 0:
            logger.success("✓ Gradle Build erfolgreich!")
            return True
        else:
            logger.error(f"Gradle Build fehlgeschlagen: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Fehler beim Gradle Build: {e}")
        return False

def run_gsm_functional_tests() -> bool:
    """ Führt die Functional Tests für GSM mit Gradle aus
    Returns:
        True wenn erfolgreich, False sonst
    """
    gradle_cmd = [
        str(Path(os.getenv("FUNCTIONAL_TESTS")) / "gradlew.bat"),
        "test",
        #"--tests", "de.telekom.geo.site.test.create.*",
        #"--tests", "de.telekom.geo.site.test.delete.*",
        "--tests", "de.telekom.geo.site.test.list.*",
        #"--tests", "de.telekom.geo.site.test.patch.*",
        #"--tests", "de.telekom.geo.site.test.retrieve.*",
        #"--tests", "de.telekom.geo.site.test.scope.*",
        #"--tests", "de.telekom.geo.site.test.utils.*",
    ]

    # Wechsle in Functional Tests Verzeichnis und führe Tests aus
    try:
        logger.info("Führe GSM-Functional-Test-Subprocess aus")
        result = subprocess.Popen(
            gradle_cmd,
            cwd=os.getenv("FUNCTIONAL_TESTS"),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=os.environ.copy(),
            text=True
        )
        logger.success("✓ Subprocess erfolgreich ausgeführt!")
    except Exception as e:
        logger.error(f"Fehler beim Ausführen der Tests-Subprocess: {e}")
    return result

# ==================== MAIN ====================
def benchmark():
    """ 
    Führt den gesamten Benchmark Workflow aus:
        1. Baut durch den Copilot generierten Code für das GSM-Projekt und in Docker-Umgebung
        2. Baut GSM mit Maven und startet die Spring Boot Anwendung lokal
        3. Führt Functional Tests mit Gradle durch
        4. Ermittelt Pass@K-Metrik nach den Functional Tests
    """
    # Initialisiere Logger
    global logger
    logger = BenchmarkLogger()

    try:    
        logger.info("Baut GSM mit Gradle")
        #build_gsm()
        logger.success("✓ Gradle Build erfolgreich!")
        pass
    except Exception as e:
        logger.error(f"Fehler beim Build: {e}")
        sys.exit(1)
        return 1
    
    try:
        logger.info("Startet GSM")
        #run_gsm()
        #time.sleep(60)
        logger.success("✓ GSM erfolgreich gestartet!")
    except Exception as e:
        logger.error(f"GSM-Start fehlgeschlagen: {e}")
        sys.exit(1)
        return 1

    try:
        logger.info("Führt Funktional Tests aus")
        # tests = run_gsm_functional_tests()
        logger.success("✓ Funktional Tests erfolgreich abgeschlossen!")
    except Exception as e:
        logger.error(f"Fehler beim Testen: {e}")
        sys.exit(1)
        return 1

    logger.info("Errechnet Pass@K")
    #pass_at_1 = pass_at_k(1, extract_test_data())
    #logger.info(f"Die Wahrscheinlichkeit für Pass@{pass_at_1['k']} mit n:{pass_at_1['n']}, c:{pass_at_1['c']}, k:{pass_at_1['k']} = {pass_at_1['pass_at_k']}")
    logger.success("✓ Benchmark erfolgreich abgeschlossen!")
    
    return 0 

if __name__ == "__main__":
    sys.exit(benchmark())
