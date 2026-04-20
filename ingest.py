from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma



Data_path = "./backend/Data/Md/"
Db_path = "./backend/db"

def preparar_banco():
    headers_to_split_on = [
        ("#", "titulo_principal"),
        ("##", "origem_conhecimento"), 
        ("###", "subtopico"),
    ]
    
    try : 

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
            )
    except Exception as e :
        print(f"não há header para dividir, {e}")

    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=80
        )
    
    try : 
        loader = DirectoryLoader(
            Data_path,
            glob="*.md",
            loader_cls=TextLoader
             )
    except Exception as e : 
        print(f"Diretorio de dados errado, ou erro em achar arquivos com final .md. {e}")

    
    try:
        documentos = loader.load()
    except Exception as e:
        print(f"Falha no Loader: {e}")
        return

    if not documentos:
        print("Nenhum documento encontrado.")
        return

    fragmentos_do_rag = []

    for doc in documentos:
        chunks_estruturados = markdown_splitter.split_text(doc.page_content)
        chunks_finais = text_splitter.split_documents(chunks_estruturados)
        fragmentos_do_rag.extend(chunks_finais)

    print(f" Processados {len(documentos)} arquivos.")
    print(f" Criados {len(fragmentos_do_rag)} fragmentos com âncoras de metadados")


    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    try:
        vectorstore = Chroma.from_documents(
            documents=fragmentos_do_rag,
            embedding=embeddings,
            persist_directory=Db_path,
            collection_name="verso"
        )
        print(f" O banco 'verso' está pronto para o Self-Healing em {Db_path}")
    except Exception as e:
        print(f"Erro ao persistir banco no Chroma: {e}")

if __name__ == "__main__":
    preparar_banco()