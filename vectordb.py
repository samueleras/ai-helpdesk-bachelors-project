from typing import Callable, List, Tuple
from langchain_ollama import OllamaEmbeddings
from pymilvus import MilvusClient, DataType
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from PyPDF2 import PdfReader
from pathlib import Path
import threading
from custom_types import AppConfig, Ticket

observer_started = False


def _create_user_and_schema():
    try:
        milvus_client: MilvusClient = MilvusClient(
            uri=config["milvus"]["host"], token="root:Milvus"
        )
    except:
        print(
            "Error: Cannot access root. Root password has to remain default for initial start up."
        )
        return
    try:
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
            schema.add_field(
                field_name="text", datatype=DataType.VARCHAR, max_length=10000
            )
            schema.add_field(field_name="metadata", datatype=DataType.JSON)

            index_params = milvus_client.prepare_index_params()

            index_params.add_index(field_name="id", index_type="STL_SORT")

            index_params.add_index(
                field_name="embedding",
                index_type=config["milvus"]["index_type_rag"],
                metric_type=config["milvus"]["metric_type_rag"],
            )

            try:
                milvus_client.create_collection(
                    collection_name="collection_rag",
                    schema=schema,
                    index_params=index_params,
                )
            except:
                print("Collection already exists")

            schema = MilvusClient.create_schema(
                auto_id=False,
                enable_dynamic_field=False,
            )

            schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
            schema.add_field(
                field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=1024
            )
            schema.add_field(
                field_name="title", datatype=DataType.VARCHAR, max_length=200
            )

            index_params = milvus_client.prepare_index_params()

            index_params.add_index(field_name="id", index_type="STL_SORT")

            index_params.add_index(
                field_name="embedding",
                index_type=config["milvus"]["index_type_tickets"],
                metric_type=config["milvus"]["metric_type_tickets"],
            )

            try:
                milvus_client.create_collection(
                    collection_name="collection_ticket",
                    schema=schema,
                    index_params=index_params,
                )
            except:
                print("Collection already exists")

    except Exception as e:
        print(f"Creating Milvus User and Collections failed: {e}")
        raise RuntimeError(f"Creating Milvus User and Collections failed: {e}") from e


def _initialize_directory(milvus_client: MilvusClient, directory: str):
    try:
        res = milvus_client.query(
            collection_name="collection_rag",
            limit=1,
            filter="id >= 0",
        )

        # Abort if there are already entries in the vector db
        if res:
            return

        path = Path(directory)
        pdf_files = list(path.glob("*.pdf"))

        for file in pdf_files:
            file_path = path / file
            file_name = os.path.basename(file_path)
            os.system(f'attrib -h "{file_path}"')
            try:
                reader = PdfReader(file_path)
            except Exception as e:
                print(f"Error on reading PDF file: {e}")
                return
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            text_splitter = RecursiveCharacterTextSplitter()
            text_chunks = []
            metadata_list = []

            for text_chunk in text_splitter.split_text(text):
                text_chunks.append(text_chunk)
                metadata_list.append(file_name)

            embeddings = embedding_model.embed_documents(text_chunks)

            data = [
                {"embedding": embedding, "text": text, "metadata": metadata}
                for embedding, text, metadata in zip(
                    embeddings, text_chunks, metadata_list
                )
            ]

            res = milvus_client.insert(collection_name="collection_rag", data=data)
            print(res)
    except Exception as e:
        print(f"Milvus Directory Initialization failed: {e}")
        raise RuntimeError(f"Milvus Directory Initialization failed: {e}") from e


