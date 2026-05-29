import subprocess
from pathlib import Path
import sys
import os

GSM_PATH = Path(r"C:\DEV\Workspaces\geographic-site-management")

LLM_BENCHMARK = Path(__file__).parent

def run_gsm():

    print(f"Starting Spring Boot application from: {GSM_PATH}")
    print("-" * 60)

    mvnw_path = GSM_PATH / 'mvnw.cmd'
    
    if not mvnw_path.exists():
        print(f"Error: mvnw.cmd not found at {mvnw_path}")
        sys.exit(1)

    try:
        process = subprocess.Popen(
            [str(mvnw_path), 'spring-boot:run'],
            cwd=GSM_PATH,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=os.environ.copy()
        )

        print("Spring Boot wird in einem neuen Fenster gestartet...")

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_gsm()
    pass