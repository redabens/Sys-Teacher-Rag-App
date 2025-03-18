import streamlit as st
import requests

# Interface Streamlit
st.title("System Exploitation Teacher")

def wait_for_fastapi():
    """Attend que FastAPI soit prêt"""
    st.info("Attente du démarrage de l'API...")
    max_retries = 30
    for i in range(max_retries):
        try:
            # Essayer de se connecter à FastAPI
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                st.success("API prête!")
                return True
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                time.sleep(2)  # Attendre 2 secondes entre chaque tentative
                continue
            else:
                st.error("Impossible de se connecter à l'API")
                return False

# Attendre que FastAPI soit prêt
if not wait_for_fastapi():
    st.stop()

# Initialisation du résumé RAG dans session_state
if "rag_summary" not in st.session_state:
    response = requests.get("http://localhost:8000/get_rag_summary")
    if response.status_code == 200:
        st.session_state.rag_summary = response.json()["summary"]
    else:
        st.error("Une erreur s'est produite lors de la génération du résumé.")

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar pour les contrôles
with st.sidebar:
    st.title("Contrôles")
    if st.button("Rafraîchir le résumé RAG"):
        response = requests.get("http://localhost:8000/get_rag_summary")
        if response.status_code == 200:
            st.session_state.rag_summary = response.json()["summary"]
            st.success("Résumé RAG mis à jour!")
        else:
            st.error("Une erreur s'est produite lors de la génération du résumé.")
    
    debug_mode = st.checkbox("Mode Debug", value=False)
    if debug_mode:
        st.write("Résumé RAG actuel:", st.session_state.rag_summary)

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie de la question
input_text = st.chat_input("Cher Etudiant, posez votre question:")

if input_text:
    # Affichage de la question de l'utilisateur
    with st.chat_message("user"):
        st.markdown(input_text)
    st.session_state.messages.append({"role": "user", "content": input_text})

    # with st.spinner("Amélioration de votre question..."):
    #     # Amélioration de la question avec contexte RAG
    #     improved_query = query_improver_chain.invoke({
    #         "input": input_text,
    #         "rag_summary": st.session_state.rag_summary.content
    #     })
        
    #     if debug_mode:
    #         st.sidebar.write("Question originale:", input_text)
    #         st.sidebar.write("Question améliorée:", str(improved_query.content))

    # Préparation de l'historique formaté
    chat_history = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in st.session_state.messages
    ])

    with st.spinner("En train de réfléchir pour répondre à votre question..."):
        response = requests.post("http://localhost:8000/chat", json={"input": input_text, "chat_history": chat_history})
        if response.status_code == 200:
            final_answer = response.json()["answer"]
        else:
            st.error("Une erreur s'est produite lors de la génération de la réponse.")
        
        # # Vérification et correction de la réponse
        # final_answer, was_corrected = verify_and_correct_response(
        #     question=str(improved_query.content),
        #     answer=response["answer"],
        #     context=response.get("context", ""),
        #     llm=llm
        # )
        
        # Affichage et sauvegarde de la réponse
        with st.chat_message("assistant"):
            # if was_corrected:
            #     st.warning("La réponse initiale a été corrigée pour plus de précision.")
            st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})