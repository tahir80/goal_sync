import os
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone

# Initialize Pinecone
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENVIRONMENT_REGION"],
)

async def ingest_docs(index_name, chat_history) -> None:

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

    # Check if the index is empty or not
    index = pinecone.Index(index_name)
    index_stats = index.describe_index_stats()
    print(index_stats)
    # if index_stats[0].num_documents == 0:
    #     # Index is empty, add the chat history
    #     Pinecone.from_documents(chat_history, embeddings, index_name=index_name)
    # else:
    #     # Index is not empty, update the embeddings (upsert operation)
    #     Pinecone.upsert_documents(chat_history, embeddings, index_name=index_name)
    