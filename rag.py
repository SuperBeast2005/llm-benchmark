from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document
from langchain_classic.embeddings import CacheBackedEmbeddings  
from langchain_classic.storage import LocalFileStore 
from pathlib import Path
import os
import time
import re
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

def perform_java_chunking(code_document, chunk_size=150, chunk_overlap=30) -> list[Document]:
    """
    Performs recursive chunking on Java code documents using language-aware splitting.
    
    Args:
        code_document (str): The Java code document to process
        chunk_size (int): The target size of each chunk in characters
        chunk_overlap (int): The number of characters of overlap between chunks
        
    Returns:
        list: The chunked code as Document objects with metadata
    """
    code_splitter = RecursiveCharacterTextSplitter.from_language(
                        language=Language.JAVA,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""]
    )
    documents = []
    vollstaendiger_pfad = code_document
    if str(vollstaendiger_pfad).endswith((".java", ".md", ".txt", ".sql", ".class")):  # Nur bestimmte Dateitypen verarbeiten
        try:
            with open(vollstaendiger_pfad, "r", encoding="utf-8") as f:
                content = f.read()
                if str(vollstaendiger_pfad).endswith((".java", ".class")):
                        # Split the code into chunks
                        code_chunks = code_splitter.split_text(code_document)
                        print(f"Code document split into {len(code_chunks)} chunks")
                        # Extract functions and classes for better metadata
                        for i, chunk in enumerate(code_chunks):
                            # Try to identify code structure
                            function_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', chunk)
                            class_match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', chunk)
                            import_match = re.search(r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)', chunk)
                            # Determine chunk type
                            chunk_type = "code_segment"
                            if function_match:
                                chunk_type = "function"
                                structure_name = function_match.group(1)
                            elif class_match:
                                chunk_type = "class"
                                structure_name = class_match.group(1)
                            elif import_match:
                                chunk_type = "import"
                                structure_name = import_match.group(1)
                            else:
                                structure_name = f"segment_{i}"
                            # Create document with enhanced metadata
                            doc = Document(
                                page_content=chunk,
                                metadata={
                                    "source": vollstaendiger_pfad,
                                    "chunk_id": i,
                                    "total_chunks": len(code_chunks),
                                    "language": Language.JAVA,
                                    "chunk_type": chunk_type,
                                    "structure_name": structure_name,
                                    "lines": chunk.count('\n') + 1
                                }
                            )
                            #print(f"Dokument: {doc.metadata['source']} gechunked als {chunk_type} '{structure_name}' mit {doc.metadata['lines']} Zeilen")
                            documents.append(doc)
        except Exception as e:
            print(f"Fehler beim Verarbeiten von {vollstaendiger_pfad}: {e}")
            with open(vollstaendiger_pfad, "r", encoding="cp1252", errors="ignore") as f:
                content = f.read()
                code_chunks = text_splitter.split_text(content)
                for i, chunk in enumerate(code_chunks):
                   vollstaendiger_pfad = Document(
                       page_content=chunk,
                       metadata={
                           "source": str(code_document),
                           "chunk_id": i,
                           "total_chunks": len(code_chunks), # Dateiendung als Sprache
                           "lines": chunk.count('\n') + 1
                       }
                   )
                   print(f"Dokument: {vollstaendiger_pfad}")
                   documents.append(vollstaendiger_pfad)
    else:
        pass

    return documents

# Example: caching a query embedding
#text = "GSM-API: Was ist die Funktion der GeographicSitesController Klasse?"
#single_vector = embeddings.embed_query(text)
#print(str(single_vector)[:100])  # Show the first 100 characters of the vector

def parse_documents(projekt_pfad: Path):
    dateiliste = []
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,  # chunk size (characters)
    chunk_overlap=30,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
    )
    # os.walk geht automatisch durch alle Unterverzeichnisse
    for root, dirs, files in os.walk(projekt_pfad):
        root_path = Path(root)
        for datei in files:
            datei_pfad = root_path / datei
            if str(datei_pfad).endswith((".java", ".md", ".txt", ".sql", ".class")):
                list_of_chunked_docs = perform_java_chunking(datei_pfad)
                for doc in list_of_chunked_docs:
                    dateiliste.extend([doc])
    return dateiliste

docs = parse_documents(GSM_PATH)

document_ids = vector_store.add_documents(documents=docs)
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