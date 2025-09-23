import os
import hashlib
import pandas
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pymongo import MongoClient

MONGO_CONNECTION_STRING_DEFAULT = "mongodb://root:P3XWyYhNNA@mongo-db-mongodb-0.mongo-db-mongodb-headless:27017,mongo-db-mongodb-1.mongo-db-mongodb-headless:27017,mongo-db-mongodb-2.mongo-db-mongodb-headless:27017,mongo-db-mongodb-3.mongo-db-mongodb-headless:27017/katonic?authMechanism=DEFAULT&authSource=admin"
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING", MONGO_CONNECTION_STRING_DEFAULT)
FM_META_COLLECTION = "mytrainingmodels"


## To avoid creating multiple mongo connections
client = MongoClient(MONGO_CONNECTION_STRING)
DB_NAME = client.get_default_database().name 
mydb = client[DB_NAME]

def generate_16_byte_key(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).digest()
    return sha256_hash[:16]


def generate_32_byte_key(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).digest()
    return sha256_hash[:32]


input_string = "Katonic@U7OS4o0mren8OHsIibbKOvekpJHx3T2020"
key = generate_32_byte_key(input_string)
iv = generate_16_byte_key(input_string)


def decrypt_encryption_seed(text):
    encrypted_data = bytes.fromhex(text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode("utf-8")

def get_local_mongo_db():
    # client = MongoClient(MONGO_CONNECTION_STRING)
    # DB_NAME = client.get_default_database().name 
    # mydb = client[DB_NAME]
    return mydb

def get_local_mongo_llm_meta(SERVICE_TYPE, project_name=None):
    collection = get_local_mongo_db()[FM_META_COLLECTION]
    df = pandas.DataFrame(collection.find({}))
    if project_name is None:
        return df[df["modelName"] == SERVICE_TYPE]
    else:
        filtered_df = df[df["metadata"].apply(lambda x: isinstance(x, dict) and x.get("projectName") == project_name)]
        return filtered_df if not filtered_df.empty else []

def get_model_endpoint(modelName):
    model_data = get_local_mongo_llm_meta(modelName)
    endpoint = model_data["metadata"].values[0]["endpoint"]
    return endpoint

def get_llm_provider(service_type):
    provider = None
    try:
        provider = get_model_provider(service_type)
        #logger.info(f"Provider: {provider}")
        if provider not in ["TGI LLM", "VLLM LLM", "LLAMA", "Custom LLM"]:
            model_name = get_model_endpoint(service_type)
        elif provider in ["LLAMA", "Custom LLM"]:
            provider = "katonic"
            model_name = service_type
        else:
            model_name = service_type
        return provider, model_name
    except Exception as e:
        if provider == None:
            err = f"The choosen model {service_type} is not available in the backend LLM engine."
            print(err)
            return str(err)
        else:
            print(str(e))
            return str(e)

def get_model_provider(modelName):
    if modelName=="katonicLLM":
        return "katonic"
    if modelName=="CUSTOM TEI EMBEDDING":
        return "katonic"
    model_data = get_local_mongo_llm_meta(modelName)
    provider = model_data["parent"].values[0]
    return provider

def get_local_mongo_cost_collection():
    return get_local_mongo_db()[FM_META_COLLECTION]