class DirectoryWatcher(FileSystemEventHandler):
    def __init__(self, milvus_client: MilvusClient):
        self.milvus_client = milvus_client
        self.last_event: Tuple[
            str, str
        ] = ()  # Tracks the last event type for each file path

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.process_unique_event(
                event.src_path, "created/modified", self.process_file
            )

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.process_unique_event(
                event.src_path, "created/modified", self.process_file
            )

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.process_unique_event(event.src_path, "deleted", self.delete_vectors)

    def process_unique_event(
        self, file_path: str, event_type: str, callback: Callable[[str], None]
    ) -> None:
        # Process each event just ones, as windows sometimes logs them multiple time
        event = (file_path, event_type)
        # Abort if this file was processed already
        if self.last_event == event:
            return
        self.last_event = event
        callback(file_path)

    def process_file(self, file_path: str) -> None:
        print(f"Processing file: {file_path}")
        try:
            os.system(f'attrib -h "{file_path}"')
            file_name = os.path.basename(file_path)
            try:
                reader = PdfReader(file_path)
            except:
                print("Error: File not readable. Only pdf files are supported.")
                return
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            text_splitter = RecursiveCharacterTextSplitter()
            text_chunks = []
            metadata_list = []

            for text_chunk in text_splitter.split_text(text):
                text_chunks.append(text_chunk)
                metadata_list.append(file_name)

            embeddings = embedding_model.embed_documents(text_chunks)

            data = [
                {"embedding": embedding, "text": text, "metadata": metadata}
                for embedding, text, metadata in zip(
                    embeddings, text_chunks, metadata_list
                )
            ]

            res = milvus_client.insert(collection_name="collection_rag", data=data)
            print(res)
        except Exception as e:
            print(f"Processing PDF File failed: {e}")

    def delete_vectors(self, file_path: str) -> None:
        print(f"Deleting vectors for file: {file_path}")
        try:
            file_name = os.path.basename(file_path)
            res = milvus_client.delete(
                collection_name="collection_rag",
                filter=f'metadata == "{file_name}"',
            )
            print(res)
        except Exception as e:
            print(f"Processing PDF File failed: {e}")


def _watch_directory(milvus_client: MilvusClient, directory: str) -> None:
    event_handler: DirectoryWatcher = DirectoryWatcher(milvus_client)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    print(f"Watching directory: {directory}")
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


def initialize_milvus(config_file: AppConfig):
    global milvus_client, config, embedding_model, observer_started
    config = config_file
    embedding_model = OllamaEmbeddings(model=config["ollama"]["embedding_model"])
    milvus_client = None
    attempts = 0

    print("Initiating Milvus DB connection...")

    try:
        while not milvus_client and attempts < 3:
            try:
                milvus_client = MilvusClient(
                    uri=config["milvus"]["host"],
                    token=config["milvus"]["user"] + ":" + os.getenv("MILVUS_PASSWORD"),
                )
                print("Load available Collections:", milvus_client.list_collections())
                milvus_client.load_collection(collection_name="collection_rag")
                milvus_client.load_collection(collection_name="collection_ticket")
            except Exception as e:
                print(f"Error on loading collections {e}")
                print(
                    "Creating user or adjusting password and creating schema if it does not exist."
                )
                _create_user_and_schema()
            attempts += 1

        if not milvus_client:
            raise ConnectionError("Connecting to Milvus failed.")
        # Clear whole vector db
        """ try:
            result = milvus_client.delete(
                collection_name="collection_rag", filter="id >= 0"
            )
            print(f"Deletion result: {result}")
        except Exception as e:
            print(f"Error during deletion: {e}") """
        _initialize_directory(
            milvus_client, config["milvus"]["rag_documents_folder_absolute_path"]
        )
        watcher_thread = threading.Thread(
            target=_watch_directory,
            args=(
                milvus_client,
                config["milvus"]["rag_documents_folder_absolute_path"],
            ),
            daemon=True,
        )
        watcher_thread.start()
    except Exception as e:
        print(f"Milvus initialization failed: {e}")
        raise RuntimeError(f"Milvus initialization failed: {e}") from e


def retrieve_documents_milvus(query: str) -> List[dict]:
    try:
        query_vector = embedding_model.embed_query(query)
        return milvus_client.search(
            collection_name="collection_rag",
            anns_field="embedding",
            data=[query_vector],
            limit=config["milvus"]["number_of_retrieved_documents"],
            search_params={"metric_type": config["milvus"]["metric_type_rag"]},
            output_fields=["text", "metadata"],
        )[0]
    except Exception as e:
        print(f"Document retrieval failed: {e}")
        return []


def store_ticket_milvus(ticket: Ticket) -> None:
    try:
        embedding = embedding_model.embed_documents(ticket["summary"])

        data = [{"id": ticket["id"], "embedding": embedding, "title": ticket["title"]}]

        milvus_client.insert(collection_name="collection_ticket", data=data)
    except Exception as e:
        print(f"Storing ticket in Milvus failed: {e}")
        return None


def retrieve_similar_tickets_milvus(ticket: Ticket) -> List[dict]:
    try:
        query_vector = embedding_model.embed_query(ticket["summary"])
        return milvus_client.search(
            collection_name="collection_ticket",
            anns_field="embedding",
            data=[query_vector],
            limit=5,
            search_params={"metric_type": "COSINE"},
            output_fields=["title"],
        )[0]
    except Exception as e:
        print(f"Retrieving similar tickets failed: {e}")
        return []
