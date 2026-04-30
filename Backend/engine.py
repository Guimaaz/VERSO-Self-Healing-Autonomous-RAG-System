import os
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import prompt_summarized,final_prompt_file,judge_prompt_file

db_path = "./backend/db"
memory_path = "./backend/Data/Md/memory.md"

class VersoEngine:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = ChatOllama(model="llama3", temperature=0) 
        self.vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings,
            collection_name="verso"
        )
        print(" Verso Engine: Connected with database")

    def commit_memory(self, fact, id_conversation ="session"):
        with open(memory_path, "a", encoding="utf-8") as memory_open:
            memory_open.write(f"\n## {id_conversation }\n")
            memory_open.write(f"- {fact}\n")

        self.vectorstore.add_texts(
            texts=[fact],
            metadatas=[{"origin_of_knowledge": id_conversation }]
        )
        print(f"Memória atualizada: {fact[:50]}...")
    def summarize_and_save(self, history):
        if not history:
            return

        print("Verse: Summarizing the conversation for long-term memory...")
        
        prompt_summarization = ChatPromptTemplate.from_template(prompt_summarized)
        
        chain = prompt_summarization | self.llm | StrOutputParser()
        resume = chain.invoke({"history": history})
        
        self.commit_memory(resume, id_conversation ="resume_session" + os.urandom(2).hex())

    def search_for_knowledge(self, question):
        docs = self.vectorstore.similarity_search(question, k=3)
        return docs

    def context_judge(self, question, context, history):
        prompt_judge = ChatPromptTemplate.from_template(judge_prompt_file)
        
        chain = prompt_judge | self.llm | StrOutputParser()
        decision = chain.invoke({"question": question, "context": context, "history": history})
        return decision.strip().upper()

    def answering(self, question, session_history):
        docs = self.search_for_knowledge(question)
        raw_context = "\n".join([d.page_content for d in docs])
        recent_history = "\n".join(session_history[-6:]) if session_history else "No history yet."
        
        decision = self.context_judge(question, raw_context, recent_history)
        
        if "I_DO_NOT_KNOW" in decision:
            return "I understand you asked about something personal or related to the project, but I can't recall that detail. Could you give me more context?"

        elif "USA_RAG" in decision or "GENERAL" in decision:
            final_prompt = ChatPromptTemplate.from_template(final_prompt_file)
            chain = final_prompt | self.llm | StrOutputParser()
            return chain.invoke({"question": question, "context": raw_context, "history": recent_history})
        else:
            return "I was unable to process this information based on my current protocols"
if __name__ == "__main__":
    verso = VersoEngine()
    session_history = []
    
    print("\n VERSO SYSTEM ONLINE | type : exit to finish the session and summarize the conversation ")

    while True:
        question = input("👤 You: ")
        
        if question.lower() in ["exit"]:
            if session_history:
                verso.summarize_and_save("\n".join(session_history))
            print(" Verso: Memory synchronized. Closing")
            break
        answer = verso.answering(question, session_history)
        
        session_history.append(f"User: {question}")
        session_history.append(f"AI: {answer}")
        
        print(f"\nVerso: {answer}\n")