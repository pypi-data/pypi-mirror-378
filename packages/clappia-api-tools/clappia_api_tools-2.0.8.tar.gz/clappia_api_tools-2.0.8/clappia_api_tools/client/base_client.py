from abc import ABC
from typing import Optional
from clappia_api_tools.utils.api_utils import ClappiaAPIKeyUtils, ClappiaAuthTokenUtils


class BaseClappiaClient(ABC):
    """Base client with shared functionality for all Clappia clients.

    This class provides the common initialization and shared utilities
    that all specialized Clappia clients will inherit from.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize base Clappia client.
        Args:
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url
        self.timeout = timeout

class BaseAPIKeyClient(BaseClappiaClient):
    """Base client for API key authentication.

    This class provides the common initialization and shared utilities
    for clients that use API key authentication.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize base API key client.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        super().__init__(base_url, timeout)
        self.api_utils = ClappiaAPIKeyUtils(api_key, base_url, timeout)


class BaseAuthTokenClient(BaseClappiaClient):
    """Base client for auth token authentication.

    This class provides the common initialization and shared utilities
    for clients that use auth token and workplace ID authentication.
    """

    def __init__(
        self,
        auth_token: Optional[str] = None,
        workplace_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize base auth token client.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        super().__init__(base_url, timeout)
        self.api_utils = ClappiaAuthTokenUtils(auth_token, workplace_id, base_url, timeout)


