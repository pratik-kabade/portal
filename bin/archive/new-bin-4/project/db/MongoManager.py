# import MongoClient
from pymongo import MongoClient
from project.util.genesislogger import GenesisLogger
import os
 
# Instantiating Logger
logger = GenesisLogger.get_instance()

# Singleton class to allow only one instance of this class 
# and allows the calling method to call static method directly.
class MongoManager:
   
  _instance = None
  #connections = []
  
  @staticmethod 
  def get_instance():
    if MongoManager._instance == None:
        MongoManager._instance = MongoManager()
    else:
       logger.debug(f"Found instance. Returning...")
    return MongoManager._instance

  # MongoManager constructor to initialize 
  def __new__(cls,*args, **kwargs):
    """Creates a new instance of MongoClientPool or returns the existing one."""
    if not cls._instance:
        cls._instance = super().__new__(cls)
        cls._instance.__init__()
    return cls._instance

  # Init method to initialize the database connection
  def __init__(self):
    self.uri = os.getenv("MONGODB_URL")
    self.pool_size = int(os.getenv("MONGODB_POOLSIZE"))
    self.connections = []  # List to store available connections
    for x in range(0,self.pool_size):
        self.connections.append(MongoClient(self.uri))
        

  def _create_connection(self):
        try:
            logger.debug("Initializing for first time - Create Connections")
            client = MongoClient(self.uri)
            return client
        except Exception as e:
            raise e

    # Method to return connection object to calling class
  def get_connection(self):
    """Obtains a MongoClient instance from the pool or creates a new one."""
    return self.connections.pop()  # Get a connection from the pool
      
  def release_connection(self, connection):
    """Returns a connection to the pool."""
    self.connections.append(connection)
