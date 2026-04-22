import os
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import prompt_sumarizado

db_path = "./backend/db"
memoria_path = "./backend/Data/Md/Memoria.md"

class VersoEngine:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = ChatOllama(model="llama3", temperature=0) 
        self.vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings,
            collection_name="verso"
        )
        print(" Verso Engine: Banco de dados conectado.")

    def modelo_salvamento(self, fato, id_conversa="sessão"):
        with open(memoria_path, "a", encoding="utf-8") as memoria_open:
            memoria_open.write(f"\n## {id_conversa}\n")
            memoria_open.write(f"- {fato}\n")

        self.vectorstore.add_texts(
            texts=[fato],
            metadatas=[{"origem_conhecimento": id_conversa}]
        )
        print(f"Memória atualizada: {fato[:50]}...")
    def sumarizar_e_salvar(self, historico):
        if not historico:
            return

        print("Verso: Sumarizando conversa para memória de longo prazo...")
        
        prompt_sumarizacao = ChatPromptTemplate.from_template(prompt_sumarizado)
        
        chain = prompt_sumarizacao | self.llm | StrOutputParser()
        resumo = chain.invoke({"historico": historico})
        
        self.modelo_salvamento(resumo, id_conversa="Resumo_Sessao_" + os.urandom(2).hex())

    def buscar_conhecimento(self, pergunta):
        docs = self.vectorstore.similarity_search(pergunta, k=3)
        return docs

    def juiz_de_contexto(self, pergunta, contexto):
        prompt_juiz = ChatPromptTemplate.from_template("""
        Você é um Juiz de Qualidade. Sua tarefa é avaliar se o contexto abaixo é útil para responder à pergunta.
        Responda apenas com 'SIM' ou 'NAO'.
        
        Pergunta: {pergunta}
        Contexto: {contexto}
        """)
        
        chain = prompt_juiz | self.llm | StrOutputParser()
        decisao = chain.invoke({"pergunta": pergunta, "contexto": contexto})
        return decisao.strip().upper()

    def responder(self, pergunta):
        docs = self.buscar_conhecimento(pergunta)
        contexto_bruto = "\n".join([d.page_content for d in docs])
        
        decisao = self.juiz_de_contexto(pergunta, contexto_bruto)
        
        if "SIM" in decisao:
            prompt_final = ChatPromptTemplate.from_template("""
            Você é o sistema VERSO. Responda diretamente usando o contexto.
            Não se apresente e não diga 'Olá' se não for a primeira interação.
            Seja um professor direto e didático.

            Contexto: {contexto}
            Pergunta: {pergunta}
            """)
            chain = prompt_final | self.llm | StrOutputParser()
            return chain.invoke({"pergunta": pergunta, "contexto": contexto_bruto})
        else:
            return "Informação não encontrada no manual ou memória."
if __name__ == "__main__":
    verso = VersoEngine()
    historico_sessao = []
    
    print("\n VERSO SYSTEM ONLINE | Olá, Gustavo.")

    while True:
        pergunta = input("👤 Você: ")
        
        if pergunta.lower() in ["sair", "exit", "quit"]:
            if historico_sessao:
                verso.sumarizar_e_salvar("\n".join(historico_sessao))
            print(" Verso: Memória sincronizada. Encerrando...")
            break
        
        resposta = verso.responder(pergunta)
        
        historico_sessao.append(f"User: {pergunta}")
        historico_sessao.append(f"AI: {resposta}")
        
        print(f"\nVerso: {resposta}\n")