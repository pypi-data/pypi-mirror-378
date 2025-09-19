"""
Clappia Tools - LangChain integration for Clappia API

This package provides a unified client for interacting with Clappia APIs.
"""

from .client.app_definition_client import AppDefinitionClient, AppDefinitionAPIKeyClient, AppDefinitionAuthTokenClient
from .client.submission_client import SubmissionClient, SubmissionAPIKeyClient, SubmissionAuthTokenClient
from .client.workflow_definition_client import WorkflowDefinitionClient, WorkflowDefinitionAPIKeyClient, WorkflowDefinitionAuthTokenClient
from .client.analytics_client import AnalyticsClient, AnalyticsAPIKeyClient, AnalyticsAuthTokenClient
from .client.workplace_client import WorkplaceClient, WorkplaceAPIKeyClient, WorkplaceAuthTokenClient
from .client.base_client import BaseClappiaClient


__version__ = "1.0.2"
__all__ = [
    "AppDefinitionClient",
    "AppDefinitionAPIKeyClient",
    "AppDefinitionAuthTokenClient",
    "SubmissionClient",
    "SubmissionAPIKeyClient",
    "SubmissionAuthTokenClient",
    "WorkflowDefinitionClient",
    "WorkflowDefinitionAPIKeyClient",
    "WorkflowDefinitionAuthTokenClient",
    "AnalyticsClient",
    "WorkplaceClient",
    "WorkplaceAPIKeyClient",
    "WorkplaceAuthTokenClient",
    "BaseClappiaClient",
]


def __dir__():
    return __all__
