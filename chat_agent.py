from langchain_community.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
import chromadb

# —————— Initialization ——————
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Connect to ChromaDB collection
vectorstore = Chroma(
    client=chromadb.PersistentClient(path="./chroma_db"),
    collection_name="food_text_embeddings",
    embedding_function=embedding_model
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer" )

llm = Ollama(model="llama2")

# Create the conversational retrieval agent
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    return_source_documents=True,
    output_key="answer"
)