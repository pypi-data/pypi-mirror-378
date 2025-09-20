import os
SERVER_DOMAIN_DEFAULT = "http://log-ingestor.application.svc.cluster.local:3000"
EXTRACION_API_DEFAULT = "http://extraction-api.application.svc.cluster.local:8000/api/v1/"
QDRANT_URL_DEFAULT = "http://qdrant-headless.ace.svc.cluster.local:6333"

QDRANT_URL = os.getenv("QDRANT_URL", QDRANT_URL_DEFAULT)
SERVER_DOMAIN = "http://log-ingestor:3000"
CUSTOM_EMBEDDING_ROUTE_DEFAULT = "http://all-minilm-l6-v2-svc.application.svc.cluster.local:8080"
CUSTOM_EMBEDDING_ROUTE = os.getenv("CUSTOM_EMBEDDING_ROUTE", CUSTOM_EMBEDDING_ROUTE_DEFAULT)

COLLECTION_NAME = "KATONIC_KNOWLEDGE"
TEMP_FILE_COLLECTION_NAME = "TEMPORARY_FILE_KNOWLEDGE"
FAQ_COLLECTION_NAME = "FAQ"

EXTRACION_API = os.getenv("EXTRACTION_API", EXTRACION_API_DEFAULT)
PERSONALIZED_PROMPTS_API = (
    f"{SERVER_DOMAIN}/prompts/api/personalized"
)


GENERAL_SETTINGS = "/logs/api/settings/get/general"
PERMISSION_FIND = "/logs/api/knowledgedrive/get" # (POST) Find the permission document based on user email
''' 
userEmail
'''

WEB = "Websites"
SHAREPOINT = "Sharepoint"
FILE = "File"
FAQ = "FAQ"
YOUTUBE = "Youtube"
CONFLUENCE = "Confluence"
GITHUB = "Github"
GDRIVE = "Gdrive"
JIRA = "Jira"
IMAGE = "Image"
API = "Api"
SOURCES = [
    WEB,
    SHAREPOINT,
    FILE,
    FAQ,
    YOUTUBE,
    CONFLUENCE,
    GITHUB,
    GDRIVE,
    JIRA,
    IMAGE,
    API,
]
# ENV Variables


SERVICE_TYPE = os.environ["SERVICE_TYPE"]


# Embedding Type


OPENAI = "OpenAI"
ALLMINILM = "allminilm"
AZURE_OPENAI = "Azure OpenAI"
REPLICATE = "Replicate"
VLLM = "VLLM Embedding"
TOP_CHUNKS = 6

PERSONALIZED_PROMPTS_API = (
    f"{SERVER_DOMAIN}/prompts/api/personalized"
)


GENERAL_SEP_PAT = "--------------"  # Same length as Langchain's separator
CODE_BLOCK_PAT = "```\n{}\n```"
TRIPLE_BACKTICK = "```"
QUESTION_PAT = "Query:"
FINAL_QUERY_PAT = "Final Query:"
THOUGHT_PAT = "Thought:"
ANSWER_PAT = "Answer:"
ANSWERABLE_PAT = "Answerable:"
FINAL_ANSWER_PAT = "Final Answer:"
UNCERTAINTY_PAT = "?"
