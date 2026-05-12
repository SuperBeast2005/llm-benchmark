# LLM-Benchmark

Ein umfassendes Benchmark-Tool zur Evaluierung von Large Language Models (LLMs) bei der Code-Generierung.

## Überblick

Dieses Projekt ermöglicht die systematische Bewertung verschiedener LLM-Modelle bei der Generierung von Programm-Code. Es nutzt verschiedene Prompt-Techniken und bewertet die Qualität des generierten Codes durch automatisierte Unit-Tests.

![LLM-Benchmark Workflow](Pass@k-Benchmark.jpg)

## Projektstruktur

```
llm-benchmark/
├── benchmark.py          # Hauptmodul für LLM-Benchmarking
├── ai_unittest.py        # Unit-Tests für generierte Codes
├── passatk.py            # Pass@K Metrik-Berechnung
├── prompt.py             # Prompt-Verwaltung
├── generated_code/       # Speicherort für generierte Codes
└── README.md             # Diese Datei
```

## Module

### benchmark.py

Das Hauptmodul für die Benchmark-Durchführung. Es koordiniert:

- **Modellauswahl**: Unterstützt verschiedene LLM-Modelle (GPT-5.4, Gemini Pro 3, Claude Sonnet 4.6)
- **Prompt-Techniken**: 
  - Zero-Shot Prompting
  - Few-Shot Prompting
  - Caveman Prompting
  - Chain-of-Thoughts Prompting
- **Code-Generierung**: Generiert Code basierend auf Benutzer-Prompts
- **Speicherung**: Speichert generierte Codes und Metadaten in strukturierten Verzeichnissen

**Hauptfunktion:**
```python
ai_benchmark(model_name: str, user_prompt: Prompt, system_prompt: str | None, tools: list | None) -> str
```

Die Funktion:
- Erstellt einen Agent mit dem angegebenen Modell
- Ruft das Modell mit dem Prompt auf
- Extrahiert Token-Nutzung und Antworten
- Speichert die Ergebnisse in `generated_code/{model}/{prompt_type}.py` und `.txt`

### ai_unittest.py

Automatisierte Tests zur Validierung von generiertem Code. 

**Funktionen:**
- Importiert generierte Code-Module
- Führt Unit-Tests durch
- Berechnet Pass@K Metriken
- Liefert detaillierte Test-Berichte mit:
  - Anzahl durchgeführter Tests
  - Erfolgreich bestandene Tests
  - Fehlgeschlagene Tests
  - Fehler in der Code-Ausführung

**Beispiel-Output:**
```
--- Zusammenfassung ---
Anzahl der Tests: 1
Erfolgreich: 1
Fehlgeschlagen: 0
Fehler (Code-Errors): 0
```

### passatk.py

Berechnet die **Pass@K Metrik** - eine Standard-Evaluierungsmetrik für Code-Generierung.

**Parameter:**
- `n`: Gesamtzahl der generierten Code-Samples
- `c`: Anzahl der Samples, die alle Unit-Tests bestehen
- `k`: Anzahl der betrachteten Top-Samples

**Formel:**
$$\text{Pass@K} = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}$$

**Interpretation:**
- Gibt die Wahrscheinlichkeit an, dass mindestens einer der Top-K Samples korrekt ist
- Wert zwischen 0% und 100%

**Beispiel:**
```python
# Wahrscheinlichkeit mit 10 Samples, 3 korrekt, Top-5 betrachten
calculate_pass_at_k(10, 3, 5)  # Output: ca. 99.17%
```

## Workflow

Der Benchmark-Prozess folgt diesem Ablauf:

1. **Use-Case Definition**: Spezifische Programmieraufgaben (z.B. API-Endpoints)
2. **Prompt-Auswahl**: Verschiedene Prompt-Techniken auswählen
3. **LLM-Auswahl**: Eines oder mehrere LLM-Modelle bestimmen
4. **Anfrage-Ausführung**: LLM mit Use-Case und Prompt aufrufen
5. **Response-Speicherung**: Generierte Codes als .py und Metadaten als .txt speichern
6. **Test-Validierung**: Code mit Unit-Tests validieren
7. **Metrik-Berechnung**: Pass@K Metrik berechnen und auswerten

## Verwendungsbeispiel

```python
from benchmark import ai_benchmark
from prompt import Prompt

# Einen Benchmark durchführen
ai_benchmark(
    model_name="openai:WARN-GLOBAL_gpt-5.4",
    system_prompt="Your task is to generate python code for the given user prompt. Only generate python code and nothing else.",
    user_prompt=Prompt("test", "Return the factorial of a number in python."),
    tools=None
)
```

## Beispiel-Output

Hier ist ein Beispiel für die Ausgabe der `ai_benchmark` Funktion (aus `generated_code/gpt_5_4/test.txt`):

```
Model: gpt-5.4
Prompt-Type: test
Prompt Tokens: 56        
Prompt:
Return the factorial of a number in python.

Completion Tokens: 56
Response:

def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

## Tests ausführen

Unit-Tests für generierte Codes starten:

```bash
python ai_unittest.py
```

## Anforderungen

- Python 3.8+
- langchain
- langfuse
- python-dotenv
- Zugriff auf LLM-APIs (OpenAI, Google, Anthropic)

## Lizenz

Dieses Projekt ist Teil einer Bachelor-Arbeit.
