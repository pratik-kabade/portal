from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import time
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
import os
import logging
from llama_parse import LlamaParse
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"
from util.genesislogger import GenesisLogger

logger = GenesisLogger.get_instance()
class clsLlamaIndexManager:
        _instance = None

        @staticmethod
        def get_instance():
            if clsLlamaIndexManager._instance == None:
                clsLlamaIndexManager._instance = clsLlamaIndexManager()
            else:
                logger.info("Instance Found")
            return clsLlamaIndexManager._instance

        def __new__(cls,*args, **kwargs):
           if not cls._instance:
              cls._instance = super().__new__(cls)
           return cls._instance

        def __init__(self):

            Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
            Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

            self.base_vectorstore_dir =str(os.getenv("VECTOR_STORE_PATH"))
            if not os.path.exists(self.base_vectorstore_dir):
                os.makedirs(self.base_vectorstore_dir)
            print(self.base_vectorstore_dir)

            # Dictionary to keep track of loaded indexes and directories
            self.query_engine_dic = {}

            # Loop through all the directories in vectorstore path
            project_folders = os.listdir(self.base_vectorstore_dir)
            for project_name in project_folders:
                project_vectorstore_path = os.path.join(self.base_vectorstore_dir, project_name)

                if not os.path.exists(os.path.join(self.base_vectorstore_dir,project_name, "default__vector_store.json")):
                   data_dir = "./data"

                   for filename in os.list(os.path.join(data_dir,project_name)):
                        filepath = os.path.join(data_dir,project_name,filename)
                        documents =  LlamaParse(result_type="text").load_data(file_path)
                        #documents = SimpleDirectoryReader("./data").load_data()
                        index = VectorStoreIndex.from_documents(documents)
                        # save index to disk
                        index.storage_context.persist(persist_dir=project_vectorstore_path)
                        self.query_engine_dic[projectname] = index
                else:
                   logger.debug("loading existing index")
                   storage_context = StorageContext.from_defaults(persist_dir=project_vectorstore_path)
                   index = load_index_from_storage(storage_context=storage_context)
                   self.query_engine_dic[project_name] = index
                self.query_engine = self.query_engine_dic[project_name].as_query_engine()




        def run_ingest(self,filename,project_name):

            try:
               # Ensure the project data directory exists
               file_path = os.path.join(os.getenv("DATA_PATH"), project_name,filename)

               # Check if the document exists
               if not os.path.isfile(file_path):
                   logger.error(f"File {filename} not found")
                   return

               project_vectorstore_path = os.path.join(self.base_vectorstore_dir, project_name)

               # Load document data
               documents = LlamaParse(result_type="text").load_data(file_path)
               index = VectorStoreIndex.from_documents(documents)
               index.storage_context.persist(persist_dir=project_vectorstore_path)

               # Update the in-memory index and directory
               self.query_engine_dic[project_name] = index
               logger.info(f"Document {filename} ingested and stored in {project_vectorstore_path}")

            except Exception as e:
                print("error in ingest",e)
                logger.error(e)


        def getQueryEngine(self, projectname):
            if projectname is None:
                logger.debug("Project name is not provided")
                return None
            if projectname not in self.query_engine_dic:
                logger.debug(f"No query engine found for project '{projectname}'")
                return None
            return self.query_engine_dic[projectname].as_query_engine()
