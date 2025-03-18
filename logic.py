from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.callbacks import BaseCallbackHandler
import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware



load_dotenv()

os.environ["LANGCHAIN_API_KEY"]= os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]= "true"

# Constantes
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
K_DOCUMENTS = 10
EMBEDDING_MODEL_NAME = "nomic-embed-text"
PDF_DIR = "./Sys"


# Initialiser le LLM (Groq Api Inference)
llm = ChatOllama(model="llama3")
# Fonctions
# Fonction pour traiter les documents
def process_documents(PDF_DIR=PDF_DIR):
    docs = PyPDFDirectoryLoader(PDF_DIR).load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
    )
    documents = text_splitter.split_documents(docs)
    return docs, documents

# Fonction pour générer un résumé des documents
def get_rag_summary(docs):
    try:
        # Créer un prompt pour générer un résumé
        summary_prompt = ChatPromptTemplate.from_template("""
        Tu es un expert en systèmes d'exploitation chargé de créer un résumé concis et structuré.
        
        Analyse le contexte suivant :
        <context>
        {context}
        </context>
        
        Génère moi un sommaire detaillers de tous les points sujets couverts dans le contexte.
        Tu dois detailler chaque point briévement et expliquer son importance.
        
        Ce sommaire sera utilisé comme contexte a un llm pour améliorer les questions de l'utilisateur.
        """)
        
        # Concaténer tous les page_content
        full_context = "\n\n".join([doc.page_content for doc in docs])
        print(f"Contexte complet généré, longueur: {len(full_context)}")
        
        # Créer une chaîne simple pour le résumé
        summary_chain = summary_prompt | llm
        
        # Obtenir le résumé en passant directement le contexte complet
        response = summary_chain.invoke({"context": full_context})
        print(f"Réponse du LLM: {response}")
        
        return response
    except Exception as e:
        print(f"Erreur dans get_rag_summary: {str(e)}")
        raise e

# Créer les embeddings avec Ollama Embeddings
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
docs, documents = process_documents()
vectorstore = Chroma.from_documents(documents, embedding=embeddings)


# Prompts

# Template du prompt principal
main_prompt = ChatPromptTemplate.from_template("""
    Vous êtes un **professeur expert**, chargé d'expliquer un sujet de manière **pédagogique, complète et précise**.  
    Votre mission est d'enseigner le sujet **comme si vous expliquiez à des étudiants**, en les aidant à comprendre en profondeur.  

    ### **Méthodologie d'analyse et d'explication :**  
    🔍 **Analyse du contexte fourni** :  
    - Lisez et comprenez attentivement le contexte avant de formuler une réponse.  
    - Identifiez les concepts clés et les informations pertinentes liées à la question posée.  
    - Vérifiez si certaines informations sont manquantes ou si des erreurs doivent être corrigées.  

    📚 **Méthodologie d'enseignement** :  
    1️⃣ **Introduction claire** : Présentez le sujet en expliquant son importance et son utilité.  
    2️⃣ **Explication progressive** : Développez les concepts de manière claire, en partant des bases avant d'aller vers des notions plus avancées.  
    3️⃣ **Illustrations et analogies** : Utilisez des exemples concrets et des analogies pour faciliter la compréhension.  
    4️⃣ **Correction des confusions fréquentes** : Anticipez les erreurs ou malentendus que les apprenants pourraient avoir.  
    5️⃣ **Exemples d'application** : Montrez comment ces connaissances peuvent être appliquées en pratique.  
    6️⃣ **Regroupement final** : Présentez **tout ce qui a été expliqué** sous une forme claire et organisée.  
    7️⃣ **Ajoutez une section "📌 Ce que les étudiants oublient souvent"**

    ### **Historique de la conversation :**
    {chat_history}
    
    ### **Contexte donné :**  
    <context>  
    {context}  
    </context>  

    ### **Question actuelle :**  
    {input}  

    📖 **Explication pédagogique détaillée :**
    """)

# Création des chaînes
retriever = vectorstore.as_retriever(search_kwargs={"k": K_DOCUMENTS})
document_chain = create_stuff_documents_chain(llm=llm, prompt=main_prompt)
qa_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=document_chain)

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A server that uses Langchain for a teacher chatbot",
)
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/get_rag_summary")
async def get_summary_endpoint():
    try:
        summary = get_rag_summary(docs)
        print(summary)
        return {"summary": summary.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        input = data.get("input")
        chat_history = data.get("chat_history")
        response = qa_chain.invoke({"input": input, "chat_history": chat_history})
        return {"answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


        
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
