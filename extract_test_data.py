from pathlib import Path
import json
import xml.etree.ElementTree as ET
from benchmark_logger import BenchmarkLogger

logger = BenchmarkLogger()

TEST_DATA_DIR = Path(r"C:\DEV\Workspaces\gsm-functional-tests\build\test-results\test")
TEST_CLASS_PATH = Path(r"C:\DEV\Workspaces\gsm-functional-tests\src\test\java\de\telekom\geo\site\test") 
TEST_RESULTS = Path(r"test_results")
endpoints = ["create", "delete", "list", "patch", "retrieve"]

def extract_test_data() -> dict:
    """Extrahiert die Testergebnisse der GSM Functional Tests aus den XML Dateien der funktionalen Tests und speichert sie in JSON Dateien."""
    results={}
    #Lesen der XML Dateien der jeweiligen Endpunkt-Tests
    logger.info("Extrahiere die Testergebnisse aus den XML-Dateien")
    try:
        for endpoint in endpoints:
            suite_info = {
                    "tests": [],
                    "passed": 0,
                    "failures": 0,
                    "errors": 0,
                    "skipped": 0,
                    }

            for test in TEST_DATA_DIR.glob("*.xml"):
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

if __name__ == "__main__":
    print(extract_test_data())