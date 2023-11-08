from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts.prompt import PromptTemplate

class chainhandler:
    def __init__(self, openai_api_key, embedder,memory):
        self.openai_api_key = openai_api_key
        self.embedder = embedder
        self.memory = memory

    def get_qa_chain(self, vector_store):
        
        qatemplate = """Your purpose is to debunk claims and give information about them to the user. Respond to queries asked by users in relation to claims made by people, by looking into your own knowledge base provided. Don't counter-confirm yourself, say whatever you want one time itself. ONLY RESPOND WITH INFORMATION FROM YOUR RETRIEVER, DO NOT USE YOUR OWN ASSUMPTIONS.
        Be hospitable to the user, and act like a helpful assistant. Describe your purpose if the user asks you anything.
        DONT ANSWER FROM YOUR OWN EXPERIENCE. DO NOT SPECULATE. DO NOT REFER TO THINGS FROM YOUR ALREADY EXISTING DATABASE, ONLY ADHERE TO WHATEVER IS AVAILABLE IN THE KNOWLEDGE BASE DEFINED.
        You can use the variables below to get more context incase the user decides to cross question you in any case. Don't repeat yourself, try to focus on more recent instances of events instead of replying with older ones.
        Make sure to be hospitable. Use only one source document that is most relevant. Dont add sentences like thats correct or you are correct in your answer.
        Chat History : {chat_history}
        Question : {question}
        Helpful and humane Answer : """
        
        CONDENSE_QUESTION_PROMPT = PromptTemplate(template=qatemplate, input_variables=["chat_history", "question"])

        llm = ChatOpenAI(
            streaming=True,
            openai_api_key=self.openai_api_key,
            model_name="gpt-4-0613",
            temperature=0.0,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        qachain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vector_store.as_retriever(),
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            memory=self.memory,
            return_source_documents=True
        )

        return qachain