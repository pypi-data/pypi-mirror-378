import requests
from routes.utilities.constants import PERSONALIZED_PROMPTS_API
# Logger removed
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

# Logger removed


def answer_validation_prompt():
    try:
        prompts_setting = requests.get(PERSONALIZED_PROMPTS_API).json()
        # Logger removed
        QUESTION_PAT = "Query:"
        ANSWER_PAT = "Answer:"
        if prompts_setting['answerValidationPrompt']['enable'] and prompts_setting['answerValidationPrompt']['prompt']:
            ANSWER_VALIDITY_PROMPT = prompts_setting['answerValidationPrompt']['prompt']
            ANSWER_VALIDITY_PROMPT = ANSWER_VALIDITY_PROMPT.replace("{QUESTION_PAT}","Query:")
            ANSWER_VALIDITY_PROMPT = ANSWER_VALIDITY_PROMPT.replace("{ANSWER_PAT}","Answer:")
            ANSWER_VALIDITY_MODEL_SERVICE = prompts_setting['answerValidationPrompt']['model']
        else:
            ANSWER_VALIDITY_PROMPT = """
            You are an assistant to identify invalid Query/Answer pairs coming from a large language model.\
            The Query/Answer pair is invalid if any of the following are True:
            1. Query is asking for information regarding something or someone but the Answer is not \
            satisfying or justifying the given Query, so this is invalid.
            2. Answer addresses a related but different query. To be helpful, the model may provide \
            related information about a query but it won't match what the user is asking, this is invalid.
            3. Answer is just some form of "I don\'t know" or "not enough information" without significant \
            additional useful information. Explaining why it does not know or cannot answer is invalid.

            Query: {user_query}
            Answer: {llm_answer}

            ------------------------
            You MUST answer in EXACTLY the following format:
            ```
            1. True or False
            2. True or False
            3. True or False
            Final Answer: Valid or Invalid
            ```

            Hint: Remember, if ANY of the conditions are True, it is Invalid.
            """.strip()
        return ANSWER_VALIDITY_PROMPT
    except Exception as e:
        # Logger removed        
        return str(e)