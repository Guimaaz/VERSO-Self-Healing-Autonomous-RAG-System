from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


Data_path = "./backend/Data/Md/"
Db_path = "./backend/db"

def preparar_banco():
    try :
        loader = DirectoryLoader(
            Data_path, 
            glob="*.md", 
            loader_cls=UnstructuredMarkdownLoader
        )
    except  Exception  as e : 
        print(f"erro no Loader, não foi possivel achar pastar em formato .md, ou houve algum erro com o formato do leitor {e}")
    
    documentos = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )

    try : 
        fragmentos = text_splitter.split_documents(documentos)
    except Exception as e :
        print(f"erro no chunking de documentos {e}")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    try :
        vectorstore = Chroma.from_documents(
            documents=fragmentos,
            embedding=embeddings,
            persist_directory=Db_path,
            collection_name="verso"
        )
    except Exception as e :
        print(f"erro ao gerar o vector store {e}")
        

if __name__ == "__main__":
    preparar_banco()