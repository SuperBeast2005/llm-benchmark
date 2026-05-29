from pathlib import Path
import json
import xml.etree.ElementTree as ET

TEST_DATA_DIR = Path(r"C:\DEV\Workspaces\gsm-functional-tests\build\test-results\test")
TEST_CLASS_PATH = Path(r"C:\DEV\Workspaces\gsm-functional-tests\src\test\java\de\telekom\geo\site\test") 
TEST_RESULTS = Path(r"test_results")
endpoints = ["create", "delete", "list", "patch", "retrieve"]

def extract_test_data() -> dict:
    results={}
    #Read all XML files in the test results directory and extract test case information
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

                #Join Individual Test Infomration into a single JSON file per endpoint
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
            else:
                continue
        
    #Write results to each endpoint JSON file
    for key, value in results.items():
        with open(TEST_RESULTS / key / f"{key}_results.json", "w") as f:
            json.dump(value, f)
    
    return results

if __name__ == "__main__":
    print(extract_test_data())
    #with open(Path(r"C:\DEV\Workspaces\gsm-functional-tests\build\test-results\test\TEST-de.telekom.geo.site.test.create.CreateDevelopmentAreaSiteTest.xml"), "r", encoding="utf-8") as f:
    #    content = f.read()
    #    print(content)