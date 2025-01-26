from langchain_ollama import OllamaEmbeddings
from pymilvus import MilvusClient, DataType
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


def _create_user_and_schema():
    try:
        milvus_client = MilvusClient(uri=config["milvus"]["host"], token="root:Milvus")
    except:
        print(
            "Error: Cannot access root. Root password has to remain default for initial start up."
        )
        return

    ### Create User, Roles, and Privileges ###
    if config["milvus"]["user"] in milvus_client.list_users():
        milvus_client.drop_user(user_name=config["milvus"]["user"])
    milvus_client.create_user(
        user_name=config["milvus"]["user"], password=os.getenv("MILVUS_PASSWORD")
    )
    if "vector_db_rw" not in milvus_client.list_roles():
        milvus_client.create_role(role_name="vector_db_rw")
    milvus_client.grant_privilege(
        role_name="vector_db_rw",
        object_type="Collection",
        privilege="*",
        object_name="*",
    )
    milvus_client.grant_role(
        user_name=config["milvus"]["user"], role_name="vector_db_rw"
    )


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
