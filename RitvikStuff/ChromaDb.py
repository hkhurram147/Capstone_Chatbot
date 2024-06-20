#pip3 install langchain
#pip install langchain-community
#pip3 install -U langchain-openai

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import retrieval_qa
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

#Will need OPENAI Key before initiating this
embeddings= OpenAIEmbeddings()



#data should be the document that Vidhan created
store = Chroma.from_documents(
    data,
    embeddings,
    ids = [f"{item.metadata['source']}-{index}" for index, item in enumerate(data)],
    collection_name= 'SoilMate',
persist_directory= 'db'
)
store.persist()

#Below is your retriever for Chroma
# retriever = store.as_retriever()