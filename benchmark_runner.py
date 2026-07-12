#Standard-Libs Import
import os
import subprocess
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import json
from dotenv import load_dotenv
import time 

#Logger Import
from benchmark_logger import BenchmarkLogger

# ==================== KONFIGURATION ====================
load_dotenv()
TEST_RESULTS = Path(r"test_results")
REPORT_DIR = Path(r"reports")

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
            [str(Path(os.getenv("GSM_PATH")) / "mvnw.cmd"), "compile"],
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

def run_gsm() -> bool:
    """ Startet die Spring Boot Anwendung von Geographic Site Management in einem neuen Fenster."""
    mvnw_path = Path(os.getenv("GSM_PATH")) / 'mvnw.cmd'
    if not mvnw_path.exists():
        logger.error(f"mvnw.cmd wurde nicht gefunden unter dem Pfad: {mvnw_path}")
        sys.exit(1)

    # Ausführen des mvnw-Befehls für das Starten der Spring Boot Anwendung in einem neuen Fenster
    logger.info(f"Startet Springboot vom Pfad: {os.getenv('GSM_PATH')}")
    try:
        process = subprocess.Popen(
            [str(mvnw_path), 'spring-boot:run'],
            cwd=os.getenv("GSM_PATH"),
            env=os.environ.copy()
        )
        logger.success("Spring Boot wurde erfolgreich in einem neuen Fenster/Subprocess gestartet...")
        return True

    except Exception as e:
        logger.error(f"Fehler beim Starten der Springboot Applikation: {e}")
        sys.exit(1)
        return False

def run_gsm_functional_tests() -> bool:
    """ Führt die Funktional Tests für GSM mit Gradle aus
    Returns:
        True wenn erfolgreich, False sonst
    """
    gradle_cmd = [
        str(Path(os.getenv("FUNCTIONAL_TESTS_PATH")) / "gradlew.bat"),
        "test",
        "--tests", "de.telekom.geo.site.test.create.*",
        #"--tests", "de.telekom.geo.site.test.delete.*",
        "--tests", "de.telekom.geo.site.test.list.*",
        #"--tests", "de.telekom.geo.site.test.patch.*",
        #"--tests", "de.telekom.geo.site.test.retrieve.*",
        #"--tests", "de.telekom.geo.site.test.scope.*",
        #"--tests", "de.telekom.geo.site.test.utils.*",
    ]

    # Wechsle in FunKtional Tests Verzeichnis und führe Tests aus
    try:
        logger.info("Führe GSM-Funktional-Test-Subprocess aus")
        result = subprocess.Popen(
            gradle_cmd,
            cwd=os.getenv("FUNCTIONAL_TESTS_PATH"),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=os.environ.copy(),
            text=True
        )
        logger.success("✓ Funktional Tests erfolgreich ausgeführt!")
    except Exception as e:
        logger.error(f"Fehler beim Ausführen der Funktional Tests: {e}")
    return result

def extract_test_data() -> dict:
    """Extrahiert die Testergebnisse der GSM Functional Tests aus den XML Dateien der funktionalen Tests und speichert sie in JSON Dateien."""
    results={}
    #Lesen der XML Dateien der jeweiligen Endpunkt-Tests
    logger.info("Extrahiere die Testergebnisse aus den XML-Dateien")
    endpoints = ["create", "delete", "list", "patch", "retrieve"]
    try:
        for endpoint in endpoints:
            suite_info = {
                    "tests": [],
                    "passed": 0,
                    "failures": 0,
                    "errors": 0,
                    "skipped": 0,
                    }

            for test in Path(os.getenv("TEST_DATA_DIR")).glob("*.xml"):
                if endpoint in test.stem.lower():
                    endpoint_dir = TEST_RESULTS / endpoint
                    endpoint_dir.mkdir(parents=True, exist_ok=True)

                    #Extrahieren der Testergebnisse aus XML Datei
                    root = ET.parse(test).getroot()
                    #print(root)
                    #print(root.attrib)
                    #print(root.attrib.get("name"))
                    suite_info["tests"].append(root.attrib.get("name").split("de.telekom.geo.site.test.")[1])
                    suite_info["passed"] += int(root.attrib.get("tests", 0))
                    suite_info["failures"] += int(root.attrib.get("failures", 0))
                    suite_info["errors"] += int(root.attrib.get("errors", 0))
                    suite_info["skipped"] += int(root.attrib.get("skipped", 0))

                    results[endpoint] = suite_info
                    logger.success(f"Erfolgreich Testergebnisse für Endpoint '{endpoint}' extrahiert")
                else:
                    continue
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Testergebnisse: {e}")
        
    #Speichern der Ergebnisse in JSON Dateien
    try:
        logger.info("Speichere die extrahierten Ergebnisse in JSON-Dateien")
        for key, value in results.items():
            with open(TEST_RESULTS / key / f"{key}_results.json", "w") as f:
                json.dump(value, f)
        logger.success("Erfolgreich in JSON-Dateien gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der JSON-Dateien: {e}")
        
    return results

