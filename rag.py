from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import os
import time
from langchain_classic.embeddings import CacheBackedEmbeddings  
from langchain_classic.storage import LocalFileStore 
from dotenv import load_dotenv
load_dotenv()  # Lädt die Umgebungsvariablen aus der .env-Datei

GSM_PATH = Path(r"C:\DEV\Workspaces\geographic-site-management")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1024)  # Beispiel: OpenAI Embeddings mit 1024 Dimensionen
vector_store = InMemoryVectorStore(embeddings)

# Create your underlying embeddings model
#underlying_embeddings = ... # e.g., OpenAIEmbeddings(), HuggingFaceEmbeddings(), etc.

# Store persists embeddings to the local filesystem
# This isn't for production use, but is useful for local
store = LocalFileStore(Path(__file__).parent / "./cache/")
#
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    store,
    namespace=embeddings.model
)

# Example: caching a query embedding
text = "GSM-API: Was ist die Funktion der GeographicSitesController Klasse?"
single_vector = embeddings.embed_query(text)
print(str(single_vector)[:100])  # Show the first 100 characters of the vector

def extract_documents(projekt_pfad: Path) -> list[Document]:
    dateiliste = []

    # os.walk geht automatisch durch alle Unterverzeichnisse
    for root, dirs, files in os.walk(projekt_pfad):
        for datei in files:
            # Verbindet den Ordnerpfad mit dem Dateinamen
            vollstaendiger_pfad = os.path.join(root, datei)
            print(f"Verarbeite Datei: {vollstaendiger_pfad}")
            if vollstaendiger_pfad.endswith((".java", ".md", ".txt", ".properties", ".sql")):  # Nur bestimmte Dateitypen verarbeiten
                try:
                    with open(vollstaendiger_pfad, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(vollstaendiger_pfad, "r", encoding="cp1252", errors="replace") as f:
                        content = f.read()
                #print(content)
        vollstaendiger_pfad = Document(page_content=content, metadata={"source": vollstaendiger_pfad})
        dateiliste.append(vollstaendiger_pfad)

    return dateiliste

docs = extract_documents(GSM_PATH)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

print(f"Split blog post into {len(all_splits)} sub-documents.")
print(all_splits[0])

document_ids = vector_store.add_documents(documents=all_splits)
print(document_ids[:3])


#from langchain.tools import tool
#
#@tool(response_format="content_and_artifact")
#def retrieve_context(query: str):
#    """Retrieve information to help answer a query."""
#    retrieved_docs = vector_store.similarity_search(query, k=2)
#    serialized = "\n\n".join(
#        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
#        for doc in retrieved_docs
#    )
#    return serialized, retrieved_docs

if __name__ == "__main__":
    #print(extract_documents(GSM_PATH))
    pass