class Prompt: 
    """ Repräsentiert einen Prompt für die Codegenerierung.
    
    Attributes:
        prompt_type (str): Der Typ des Prompts (z.B. "fewshot", "cot", etc.).
        use_case (str): Der Anwendungsfall, für den der Prompt verwendet wird (z.B. "Fakultaet").
        prompt (str): Der eigentliche Prompt-Text, der an das Modell gesendet wird.
    """
    def __init__(self, prompt_type: str, use_case: str, prompt: str):
        self.prompt_type = prompt_type
        self.use_case = use_case
        self.prompt = prompt