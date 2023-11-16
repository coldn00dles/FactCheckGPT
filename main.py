from claimreview.keysInstance import keysInstance
from claimreview.vstoreInstance import vstoreInstance
from claimreview.Embeddings import Embeddings
from claimreview.memoryhandler import memoryhandler
from claimreview.chainhandler import chainhandler
from claimreview.prompts import Prompt
from fastapi import FastAPI
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from fastapi.responses import StreamingResponse
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from typing import AsyncIterable
from pydantic import BaseModel
import asyncio


class Message(BaseModel):  #pydantic object for message input
    content: str

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

#import prompts

prompt = Prompt()
condensed_question_template = prompt.get_prompt()

qa_chain_initializer = chainhandler(openai_api_key, embedder, memory)

app = FastAPI()

@app.get("/api")   #return api status
async def hello_word():  
    return "Yo! Hello world, The backend is running !!!"

async def send_message(query: str) -> AsyncIterable[str]:      #returns streamed output from chatbot
    callbackhandler = AsyncIteratorCallbackHandler()
    model = qa_chain_initializer.get_model(callback_handler=callbackhandler)
    qachain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=vector_store.as_retriever(),
        condense_question_prompt=condensed_question_template,
        memory=memory,
        return_source_documents=True
    )
    
    task = asyncio.create_task(
        qachain.acall({
            "question" : query
        }, return_only_outputs=True)
    )
    try:
        async for token in callbackhandler.aiter():
            yield token 
    except Exception as e:
        print(f"Exception caught : {e}")
    finally:
        callbackhandler.done.set()
        
    await task
    callbackhandler.done.set()

@app.post("/api/chatbot/")
async def chatstream(question: Message):
    answer = send_message(question.content)
    return StreamingResponse(
        answer,media_type="text/event-stream"
    )

