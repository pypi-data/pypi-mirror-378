#!/usr/bin/env python
# Script              : Main script for LLM configuration and Initialization
# Component           : GenAi model deployment
# Author              : Vinay Namani
# Copyright (c)       : 2024 Katonic Pty Ltd. All rights reserved.


# -----------------------------------------------------------------------------
#                        necessary Imports
# -----------------------------------------------------------------------------


import os
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate 
from routes.utilities.utils import get_llm_provider
from routes.models import completion
# Logger removed
from langchain.prompts.few_shot import FewShotPromptTemplate
from nltk.corpus import words  
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
# Default ENV variables
import requests
from routes.utilities.constants import (GENERAL_SEP_PAT,
                                        CODE_BLOCK_PAT,
                                        TRIPLE_BACKTICK,
                                        QUESTION_PAT,
                                        FINAL_QUERY_PAT,
                                        THOUGHT_PAT,
                                        ANSWER_PAT,
                                        ANSWERABLE_PAT,
                                        FINAL_ANSWER_PAT,
                                        UNCERTAINTY_PAT)

from routes.utilities.mongo_init import get_general_settings

output_parser = CommaSeparatedListOutputParser()
format_instructions = output_parser.get_format_instructions()



# Logger removed
greetings = ["Hello","Hi","Hey","Good morning","Good afternoon","Good evening","Howdy","Greetings","Salaam","Namaste","Bonjour","Ciao","Hallo",
                "Hola","Holla","Aloha","It's nice to meet you","Pleased to meet you","How do you do?","Howdy","What's up?","How's it going?",
                "Hi there","Good to see you","Long time no see"]
prefixes_to_avoid = ["Scope of Knowledge Inquiry",
                    "Scope of Knowledge Clarification",
                    "Scope Limitation",
                    "Scope Limitation Inquiry",
                    "Unknown Term", 
                    "Limitation of Knowledge",
                    "Out of Scope",
                    "Out of Knowledge",
                    "Out of Scope Inquiry",
                    "Scope Limitation Explanation",
                    "Unknown Person",
                    "No knowledge for",
                    "No Knowledge Associated",
                    "Unknown Inquiry"]
useful_prefixes = ["Clarifying about",
                "Inquiring about",
                "Seeking information on ",
                "Asking about",
                "Exploring about",
                "Getting the information about",
                "Wanting to Know about",
                ]

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
QUOTE_PAT = "Quote:"
QUOTES_PAT_PLURAL = "Quotes:"
INVALID_PAT = "Invalid:"
SOURCES_KEY = "sources"

def handle_brand_voice(brand_voice, prompt):
    prompt.template = f"{brand_voice} \n " + prompt.template
    return prompt

def handle_persona_prompt(persona_prompt, prompt):
    prompt.template = f"{persona_prompt} \n " + prompt.template
    return prompt

