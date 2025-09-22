# from typing import List, Dict, Any, Optional, Union
# from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate,SystemMessagePromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from src.contracts.feature_orchestrator.feature_orchestrator import OrchestratorOutput, _DraftWrapper,_FinalizeWrapper, OrchestratorDraftOutput, OrchestratorFinalizeOutput
# # from llms.langraph_wrapper_gpt import ChubbGPT
# from prompts.feature_extractor import feature_orchestrator_prompt
# import json
# from typing import List, Dict, Any, Optional, Union
# import os


# class featureOrchestrator:
#   def __init__(self):
#     self.rag_params = {
#       "gpt_config_params": {
#         "OPENAI_API_KEY":"",
#         "username": "",
#         "session_id": "",
#         "max_tokens": ,
#         "frequency_penalty": ,
#         "presence_penalty": ,
#         "temperature":,
#         "top_p": ,
#         "num_chances": ,
#         "Content-Type": "",
#         "App_ID": "",
#         "App_Key": "",
#         "apiVersion": '',
#         "Resource": "",
#         "API_TOKEN_URL": "",
#         "API_URL": (
#         ),
#       },
#       },
#       "params_for_chunking": {
#         "split_by": "word",
#         "split_length": 150,
#         "split_overlap": 30,
#         "split_respect_sentence_boundary": True
#       }
#     self._chain = None

#   def build_feature_orchestrator_chain(self):
#     system_text = feature_orchestrator_prompt
#    # parser = PydanticOutputParser(pydantic_object=SingleCTEOutput)
#     messages = [
#         SystemMessagePromptTemplate.from_template(system_text),
#         HumanMessagePromptTemplate.from_template("mode: {mode}\n\nuser_request_text:\n{user_request_text}\n\nuser_feedback_json:\n{user_feedback_json}\n\nReturn JSON only.")
#           ]
#     prompt = ChatPromptTemplate.from_messages(messages)
#     llm = ChubbGPT(rag_params=self.rag_params)
#     return prompt | llm
#  # | parser

#   def run_feature_orchestrator(self, mode: str, user_request_text: str, user_feedback_json: dict | None = None) -> OrchestratorOutput:
#     """
#     Returns a JSON string:
#       - draft: proposed_features + questions_for_user
#       - finalize: features (FeatureDefinitionSpec list)
#     """
#     chain = self.build_feature_orchestrator_chain()
#    # result = None
#     payload: Dict[str, Any] = {
#             "mode": mode,
#             "user_request_text": user_request_text,
#             "user_feedback_json": user_feedback_json or {}
#             }
#     result = chain.invoke(payload)
#     print("result from the orchestrator agent",result )
#     if mode == 'draft':
#       return self.parse_draft_mode(result)
#     elif mode == 'finalize':
#       return self.parse_finalize_mode(result)
#     else:
#       raise ValueError(f"Unsupported mode: {mode}")

#   def parse_finalize_mode(self, result: str) -> _FinalizeWrapper:
#     """
#     Parses the result for 'finalize' mode and wraps it in _FinalizeWrapper.
#     """
#     parsed_result = json.loads(result)
#     orchestrator_output = OrchestratorFinalizeOutput(**parsed_result)
#     OrchestratorFinalizeOutput
#     return _FinalizeWrapper(
#       mode="finalize",
#       payload=orchestrator_output
#     )

#   def parse_draft_mode(self, result: str) -> _DraftWrapper:
#     """
#     Parses the result for 'draft' mode and wraps it in _DraftWrapper.
#     """
#     parsed_result = json.loads(result)
#     orchestrator_output = OrchestratorDraftOutput(**parsed_result)
#     return _DraftWrapper(
#       mode="draft",
#       payload=orchestrator_output
#     )