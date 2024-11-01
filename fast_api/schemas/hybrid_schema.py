from typing import List, Optional, Set
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
)

class CustomRetriever(BaseRetriever):
    """Custom retriever that performs semantic search with filtering by multiple document IDs."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        document_ids: Optional[Set[str]] = None,
    ) -> None:
        """Initialize with vector retriever and an optional set of document IDs to filter."""

        self._vector_retriever = vector_retriever
        self._document_ids = document_ids  # Parameter for filtering by multiple document IDs
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query, filtered by a set of document IDs if provided."""

        # Retrieve nodes using the vector retriever
        vector_nodes = self._vector_retriever.retrieve(query_bundle)

        # Filter nodes by document_ids if specified
        if self._document_ids:
            vector_nodes = [n for n in vector_nodes if n.node.document_id in self._document_ids]

        return vector_nodes