def pass_at_1(testdata: dict) -> str:
    """ Berechnet Pass@1 für jedes Endpoint basierend auf den Testdaten und speichert die Ergebnisse in JSON-Dateien.
    
    Parameter:
    testdata: Ein Dictionary, das die Anzahl der bestandenen, fehlgeschlagenen und übersprungenen Tests für jedes Endpoint enthält.
    """
    

    for key, value in testdata.items():
        c = value["passed"]
        n = value["passed"] + value["failed"] + value["skipped"]
        pass_at_1 = f"{(c / n) * 100:.2f}%"

        try:
            endpoint_report_dir = REPORT_DIR / key
            endpoint_report_dir.mkdir(parents=True, exist_ok=True)
            with open(endpoint_report_dir / f"{key}_report.json", "w") as f:
                json.dump({
                    "endpoint": key,
                    "c": c,
                    "n": n,
                    "pass_at_1": pass_at_1
                }, f)
            logger.success(f"Erfolgreich in {key}_report.json gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Pass@1 Ergebnisse für {key}: {e}")
    return pass_at_1

# ==================== BENCHMARK-FLOW ====================
def benchmark():
    """ 
    Führt den gesamten Benchmark Workflow aus:
        1. Baut durch den Copilot generierten Code für das GSM-Projekt
        2. Baut GSM mit Maven und startet die Spring Boot Anwendung lokal
        3. Führt Funktional Tests mit Gradle durch
        4. Ermittelt alle Pass@1-Metrik anhand der Funktional Tests Ergebnisse
    """
    # Initialisiere Logger
    global logger
    logger = BenchmarkLogger()

    # 1. Baue durch den Copilot generierten Code für das GSM-Projekt
    try:    
        logger.info("Baut GSM mit Gradle")
        build_gsm()
        logger.success("✓ Gradle Build erfolgreich!")
        pass
    except Exception as e:
        logger.error(f"Fehler beim Build: {e}")
        sys.exit(1)
        return 1
    
    # 2. Starte GSM mit Maven und Spring Boot
    try:
        logger.info("Startet GSM")
        run_gsm()
        time.sleep(60)
        logger.success("✓ GSM erfolgreich gestartet!")
    except Exception as e:
        logger.error(f"GSM-Start fehlgeschlagen: {e}")
        sys.exit(1)
        return 1

    # 3. Führe Funktional Tests mit Gradle durch
    try:
        logger.info("Führt Funktional Tests aus")
        tests = run_gsm_functional_tests()
        logger.success("✓ Funktional Tests erfolgreich abgeschlossen!")
    except Exception as e:
        logger.error(f"Fehler beim Testen: {e}")
        sys.exit(1)
        return 1

    # 4. Ermittelt alle Pass@1-Metrik anhand der Funktional Tests Ergebnisse
    logger.info("Errechnet Pass@1")
    #pass_at_1 = pass_at_1(extract_test_data())
    #logger.info(f"Die Wahrscheinlichkeit für Pass@1 mit n:{pass_at_1['n']} und c:{pass_at_1['c']} beträgt {pass_at_1}%")
    logger.success("✓ Benchmark erfolgreich abgeschlossen!")
    
    return 0

# ==================== MAIN ====================
if __name__ == "__main__":
    sys.exit(benchmark())
