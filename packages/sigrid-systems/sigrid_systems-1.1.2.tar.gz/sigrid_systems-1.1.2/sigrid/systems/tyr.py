"""
TYR - ECHR Analysis API

Justice through sacrifice. TYR provides intelligent ECHR case analysis,
tracing doctrinal connections and precedents across 47 legal systems.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING

from .types import AnalysisEvent, Documents
from .stream import AnalysisStream

if TYPE_CHECKING:
    from .client import Client


class TYRClient:
    """
    TYR API client for ECHR case analysis.

    This class is not meant to be instantiated directly.
    Access it through the main Client instance:

        api_client = Client(api_key="key", user_id="user")
        await api_client.tyr.analyze(documents, query)
    """

    def __init__(self, client: "Client"):
        """Initialize TYR client with parent client reference."""
        self._client = client

    async def analyze(
        self,
        documents: Documents,
        query: str,
        *,
        include_reasoning: bool = True,
        correlation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> List[AnalysisEvent]:
        """
        Analyze documents for ECHR compliance and return all events.

        Args:
            documents: List of legal documents to analyze
            query: ECHR analysis query (e.g., "@caselaw article 6(3)c")
            include_reasoning: Include LLM reasoning steps
            correlation_id: Optional correlation ID for tracking
            idempotency_key: Optional idempotency key for retries

        Returns:
            List of all analysis events
        """
        # Delegate to parent client's implementation
        return await self._client._analyze_impl(
            documents=documents,
            query=query,
            include_reasoning=include_reasoning,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key
        )

    def analyze_stream(
        self,
        documents: Documents,
        query: str,
        *,
        include_reasoning: bool = True,
        correlation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> AnalysisStream:
        """
        Stream ECHR analysis results in real-time.

        Args:
            documents: List of legal documents to analyze
            query: ECHR analysis query (e.g., "@caselaw article 6(3)c")
            include_reasoning: Include LLM reasoning steps
            correlation_id: Optional correlation ID for tracking
            idempotency_key: Optional idempotency key for retries

        Returns:
            AnalysisStream context manager for streaming events
        """
        # Delegate to parent client's implementation
        return self._client._analyze_stream_impl(
            documents=documents,
            query=query,
            include_reasoning=include_reasoning,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key
        )

    async def get_session_log(
        self,
        session_id: str,
        *,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get TYR analysis session log by ID.

        Args:
            session_id: Session identifier from previous analysis
            correlation_id: Optional correlation ID

        Returns:
            Session log data with analysis history
        """
        return await self._client.get_session_log(
            session_id,
            correlation_id=correlation_id
        )

    async def get_user_logs(
        self,
        *,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all TYR analysis logs for the current user.

        Args:
            correlation_id: Optional correlation ID

        Returns:
            User logs data with all analysis history
        """
        return await self._client.get_user_logs(
            correlation_id=correlation_id
        )