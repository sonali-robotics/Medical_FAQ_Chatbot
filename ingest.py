import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_PATH = "data"
FAISS_PATH = "faiss_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

print("Step 1: Loading PDFs from data/ folder...")
loader = PyPDFDirectoryLoader(DATA_PATH)
documents = loader.load()

if len(documents) == 0:
    print("No PDFs found in data/ folder. Please add some PDFs and try again.")
    exit()

print(f"  Loaded {len(documents)} pages.")

print("Step 2: Splitting text into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)
chunks = splitter.split_documents(documents)
print(f"  Created {len(chunks)} chunks.")

print("Step 3: Loading embedding model (downloads ~90MB on first run)...")
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

print("Step 4: Creating FAISS index and saving to disk...")
db = FAISS.from_documents(chunks, embeddings)
db.save_local(FAISS_PATH)

print("\n✅ Done! FAISS index saved.")
print(f"   Files created: {FAISS_PATH}/index.faiss")
print(f"                  {FAISS_PATH}/index.pkl")