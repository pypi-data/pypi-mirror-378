# core/state.py
from typing import TypedDict

class AssistantState(TypedDict, total=False):
    query: str
    codegen_response: str
    debug_response: str
    explain_response: str
    file_saved: str
    saved_filename: str
