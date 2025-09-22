"""
Abstract interfaces for the cognitive memory system.

This module defines the core abstractions that enable component swapping,
testing, and scaling as outlined in the technical specification.
"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from .memory import ActivationResult, CognitiveMemory, SearchResult


class EmbeddingProvider(ABC):
    """Abstract interface for embedding models."""

    @abstractmethod
    def encode(self, text: str) -> np.ndarray:
        """Encode a single text into a vector representation."""
        pass

    @abstractmethod
    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts into vector representations."""
        pass


class VectorStorage(ABC):
    """Abstract interface for vector databases."""

    @abstractmethod
    def store_vector(
        self, id: str, vector: np.ndarray, metadata: dict[str, Any]
    ) -> None:
        """Store a vector with associated metadata."""
        pass

    @abstractmethod
    def search_similar(
        self, query_vector: np.ndarray, k: int, filters: dict | None = None
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def delete_vector(self, id: str) -> bool:
        """Delete a vector by ID."""
        pass

    @abstractmethod
    def update_vector(
        self, id: str, vector: np.ndarray, metadata: dict[str, Any]
    ) -> bool:
        """Update an existing vector and its metadata."""
        pass

    @abstractmethod
    def delete_vectors_by_ids(self, memory_ids: list[str]) -> list[str]:
        """Delete vectors by their IDs. Returns list of successfully deleted memory IDs."""
        pass


class ActivationEngine(ABC):
    """Abstract interface for memory activation."""

    @abstractmethod
    def activate_memories(
        self, context: np.ndarray, threshold: float, max_activations: int = 50
    ) -> ActivationResult:
        """Activate memories based on context with spreading activation."""
        pass


class DimensionExtractor(ABC):
    """Abstract interface for multi-dimensional feature extraction."""

    @abstractmethod
    def extract_dimensions(self, text: str) -> dict[str, np.ndarray]:
        """Extract emotional, temporal, contextual, and social dimensions."""
        pass


class MemoryStorage(ABC):
    """Abstract interface for memory persistence."""

    @abstractmethod
    def store_memory(self, memory: CognitiveMemory) -> bool:
        """Store a cognitive memory."""
        pass

    @abstractmethod
    def retrieve_memory(self, memory_id: str) -> CognitiveMemory | None:
        """Retrieve a memory by ID."""
        pass

    @abstractmethod
    def update_memory(self, memory: CognitiveMemory) -> bool:
        """Update an existing memory."""
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        pass

    @abstractmethod
    def get_memories_by_level(self, level: int) -> list[CognitiveMemory]:
        """Get all memories at a specific hierarchy level."""
        pass

    @abstractmethod
    def get_memories_by_source_path(self, source_path: str) -> list[CognitiveMemory]:
        """Get memories by source file path from metadata."""
        pass

    @abstractmethod
    def delete_memories_by_source_path(self, source_path: str) -> int:
        """Delete all memories associated with a source file path. Returns count of deleted memories."""
        pass

    @abstractmethod
    def get_memories_by_tags(self, tags: list[str]) -> list[CognitiveMemory]:
        """Get memories that have any of the specified tags."""
        pass

    @abstractmethod
    def delete_memories_by_tags(self, tags: list[str]) -> int:
        """Delete memories that have any of the specified tags. Returns count of deleted memories."""
        pass

    @abstractmethod
    def delete_memories_by_ids(self, memory_ids: list[str]) -> int:
        """Delete memories by their IDs. Returns count of deleted memories."""
        pass


class ConnectionGraph(ABC):
    """Abstract interface for memory connection tracking."""

    @abstractmethod
    def add_connection(
        self,
        source_id: str,
        target_id: str,
        strength: float,
        connection_type: str = "associative",
    ) -> bool:
        """Add a connection between two memories."""
        pass

    @abstractmethod
    def get_connections(
        self, memory_id: str, min_strength: float = 0.0
    ) -> list[CognitiveMemory]:
        """Get connected memories above minimum strength threshold."""
        pass

    @abstractmethod
    def update_connection_strength(
        self, source_id: str, target_id: str, new_strength: float
    ) -> bool:
        """Update the strength of an existing connection."""
        pass

    @abstractmethod
    def remove_connection(self, source_id: str, target_id: str) -> bool:
        """Remove a connection between memories."""
        pass


class MemoryLoader(ABC):
    """Abstract interface for loading external content into cognitive memory."""

    @abstractmethod
    def load_from_source(
        self, source_path: str, **kwargs: Any
    ) -> list[CognitiveMemory]:
        """
        Load cognitive memories from an external source.

        Args:
            source_path: Path to the source content
            **kwargs: Loader-specific parameters

        Returns:
            List of CognitiveMemory objects created from the source
        """
        pass

    @abstractmethod
    def extract_connections(
        self, memories: list[CognitiveMemory]
    ) -> list[tuple[str, str, float, str]]:
        """
        Extract connections between memories.

        Args:
            memories: List of memories to analyze for connections

        Returns:
            List of tuples: (source_id, target_id, strength, connection_type)
        """
        pass

    @abstractmethod
    def validate_source(self, source_path: str) -> bool:
        """
        Validate that the source can be processed by this loader.

        Args:
            source_path: Path to validate

        Returns:
            True if source is valid for this loader
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """
        Get list of file extensions supported by this loader.

        Returns:
            List of supported file extensions (e.g., ['.md', '.markdown'])
        """
        pass

    def upsert_memories(self, memories: list[CognitiveMemory]) -> bool:
        """
        Update existing memories or insert new ones using deterministic IDs.

        This method provides default backward-compatible behavior for existing
        loaders. Override this method to implement true upsert capabilities.

        Args:
            memories: List of memories to upsert

        Returns:
            True if all operations succeeded, False otherwise
        """
        # Default implementation for backward compatibility
        # This will be overridden in loaders that support true upsert
        # For now, we don't have access to cognitive_system here, so we defer to subclasses
        raise NotImplementedError(
            "Subclasses must implement upsert_memories() method. "
            "Default behavior should call store_memory for each memory."
        )


class CognitiveSystem(ABC):
    """High-level interface for the complete cognitive memory system."""

    @abstractmethod
    def store_experience(self, text: str, context: dict[str, Any] | None = None) -> str:
        """Store a new experience and return its memory ID."""
        pass

    @abstractmethod
    def retrieve_memories(
        self,
        query: str,
        types: list[str] | None = None,
        max_results: int = 20,
    ) -> dict[str, list[CognitiveMemory]]:
        """Retrieve memories of specified types for a query."""
        pass

    @abstractmethod
    def consolidate_memories(self) -> dict[str, int]:
        """Trigger episodic to semantic memory consolidation."""
        pass

    @abstractmethod
    def get_memory_stats(self) -> dict[str, Any]:
        """Get system statistics and metrics."""
        pass

    @abstractmethod
    def load_memories_from_source(
        self, loader: MemoryLoader, source_path: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Load memories from external source using specified loader.

        Args:
            loader: MemoryLoader instance to use
            source_path: Path to the source content
            **kwargs: Additional parameters for the loader

        Returns:
            Dictionary containing load results and statistics
        """
        pass

    @abstractmethod
    def upsert_memories(self, memories: list[CognitiveMemory]) -> dict[str, Any]:
        """
        Update existing memories or insert new ones using deterministic IDs.

        Args:
            memories: List of memories to upsert

        Returns:
            Dictionary containing upsert results and statistics
        """
        pass

    @abstractmethod
    def delete_memories_by_source_path(self, source_path: str) -> dict[str, Any]:
        """
        Delete all memories associated with a source file path.

        Args:
            source_path: Source file path to delete memories for

        Returns:
            Dictionary containing deletion results and statistics
        """
        pass

    @abstractmethod
    def atomic_reload_memories_from_source(
        self, loader: MemoryLoader, source_path: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Atomically reload memories from a source by deleting existing ones first.

        This ensures consistency by treating delete+reload as a single operation.

        Args:
            loader: MemoryLoader instance to use
            source_path: Path to the source content
            **kwargs: Additional parameters for the loader

        Returns:
            Dictionary containing combined operation results and statistics
        """
        pass

    @abstractmethod
    def retrieve_memory(self, memory_id: str) -> CognitiveMemory | None:
        """Retrieve a memory by ID."""
        pass

    @abstractmethod
    def get_memories_by_tags(self, tags: list[str]) -> list[CognitiveMemory]:
        """Get memories that have any of the specified tags."""
        pass

    @abstractmethod
    def delete_memory_by_id(self, memory_id: str) -> dict[str, Any]:
        """Delete a single memory by its ID."""
        pass

    @abstractmethod
    def delete_memories_by_tags(self, tags: list[str]) -> dict[str, Any]:
        """Delete memories that have any of the specified tags."""
        pass
