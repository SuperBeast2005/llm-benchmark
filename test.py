import asyncio
from copilot import CopilotClient
from copilot.session import PermissionHandler
from prompt import Prompt

GENERATED_JAVA_DIR = Path(__file__).parent / "generated_code" 
FUNCTIONAL_TESTS = Path(r"C:\DEV\Workspaces\gsm-functional-tests")

GSM_APP = Path(r"C:\DEV\Workspaces\geographic-site-management\src\main\java\de\telekom\gsm\api\GeographicSitesController.java")

#LLM's
gpt = "gpt-5-mini"
#Prompts
caveman = Prompt("caveman", 
                 "Endpunkt für den Test listGeographicSite implementieren", 
                 f"Bitte implementiere unter dem Verzeichnis {GENERATED_JAVA_DIR} eine Java-Methode, die den Endpunkt für den Test listGeographicSite implementiert.\
                Der Test befindet sich unter dem Verzeichnis {FUNCTIONAL_TESTS}. Ziel ist es dass die Test listGeographicSite erfolgreich durchläuft.\
                Den Controller findest du unter {GSM_APP}.\
                Frage mich nach nichts, einfach nur den generierten Code in eine Java-Datei unter {GENERATED_JAVA_DIR} speichern. Du hast die Erlaubnis, auf das Dateisystem zuzugreifen und Dateien zu lesen und zu schreiben."
                )

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session(on_permission_request=PermissionHandler.approve_all, model="gpt-5-mini")
    response = await session.send_and_wait(r'Pls write Java Code that successfully passes the following test: r"C:\\DEV\\Workspaces\\functional-tests\\src\\test\\java\\de\\telekom\\geo\\address\\test\\address\\address\\list" \
                                            I give u the permission to access the file system and read the content of the file. The file contains a Java code snippet.\
                                            Your task is to write Java code that successfully passes the test by reading the content of the file and executing it.\
                                           Pls write the Java Code in a file under the path C:\Users\A200274077\OneDrive - Deutsche Telekom AG\Desktop\Studium\Semester 6\Bachelor-Arbeit\llm-benchmark\generated_code')
    print(response.data.content)

    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())

async def invoke_copilot(model: str, user_prompt: Prompt) -> str:
    client = CopilotClient()
    await client.start()

    session = await client.create_session(on_permission_request=PermissionHandler.approve_all, model=model)
    response = await session.send_and_wait(user_prompt.prompt)

    await client.stop()
    return response.data.content