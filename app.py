import os
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from login_page import show_login_page

# Load environment variables
load_dotenv()

FAISS_PATH  = "faiss_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL  = "llama-3.1-8b-instant"

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# ---------------- LOAD MODELS ----------------
@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

@st.cache_resource
def load_llm():
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=0.2,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

# ---------------- MAIN LOGIC ----------------
def get_answer(question: str) -> dict:
    db  = load_vectorstore()
    llm = load_llm()

    retriever = db.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in docs])

    # 🌐 Language logic
    selected_lang = st.session_state.get("language", "Auto (Detect)")

    if selected_lang == "Auto (Detect)":
        lang_instruction = "Detect the language of the question and respond in the same language."
    else:
        lang_instruction = f"Always respond in {selected_lang}, regardless of the question language."

    # Prompt
    if context.strip():
        filled_prompt = f"""
You are a helpful medical information assistant.

Instructions:
- {lang_instruction}
- Use the context if it is relevant.
- If not useful, use your own medical knowledge.
- Never make up information.
- If unsure, say you don't know.
- Always recommend consulting a real doctor.

Context:
{context}

Question: {question}

Answer:
"""
    else:
        filled_prompt = f"""
You are a helpful medical information assistant.

Instructions:
- {lang_instruction}
- Answer using your own knowledge.
- Never make up information.
- If unsure, say you don't know.
- Always recommend consulting a real doctor.

Question: {question}

Answer:
"""

    response = llm.invoke(filled_prompt)

    return {
        "result": response.content,
        "source_documents": docs
    }

# ---------------- UI ----------------
st.set_page_config(
    page_title="Medical FAQ Chatbot🩺",
    page_icon="🩺",
    layout="centered"
)

col1, col2 = st.columns([4, 1])

with col1:
    st.title("Medical FAQ Chatbot🩺")
    st.caption(f"Logged in as *{st.session_state.username}*")

with col2:
    st.write("")
    st.write("")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# ---------------- CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role = msg["role"]
    label = "You" if role == "user" else "Bot"
    with st.chat_message(role):
        st.markdown(f"*{label}:* {msg['content']}")

if user_input := st.chat_input("Ask a medical question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(f"*You:* {user_input}")

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = get_answer(user_input)
                answer = result["result"]
                sources = result["source_documents"]

                st.markdown(f"*Bot:* {answer}")

                with st.expander("📄 Sources"):
                    for i, doc in enumerate(sources, 1):
                        src  = doc.metadata.get("source", "Unknown")
                        page = doc.metadata.get("page", "?")
                        st.markdown(f"*Source {i}:* {os.path.basename(src)} — Page {page}")
                        st.markdown(f"> {doc.page_content[:300]}...")

            except FileNotFoundError:
                answer = "FAISS index not found. Run ingest.py first."
                st.error(answer)
            except Exception as e:
                answer = f"Error: {str(e)}"
                st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------------- SIDEBAR ----------------
with st.sidebar:

    # 🌐 Language Selector
    st.header("🌐 Language")
    language = st.selectbox(
        "Choose response language:",
        ["Auto (Detect)", "English", "Hindi", "Spanish", "French"]
    )
    st.session_state.language = language

    st.header("About")
    st.info(
        "Welcome to the *Medical FAQ chatbot* for general health questions.\n\n"
        "⚠️ Always consult a real doctor for medical advice."
    )

    st.header("Topics")
    st.markdown("""
    1. Common diseases & conditions
    2. Symptoms & treatments
    3. Medicines & side effects
    4. General health knowledge
    """)
    st.header("Chat Controls")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.header("Knowledge Base")
    if os.path.exists(FAISS_PATH):
        st.success("This chatbot uses a curated medical knowledge base to provide accurate, reliable, and context-aware health information.")
    else:
        st.error("FAISS index missing. Run ingest.py.")