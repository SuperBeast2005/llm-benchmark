"""
Java Benchmark Runner - Führt Python-Benchmark aus und testet generierten Java Code
Workflow:
1. Generiert Java Code via LLM Benchmark
2. Speichert generierten Code in separates Verzeichnis
3. Führt Gradle Tests aus
4. Vergleicht Ergebnisse
5. Generiert kombiniertem Report
"""
#Standard-Libs Import
import os
import subprocess
from pathlib import Path
from datetime import datetime
import sys
import time
import json

#Eigene Module Import
from benchmark_logger import BenchmarkLogger
from prompt import Prompt
from gsm_runner import run_gsm
from benchmark import ai_benchmark
from passatk import pass_at_k
from extract_testdata import extract_test_data

# ==================== KONFIGURATION ====================
GSM_PATH = Path(r"C:\DEV\Workspaces\geographic-site-management")
GSM_APP = Path(r"C:\DEV\Workspaces\geographic-site-management\src\main\java\de\telekom\gsm\api\GeographicSitesController.java")
FUNCTIONAL_TESTS = Path(r"C:\DEV\Workspaces\gsm-functional-tests")
LLM_BENCHMARK = Path(__file__).parent

# Generierte Java Code Verzeichnisse
GENERATED_JAVA_DIR = Path(__file__).parent / "generated_code" 
REPORT_DIR = Path(__file__).parent / "reports"
TEST_RESULTS = Path(r"C:\DEV\Workspaces\gsm-functional-tests\build\test-results\test\binary")

# ==================== LLM'S & PROMPTS ====================
#LLM's
claude = "claude-sonnet-4-6"
gemini = "openai:WARN-GLOBAL_gemini-3-pro-preview"
chat_gpt = "openai:gpt-4.1"
mistral = "mistral-large-3"

llms: list[str] = [
    chat_gpt,
    mistral
]

#Prompts
few_shot = Prompt("fewshot", 
                  "Fakultaet", 
                  "Erstelle eine Java Klasse, die die Fakultät einer Zahl berechnet. Zeige 2 Beispiele in der Klasse."
                  )

caveman = Prompt("caveman", 
                 "Fakultaet", 
                 "Erstelle eine Java Klasse, Soll Fakütltät brechen. Zeige 2 Beispiele in der Klasse."
                 )

cot = Prompt("cot",
             "Fakultaet", 
             "Erstelle eine Java Klasse, die die Fakultät einer Zahl berechnet. Zeige 2 Beispiele in der Klasse. Erkläre deine Schritte in Java Kommentaren."
             )

react = Prompt("react", 
               "Fakultaet", 
               "Erstelle eine Java Klasse, die die Fakultät einer Zahl berechnet. Verwende die React Methode. Zeige 2 Beispiele in der Klasse."
               )

prompts: list[Prompt] = [few_shot, caveman, cot, react]
test_prompts: list[Prompt] = [
    few_shot,
    caveman,
]

#Java System Prompt
system_prompt = """Your task is to generate java code for the given user prompt. 
Only generate java code and nothing else. The code should be a complete, compilable class.
If you include any explanations or comments, please add them as java comments.
Make sure the code is production-ready, includes proper error handling and has the same class name as the java file name."""

# ==================== GENERIERUNG & EINBINDUNG DES JAVA CODES ====================
def run_python_benchmark(models: list[str], prompts: list[Prompt]):
    try:
        for llm in models:
            for user_prompt in prompts:
                logger.info("=" * 60)
                logger.info(f"Generiert Code für:{user_prompt.use_case} mit Prompt-Typ:{user_prompt.prompt_type} und Modell:{llm}")

                # Führe Benchmark aus
                ai_benchmark(
                    model_name=llm,
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    tools=None
                )
                logger.info("=" * 60)
                logger.success("Code Generieren erfolgreich abgeschlossen")
    
    except Exception as e:
        logger.info("=" * 60)
        logger.error(f"Fehler beim Code Generieren: {str(e)}")
        raise
    return models, prompts

