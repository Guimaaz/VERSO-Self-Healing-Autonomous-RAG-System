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
        Avalie se a pergunta refere-se a informações específicas de projetos, decisões anteriores ou dados contidos no manual/memória local.

        - Se a resposta estiver no contexto: Responda 'USA_RAG'.
        - Se a pergunta for geral (ciência, código, etc) e não houver nada no contexto: Responda 'GERAL'.
        - Se for sobre o histórico do usuário/projeto mas o contexto estiver vazio: Responda 'NAO_SEI'.

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
        
        if "NAO_SEI" in decisao:
            return "Eu entendi que você perguntou sobre algo pessoal ou do projeto, mas não encontrei esse detalhe na minha memória. Pode me dar mais contexto?"

        elif "USA_RAG" in decisao or "GERAL" in decisao:
            prompt_final = ChatPromptTemplate.from_template("""
            Você é o sistema VERSO, uma inteligência especializada em recuperação de conhecimento e assistência técnica.
            Sua autoridade máxima emite-se do CONTEXTO LOCAL abaixo.

            ### REGRAS DE EXECUÇÃO:
            1. ESPELHAMENTO DE IDIOMA: Responda obrigatoriamente no mesmo idioma da última frase do Usuário. Se ele falar em Inglês, responda em Inglês. Se for Alemão, responda em Alemão.
            2. PRIORIDADE DE DADOS: O CONTEXTO LOCAL é a sua única fonte de verdade para assuntos pessoais, nomes de projetos e histórico. Se houver conflito com seu treinamento geral, o CONTEXTO LOCAL vence.
            3. ANTI-ALUCINAÇÃO: Jamais diga que "não tem acesso a arquivos" ou que "é apenas um modelo Llama". Você É o VERSO e os dados estão diante de você.
            4. FILTRO DE ENCERRAMENTO: Se o Usuário apenas agradecer (ex: "obrigado", "thanks", "danke") ou encerrar o assunto, responda de forma extremamente breve e aguarde. NÃO inicie novas explicações ou resumos sem ser solicitado.

            ### POSTURA:
            - Seja um professor direto, didático e brutalmente honesto.
            - Trate o interlocutor como "Usuário", mantendo o anonimato e a neutralidade.
            - Sem saudações desnecessárias ou introduções vazias.

            CONTEXTO LOCAL: {contexto}
            PERGUNTA: {pergunta}
            """)
            chain = prompt_final | self.llm | StrOutputParser()
            return chain.invoke({"pergunta": pergunta, "contexto": contexto_bruto})
        else:
            return "Não consegui processar essa informação com base nos meus protocolos atuais."
if __name__ == "__main__":
    verso = VersoEngine()
    historico_sessao = []
    
    print("\n VERSO SYSTEM ONLINE | type : sair, exit or quit to finishe the session and summarize the conversations ")

    while True:
        pergunta = input("👤 You: ")
        
        if pergunta.lower() in ["sair", "exit", "quit"]:
            if historico_sessao:
                verso.sumarizar_e_salvar("\n".join(historico_sessao))
            print(" Verso: Memória sincronizada. Encerrando...")
            break
        
        resposta = verso.responder(pergunta)
        
        historico_sessao.append(f"User: {pergunta}")
        historico_sessao.append(f"AI: {resposta}")
        
        print(f"\nVerso: {resposta}\n")