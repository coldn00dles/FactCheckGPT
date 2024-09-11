from pinecone import Pinecone as pc
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv

class vstoreInstance:
    def __init__(self, pinecone_api_key):
        self.pinecone_api_key = pinecone_api_key
        load_dotenv()  
        self.index_name = os.getenv("INDEXNAME")  
        self.pc = pc(api_key=pinecone_api_key, environment="gcp-starter")

    def get_index(self):
        return self.pc.Index(self.index_name)

    def get_vector_store(self,index, embedder, text_field):
        return PineconeVectorStore(index, embedder, text_field)