def prompt_config(PERSONALIZED_PROMPTS_API, prompt_app):
    SUPPORT_PROMPT = None
    REQUIRE_CITATION_STATEMENT = None
    CONVERSATION_TITLE_PROMPT = None
    SYSTEM_PROMPT_CHAT_RENAME = None
    QUERY_REPHRASE = None
    SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT = None
    SEARCH_SUMMARY_TEMPLATE = None
    VALIDATE_QUES_PROMPT = None
    RESTRICTED_TERMS_STATUS = None
    RESTRICTION_MESSAGE = None
    RESTRICTED_TERMS = None
    ORGANIZATIONAL_POLICY_STATUS = None
    ORGANIZATIONAL_POLICY_PROMPT = None
    ORGANIZATIONAL_POLICY_MODEL = None
    FOLLOWUP_MODEL_STATUS = None
    FOLLOWUP_MODEL_SERVICE = None
    RENAME_CHAT_MODEL_SERVICE = None
    try:
        QUOTE_PAT = "Quote:"
        QUOTES_PAT_PLURAL = "Quotes:"
        INVALID_PAT = "Invalid:"
        SOURCES_KEY = "sources"

        prompts_setting = requests.get(PERSONALIZED_PROMPTS_API).json()

        general_settings = get_general_settings()

        TOP_CHUNKS = general_settings["advanceSettingConfig"]["ace"]["noOfChunks"]
        citation_status = general_settings["katonicAceConfig"]["ace"]["source-citation"]
        REQUIRE_CITATION_STATEMENT=""

        if citation_status:  
            REQUIRE_CITATION_STATEMENT = """
            Cite relevant statements INLINE STRICTLY using the exact same format as <span>1</span>, <span>2</span>, <span>3</span>, etc \
        to reference the document number, \
        DO NOT provide a reference section at the end and DO NOT provide any links following the citations.\
        Your document citation number should RANGE from 1 to 6.
        """.strip()
        
        #personality = prompts_setting["systemPrompt"]["personality"]
        instructions = prompts_setting["contentFilterPrompt"]["restrictedMessage"]

        # if not personality:
        #     personality = "Make sure to address the user's queries politely."

        # if not instructions:
        #     instructions = "Compose a comprehensive reply to the query using the search results given."

        # personality_and_instructions = f"""
        #             As a professional chatbot this will be your personality: {personality},
        #             """
        ##and these are your instructions: {instructions}

        

        restricted_terms = prompts_setting["contentFilterPrompt"]["restrictedTerms"]
        if not restricted_terms:
            restricted_terms = []

        no_langchain_prompt = """
                    Note:
                    Make sure to address the user's queries politely.
                    Compose a comprehensive reply to the query using the search results given.
                    1. Respond to the questions based on the given context. 
                    2. Please refrain from inventing responses nd kindly respond with "I apologize, but that falls outside of my current scope of knowledge.".
                    3. Use as much detail when as possible when responding. Answer step-by-step."""

        if prompts_setting["systemPrompt"]["systemPrompt"]:
            support_template = prompts_setting["systemPrompt"]["systemPrompt"]
            split_prompt_citation = support_template.split("CITATION:")
            support_template = split_prompt_citation[0]
            if len(split_prompt_citation) >= 2:
                if citation_status:  
                    REQUIRE_CITATION_STATEMENT = split_prompt_citation[1].rstrip().format(TOP_CHUNKS=TOP_CHUNKS)
            # Logger removed
            # Logger removed
        else:
            support_template = """Note\
                        Make sure to address the user's queries politely.\
                        Compose a comprehensive reply to the query using the search results given.\
                        1. Respond to the questions based on the given context. \
                        2. Please refrain from inventing responses.\
                        3. Use as much detail when as possible when responding. Answer step-by-step.\
                        4. Locate the answer within the given context.\
                        5. Keep the response within 3000 tokens.\
                        6. If a user asks the questions like please summarise the above, then you should summarize the previous answer you provided which can be fetched from the history\
                        7. If the user queries based on its previous questions please surround your answers based on the history of previous questions\
                        8. Write your answer in markdown format, make sure it is beautiful and easy to read (e.g. use headings, lists, bold, italic, etc.)

                    IMPORTANT NOTE: Don't answer question outside of provided context and kindly respond with "I apologize, but that falls outside of my current scope of knowledge."\

                    Use the following context to answer the question:\
                            ------

                            CONTEXT:
                            {context}

                            CHAT HISTORY:
                            {chat_history}

                            QUESTION:
                            {question}
                            """
        final_template = support_template

        SUPPORT_PROMPT = PromptTemplate(
            template=final_template,
            input_variables=["chat_history", "context", "question"],
        )

        if (
            prompts_setting["searchSummaryPrompt"]["enable"]
            and prompts_setting["searchSummaryPrompt"]["prompt"]
        ):
            INITIAL_SEARCH_SUMMARY_TEMPLATE = prompts_setting["searchSummaryPrompt"][
                "prompt"
            ]
            # Logger removed

            SEARCH_SUMMARY_MODEL_SERVICE = prompts_setting["searchSummaryPrompt"][
                "model"
            ]
        else:
            INITIAL_SEARCH_SUMMARY_TEMPLATE = """
                        Note:
                        You will receive a bunch of text in chunks as context. Your task is to summarize those chunks BRIEFLY, based on the user query that is {question} and also cite relevant statements INLINE using the format <span>1</span>, <span>2</span>,  <span>3</span>, etc to reference the document number, \
                        DO NOT provide a reference at the end and DO NOT provide any links following the citations. DONOT LEAVE THE INCOMPLETE SUMMARY.
                        If the provided context does not contain relevent information to the user query the answer, then respond with "I apologize, but the following search results does not contain the information you are looking for, Please try to search another question based on the knowledge provided to me". Please refrain from inventing responses.
                        IMPORTANT NOTE: Don't answer question outside of provided context and kindly respond with "I apologize, but the following search results does not contain the information you are looking for, Please try to search another question based on the knowledge provided to me"
                        Use the following context to summarise:\
                        STRICTLY GIVE THE SUMMARY IN 150 WORDS ONLY AS RESPONSE OR ELSE YOU WILL BE PENALISED
                        ------
                        CONTEXT:
                        {context}
                        """
        SEARCH_SUMMARY_TEMPLATE = PromptTemplate(
            template=INITIAL_SEARCH_SUMMARY_TEMPLATE,
            input_variables=["context", "question"],
        )

        SYSTEM_PROMPT_CHAT_RENAME = """You are an expert at generating very creative and unique title for any conversation or question."""
        if (
            prompts_setting["conversationNamePrompt"]["enable"]
            and prompts_setting["conversationNamePrompt"]["prompt"]
        ):
            INITIAL_CONVERSATION_TITLE_PROMPT_TEMPLATE = prompts_setting[
                "conversationNamePrompt"
            ]["prompt"]
            RENAME_CHAT_MODEL_SERVICE = prompts_setting["conversationNamePrompt"][
                "model"
            ]
        else:
            INITIAL_CONVERSATION_TITLE_PROMPT_TEMPLATE = """You will be provided with a conversation snippet between a user and an AI assistant.
            Your task is to generate a 5 WORDS concise and informative title that captures the essence of the conversation.
            Consider the main topic, the user's intent in the query, and the key points in the AI's response when crafting the title.
            Use below examples to understand what type of responses to generate: 
            Example Input 1

            Human 1: "Hello"
            AI 1: "Hi, how can I assit you?"

            Example Output 1
            Title 1: "Initial Greeting",
            ###   
            Example Input 2
            Human 2: "haha"
            AI 2: "I apologize, but that falls outside of my current scope of knowledge."

            Example Output 2
            Title: "Casual chat",
            ###
            Example Input 3
            Human 3: "Who is t?"
            AI 3: "I apologize, but that falls outside of my current scope of knowledge."

            Example Output 3
            Title 3: "Asking about t"
            ###
            Example Input 4
            Human 4: "What is Katonic?"
            AI 4: "Katonic is an Australian generative artificial intelligence (AI) and machine learning company known for its no-code Katonic Generative AI platform. This platform is celebrated for its simplicity and intuitiveness, enabling both small and large businesses to swiftly create powerful enterprise-grade AI applications without the need for coding. It leverages the highly awarded Katonic machine learning operations (MLOps) to manage the entire lifecycle of AI application development, including data preparation, model training, model deployment, model monitoring, and automation, ensuring high accuracy, reliability, and efficiency. Katonic AI's solutions can be deployed across various environments, including multi-cloud, on-premises, or edge computing setups. The company has earned significant recognition in the industry, being the only AI company from the Asia-Pacific region to be featured in Everest Group’s MLOps Products PEAK Matrix® 2022 and winning the Frost & Sullivan Best Practices Entrepreneurial Company of the Year Award in the APAC MLOps industry"

            Example Output 4
            Title 4: "Katonic AI Company Overview"
            ###
            Example Input 5
            Human 5: "Hi"
            AI 5: "No Knowledge associated with you"

            Example Output 5
            Title 5: "Initial Greeting",
            ###  
            Use keywords to create a clear and concise conversation title as described in above examples.

            Conversation
            ##############
            {chat_history}
            ###################

            ONLY GIVE TITLE AS RESPONSE:

            """
        INITIAL_CONVERSATION_TITLE_PROMPT = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    INITIAL_CONVERSATION_TITLE_PROMPT_TEMPLATE
                )
            ],
            input_variables=["chat_history"],
        )

        CONVERSATION_TITLE_PROMPT = INITIAL_CONVERSATION_TITLE_PROMPT

        if (
            prompts_setting["followUpQuestionPrompt"]["enable"]
            and prompts_setting["followUpQuestionPrompt"]["prompt"]
        ):
            INITIAL_SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT = (
                prompts_setting["followUpQuestionPrompt"]["prompt"]
            )
            FOLLOWUP_MODEL_STATUS = True
            FOLLOWUP_MODEL_SERVICE = prompts_setting["followUpQuestionPrompt"]["model"]
        else:
            FOLLOWUP_MODEL_STATUS = False
            INITIAL_SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT = """You are an expert at creating questions and your task is to generate the top 3 follow-up well defined questions that would likely to be asked on the provided context.
            #############
            Context: {response} 
            ##########################
            MAKE SURE you GENERATE VALID and FULL QUESTIONS ONLY and INSTEAD of 1 WORD

            Use below examples, understand the pattern and generate the OUTPUT STRICTLY in the below specified format:
            
            Example Output 1
            ["Who is the Prime Minister of India?","What are the main responsibilities of the Prime Minister?","How is the Prime Minister selected or appointed in your country?"]
            #######
            
            Example Output 2
            ["Where is the Taj Mahal located?","What is the architectural style of the Taj Mahal?","What is the significance of the Taj Mahal?"]
            #######
            
            Any other format is highly unacceptable.
            Do not generate any questions if the given context says no knowledge associated, or out of scope of its knowledge.

            """
        SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    INITIAL_SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT
                )
            ],
            input_variables=["response"],
        )

        if (
            prompts_setting["questionValidationPrompt"]["enable"]
            and prompts_setting["questionValidationPrompt"]["prompt"]
        ):
            ANSWERABLE_PROMPT = prompts_setting["questionValidationPrompt"]["prompt"]
            ANSWERABLE_PROMPT = ANSWERABLE_PROMPT.replace("{QUESTION_PAT}", "Query:")
            ANSWERABLE_PROMPT = ANSWERABLE_PROMPT.replace(
                "{GENERAL_SEP_PAT}", "---------------"
            )
            ANSWERABLE_PROMPT = ANSWERABLE_PROMPT.replace("{ANSWERABLE_PAT}", "Answer:")
            QUESTION_VALIDITY_MODEL_SERVICE = prompts_setting[
                "questionValidationPrompt"
            ]["model"]
        else:
            ANSWERABLE_PROMPT = f"""
            You are a helper tool to determine if the user query is a valid and defined question also is answerable using retrieval augmented generation.
            The main system will try to answer the user query based on ONLY the top 5 most relevant \
            documents found from search.
            Sources contain both up to date and proprietary information for the specific team.
            For named or unknown entities, assume the search will find relevant and consistent knowledge \
            about the entity.
            The system is not tuned for writing code.
            The system is not tuned for interfacing with structured data via query languages like SQL.
            If the question might not require code or query language, then assume it can be answered without \
            code or query language.
            Determine if that system should attempt to answer.
            "ANSWERABLE" must be exactly "True" or "False"
            {GENERAL_SEP_PAT}
            {QUESTION_PAT.upper()} Slack?
            ```
            {THOUGHT_PAT.upper()} First the system must determine what exactly the user meant with Slack. \
            By fetching 5 documents related to Slack contents, it is not possible to determine what user is trying to ask as question.
            {ANSWERABLE_PAT.upper()} False
            ```
            {QUESTION_PAT.upper()} Assistant is unreachable.
            ```
            {THOUGHT_PAT.upper()} The system searches documents related to Assistant being unreachable. \
            Assuming the documents from search contains situations where Assistant is not reachable and \
            contains a fix, the query may be answerable.
            {ANSWERABLE_PAT.upper()} True
            ```
            {QUESTION_PAT.upper()} How many customers do we have
            ```
            {THOUGHT_PAT.upper()} Assuming the retrieved documents contain up to date customer acquisition \
            information including a list of customers, the query can be answered. It is important to note \
            that if the information only exists in a SQL database, the system is unable to execute SQL and \
            won't find an answer.
            {ANSWERABLE_PAT.upper()} True
            ```
            {QUESTION_PAT.upper()} {{user_query}}
            """.strip()

        if prompts_setting["responsePrompt"]:
            RESPONSE_PROMPT = prompts_setting["responsePrompt"]
        else:
            RESPONSE_PROMPT = {}
        VALIDATE_QUES_PROMPT = PromptTemplate.from_template(ANSWERABLE_PROMPT)

        QUERY_REPHRASE = f"""
        Given the following conversation and a follow up input, rephrase the follow up into a SHORT, \
        standalone question (which captures any relevant context from previous messages) for a vectorstore.
        IMPORTANT: EDIT THE QUERY TO BE AS CONCISE AS POSSIBLE. Respond with a complete sentence as question.
        If there is a clear change in topic, disregard the previous messages.
        If you receive single word as query just rephrase it in proper complete sentence as question
        NOTE: IF HISTORY is  NOT AVAILABLE PLEASE REPHRASE the QUERY in POLITE, FORMAL and PLAIN ENGLISH
        Strip out any information that is not relevant for the retrieval task.
        If the follow up message is an error or code snippet, repeat the same input back EXACTLY.
        
        {GENERAL_SEP_PAT}
        Chat History:
        {{chat_history}}
        {GENERAL_SEP_PAT}

        Follow Up Input: {{question}}

        Example Input 1:
        User query:Katonic
        Example Output 1:
        Assistant response: What is Katonic?

        Example Input 2:
        User query: Where is Taj Mahal?
        Example Output 2:
        Assistant response:Where is the Taj Mahal located?

        Standalone question (Respond with only the short combined query):
        """

        if prompts_setting["contentFilterPrompt"]["restrictedMessage"]:
            RESTRICTED_TERMS_STATUS = prompts_setting["contentFilterPrompt"][
                "contentFiltering"
            ]["restrictedTerms"]
            try:
                RESTRICTED_TERMS = prompts_setting["contentFilterPrompt"][
                    "restrictedTerms"
                ]
            except Exception as e:
                RESTRICTED_TERMS = ""
            try:
                RESTRICTION_MESSAGE = prompts_setting["contentFilterPrompt"][
                    "restrictedMessage"
                ]
            except Exception as e:
                RESTRICTION_MESSAGE = (
                    "A restricted terms has been found in the conversation."
                )

        if (
            prompts_setting["organizationPolicyPrompt"]["enable"]
            and prompts_setting["organizationPolicyPrompt"]["prompt"]
        ):
            ORGANIZATIONAL_POLICY_PROMPT = prompts_setting["organizationPolicyPrompt"][
                "prompt"
            ]
            ORGANIZATIONAL_POLICY_STATUS = prompts_setting["organizationPolicyPrompt"][
                "enable"
            ]
            try:
                ORGANIZATIONAL_POLICY_MODEL = prompts_setting[
                    "organizationPolicyPrompt"
                ]["model"]
            except Exception as e:
                ORGANIZATIONAL_POLICY_MODEL = None

        return (
            SUPPORT_PROMPT,
            REQUIRE_CITATION_STATEMENT,
            CONVERSATION_TITLE_PROMPT,
            SYSTEM_PROMPT_CHAT_RENAME,
            QUERY_REPHRASE,
            SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT,
            SEARCH_SUMMARY_TEMPLATE,
            VALIDATE_QUES_PROMPT,
            RESPONSE_PROMPT,
            RESTRICTED_TERMS_STATUS,
            RESTRICTION_MESSAGE,
            RESTRICTED_TERMS,
            ORGANIZATIONAL_POLICY_STATUS,
            ORGANIZATIONAL_POLICY_PROMPT,
            ORGANIZATIONAL_POLICY_MODEL,
            FOLLOWUP_MODEL_STATUS,
            FOLLOWUP_MODEL_SERVICE,
            RENAME_CHAT_MODEL_SERVICE,
            None
        )
    except Exception as e:
        # Logger removed
        return None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,str(e)


def initialize_llm_models(service_type, logger, module=None):
    #print("values: ",get_llm_provider(service_type, logger))
    provider, model_name = get_llm_provider(service_type, logger)
    # Logger removed
    return completion.get_llm(service_type, provider, model_name, logger, module)


def is_english_word(word):
    return word.lower() in words.words()

def create_policy_prompt(policies, input_question):
    formatted_string = "The policies are:\n"
    for policy in policies:
        formatted_string += f"- {policy}\n"
    formatted_string += f"\nInput: {input_question}.\n"

    base_policy_prompt = """
    You are a policy reviewer, your job is to take a policy and classify if the given input falls under that policy or not.
    If the input violates any one of the policy return true otherwise false.
    Be very strict with the policies.
    NOTE: ONLY GIVE THE OUTPUT WITH JSON AND NO EXTRA EXPLANATION
    NOTE: MAKE SURE TO CATER INDIRECT QUESTIONS ON POLICY
    NOTE: IF THE INPUT QUERY NOT VOILATING ANY POLICY RETURN POLICY AS NON-VIOLATING POLICY
    The output should be a json like below:
    {
    "output": <True or False>,
    "policy": <policy>
    } 
    """
    return base_policy_prompt + formatted_string    

