import subprocess
from pathlib import Path
import sys
import os
from benchmark_logger import BenchmarkLogger

logger = BenchmarkLogger()

GSM_PATH = Path(r"C:\DEV\Workspaces\geographic-site-management")
LLM_BENCHMARK = Path(__file__).parent

def run_gsm():
    """ Startet die Spring Boot Anwendung von Geographic Site Management in einem neuen Fenster."""
    mvnw_path = GSM_PATH / 'mvnw.cmd'
    if not mvnw_path.exists():
        logger.error(f"mvnw.cmd wurde nicht gefunden unter dem Pfad: {mvnw_path}")
        sys.exit(1)

    # Ausführen des mvnw-Befehls für das Starten der Spring Boot Anwendung in einem neuen Fenster
    logger.info(f"Startet Springboot vom Pfad: {GSM_PATH}")
    try:
        process = subprocess.Popen(
            [str(mvnw_path), 'spring-boot:run'],
            cwd=GSM_PATH,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=os.environ.copy()
        )
        logger.success("Spring Boot wurde erfolgreich in einem neuen Fenster/Subprocess gestartet...")

    except KeyboardInterrupt:
        process.terminate()
        logger.warning("GSM durch Keyboard Interupt terminiert")
        sys.exit(0)
    except Exception as e:
        print(f"Fehler beim Starten der Springboot Applikation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_gsm()
    pass