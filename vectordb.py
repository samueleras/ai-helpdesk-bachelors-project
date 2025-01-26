from langchain_ollama import OllamaEmbeddings
from pymilvus import MilvusClient, DataType
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


def _create_user_and_schema():
    return


def initialize_milvus(config_file):
    global milvus_client, config, embedding_model
    config = config_file
    embedding_model = OllamaEmbeddings(model=config["ollama"]["embedding_model"])
    milvus_client = None
    attempts = 0

    while not milvus_client and attempts < 3:
        try:
            milvus_client = MilvusClient(
                uri=config["milvus"]["host"],
                token=config["milvus"]["user"] + ":" + os.getenv("MILVUS_PASSWORD"),
            )
            if not milvus_client.has_collection(collection_name="collection_rag"):
                raise Exception
        except:
            print("Creating user or adjusting password")
            _create_user_and_schema()
        attempts += 1

    if not milvus_client:
        raise ConnectionError("Connecting to Milvus failed.")
