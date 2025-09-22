"""
Cognitive system coordinator implementing the high-level CognitiveSystem interface.

This module provides the main facade for the cognitive memory system, coordinating
between encoding, storage, and retrieval subsystems through their abstract interfaces.
All dependencies are injected through interfaces to enable testing and component swapping.
"""

import time
import uuid
from datetime import datetime
from typing import Any

from loguru import logger

from .config import SystemConfig
from .interfaces import (
    ActivationEngine,
    CognitiveSystem,
    ConnectionGraph,
    EmbeddingProvider,
    MemoryLoader,
    MemoryStorage,
    VectorStorage,
)
from .memory import CognitiveMemory


class CognitiveMemorySystem(CognitiveSystem):
    """
    Main cognitive memory system coordinator.

    Implements the high-level CognitiveSystem interface by coordinating between
    encoding, storage, and retrieval subsystems. Uses dependency injection
    for all components to enable testing and component swapping.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_storage: VectorStorage,
        memory_storage: MemoryStorage,
        connection_graph: ConnectionGraph,
        activation_engine: ActivationEngine,
        config: SystemConfig,
    ):
        """
        Initialize cognitive memory system with injected dependencies.

        Args:
            embedding_provider: Interface for text encoding
            vector_storage: Interface for vector similarity storage
            memory_storage: Interface for memory persistence
            connection_graph: Interface for memory connections
            activation_engine: Interface for memory activation
            config: System configuration
        """
        self.embedding_provider = embedding_provider
        self.vector_storage = vector_storage
        self.memory_storage = memory_storage
        self.connection_graph = connection_graph
        self.activation_engine = activation_engine
        self.config = config

        logger.info(
            "Cognitive memory system initialized",
            components=[
                "embedding_provider",
                "vector_storage",
                "memory_storage",
                "connection_graph",
                "activation_engine",
            ],
        )

    def store_experience(self, text: str, context: dict[str, Any] | None = None) -> str:
        """
        Store a new experience and return its memory ID.

        Args:
            text: The experience text to store
            context: Optional context information

        Returns:
            str: Unique memory ID for the stored experience
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for experience storage")
            return ""

        try:
            # Generate unique memory ID
            memory_id = str(uuid.uuid4())
            current_time = datetime.now()

            # Prepare content with tags for encoding
            content_for_embedding = text
            if context and context.get("tags"):
                content_for_embedding = f"{text} {' '.join(context['tags'])}"

            # Encode the experience
            embedding = self.embedding_provider.encode(content_for_embedding)

            # Determine hierarchy level based on context or heuristics
            if context and "hierarchy_level" in context:
                hierarchy_level = context["hierarchy_level"]
                if hierarchy_level not in [0, 1, 2]:
                    logger.warning(
                        f"Invalid hierarchy level {hierarchy_level}, using L2"
                    )
                    hierarchy_level = 2
            else:
                hierarchy_level = self._determine_hierarchy_level(text)

            # Prepare metadata with source_type for deterministic content-type decay detection
            memory_metadata = {}
            if context:
                memory_metadata.update(context)
            # Set source_type based on context or default to manual_entry
            if "source_type" not in memory_metadata:
                memory_metadata["source_type"] = "manual_entry"

            # Create cognitive memory object
            memory = CognitiveMemory(
                id=memory_id,
                content=text.strip(),
                memory_type="episodic" if hierarchy_level == 2 else "semantic",
                hierarchy_level=hierarchy_level,
                dimensions=context.get("dimensions", {}) if context else {},
                timestamp=current_time,
                strength=1.0,
                access_count=0,
                metadata=memory_metadata,
                tags=context.get("tags") if context else None,
            )

            # Attach the embedding to the memory object
            memory.cognitive_embedding = embedding

            # Store in memory persistence
            if not self.memory_storage.store_memory(memory):
                logger.error(
                    "Failed to store memory in persistence layer", memory_id=memory_id
                )
                return ""

            # Store in vector storage with metadata
            vector_metadata = {
                "memory_id": memory_id,
                "content": text.strip(),
                "memory_type": memory.memory_type,
                "hierarchy_level": hierarchy_level,
                "timestamp": current_time.timestamp(),
                "strength": 1.0,
                "access_count": 0,
            }

            # Add context metadata if provided
            if context:
                for key, value in context.items():
                    if key not in vector_metadata:
                        vector_metadata[key] = value

            self.vector_storage.store_vector(memory_id, embedding, vector_metadata)

            logger.info(
                "Experience stored successfully",
                memory_id=memory_id,
                text_length=len(text),
                hierarchy_level=hierarchy_level,
                memory_type=memory.memory_type,
            )

            return memory_id

        except Exception as e:
            logger.error(
                "Failed to store experience",
                text_preview=text[:100] + "..." if len(text) > 100 else text,
                error=str(e),
            )
            return ""

    def retrieve_memories(
        self,
        query: str,
        types: list[str] | None = None,
        max_results: int = 20,
    ) -> dict[str, list[CognitiveMemory]]:
        """
        Retrieve memories of specified types for a query.

        Args:
            query: Query text to search for
            types: List of memory types to retrieve ("core", "peripheral")
            max_results: Maximum number of results to return

        Returns:
            Dict mapping memory types to lists of CognitiveMemory objects
        """
        if not query or not query.strip():
            logger.warning("Empty query provided for memory retrieval")
            return {"core": [], "peripheral": []}

        if types is None:
            types = ["core", "peripheral"]

        try:
            # Encode the query
            query_embedding = self.embedding_provider.encode(query.strip())

            results: dict[str, list[CognitiveMemory]] = {
                "core": [],
                "peripheral": [],
            }

            # Add tag-based memories first, then activation-based memories
            if "core" in types or "peripheral" in types:
                self._add_tag_memories(query, types, results, max_results)
                self._add_activation_memories(
                    query_embedding, types, results, max_results
                )

            # Fallback to direct vector similarity search if no core/peripheral memories found
            if (
                ("core" in types or "peripheral" in types)
                and not results["core"]
                and not results["peripheral"]
            ):
                logger.debug(
                    "No memories activated, falling back to direct vector similarity search"
                )
                # Use max_activations to respect cognitive configuration
                fallback_limit = min(max_results, self.config.cognitive.max_activations)
                similarity_results = self.vector_storage.search_similar(
                    query_embedding, k=fallback_limit
                )

                # Apply tag boost to similarity scores before filtering/splitting
                query_lower = query.strip().lower()
                for result in similarity_results:
                    if result.memory.tags:
                        tag_boost = self._calculate_tag_boost(
                            result.memory, query_lower
                        )
                        if tag_boost > 0:
                            result.similarity_score += tag_boost
                            logger.debug(
                                "Applied tag boost",
                                memory_id=result.memory.id[:8],
                                original_score=result.similarity_score - tag_boost,
                                boost=tag_boost,
                                final_score=result.similarity_score,
                            )

                # Re-sort by boosted scores to ensure tag matches rank higher
                similarity_results.sort(key=lambda x: x.similarity_score, reverse=True)

                # Split results between core and peripheral
                half = fallback_limit // 2 or 1
                top_results = similarity_results
                if "core" in types:
                    core_memories = []
                    for result in top_results[:half]:
                        # Retrieve complete memory object from SQLite storage to get tags
                        complete_memory = self.memory_storage.retrieve_memory(
                            result.memory.id
                        )
                        if complete_memory:
                            # Store similarity score in metadata for display
                            complete_memory.metadata["similarity_score"] = (
                                result.similarity_score
                            )
                            core_memories.append(complete_memory)
                        else:
                            # Fallback to incomplete memory if SQLite retrieval fails
                            result.memory.metadata["similarity_score"] = (
                                result.similarity_score
                            )
                            core_memories.append(result.memory)
                    results["core"].extend(core_memories)
                if "peripheral" in types:
                    peripheral_memories = []
                    for result in top_results[half:]:
                        # Retrieve complete memory object from SQLite storage to get tags
                        complete_memory = self.memory_storage.retrieve_memory(
                            result.memory.id
                        )
                        if complete_memory:
                            # Store similarity score in metadata for display
                            complete_memory.metadata["similarity_score"] = (
                                result.similarity_score
                            )
                            peripheral_memories.append(complete_memory)
                        else:
                            # Fallback to incomplete memory if SQLite retrieval fails
                            result.memory.metadata["similarity_score"] = (
                                result.similarity_score
                            )
                            peripheral_memories.append(result.memory)
                    results["peripheral"].extend(peripheral_memories)

            # Apply tag-based boost to improve ranking
            self._apply_tag_boost(results, query.strip())

            # Log retrieval statistics
            total_retrieved = sum(len(memories) for memories in results.values())
            logger.info(
                "Memory retrieval completed",
                query_length=len(query),
                requested_types=types,
                total_retrieved=total_retrieved,
                core_count=len(results["core"]),
                peripheral_count=len(results["peripheral"]),
            )

            return results

        except Exception as e:
            logger.error(
                "Failed to retrieve memories",
                query_preview=query[:100] + "..." if len(query) > 100 else query,
                types=types,
                error=str(e),
            )
            return {"core": [], "peripheral": []}

    def _determine_hierarchy_level(self, text: str) -> int:
        """
        Determine hierarchy level based on content analysis.

        L0 (Concepts): Abstract ideas, principles, concepts, algorithms
        L1 (Contexts): Situational memories, workflow patterns, meetings
        L2 (Episodes): Specific experiences, events, activities

        Args:
            text: The experience text to analyze

        Returns:
            int: Hierarchy level (0, 1, or 2)
        """
        text_lower = text.lower().strip()

        # L0 indicators: abstract concepts, learning, principles
        concept_keywords = [
            "concept",
            "principle",
            "theory",
            "algorithm",
            "pattern",
            "methodology",
            "approach",
            "technique",
            "strategy",
            "framework",
            "architecture",
            "design pattern",
            "best practice",
            "paradigm",
            "learning",
            "understanding",
            "knowledge",
        ]

        # L1 indicators: contexts, workflows, meetings, planning
        context_keywords = [
            "meeting",
            "collaboration",
            "planning",
            "workflow",
            "process",
            "sprint",
            "project",
            "team",
            "discussion",
            "review",
            "session",
            "standup",
            "retrospective",
            "brainstorm",
            "about",
        ]

        # L2 indicators: specific activities and actions
        activity_keywords = [
            "working on",
            "debugging",
            "implementing",
            "fixing",
            "building",
            "coding",
            "testing",
            "deploying",
            "troubleshooting",
            "optimizing",
            "with",
            "using",
            "problems",
        ]

        # Count indicators
        concept_score = sum(1 for keyword in concept_keywords if keyword in text_lower)
        context_score = sum(1 for keyword in context_keywords if keyword in text_lower)
        activity_score = sum(
            1 for keyword in activity_keywords if keyword in text_lower
        )

        # Determine level based on highest scoring category
        if concept_score > context_score and concept_score > activity_score:
            return 0  # L0: Concepts
        elif context_score > activity_score:
            return 1  # L1: Contexts
        else:
            return 2  # L2: Episodes (default for specific activities)

    def consolidate_memories(self) -> dict[str, int]:
        """
        Trigger episodic to semantic memory consolidation.

        Returns:
            Dict with consolidation statistics
        """
        try:
            logger.info("Starting memory consolidation process")

            # Get all episodic memories from L2 (episodes)
            episodic_memories = self.memory_storage.get_memories_by_level(2)

            consolidation_stats = {
                "total_episodic": len(episodic_memories),
                "consolidated": 0,
                "failed": 0,
                "skipped": 0,
            }

            # Simple consolidation logic: promote frequently accessed memories
            current_time = datetime.now()

            for memory in episodic_memories:
                try:
                    # Check if memory meets consolidation criteria
                    age_seconds = (current_time - memory.timestamp).total_seconds()
                    if (
                        memory.access_count >= 5  # Accessed multiple times
                        and memory.strength > 0.8  # High strength
                        and age_seconds > 86400
                    ):  # At least 1 day old
                        # Create semantic version
                        semantic_memory = CognitiveMemory(
                            id=str(uuid.uuid4()),
                            content=memory.content,
                            memory_type="semantic",
                            hierarchy_level=1,  # Move to L1 (contexts)
                            dimensions=memory.dimensions,
                            timestamp=current_time,
                            strength=memory.strength
                            * 0.9,  # Slight decay during consolidation
                            access_count=0,  # Reset access count
                        )

                        # Store semantic memory
                        if self.memory_storage.store_memory(semantic_memory):
                            # Re-encode and store in vector storage
                            embedding = self.embedding_provider.encode(memory.content)
                            vector_metadata = {
                                "memory_id": semantic_memory.id,
                                "content": semantic_memory.content,
                                "memory_type": "semantic",
                                "hierarchy_level": 1,
                                "timestamp": current_time,
                                "strength": semantic_memory.strength,
                                "access_count": 0,
                            }

                            self.vector_storage.store_vector(
                                semantic_memory.id, embedding, vector_metadata
                            )

                            # Add connection from episodic to semantic
                            self.connection_graph.add_connection(
                                memory.id, semantic_memory.id, 0.9, "consolidation"
                            )

                            consolidation_stats["consolidated"] += 1
                            logger.debug(
                                "Memory consolidated",
                                episodic_id=memory.id,
                                semantic_id=semantic_memory.id,
                            )
                        else:
                            consolidation_stats["failed"] += 1
                    else:
                        consolidation_stats["skipped"] += 1

                except Exception as e:
                    logger.error(
                        "Failed to consolidate individual memory",
                        memory_id=memory.id,
                        error=str(e),
                    )
                    consolidation_stats["failed"] += 1

            logger.info("Memory consolidation completed", **consolidation_stats)

            return consolidation_stats

        except Exception as e:
            logger.error("Memory consolidation process failed", error=str(e))
            return {"total_episodic": 0, "consolidated": 0, "failed": 0, "skipped": 0}

    def get_memory_stats(self) -> dict[str, Any]:
        """
        Get system statistics and metrics.

        Returns:
            Dict containing various system statistics
        """
        try:
            # Initialize with proper typing
            memory_counts: dict[str, Any] = {}
            storage_stats: dict[str, Any] = {}

            stats: dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "system_config": {
                    "activation_threshold": self.config.cognitive.activation_threshold,
                    "max_activations": self.config.cognitive.max_activations,
                    "consolidation_threshold": self.config.cognitive.consolidation_threshold,
                },
                "memory_counts": memory_counts,
                "storage_stats": storage_stats,
                "error": None,
            }

            # Get memory counts by level
            try:
                for level in [0, 1, 2]:
                    memories = self.memory_storage.get_memories_by_level(level)
                    level_name = ["concepts", "contexts", "episodes"][level]
                    memory_counts[f"level_{level}_{level_name}"] = len(memories)
            except Exception as e:
                logger.warning("Failed to get memory counts", error=str(e))
                memory_counts["error"] = str(e)

            # Get vector storage statistics if available
            try:
                if hasattr(self.vector_storage, "get_storage_stats"):
                    # Call the method and update our stats dict
                    vector_stats = self.vector_storage.get_storage_stats()
                    storage_stats.update(vector_stats)
            except Exception as e:
                logger.warning("Failed to get storage stats", error=str(e))
                storage_stats["error"] = str(e)

            # Add embedding provider info if available
            try:
                if hasattr(self.embedding_provider, "get_model_info"):
                    embedding_info = self.embedding_provider.get_model_info()
                    stats["embedding_info"] = embedding_info
            except Exception as e:
                logger.debug("Embedding provider info not available", error=str(e))

            return stats

        except Exception as e:
            logger.error("Failed to generate system stats", error=str(e))
            return {
                "timestamp": time.time(),
                "error": str(e),
                "system_config": {},
                "memory_counts": {},
                "storage_stats": {},
            }

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
        if not loader.validate_source(source_path):
            error_msg = f"Source validation failed for {source_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "memories_loaded": 0,
                "connections_created": 0,
                "processing_time": 0.0,
            }

        start_time = time.time()

        try:
            logger.info(f"Starting memory loading from {source_path}")

            # Load memories from source
            memories = loader.load_from_source(source_path, **kwargs)
            logger.info(f"Loaded {len(memories)} raw memories from source")

            # Store memories in the system
            stored_count = 0
            failed_count = 0

            for memory in memories:
                try:
                    # Encode the memory content
                    embedding = self.embedding_provider.encode(memory.content)
                    memory.cognitive_embedding = embedding

                    # Store in memory persistence
                    if self.memory_storage.store_memory(memory):
                        # Store in vector storage with metadata
                        vector_metadata = {
                            "memory_id": memory.id,
                            "content": memory.content,
                            "memory_type": memory.memory_type,
                            "hierarchy_level": memory.hierarchy_level,
                            "timestamp": memory.timestamp.timestamp()
                            if memory.timestamp
                            else time.time(),
                            "source_type": "loaded",
                            **memory.metadata,
                        }

                        self.vector_storage.store_vector(
                            memory.id, embedding, vector_metadata
                        )
                        stored_count += 1

                        logger.debug(
                            f"Stored memory L{memory.hierarchy_level}: {memory.metadata.get('title', 'Untitled')[:50]}"
                        )
                    else:
                        failed_count += 1
                        logger.warning(f"Failed to store memory: {memory.id}")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error storing memory {memory.id}: {e}")

            # Extract and store connections
            connections_created = 0
            connections_failed = 0

            if stored_count > 0:
                try:
                    logger.info("Parsing connections between memories...")
                    connections = loader.extract_connections(memories)
                    logger.info(f"Extracted {len(connections)} potential connections")

                    for source_id, target_id, strength, connection_type in connections:
                        try:
                            if self.connection_graph.add_connection(
                                source_id, target_id, strength, connection_type
                            ):
                                connections_created += 1
                            else:
                                connections_failed += 1
                        except Exception as e:
                            connections_failed += 1
                            logger.debug(
                                f"Failed to store connection {source_id} -> {target_id}: {e}"
                            )

                except Exception as e:
                    logger.error(f"Failed to extract connections: {e}")

            processing_time = time.time() - start_time

            # Prepare results
            results = {
                "success": True,
                "source_path": source_path,
                "loader_type": loader.__class__.__name__,
                "memories_loaded": stored_count,
                "memories_failed": failed_count,
                "connections_created": connections_created,
                "connections_failed": connections_failed,
                "processing_time": processing_time,
                "hierarchy_distribution": self._calculate_hierarchy_distribution(
                    memories
                ),
                "error": None,
            }

            logger.info(
                "Memory loading completed successfully",
                **{k: v for k, v in results.items() if k != "error"},
            )

            return results

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Memory loading failed: {str(e)}"
            logger.error(error_msg)

            return {
                "success": False,
                "error": error_msg,
                "source_path": source_path,
                "loader_type": loader.__class__.__name__,
                "memories_loaded": 0,
                "connections_created": 0,
                "processing_time": processing_time,
            }

    def upsert_memories(self, memories: list[CognitiveMemory]) -> dict[str, Any]:
        """
        Update existing memories or insert new ones using deterministic IDs.

        Args:
            memories: List of memories to upsert

        Returns:
            Dictionary containing upsert results and statistics
        """
        start_time = time.time()

        try:
            updated_count = 0
            inserted_count = 0
            failed_count = 0

            logger.info("Starting memory upsert operation", memory_count=len(memories))

            for memory in memories:
                try:
                    # Check if memory already exists using its ID
                    existing_memory = self.memory_storage.retrieve_memory(memory.id)

                    if existing_memory:
                        # Update existing memory
                        if self.memory_storage.update_memory(memory):
                            # Update vector storage as well
                            embedding = self.embedding_provider.encode(memory.content)

                            # Delete old vector first
                            self.vector_storage.delete_vector(memory.id)

                            # Store updated vector
                            self.vector_storage.store_vector(
                                memory.id,
                                embedding,
                                {
                                    "hierarchy_level": memory.hierarchy_level,
                                    "memory_type": memory.memory_type,
                                    "timestamp": memory.timestamp.isoformat(),
                                    "strength": memory.strength,
                                    **memory.metadata,
                                },
                            )
                            updated_count += 1
                            logger.debug(f"Updated memory: {memory.id}")
                        else:
                            failed_count += 1
                            logger.warning(f"Failed to update memory: {memory.id}")
                    else:
                        # Insert new memory - store in both memory storage and vector storage
                        if self.memory_storage.store_memory(memory):
                            # Also store in vector storage
                            embedding = self.embedding_provider.encode(memory.content)
                            self.vector_storage.store_vector(
                                memory.id,
                                embedding,
                                {
                                    "hierarchy_level": memory.hierarchy_level,
                                    "memory_type": memory.memory_type,
                                    "timestamp": memory.timestamp.isoformat(),
                                    "strength": memory.strength,
                                    **memory.metadata,
                                },
                            )
                            inserted_count += 1
                            logger.debug(f"Inserted new memory: {memory.id}")
                        else:
                            failed_count += 1
                            logger.warning(f"Failed to insert memory: {memory.id}")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error upserting memory {memory.id}: {e}")

            processing_time = time.time() - start_time

            results = {
                "success": True,
                "total_memories": len(memories),
                "updated_count": updated_count,
                "inserted_count": inserted_count,
                "failed_count": failed_count,
                "processing_time": processing_time,
                "error": None,
            }

            logger.info(
                "Memory upsert operation completed",
                **{k: v for k, v in results.items() if k != "error"},
            )

            return results

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Memory upsert failed: {str(e)}"
            logger.error(error_msg)

            return {
                "success": False,
                "error": error_msg,
                "total_memories": len(memories),
                "updated_count": 0,
                "inserted_count": 0,
                "failed_count": len(memories),
                "processing_time": processing_time,
            }

    def delete_memories_by_source_path(self, source_path: str) -> dict[str, Any]:
        """
        Delete all memories associated with a specific source path.

        This method handles both vector storage and metadata deletion to ensure
        complete removal of memories from the system.

        Args:
            source_path: The source path to delete memories for

        Returns:
            Dictionary containing deletion results and statistics
        """
        start_time = time.time()

        try:
            logger.info(
                "Starting memory deletion by source path", source_path=source_path
            )

            # First, get all memories to be deleted for vector cleanup
            memories_to_delete = self.memory_storage.get_memories_by_source_path(
                source_path
            )

            if not memories_to_delete:
                logger.info(
                    "No memories found for source path", source_path=source_path
                )
                return {
                    "source_path": source_path,
                    "deleted_count": 0,
                    "vector_deletion_failures": 0,
                    "processing_time": time.time() - start_time,
                }

            # Delete vectors from Qdrant
            vector_deletion_failures = 0
            for memory in memories_to_delete:
                try:
                    success = self.vector_storage.delete_vector(memory.id)
                    if not success:
                        vector_deletion_failures += 1
                        logger.warning("Failed to delete vector", memory_id=memory.id)
                except Exception as e:
                    vector_deletion_failures += 1
                    logger.error(
                        "Error deleting vector", memory_id=memory.id, error=str(e)
                    )

            # Delete memory connections if connection graph exists
            if hasattr(self, "connection_graph") and self.connection_graph:
                for memory in memories_to_delete:
                    try:
                        # Remove connections involving this memory
                        # Note: We don't have a direct method for this in the interface,
                        # but SQLite foreign keys should handle cascading deletes
                        pass
                    except Exception as e:
                        logger.warning(
                            "Error removing connections",
                            memory_id=memory.id,
                            error=str(e),
                        )

            # Delete metadata from SQLite
            deleted_count = self.memory_storage.delete_memories_by_source_path(
                source_path
            )

            processing_time = time.time() - start_time

            logger.info(
                "Memory deletion completed",
                source_path=source_path,
                deleted_count=deleted_count,
                vector_deletion_failures=vector_deletion_failures,
                processing_time=processing_time,
            )

            return {
                "source_path": source_path,
                "deleted_count": deleted_count,
                "vector_deletion_failures": vector_deletion_failures,
                "processing_time": processing_time,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "Failed to delete memories by source path",
                source_path=source_path,
                error=str(e),
                processing_time=processing_time,
            )
            return {
                "source_path": source_path,
                "deleted_count": 0,
                "vector_deletion_failures": 0,
                "processing_time": processing_time,
                "error": str(e),
            }

    def delete_memory_by_id(self, memory_id: str) -> dict[str, Any]:
        """
        Delete a single memory by its ID.

        This method handles both vector storage and metadata deletion to ensure
        complete removal of the memory from the system.

        Args:
            memory_id: The memory ID to delete

        Returns:
            Dictionary containing deletion results and statistics
        """
        start_time = time.time()

        try:
            logger.info("Starting memory deletion by ID", memory_id=memory_id)

            # First, get the memory to verify it exists
            memory = self.memory_storage.retrieve_memory(memory_id)
            if not memory:
                logger.info("Memory not found", memory_id=memory_id)
                return {
                    "memory_id": memory_id,
                    "deleted_count": 0,
                    "vector_deletion_failures": 0,
                    "processing_time": time.time() - start_time,
                }

            # Delete vector from Qdrant
            vector_deletion_failures = 0
            try:
                success = self.vector_storage.delete_vector(memory_id)
                if not success:
                    vector_deletion_failures = 1
                    logger.warning("Failed to delete vector", memory_id=memory_id)
            except Exception as e:
                vector_deletion_failures = 1
                logger.error("Error deleting vector", memory_id=memory_id, error=str(e))

            # Delete metadata from SQLite
            success = self.memory_storage.delete_memory(memory_id)
            deleted_count = 1 if success else 0

            processing_time = time.time() - start_time

            logger.info(
                "Memory deletion completed",
                memory_id=memory_id,
                deleted_count=deleted_count,
                vector_deletion_failures=vector_deletion_failures,
                processing_time=processing_time,
            )

            return {
                "memory_id": memory_id,
                "deleted_count": deleted_count,
                "vector_deletion_failures": vector_deletion_failures,
                "processing_time": processing_time,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "Failed to delete memory by ID",
                memory_id=memory_id,
                error=str(e),
                processing_time=processing_time,
            )
            return {
                "memory_id": memory_id,
                "deleted_count": 0,
                "vector_deletion_failures": 0,
                "processing_time": processing_time,
                "error": str(e),
            }

    def delete_memories_by_tags(self, tags: list[str]) -> dict[str, Any]:
        """
        Delete all memories that have any of the specified tags.

        This method handles both vector storage and metadata deletion to ensure
        complete removal of memories from the system.

        Args:
            tags: List of tags to match against memory tags

        Returns:
            Dictionary containing deletion results and statistics
        """
        start_time = time.time()

        try:
            logger.info("Starting memory deletion by tags", tags=tags)

            # First, get all memories to be deleted for vector cleanup
            memories_to_delete = self.memory_storage.get_memories_by_tags(tags)

            if not memories_to_delete:
                logger.info("No memories found with tags", tags=tags)
                return {
                    "tags": tags,
                    "deleted_count": 0,
                    "vector_deletion_failures": 0,
                    "processing_time": time.time() - start_time,
                }

            # Delete vectors from Qdrant
            memory_ids = [memory.id for memory in memories_to_delete]
            successfully_deleted_vectors = self.vector_storage.delete_vectors_by_ids(
                memory_ids
            )
            vector_deletion_failures = len(memory_ids) - len(
                successfully_deleted_vectors
            )

            if vector_deletion_failures > 0:
                logger.warning(
                    "Some vectors failed to delete",
                    total_vectors=len(memory_ids),
                    failed_count=vector_deletion_failures,
                )

            # Delete metadata from SQLite
            deleted_count = self.memory_storage.delete_memories_by_tags(tags)

            processing_time = time.time() - start_time

            logger.info(
                "Memory deletion completed",
                tags=tags,
                deleted_count=deleted_count,
                vector_deletion_failures=vector_deletion_failures,
                processing_time=processing_time,
            )

            return {
                "tags": tags,
                "deleted_count": deleted_count,
                "vector_deletion_failures": vector_deletion_failures,
                "processing_time": processing_time,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "Failed to delete memories by tags",
                tags=tags,
                error=str(e),
                processing_time=processing_time,
            )
            return {
                "tags": tags,
                "deleted_count": 0,
                "vector_deletion_failures": 0,
                "processing_time": processing_time,
                "error": str(e),
            }

    def retrieve_memory(self, memory_id: str) -> CognitiveMemory | None:
        """Retrieve a memory by ID."""
        return self.memory_storage.retrieve_memory(memory_id)

    def get_memories_by_tags(self, tags: list[str]) -> list[CognitiveMemory]:
        """Get memories that have any of the specified tags."""
        return self.memory_storage.get_memories_by_tags(tags)

    def atomic_reload_memories_from_source(
        self, loader: Any, source_path: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Atomically reload memories from a source by deleting existing ones first.

        This method ensures consistency by treating delete+reload as a single operation.
        It first deletes all existing memories from the source path, then loads new ones.

        Args:
            loader: MemoryLoader instance to use for loading
            source_path: Path to the source file
            **kwargs: Additional loader parameters

        Returns:
            Dictionary containing combined operation results:
            - success: bool - True if operation completed successfully
            - deleted_count: int - Number of memories deleted
            - memories_loaded: int - Number of new memories loaded
            - connections_created: int - Number of connections created
            - processing_time: float - Total time for both operations
            - hierarchy_distribution: dict - Distribution of new memories by level
            - error: str | None - Error message if operation failed
        """
        start_time = time.time()

        try:
            logger.info(f"Starting atomic reload for source: {source_path}")

            # Step 1: Delete existing memories
            delete_result = self.delete_memories_by_source_path(source_path)
            deleted_count = delete_result.get("deleted_count", 0)

            if delete_result.get("error"):
                logger.warning(
                    f"Delete operation had errors but continuing: {delete_result['error']}"
                )

            # Step 2: Load new memories
            load_result = self.load_memories_from_source(loader, source_path, **kwargs)

            processing_time = time.time() - start_time

            if load_result.get("success", False):
                logger.info(
                    f"Atomic reload completed: deleted {deleted_count}, "
                    f"loaded {load_result.get('memories_loaded', 0)} memories from {source_path}"
                )

                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "memories_loaded": load_result.get("memories_loaded", 0),
                    "connections_created": load_result.get("connections_created", 0),
                    "memories_failed": load_result.get("memories_failed", 0),
                    "connections_failed": load_result.get("connections_failed", 0),
                    "processing_time": processing_time,
                    "hierarchy_distribution": load_result.get(
                        "hierarchy_distribution", {}
                    ),
                    "source_path": source_path,
                    "loader_type": loader.__class__.__name__,
                    "error": None,
                }
            else:
                # Load failed, but delete succeeded
                error_msg = f"Load operation failed after successful delete: {load_result.get('error', 'Unknown error')}"
                logger.error(error_msg)

                return {
                    "success": False,
                    "deleted_count": deleted_count,
                    "memories_loaded": 0,
                    "connections_created": 0,
                    "memories_failed": 0,
                    "connections_failed": 0,
                    "processing_time": processing_time,
                    "hierarchy_distribution": {},
                    "source_path": source_path,
                    "loader_type": loader.__class__.__name__,
                    "error": error_msg,
                }

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Atomic reload failed: {str(e)}"
            logger.error(error_msg)

            return {
                "success": False,
                "deleted_count": 0,
                "memories_loaded": 0,
                "connections_created": 0,
                "memories_failed": 0,
                "connections_failed": 0,
                "processing_time": processing_time,
                "hierarchy_distribution": {},
                "source_path": source_path,
                "loader_type": loader.__class__.__name__ if loader else "Unknown",
                "error": error_msg,
            }

    def _calculate_hierarchy_distribution(
        self, memories: list[CognitiveMemory]
    ) -> dict[str, int]:
        """Calculate distribution of memories across hierarchy levels."""
        distribution = {"L0": 0, "L1": 0, "L2": 0}

        for memory in memories:
            level_key = f"L{memory.hierarchy_level}"
            if level_key in distribution:
                distribution[level_key] += 1

        return distribution

    def _apply_tag_boost(
        self, results: dict[str, list[CognitiveMemory]], query: str
    ) -> None:
        """
        Apply tag-based boost to memories when their tags appear in the query.

        Args:
            results: Dictionary with 'core' and 'peripheral' memory lists
            query: Original query string
        """
        if not query:
            return

        query_lower = query.lower()

        # Process both core and peripheral memories
        for memory_type in ["core", "peripheral"]:
            if memory_type not in results:
                continue

            # Create list of (memory, boost_score) tuples
            memory_boosts = []
            for memory in results[memory_type]:
                boost = self._calculate_tag_boost(memory, query_lower)
                memory_boosts.append((memory, boost))

            # Sort by boost score (descending) to put tag-matched memories first
            memory_boosts.sort(key=lambda x: x[1], reverse=True)

            # Update the results list with re-ordered memories
            results[memory_type] = [memory for memory, _ in memory_boosts]

    def _calculate_tag_boost(self, memory: CognitiveMemory, query_lower: str) -> float:
        """
        Calculate boost score for a memory based on tag matches in query.

        Args:
            memory: Memory to check for tag matches
            query_lower: Lowercase query string

        Returns:
            Boost score (0.0 to 0.8)
        """
        if not memory.tags:
            return 0.0

        boost = 0.0
        exact_matches = 0
        query_tokens = set(query_lower.split())

        for tag in memory.tags:
            tag_lower = tag.lower()

            # Exact tag match in query tokens (highest boost)
            if tag_lower in query_tokens:
                exact_matches += 1
                boost += 0.4
            # Tag appears as substring in query (moderate boost)
            elif tag_lower in query_lower:
                boost += 0.2

        # Additional boost for multiple exact matches
        if exact_matches >= 2:
            boost += 0.1

        return min(boost, 0.8)  # Cap total boost

    def _add_tag_memories(
        self,
        query: str,
        types: list[str],
        results: dict[str, list[CognitiveMemory]],
        max_results: int,
    ) -> None:
        """Add memories that match query words as tags."""
        query_tokens = query.strip().lower().split()
        tag_memories = self.memory_storage.get_memories_by_tags(query_tokens)

        for memory in tag_memories:
            if "core" in types and len(results["core"]) < max_results // 2:
                results["core"].append(memory)
            elif (
                "peripheral" in types and len(results["peripheral"]) < max_results // 2
            ):
                results["peripheral"].append(memory)

    def _add_activation_memories(
        self,
        query_embedding: Any,
        types: list[str],
        results: dict[str, list[CognitiveMemory]],
        max_results: int,
    ) -> None:
        """Add memories from activation engine (only fill remaining slots)."""
        activation_result = self.activation_engine.activate_memories(
            context=query_embedding,
            threshold=self.config.cognitive.activation_threshold,
            max_activations=self.config.cognitive.max_activations,
        )

        if "core" in types:
            remaining_slots = max_results // 2 - len(results["core"])
            if remaining_slots > 0:
                results["core"].extend(
                    activation_result.core_memories[:remaining_slots]
                )

        if "peripheral" in types:
            remaining_slots = max_results // 2 - len(results["peripheral"])
            if remaining_slots > 0:
                results["peripheral"].extend(
                    activation_result.peripheral_memories[:remaining_slots]
                )


def create_cognitive_system(
    embedding_provider: EmbeddingProvider,
    vector_storage: VectorStorage,
    memory_storage: MemoryStorage,
    connection_graph: ConnectionGraph,
    activation_engine: ActivationEngine,
    config: SystemConfig,
) -> CognitiveMemorySystem:
    """
    Factory function to create a cognitive memory system.

    Args:
        embedding_provider: Interface for text encoding
        vector_storage: Interface for vector similarity storage
        memory_storage: Interface for memory persistence
        connection_graph: Interface for memory connections
        activation_engine: Interface for memory activation
        config: System configuration

    Returns:
        CognitiveMemorySystem: Configured system instance
    """
    return CognitiveMemorySystem(
        embedding_provider=embedding_provider,
        vector_storage=vector_storage,
        memory_storage=memory_storage,
        connection_graph=connection_graph,
        activation_engine=activation_engine,
        config=config,
    )
