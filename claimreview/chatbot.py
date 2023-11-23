from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap
from langchain.schema.output_parser import StrOutputParser
from langchain.chat_models import ChatOpenAI
from claimreview.prompts import Prompt
import regex as re
class Chatbot:
    def __init__(self,vector_store,openai_api_key):
        self.retriever = vector_store.as_retriever()
        self.openai_api_key = openai_api_key
        self.op_parser = StrOutputParser()
        self.ptemp = Prompt()
    
    def get_lcel(self):
        llm = ChatOpenAI(
            streaming=True,
            openai_api_key=self.openai_api_key,
            model_name="gpt-4-0613",
            temperature=0.0,
        )
        prompt = self.ptemp.chatTemplate()
        chain = RunnableMap(
        {
        "context" : lambda x : self.retriever.get_relevant_documents(x["question"]),
        "question" : lambda x : x["question"]
        }) | prompt | llm | self.op_parser
        return chain
        