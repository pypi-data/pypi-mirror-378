#!/usr/bin/env python
# Script              : Main script for initializing mongo db and collections.
# Component           : GenAi model deployment
# Author              : Vinay Namani
# Copyright (c)       : 2024 Katonic Pty Ltd. All rights reserved.


# -----------------------------------------------------------------------------
#                        necessary Imports
# -----------------------------------------------------------------------------


import os
import pandas
from bson.objectid import ObjectId
from pymongo import MongoClient

# DB_NAME = "katonic"
PRICES_COLLECTION_NAME = "foundationmodels"
LOGS_COLLECTION_NAME = "generativeailogs"
FM_META_COLLECTION = "mytrainingmodels"
GENERAL_SETTINGS = "generalsettings"
MESSAGE_COLLECTION = "messages"
EMBEDDING_SERVICE_TYPE = os.getenv("EMBEDDING_SERVICE_TYPE", None)
SERVICE_TYPE = os.getenv("SERVICE_TYPE", None)
ORGANIZATIONAL_POLICIES = "organizationpolicies"
KNOWLEDGE_DRIVE = "knowledge_drive"
KNOWLEDGES_COLLECTION = "knowledges"
PROMPT_PERSONALIZATIONS = "promptpersonalizations"
PERSONA_COLLECTION = "personas"
MONGO_CONNECTION_STRING_DEFAULT = "mongodb://root:P3XWyYhNNA@mongo-db-mongodb-0.mongo-db-mongodb-headless.application.svc.cluster.local:27017,mongo-db-mongodb-1.mongo-db-mongodb-headless.application.svc.cluster.local:27017/katonic?authMechanism=DEFAULT&authSource=admin"
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING", MONGO_CONNECTION_STRING_DEFAULT)


## To avoid creating multiple mongo connections
client = MongoClient(MONGO_CONNECTION_STRING)
DB_NAME = client.get_default_database().name 
mydb = client[DB_NAME]


def get_local_mongo_db():
    # client = MongoClient(MONGO_CONNECTION_STRING)
    # DB_NAME = client.get_default_database().name 
    # mydb = client[DB_NAME]
    return mydb


def fetch_collection(COLLECTION_NAME):
    settings_collection = get_local_mongo_db()[COLLECTION_NAME]
    cursor = settings_collection.find({})
    cursor_list = list(cursor)
    settings_dict = {}
    for item in cursor_list:
        settings_dict.update(item)
    return settings_dict

def get_persona_collection(persona_id):
    collection = get_local_mongo_db()[PERSONA_COLLECTION]
    data = collection.find({'_id':ObjectId(persona_id)})
    return [document.get("personaDescription") for document in data]

def get_general_settings():
    return fetch_collection(GENERAL_SETTINGS)

def get_promptpersonalizations():
    return fetch_collection(PROMPT_PERSONALIZATIONS)


def get_local_mongo_cost_collection():
    return get_local_mongo_db()[FM_META_COLLECTION]


def get_local_mongo_logs_collection():
    return get_local_mongo_db()[LOGS_COLLECTION_NAME]


def get_local_mongo_embedding_meta():
    collection = get_local_mongo_db()[FM_META_COLLECTION]
    df = pandas.DataFrame(collection.find({}))
    return df[df["modelName"] == EMBEDDING_SERVICE_TYPE]


# def get_policy_information():
#     collection = get_local_mongo_db()["organizationpolicies"]
#     data = collection.find({'active': True})
#     return [document.get("policyDescription") for document in data]


def get_local_mongo_llm_meta(SERVICE_TYPE, project_name=None):
    collection = get_local_mongo_db()[FM_META_COLLECTION]
    df = pandas.DataFrame(collection.find({}))
    if project_name is None:
        return df[df["modelName"] == SERVICE_TYPE]
    else:
        filtered_df = df[df["metadata"].apply(lambda x: isinstance(x, dict) and x.get("projectName") == project_name)]
        return filtered_df if not filtered_df.empty else []

def check_for_mongo_existance(MODEL_NAME):
    collection = get_local_mongo_db()[FM_META_COLLECTION]
    df = pandas.DataFrame(collection.find({}))
    if MODEL_NAME == "katonicLLM":
        return df[df["value"] == MODEL_NAME]
    return df[df["modelName"] == MODEL_NAME]

def get_policy_information():
    collection = get_local_mongo_db()[ORGANIZATIONAL_POLICIES]
    data = collection.find({})
    return [document.get("policyDescription") for document in data if document.get("active")]    

def get_message_collection():
    return get_local_mongo_db()[MESSAGE_COLLECTION]

def get_model_provider(modelName):
    if modelName=="katonicLLM":
        return "katonic"
    if modelName=="CUSTOM TEI EMBEDDING":
        return "katonic"
    model_data = get_local_mongo_llm_meta(modelName)
    provider = model_data["parent"].values[0]
    return provider

def get_model_endpoint(modelName):
    model_data = get_local_mongo_llm_meta(modelName)
    endpoint = model_data["metadata"].values[0]["endpoint"]
    return endpoint


def get_knowledge_id_in_permission(knowledge_ids):
    knowledge_drive_collection = get_local_mongo_db()[KNOWLEDGE_DRIVE]
    existing_docs = knowledge_drive_collection.find({ 'knowledgeId': { '$in': knowledge_ids } })

    # Extract the matching IDs from the field 'yourField'
    existing_ids = [doc['knowledgeId'] for doc in existing_docs]
    return existing_ids

def get_document_id_by_knowlegde_id(knowledge_ids, user_email):
    knowledge_drive_collection = get_local_mongo_db()[KNOWLEDGE_DRIVE]
    existing_docs = knowledge_drive_collection.find({
            'knowledgeId': { '$in': knowledge_ids },
            'accessIdentities': user_email
        })

    existing_ids = [doc['documentId'] for doc in existing_docs]
    return existing_ids

def get_document_id_in_permission(document_ids):
    knowledge_drive_collection = get_local_mongo_db()[KNOWLEDGE_DRIVE]
    existing_docs = knowledge_drive_collection.find({ 'documentId': { '$in': document_ids } })

    # Extract the matching IDs from the field 'yourField'
    existing_ids = [doc['documentId'] for doc in existing_docs]
    return existing_ids

def get_document_id_by_document_id(document_ids, user_email):
    knowledge_drive_collection = get_local_mongo_db()[KNOWLEDGE_DRIVE]
    existing_docs = knowledge_drive_collection.find({
            'documentId': { '$in': document_ids },
            'accessIdentities': user_email
        })

    existing_ids = [doc['documentId'] for doc in existing_docs]
    return existing_ids

def get_knowledges_collection():
    return get_local_mongo_db()[KNOWLEDGES_COLLECTION]

def get_regenerate_styles():
    collection = get_local_mongo_db()["promptpersonalizations"]
    df = pandas.DataFrame(collection.find({}))
    return df["responsePrompt"][0]
