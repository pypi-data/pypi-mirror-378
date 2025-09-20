from datetime import datetime
from pydantic import BaseModel
from typing import List, Any, Optional, Union, Dict


class HistoryItem(BaseModel):
    role: str
    content: str


class PredictSchema(BaseModel):
    id: str
    data: str
    document_ids: List = []
    source_type: List[str] = []
    knowledge_ids: List[str] = []
    history: List[HistoryItem] = []
    time_range: Optional[str] = ""
    user: Optional[str] = "anonymous"
    regenerate_style: Union[str, None] = None
    personaId: Optional[str] = ""
    isfilter: bool = False
    isBranVoiceEnabled: bool = False


class SearchOnWebSchema(BaseModel):
    """
    Search On Web Request Schema.
    """

    model: str
    messageId: str
    history: List[HistoryItem] = []
    query: str
    brand_voice: Optional[Union[str, None]] = None
    policies: Union[List, None]
    user: Optional[str] = "anonymous"
    actions: Optional[Dict[str, Any]] = {}
    extension: Optional[str] = ""
    conversationId: str
    fileAttached: bool = False
    regenerate_style: Union[str, None] = None
    personaId: str
    isBranVoiceEnabled: bool = False

class FileUploadSchema(BaseModel):
    conversationId: str
    filePath: List


class FileUploadCopilotSchema(BaseModel):
    filePath: List
    knowledgeId: Optional[str]

class DeleteSessionData(BaseModel):
    collectionId: str


class DeleteFileFromCollection(BaseModel):
    collectionId: str
    filePath: str


class RenameChatSchema(BaseModel):
    query: str
    query_response: str
    user: str


class DocumentSchema(BaseModel):
    data: str
    source_type: List[str] = []
    knowledge_ids: List[str] = []
    document_ids: List = []
    user: Optional[str] = "anonymous"


class FollowUpQuesSchema(BaseModel):
    query_response: str
    user: str
    
class WordCloudSchema(BaseModel):
    product_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class FeedbackUpdateSchema(BaseModel):
    messageId: str
    feedback: Dict[str, Any]

class RephraseQuesSchema(BaseModel):
    query: str
    history: List[HistoryItem] = []
    user: str


class DocSummarySchema(BaseModel):
    id: str
    query: str
    retrieved_document_list: List[Any]
    user: Optional[str] = "anonymous"
    summary_length: Optional[int] = 300


class RelevantDocsSchema(BaseModel):
    id: str
    data: str
    source_type: List[str] = []
    knowledge_ids: List[str] = []
    document_ids: List = []
    user: Optional[str] = "anonymous"


class QuesValidationSchema(BaseModel):
    query: str
    user: str


# class FeedbackUpdateSchema(BaseModel):
#     messageId: str
#     feedback: str


class RetrieveChunks(BaseModel):
    document_id: str
    start: int
    end: int


class AceCopilotSchema(BaseModel):
    id: str
    user: str
    model: str
    query: str
    systemPrompt: str = None
    temperature: float
    history: List[HistoryItem] = []
    knowledgeIds: Optional[List] = None
    actions: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    regenerate_style: Union[str, None] = None
    extension: Optional[str] = ""
    agent: Optional[Dict[str, Any]] = {}
    upload_file: bool = False
    temp_file_knowledgeIds: Optional[List] = None