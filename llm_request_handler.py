from langchain.agents import create_agent
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain_core.messages import message_to_dict
from pathlib import Path    
from prompt import Prompt
from benchmark_logger import BenchmarkLogger

#Laden der Umgebungsvariablen aus der .env Datei
from dotenv import load_dotenv
load_dotenv()

#global logger
logger = BenchmarkLogger()

system_prompt_java = """Your task is to generate java code for the given user prompt. Only generate java code and nothing else. 
    If you include any explanations or comments, please add them as java comments."""

system_prompt_python = """Your task is to generate python code for the given user prompt. Only generate python code and nothing else. 
    If you include any explanations or comments, please add them as python comments."""

def llm_request(model_name: str, user_prompt: Prompt, system_prompt: str | None, tools: list | None) -> None:
    """ Führt eine Anfrage an das LLM aus, um Code zu generieren, und speichert die Ergebnisse in Text- und Java-Dateien.
    
    Parameter:
    - model_name (str): Der Name des Modells, das für die Codegenerierung verwendet werden soll.
    - user_prompt (Prompt): Ein Prompt-Objekt, das die Details der Anfrage enthält (use_case, prompt_type, prompt).
    - system_prompt (str | None): Ein optionaler System-Prompt, der Anweisungen für die Codegenerierung enthält.
    - tools (list | None): Eine optionale Liste von Tools, die für die Codegenerierung verwendet werden können.
    """
    # Initialisieren von Langfuse Client und Handler
    langfuse = get_client()
    langfuse_handler = CallbackHandler()

    # Erstellen des Agenten und Ausführung der Anfrage
    agent = create_agent(
        model=model_name,
        system_prompt=system_prompt,
        tools=tools
    )
    for event in agent.stream(
        {"messages": [{"role": "user", "content": user_prompt.prompt}]},
        stream_mode="values",
        #config={"callbacks": [langfuse_handler]}
    ):
        try:
            #logger.info(f"Event Type: {event['type']}")
            logger.success("Events erfolgreich erhalten")
            event["messages"][-1].pretty_print()
            #logger.info(f"Event Messages: {event['messages']}\n")
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten des Events: {e}")

    # Extrahieren des generierten Code's und der Token-Nutzung aus der Antwort
    serializable_messages = [message_to_dict(m) for m in event['messages']]
    code_response = serializable_messages[1]['data']['content']
    token_usage = serializable_messages[1]['data']['response_metadata']['token_usage']
    prompt_tokens = token_usage['prompt_tokens']
    completion_tokens = token_usage['completion_tokens']

    model = model_name.split(':')[1]
    model = model.removeprefix("WARN-GLOBAL_") if model.startswith("WARN-GLOBAL_") else model
    model = model.replace('-', '_').replace('.', '_')
    
    Path(f"generated_code/{model}/{user_prompt.prompt_type}/{user_prompt.use_case}").mkdir(parents=True, exist_ok=True)

    # Speichern des generierten Code's und Token-Nutzung in einer Textdatei und die Java-Methode in einer .java Datei
    logger.info("Speichern der Ergebnisse in txt & java-Dateien")
    try:
        with open(f"generated_code/{model}/{user_prompt.prompt_type}/{user_prompt.use_case}/{user_prompt.use_case}.txt", "w") as f:
            f.write(f"\nModel: {model}\nPrompt-Type: {user_prompt.prompt_type}\nPrompt-Tokens: {prompt_tokens}\
            \nCompletion-Tokens: {completion_tokens}\nPrompt: {user_prompt.use_case}\n{user_prompt.prompt}\nSystem-Prompt:\n{system_prompt}\n")
            logger.success("Erfolgreich in txt-File gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der txt-Datei: {e}")

    try:
        with open(f"generated_code/{model}/{user_prompt.prompt_type}/{user_prompt.use_case}/{user_prompt.use_case}.java", "w") as f:
            f.write(code_response)
            logger.success("Erfolgreich in java-File gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Java-Datei: {e}")

if __name__ == "__main__":
    pass