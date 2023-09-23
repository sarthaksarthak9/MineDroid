import os
import sys
import openai
from googletrans import Translator
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY
PERSIST = False
global query
query = None

if len(sys.argv) > 1:
    query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
    loader = TextLoader("data/data.txt")  # Use this line if you only need data.txt
    # loader = DirectoryLoader("data/")
    if PERSIST:
        index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []

def run_chatbot(query):
    result = chain({"question": query, "chat_history": chat_history})
    chat_history.append((query, result['answer']))
    return result['answer']

if __name__ == "__main__":
    print("Input Some text : ")
    text = input()  # Optional, remove if you are taking input from frontend
    translator = Translator()
    detectedLang = translator.detect(text).lang
    translated = translator.translate(text, dest='en')
    outputText = run_chatbot(translated.text)
    print(translator.translate(outputText, dest=detectedLang).text)
