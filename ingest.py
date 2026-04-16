from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


Data_path = "./backend/data/md/"
Db_path = "./backend/db"

def preparar_banco():
    loader = DirectoryLoader(
        Data_path, 
        glob="./*.md", 
        loader_cls=UnstructuredMarkdownLoader
    )
    
    documentos = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )
    fragmentos = text_splitter.split_documents(documentos)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(
        documents=fragmentos,
        embedding=embeddings,
        persist_directory=Db_path,
        collection_name="ayron_lab"
    )

if __name__ == "__main__":
    preparar_banco()