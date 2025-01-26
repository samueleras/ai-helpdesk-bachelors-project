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

    ### Create Schema ###
    if not milvus_client.has_collection(collection_name="collection_rag"):

        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )

        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(
            field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=1024
        )
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=10000)
        schema.add_field(field_name="metadata", datatype=DataType.JSON)

        index_params = milvus_client.prepare_index_params()

        index_params.add_index(field_name="id", index_type="STL_SORT")

        index_params.add_index(
            field_name="embedding",
            index_type="AUTOINDEX",
            metric_type=config["milvus"]["metric_type"],
        )

        milvus_client.create_collection(
            collection_name="collection_rag",
            schema=schema,
            index_params=index_params,
        )

        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=False,
        )

        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(
            field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=1024
        )
        schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=200)

        index_params = milvus_client.prepare_index_params()

        index_params.add_index(field_name="id", index_type="STL_SORT")

        index_params.add_index(
            field_name="embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )

        milvus_client.create_collection(
            collection_name="collection_ticket",
            schema=schema,
            index_params=index_params,
        )


def _store_documents_in_vector_db(milvus_client):

    loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter()
    text_chunks = []
    metadata_list = []

    for doc in documents:
        for text_chunk in text_splitter.split_text(doc.page_content):
            text_chunks.append(text_chunk)
            metadata_list.append(doc.metadata)

    embeddings = embedding_model.embed_documents(text_chunks)

    data = [
        {"embedding": embedding, "text": text, "metadata": metadata}
        for embedding, text, metadata in zip(embeddings, text_chunks, metadata_list)
    ]

    milvus_client.insert(collection_name="collection_rag", data=data)

    """ try:
        result = milvus_client.delete(
            collection_name="collection_rag", filter="id >= 0"
        )
        print(f"Deletion result: {result}")
    except Exception as e:
        print(f"Error during deletion: {e}") """


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
    _store_documents_in_vector_db(milvus_client)
