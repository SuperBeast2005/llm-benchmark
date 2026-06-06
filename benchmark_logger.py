from pathlib import Path
from datetime import datetime

class BenchmarkLogger:
    """ Ein einfacher Logger für Benchmarking-Zwecke, der Nachrichten mit Zeitstempel und Log-Level in eine Datei schreibt.
    
    Methoden:
    - log(message: str, level: str = "INFO"): Loggt eine Nachricht mit einem bestimmten Log-Level.
    - info(message: str): Loggt eine Nachricht mit dem Log-Level "INFO".
    - error(message: str): Loggt eine Nachricht mit dem Log-Level "ERROR".
    - success(message: str): Loggt eine Nachricht mit dem Log-Level "SUCCESS".
    - warning(message: str): Loggt eine Nachricht mit dem Log-Level "WARNING".
    """
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Loggt eine Nachricht mit Zeitstempel und Log-Level
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print("=" * 60)
        print(log_message)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
            
    # Hilfsmethoden für verschiedene Log-Level
    def info(self, message: str):
        self.log(message, "INFO")
    
    def error(self, message: str):
        self.log(message, "ERROR")
    
    def success(self, message: str):
        self.log(message, "SUCCESS")
    
    def warning(self, message: str):
        self.log(message, "WARNING")

class RAGLogger:
    def __init__(self):
        pass

    def log(self, message:str, level:str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print("=" * 60)
        print(log_message)

    # Hilfsmethoden für verschiedene Log-Level
    def info(self, message: str):
        self.log(message, "INFO")
    
    def error(self, message: str):
        self.log(message, "ERROR")
    
    def success(self, message: str):
        self.log(message, "SUCCESS")
    
    def warning(self, message: str):
        self.log(message, "WARNING")