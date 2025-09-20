"""AgentLab Python Client Library

A Python client library for the AgentLab evaluation platform using Connect RPC.
"""

from .client import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions, CreateAgentVersionOptions
from .exceptions import AgentLabError, AuthenticationError, APIError
from .models import (
    EvaluationRun, EvaluatorResult, Evaluator,
    ListEvaluatorsResponse, ListEvaluationRunsResponse,
    EvaluationState, EvaluatorResultState,
    Agent, AgentVersion, ListAgentVersionsResponse
)
from .converters import convert_protobuf_object

__version__ = "0.1.0"
__all__ = [
    "AgentLabClient", "AgentLabClientOptions", "CreateEvaluationOptions", "CreateAgentVersionOptions",
    "AgentLabError", "AuthenticationError", "APIError",
    "EvaluationRun", "EvaluatorResult", "Evaluator",
    "ListEvaluatorsResponse", "ListEvaluationRunsResponse",
    "EvaluationState", "EvaluatorResultState",
    "Agent", "AgentVersion", "ListAgentVersionsResponse",
    "convert_protobuf_object"
]
