from dotenv import load_dotenv
import os
import openai 
import pinecone
import langchain
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import regex as re 
from langdetect import detect
from deep_translator import GoogleTranslator
from langchain.prompts.prompt import PromptTemplate
import speech_recognition as sr
from gtts import gTTS
import io
load_dotenv()

def init_keys():
    global openai_api_key
    global pinecone_api_key
    openai_api_key = os.getenv("OPENAIKEY")
    pinecone_api_key = os.getenv("PCKEY")
    openai.api_key = openai_api_key
    os.environ["OPENAI_API_KEY"] = openai_api_key

init_keys()

# print(openai.Engine.list()) #testing for openai key validation, don't uncomment for any other reason.

def get_index(indexName):
    pinecone.init(api_key = pinecone_api_key,environment="gcp-starter")
    return pinecone.Index(indexName)

embed = OpenAIEmbeddings(
    model = "text-embedding-ada-002",
    openai_api_key = openai_api_key
)

def get_vector_store(idx,txtfield):
    return Pinecone(idx,embed.embed_query,txtfield)


def get_chain(vstore):
    memory = ConversationBufferMemory(memory_key="chat_history")
    prompt = """Start all your sentences with sure I can assist you with that.You are supposed to answer the user about statements and claims that they ask and give appropiate replies about their validity. Speak humanely and make sure to be polite and hospitable.
    If unaware of an answer or if it cannot be found, reply normally and donot mention the phrases like As an AI in the part of your answer.
    Question : {question}
    Answer : """
    chattemplate = PromptTemplate.from_template(prompt)
    llm = ChatOpenAI(
    streaming=True,
    openai_api_key=openai_api_key,
    model_name='gpt-4-0613',
    temperature=0.0,
    callbacks=[StreamingStdOutCallbackHandler()]
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vstore.as_retriever(),
        condense_question_prompt=chattemplate,
        memory=memory
    )
    return qa 

def sourcereturn(query,vstore):
    sourcelist = []
    a = vstore.similarity_search(query, k=1)
    for doc in a:
        src = doc.metadata.get("source")
        sourcelist.append(src)

    # Function to extract domain from a URL using regex
    def extract_domain(url):
        match = re.search(r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)', url)
        return match.group(1) if match else None

    # Create a set to store unique domains
    unique_domains = set()
    filtered_sourcelist = []

    for source in sourcelist:
        domain = extract_domain(source)
        if domain is not None and domain not in unique_domains:
            filtered_sourcelist.append(source)
            unique_domains.add(domain)

    sources = "\n".join(filtered_sourcelist)
    return sources

# def voicerec():
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Speak!")
#         audio = r.listen(source)
#     try:
#         return r.recognize_whisper_api(audio, api_key=openai_api_key)
#     except sr.RequestError as e:
#         pass

# def txttospeech(text):
#     pygame.init()
#     pygame.mixer.init()
#     tts = gTTS(text)
#     audio_data = io.BytesIO()
#     tts.write_to_fp(audio_data)
#     audio_data.seek(0)
#     pygame.mixer.music.load(audio_data,"mp3")
#     pygame.mixer.music.play()

def chatbot(query,vecstore,qachain):
    claiminfo = qachain({"question" : query})["answer"]
    urls = sourcereturn(claiminfo,vecstore)
    stmt = "For more information click the links provided underneath"
    query_language = detect(query)
    translated = GoogleTranslator(source='auto', target=query_language).translate(stmt) 
    urlstatement = translated + "\n" + urls
    return claiminfo,urlstatement

pindex = get_index(os.getenv("INDEXNAME"))
vectorstore = get_vector_store(pindex,"text")
ragchain = get_chain(vectorstore)

while True:
    method = int(input("""
Demo for FactCheckGPT
Press 1 to chat with our bot via text
Press 2 to chat with our bot via speech (not working for now kindly skip)
Press 3 to exit 
Enter your response : """))
    if method==1:
        query = str(input("Enter what you heard from the internet? : "))
        claim,links = chatbot(query,vectorstore,ragchain)
        print("\n" + links)
    elif method==2:
        pass
        # query = voicerec()
        # dat,links = chatbot(query,vectorstore,ragchain)
        # print("\n" + links)
        # txttospeech(dat)
    else:
        print("Thank you for using the demo.")
        break