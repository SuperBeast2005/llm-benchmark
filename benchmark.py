from dotenv import load_dotenv
from langchain.agents import create_agent
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain_core.messages import message_to_dict
from pathlib import Path    
from prompt import Prompt

#Load environment variables from .env file
load_dotenv()

# Initialize Langfuse client
langfuse = get_client()

# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler()

system_prompt_java = "Your task is to generate java code for the given user prompt. \
                        Only generate java code and nothing else. If you include any explanations or comments, please add them as java comments."

system_prompt_python = "Your task is to generate python code for the given user prompt. \
                        Only generate python code and nothing else. If you include any explanations or comments, please add them as python comments."

zero_shot_prompt = Prompt("zeroshot", "")
few_shot_prompt = Prompt("fewshot", "")
caveman_prompt = Prompt("caveman", "")
chain_of_thoughts_prompt = Prompt("chain-of-thoughts", "")

list_of_prompts: list[Prompt] = [zero_shot_prompt, few_shot_prompt, caveman_prompt, chain_of_thoughts_prompt]

def ai_benchmark(model_name: str, user_prompt: Prompt, system_prompt: str | None, tools: list | None) -> str:
    agent = create_agent(
        model=model_name,
        system_prompt=system_prompt,
        tools=tools
    )
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt.prompt}]},
        config={"callbacks": [langfuse_handler]}
    )

    serializable_messages = [message_to_dict(m) for m in response['messages']]

    # Extract response details
    code_response = serializable_messages[1]['data']['content']
    token_usage = serializable_messages[1]['data']['response_metadata']['token_usage']
    prompt_tokens = token_usage['prompt_tokens']
    completion_tokens = token_usage['completion_tokens']

    model = model_name.split(':')[1]
    model = model.removeprefix("WARN-GLOBAL_") if model.startswith("WARN-GLOBAL_") else model

    ai_response = f"\nModel: {model}\nPrompt-Type: {user_prompt.prompt_type}\nPrompt Tokens: {prompt_tokens}\
        \nPrompt:\n{user_prompt.prompt}\n\nCompletion Tokens: {completion_tokens}\nResponse:\n\n{code_response}\n"

    model = model.replace('-', '_').replace('.', '_')
    Path(f"generated_code/{model}").mkdir(parents=True, exist_ok=True)

    # Save the AI response and the generated code to separate files
    with open(f"generated_code/{model}/{user_prompt.prompt_type}.txt", "w") as f:
        f.write(ai_response)
    
    with open(f"generated_code/{model}/{user_prompt.prompt_type}.py", "w") as f:
        f.write(code_response)
    
    return print(ai_response)

if __name__ == "__main__":
    #for prompt in list_of_prompts:
    #    ai_benchmark(
    #        model_name="openai:claude-sonnet-4-6",
    #        system_prompt=system_prompt,
    #        user_message=prompt,
    #        tools=None
    #    )
    #    ai_benchmark(
    #        model_name="openai:gpt-5.4",
    #        system_prompt=system_prompt,
    #        user_message=prompt,
    #        tools=None
    #    )
    #    ai_benchmark(
    #        model_name="openai:gemini-pro-3-preview",
    #        system_prompt=system_prompt,
    #        user_message=prompt,
    #        tools=None
    #    )
    ai_benchmark(
        model_name="openai:WARN-GLOBAL_gpt-5.4",
        system_prompt=system_prompt_python,
        user_prompt=Prompt("test", "Return the factorial of a number in python."),
        tools=None
    )
    pass