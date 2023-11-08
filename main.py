from claimreview.keysInstance import keysInstance
from claimreview.vstoreInstance import vstoreInstance
from claimreview.Embeddings import Embeddings
from claimreview.memoryhandler import memoryhandler
from claimreview.chainhandler import chainhandler
from claimreview.chatbot import Chatbot

#Sample code just to show all the classes and their initialisations

# Initialize keys
keysInstance = keysInstance()
openai_api_key = keysInstance.get_openai_api_key()
pinecone_api_key = keysInstance.get_pinecone_api_key()

# Initialize embeddings
Embeddings = Embeddings(openai_api_key)
embedder = Embeddings.get_embedding_object()

#Initialize index and vectorstore
vstoreInstance = vstoreInstance(pinecone_api_key)
idx = vstoreInstance.get_index()
vector_store = vstoreInstance.get_vector_store(idx, embedder, "text")

# Initialize MemoryHandler
memoryhandler = memoryhandler()
memory = memoryhandler.get_memory()

# Initialize QA chain and the chatbot
qa_chain_initializer = chainhandler(openai_api_key, embedder, memory)
convchain = qa_chain_initializer.get_qa_chain(vector_store)
chatbot = Chatbot(convchain)

# Sample Chatbot logic 
while True:
    user_question = str(input("\nHi what would you like to ask today?\n "))
    print(chatbot.run(user_question))


