from langchain.chat_models import ChatOpenAI
class chainhandler:
    def __init__(self, openai_api_key, embedder,memory):
        self.openai_api_key = openai_api_key
        self.embedder = embedder
        self.memory = memory
        
    def get_callback_handler(self):
        return self.callback_handler

    def get_model(self,callback_handler):
        llm = ChatOpenAI(
            streaming=True,
            openai_api_key=self.openai_api_key,
            model_name="gpt-4-1106-preview",
            temperature=0.0,
            callbacks=[callback_handler]
        )
        return llm