def write_to_gsm(model: str, prompt: Prompt): #TODO: Implementieren
    model_name = model.split(':')[1]
    model_name = model_name.removeprefix("WARN-GLOBAL_") if model_name.startswith("WARN-GLOBAL_") else model_name
    model_name = model_name.replace('-', '_').replace('.', '_')
    
    with open(f"generated_code/{prompt.use_case}/{model_name}/{prompt.prompt_type}.java", "r") as f:
        gen_code = f.read()
        print(gen_code)
    
    with open(GSM_APP, "r") as f:
        gsm_code = f.read()
        print(gsm_code)
    #    with open(GSM_PATH / r"src\main\java\de\telekom\gsm\api\GeographicSiteManagement.java", "w") as f:
    #        gsm_code.
    #        new_code = gen_code
    #        f.write(new_code)


# ==================== JAVA/GSM BUILD & TEST ====================
def build_gsm() -> bool:
    """
    Baut das Java Projekt mit Gradle
    
    Returns:
        True wenn erfolgreich, False sonst
    """
    logger.info("Baue Java Projekt mit Gradle...")
    
    if not Path(GSM_PATH).exists():
        logger.info("=" * 60)
        logger.error(f"Projekt Pfad existiert nicht: {GSM_PATH}")
        logger.warning("Bitte GSM_PATH in dieser Datei anpassen!")
        return False
    
    try:
        # Wechsle in Java Projekt Verzeichnis
        original_cwd = os.getcwd()
        os.chdir(GSM_PATH)
        
        result = subprocess.run(
            [GSM_PATH / "mvnw.cmd", "compile"],
            check=True,
            cwd=GSM_PATH
        )
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            logger.info("=" * 60)
            logger.success("Gradle Build erfolgreich")
            return True
        else:
            logger.info("=" * 60)
            logger.error(f"Gradle Build fehlgeschlagen:\n{result.stderr}")
            return False
    
    except Exception as e:
        logger.info("=" * 60)
        logger.error(f"Fehler beim Gradle Build: {str(e)}")
        return False


def run_gsm_functional_tests() -> bool:
    gradle_cmd = [
        str(FUNCTIONAL_TESTS / "gradlew.bat"),
        "test",
        #"--tests", "de.telekom.geo.site.test.create.*",
        #"--tests", "de.telekom.geo.site.test.delete.*",
        "--tests", "de.telekom.geo.site.test.list.*",
        #"--tests", "de.telekom.geo.site.test.patch.*",
        #"--tests", "de.telekom.geo.site.test.retrieve.*",
        #"--tests", "de.telekom.geo.site.test.scope.*",
        #"--tests", "de.telekom.geo.site.test.utils.*",
    ]

    result = subprocess.Popen(
        gradle_cmd,
        cwd=FUNCTIONAL_TESTS,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        env=os.environ.copy(),
        text=True
    )
    return result

# ==================== MAIN ====================
def main():
    
    # Initialisiere Logger
    global logger
    log_file = REPORT_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = BenchmarkLogger(log_file)
    
    logger.info("=" * 60)
    logger.info("Startet Benchmark")
    logger.info("=" * 60)
    logger.info("Generiert Java Code")
    #llms_n_prompts = run_python_benchmark(llms, test_prompts)
    #ai_benchmark(
    #    model_name=gemini,
    #    user_prompt=few_shot,
    #    system_prompt=system_prompt,
    #    tools=None )

    logger.info("=" * 60)
    logger.info("Fügt Java Code zum GSM hinzu")
    
    #for model in llms_n_prompts[0]:
    #    for prompt in llms_n_prompts[1]:
    #        write_to_gsm(model, prompt)
    write_to_gsm(gemini, few_shot)

    logger.info("=" * 60)
    logger.info("Baut GSM mit Gradle")
    try:    
        #build_gsm()
        pass
    except Exception as e:
        logger.error(f"Fehler beim Build: {str(e)}")
        sys.exit(1)
        return 1
    
    logger.info("=" * 60)
    logger.info("Startet GSM")
    #run_gsm()
    #time.sleep(60)

    logger.info("=" * 60)
    logger.info("Führt Functional Tests durch")
    # tests = run_gsm_functional_tests()
    # tests.wait()

    logger.info("=" * 60)
    logger.info("Errechnet Pass@K")
    #pass_at_1 = pass_at_k(1, extract_test_data())
    #logger.info(f"Die Wahrscheinlichkeit für Pass@{pass_at_1['k']} mit n:{pass_at_1['n']}, c:{pass_at_1['c']}, k:{pass_at_1['k']} = {pass_at_1['pass_at_k']}")
    
    logger.info("=" * 60)
    logger.success("✓ Benchmark erfolgreich abgeschlossen!")
    
    return 0 

if __name__ == "__main__":
    sys.exit(main())
