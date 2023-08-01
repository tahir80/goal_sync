import os
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter



# Initialize Pinecone
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENVIRONMENT_REGION"],
)

def ingest_docs(index_name, chat_history) -> None:

    # Check if the index already exists, if not, create it
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            metric='cosine',
            dimension=1536
        )

    # Initialize the embeddings
    embeddings = OpenAIEmbeddings()
    # vectorstore = Pinecone(index_name=index_name)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100, chunk_overlap=20, separators=["\n\n", "\n", " ", ""]
    )

    documents = text_splitter.split_documents(documents=chat_history)



    # Check if the index is empty or not
    index = pinecone.Index(index_name)
    index_stats = index.describe_index_stats()
    print(index_stats)
    if index_stats['total_vector_count'] == 0:
        # Index is empty, add the chat history
        Pinecone.from_documents(documents, embeddings, index_name=index_name)
    else:
        # Index is not empty, update the embeddings (upsert operation)
        Pinecone.upsert_documents(documents, embeddings, index_name=index_name)
    