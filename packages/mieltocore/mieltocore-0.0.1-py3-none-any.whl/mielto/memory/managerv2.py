from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from os import getenv
from textwrap import dedent
from typing import Any, Callable, Dict, List, Literal, Optional, Type, Union
import sys
from pydantic import BaseModel, Field
import asyncio
from mielto.db.base import BaseDb
from mielto.db.schemas import UserMemory
from mielto.models.base import Model
from mielto.models.message import Message
from mielto.tools.function import Function
from mielto.utils.log import log_debug, log_error, log_warning, set_log_level_to_debug, set_log_level_to_info
from mielto.utils.prompts import get_json_output_prompt
from mielto.utils.string import parse_response_model_str
from mielto.vectordb.base import VectorDb
from mielto.knowledge.document import Document
from mielto.utils.common import generate_prefix_ulid, generate_unique_hash



class MemorySearchResponse(BaseModel):
    """Model for Memory Search Response."""

    memory_ids: List[str] = Field(
        ..., description="The IDs of the memories that are most semantically similar to the query."
    )


@dataclass
class MemoryManager:
    """Memory Manager"""

    # Model used for memory management
    model: Optional[Model] = None

    # Provide the system message for the manager as a string. If not provided, a default prompt will be used.
    system_message: Optional[str] = None
    # Provide the memory capture instructions for the manager as a string. If not provided, a default prompt will be used.
    memory_capture_instructions: Optional[str] = None
    # Additional instructions for the manager
    additional_instructions: Optional[str] = None

    # Whether memories were created in the last run
    memories_updated: bool = False

    # ----- db tools ---------
    # Whether to delete memories
    delete_memories: bool = True
    # Whether to clear memories
    clear_memories: bool = True
    # Whether to update memories
    update_memories: bool = True
    # whether to add memories
    add_memories: bool = True

    # The database to store memories
    db: Optional[BaseDb] = None

    vector_db: Optional[VectorDb] = None

    debug_mode: bool = False

    def post_init(self):
        if self.vector_db and not self.vector_db.exists():
            self.vector_db.create()

    def __init__(
        self,
        model: Optional[Model] = None,
        system_message: Optional[str] = None,
        memory_capture_instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        db: Optional[BaseDb] = None,
        vector_db: Optional[VectorDb] = None,
        delete_memories: bool = True,
        update_memories: bool = True,
        add_memories: bool = True,
        clear_memories: bool = True,
        debug_mode: bool = False,
    ):
        self.model = model
        if self.model is not None and isinstance(self.model, str):
            raise ValueError("Model must be a Model object, not a string")
        self.system_message = system_message
        self.memory_capture_instructions = memory_capture_instructions
        self.additional_instructions = additional_instructions
        self.db = db
        self.vector_db = vector_db
        self.delete_memories = delete_memories
        self.update_memories = update_memories
        self.add_memories = add_memories
        self.clear_memories = clear_memories
        self.debug_mode = debug_mode
        self._tools_for_model: Optional[List[Dict[str, Any]]] = None
        self._functions_for_model: Optional[Dict[str, Function]] = None

        self.post_init()

    def get_model(self) -> Model:
        if self.model is None:
            try:
                from mielto.models.openai import OpenAIChat
            except ModuleNotFoundError as e:
                log_error(e)
                log_error(
                    "Mielto uses `openai` as the default model provider. Please provide a `model` or install `openai`."
                )
                exit(1)
            self.model = OpenAIChat(id="gpt-4o")
        return self.model

    def read_from_db(self, user_id: Optional[str] = None):
        if self.db:
            # If no user_id is provided, read all memories
            if user_id is None:
                all_memories: List[UserMemory] = self.db.get_user_memories()  # type: ignore
            else:
                all_memories = self.db.get_user_memories(user_id=user_id)  # type: ignore

            memories: Dict[str, List[UserMemory]] = {}
            for memory in all_memories:
                if memory.user_id is not None and memory.memory_id is not None:
                    memories.setdefault(memory.user_id, []).append(memory)

            return memories
        return None

    def fetch_memories(self, **filters: Optional[Dict[str, Any]]) -> Optional[UserMemory]:
        if self.db:
            return self.db.get_user_memories(**filters)
        return None

    def set_log_level(self):
        if self.debug_mode or getenv("MIELTO_DEBUG", "false").lower() == "true":
            self.debug_mode = True
            set_log_level_to_debug()
        else:
            set_log_level_to_info()

    def initialize(self, user_id: Optional[str] = None):
        self.set_log_level()

    # -*- Public Functions
    def get_user_memories(self, user_id: Optional[str] = None) -> Optional[List[UserMemory]]:
        """Get the user memories for a given user id"""
        if self.db:
            # if user_id is None:
            #     user_id = "default"
            # Refresh from the Db
            memories = self.fetch_memories(user_id=user_id)
            if memories is None:
                return []
            return memories
        else:
            log_warning("Memory Db not provided.")
            return []

    def get_user_memory(self, memory_id: str, user_id: Optional[str] = None) -> Optional[UserMemory]:
        """Get the user memory for a given user id"""
        if self.db:
            memory = self.db.get_user_memory(memory_id=memory_id, user_id=user_id)
            if memory:
                    return memory
            return None
        else:
            log_warning("Memory Db not provided.")
            return None

    def add_user_memory(
        self,
        memory: UserMemory,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Add a user memory for a given user id
        Args:
            memory (UserMemory): The memory to add
            user_id (Optional[str]): The user id to add the memory to. If not provided, the memory is added to the "default" user.
        Returns:
            str: The id of the memory
        """
        if self.db:
            if memory.memory_id is None:
                from uuid import uuid4

                memory_id = memory.memory_id or str(uuid4())
                memory.memory_id = memory_id

            if user_id is None:
                user_id = memory.user_id or "default"
            memory.user_id = user_id

            if not memory.updated_at:
                memory.updated_at = datetime.now()
            self._upsert_db_memory(memory=memory)

            if self.vector_db:
                asyncio.create_task(self._handle_vector_db_insert(memory=memory))

            return memory.memory_id

        else:
            log_warning("Memory Db not provided.")
            return None

    def replace_user_memory(
        self,
        memory_id: str,
        memory: UserMemory,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Replace a user memory for a given user id
        Args:
            memory_id (str): The id of the memory to replace
            memory (UserMemory): The memory to add
            user_id (Optional[str]): The user id to add the memory to. If not provided, the memory is added to the "default" user.
        Returns:
            str: The id of the memory
        """
        if self.db:

            if not memory.updated_at:
                memory.updated_at = datetime.now()

            memory.memory_id = memory_id
            memory.user_id = user_id or memory.user_id

            self._upsert_db_memory(memory=memory)

            if self.vector_db:
                asyncio.create_task(self._handle_vector_db_insert(memory=memory))

            return memory.memory_id
        else:
            log_warning("Memory Db not provided.")
            return None

    def clear(self) -> None:
        """Clears the memory."""
        if self.db:
            self.db.clear_memories()

    def delete_user_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Delete a user memory for a given user id
        Args:
            memory_id (str): The id of the memory to delete
            user_id (Optional[str]): The user id to delete the memory from. If not provided, the memory is deleted from the "default" user.
        """
        if self.db:
            self._delete_db_memory(memory_id=memory_id)
        else:
            log_warning("Memory DB not provided.")
            return None

    # -*- Agent Functions
    def create_user_memories(
        self,
        message: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> str:
        """Creates memories from multiple messages and adds them to the memory db."""
        self.set_log_level()

        if self.db is None:
            log_warning("MemoryDb not provided.")
            return "Please provide a db to store memories"

        if not messages and not message:
            raise ValueError("You must provide either a message or a list of messages")

        if message:
            messages = [Message(role="user", content=message)]

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid messages list")

        if user_id is None:
            user_id = "default"

        memories = self.fetch_memories(user_id=user_id)
        if memories is None:
            memories = {}

        existing_memories = memories.get(user_id, [])  # type: ignore
        existing_memories = [{"memory_id": memory.memory_id, "memory": memory.memory} for memory in existing_memories]
        response = self.create_or_update_memories(  # type: ignore
            messages=messages,
            existing_memories=existing_memories,
            user_id=user_id,
            agent_id=agent_id,
            team_id=team_id,
            db=self.db,
            update_memories=self.update_memories,
            add_memories=self.add_memories,
            workspace_id=workspace_id,
        )

        # We refresh from the DB
        self.read_from_db(user_id=user_id)
        return response

    async def acreate_user_memories(
        self,
        message: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> str:
        """Creates memories from multiple messages and adds them to the memory db."""
        self.set_log_level()

        if self.db is None:
            log_warning("MemoryDb not provided.")
            return "Please provide a db to store memories"

        if not messages and not message:
            raise ValueError("You must provide either a message or a list of messages")

        if message:
            messages = [Message(role="user", content=message)]

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid messages list")

        if user_id is None:
            user_id = "default"

        memories = self.read_from_db(user_id=user_id)
        if memories is None:
            memories = {}

        existing_memories = memories.get(user_id, [])  # type: ignore
        existing_memories = [{"memory_id": memory.memory_id, "memory": memory.memory} for memory in existing_memories]

        response = await self.acreate_or_update_memories(  # type: ignore
            messages=messages,
            existing_memories=existing_memories,
            user_id=user_id,
            agent_id=agent_id,
            team_id=team_id,
            db=self.db,
            update_memories=self.update_memories,
            add_memories=self.add_memories,
            workspace_id=workspace_id,
        )

        # We refresh from the DB
        self.read_from_db(user_id=user_id)

        return response

    def update_memory_task(self, task: str, user_id: Optional[str] = None) -> str:
        """Updates the memory with a task"""

        if not self.db:
            log_warning("MemoryDb not provided.")
            return "Please provide a db to store memories"

        if user_id is None:
            user_id = "default"

        memories = self.read_from_db(user_id=user_id)
        if memories is None:
            memories = {}

        existing_memories = memories.get(user_id, [])  # type: ignore
        existing_memories = [{"memory_id": memory.memory_id, "memory": memory.memory} for memory in existing_memories]
        # The memory manager updates the DB directly
        response = self.run_memory_task(  # type: ignore
            task=task,
            existing_memories=existing_memories,
            user_id=user_id,
            db=self.db,
            delete_memories=self.delete_memories,
            update_memories=self.update_memories,
            add_memories=self.add_memories,
            clear_memories=self.clear_memories,
        )

        # We refresh from the DB
        self.read_from_db(user_id=user_id)

        return response

    async def aupdate_memory_task(self, task: str, user_id: Optional[str] = None) -> str:
        """Updates the memory with a task"""
        self.set_log_level()

        if not self.db:
            log_warning("MemoryDb not provided.")
            return "Please provide a db to store memories"

        if user_id is None:
            user_id = "default"

        memories = self.read_from_db(user_id=user_id)
        if memories is None:
            memories = {}

        existing_memories = memories.get(user_id, [])  # type: ignore
        existing_memories = [{"memory_id": memory.memory_id, "memory": memory.memory} for memory in existing_memories]
        # The memory manager updates the DB directly
        response = await self.arun_memory_task(  # type: ignore
            task=task,
            existing_memories=existing_memories,
            user_id=user_id,
            db=self.db,
            delete_memories=self.delete_memories,
            update_memories=self.update_memories,
            add_memories=self.add_memories,
            clear_memories=self.clear_memories,
        )

        # We refresh from the DB
        self.read_from_db(user_id=user_id)

        return response

    # -*- Memory Db Functions
    def _upsert_db_memory(self, memory: UserMemory) -> str:
        """Use this function to add a memory to the database."""
        try:
            if not self.db:
                raise ValueError("Memory db not initialized")
            self.db.upsert_user_memory(memory=memory)
            return "Memory added successfully"
        except Exception as e:
            log_warning(f"Error storing memory in db: {e}")
            return f"Error adding memory: {e}"

    def _delete_db_memory(self, memory_id: str) -> str:
        """Use this function to delete a memory from the database."""
        try:
            if not self.db:
                raise ValueError("Memory db not initialized")
            self.db.delete_user_memory(memory_id=memory_id)
            return "Memory deleted successfully"
        except Exception as e:
            log_warning(f"Error deleting memory in db: {e}")
            return f"Error deleting memory: {e}"

    # -*- Utility Functions
    def search_user_memories(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        retrieval_method: Optional[Literal["last_n", "first_n", "agentic", "vector", "hybrid", "keyword", "agentic_vector", "agentic_keyword", "agentic_hybrid"]] = None,
        user_id: Optional[str] = None,
        **filters: Optional[Dict[str, Any]]
    ) -> List[UserMemory]:
        """Search through user memories using the specified retrieval method.

        Args:
            query: The search query for agentic or vector search. Required if retrieval_method is "agentic" or "vector".
            limit: Maximum number of memories to return. Defaults to self.retrieval_limit if not specified. Optional.
            retrieval_method: The method to use for retrieving memories. Defaults to self.retrieval if not specified.
                - "last_n": Return the most recent memories
                - "first_n": Return the oldest memories
                - "agentic": Return memories most similar to the query, but using an agentic approach
                - "vector": Return memories most similar to the query using vector similarity search
                - "hybrid": Return memories most similar to the query using vector similarity search and keyword search
                - "keyword": Return memories most similar to the query using keyword search
                - "agentic_vector": First perform vector search, then use agentic filtering to refine results
                - "agentic_keyword": First perform keyword search, then use agentic filtering to refine results
                - "agentic_hybrid": First perform hybrid search, then use agentic filtering to refine results
            user_id: The user to search for. Optional.

        Returns:
            A list of UserMemory objects matching the search criteria.
        """

        self.set_log_level()

        # Use default retrieval method if not specified
        retrieval_method = retrieval_method
        # Use default limit if not specified
        limit = limit

        # Delegate to specific strategy methods - each handles its own fetching
        if retrieval_method == "agentic":
            if not query:
                raise ValueError("Query is required for agentic search")
            return self._search_user_memories_agentic(user_id=user_id, query=query, limit=limit, **filters)

        elif retrieval_method in ["vector", "hybrid", "keyword"]:
            if not query:
                raise ValueError("Query is required for vector search")
            mems = self._search_user_memories_vector(user_id=user_id, query=query, limit=limit, **filters)
            return mems

        elif retrieval_method in ["agentic_vector", "agentic_keyword", "agentic_hybrid"]:
            if not query:
                raise ValueError("Query is required for agentic search")
            return self._search_user_memories_agentic_semantic(
                user_id=user_id, 
                query=query, 
                limit=limit, 
                semantic_method=retrieval_method.split("_")[1],  # Extract "vector", "keyword", or "hybrid"
                **filters
            )

        elif retrieval_method == "first_n":
            return self._get_first_n_memories(user_id=user_id, limit=limit, **filters)

        else:  # Default to last_n
            return self._get_last_n_memories(user_id=user_id, limit=limit, **filters)

    async def search_user_memories_async(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        retrieval_method: Optional[Literal["last_n", "first_n", "agentic", "vector", "hybrid", "keyword", "agentic_vector", "agentic_keyword", "agentic_hybrid"]] = None,
        user_id: Optional[str] = None,
        **filters: Optional[Dict[str, Any]]
    ) -> List[UserMemory]:
        """Search through user memories using the specified retrieval method (async version).

        Args:
            query: The search query for agentic or vector search. Required if retrieval_method is "agentic" or "vector".
            limit: Maximum number of memories to return. Defaults to self.retrieval_limit if not specified. Optional.
            retrieval_method: The method to use for retrieving memories. Defaults to self.retrieval if not specified.
                - "last_n": Return the most recent memories
                - "first_n": Return the oldest memories
                - "agentic": Return memories most similar to the query, but using an agentic approach
                - "vector": Return memories most similar to the query using vector similarity search
                - "hybrid": Return memories most similar to the query using vector similarity search and keyword search
                - "keyword": Return memories most similar to the query using keyword search
                - "agentic_vector": First perform vector search, then use agentic filtering to refine results
                - "agentic_keyword": First perform keyword search, then use agentic filtering to refine results
                - "agentic_hybrid": First perform hybrid search, then use agentic filtering to refine results
            user_id: The user to search for. Optional.

        Returns:
            A list of UserMemory objects matching the search criteria.
        """

        if user_id is None:
            user_id = "default"

        self.set_log_level()

        # Use default retrieval method if not specified
        retrieval_method = retrieval_method
        # Use default limit if not specified
        limit = limit

        # Delegate to specific strategy methods - each handles its own fetching
        if retrieval_method == "agentic":
            if not query:
                raise ValueError("Query is required for agentic search")
            return self._search_user_memories_agentic(user_id=user_id, query=query, limit=limit, **filters)

        elif retrieval_method in ["vector", "hybrid", "keyword"]:
            if not query:
                raise ValueError("Query is required for vector search")
            return await self._search_user_memories_vector_async(user_id=user_id, query=query, limit=limit, **filters)

        elif retrieval_method in ["agentic_vector", "agentic_keyword", "agentic_hybrid"]:
            if not query:
                raise ValueError("Query is required for agentic search")
            return await self._search_user_memories_agentic_semantic_async(
                user_id=user_id, 
                query=query, 
                limit=limit, 
                semantic_method=retrieval_method.split("_")[1],  # Extract "vector", "keyword", or "hybrid"
                **filters
            )

        elif retrieval_method == "first_n":
            return self._get_first_n_memories(user_id=user_id, limit=limit, **filters)

        else:  # Default to last_n
            return self._get_last_n_memories(user_id=user_id, limit=limit, **filters)

    def _get_response_format(self) -> Union[Dict[str, Any], Type[BaseModel]]:
        model = self.get_model()
        if model.supports_native_structured_outputs:
            return MemorySearchResponse

        elif model.supports_json_schema_outputs:
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": MemorySearchResponse.__name__,
                    "schema": MemorySearchResponse.model_json_schema(),
                },
            }
        else:
            return {"type": "json_object"}

    def _search_user_memories_agentic(self, user_id: str, query: str, limit: Optional[int] = None, **filters: Optional[Dict[str, Any]]) -> List[UserMemory]:
        """Search through user memories using agentic search."""
        # For agentic search, we can optimize by fetching a reasonable number of memories
        # for the AI to process, rather than all memories. This improves performance.
        # We fetch more than the limit to give the AI better context for selection.
        search_limit = (limit * 3) if limit else 100  # Fetch 3x the requested limit for better context
        
        db_filters = {
            **filters,
            'user_id': user_id,
            'limit': search_limit,
            'sort_by': 'updated_at',
            'sort_order': 'desc'  # Start with most recent memories for better relevance
        }
        
        # Fetch memories with database-level limiting for efficiency
        memories = self.fetch_memories(**db_filters)
        if memories is None:
            return []

        # fetch_memories returns a list, not a dictionary
        if not isinstance(memories, list):
            return []

        if not memories:
            return []

        model = self.get_model()
        response_format = self._get_response_format()

        log_debug("Searching for memories", center=True)

        # Use the fetched memories directly
        user_memories: List[UserMemory] = memories
        system_message_str = "Your task is to search through user memories and return the IDs of the memories that are related to the query.\n"
        system_message_str += "\n<user_memories>\n"
        for memory in user_memories:
            system_message_str += f"ID: {memory.memory_id}\n"
            system_message_str += f"Memory: {memory.memory}\n"
            if memory.topics:
                system_message_str += f"Topics: {','.join(memory.topics)}\n"
            system_message_str += "\n"
        system_message_str = system_message_str.strip()
        system_message_str += "\n</user_memories>\n\n"
        system_message_str += "REMEMBER: Only return the IDs of the memories that are related to the query."

        if response_format == {"type": "json_object"}:
            system_message_str += "\n" + get_json_output_prompt(MemorySearchResponse)  # type: ignore

        messages_for_model = [
            Message(role="system", content=system_message_str),
            Message(
                role="user",
                content=f"Return the IDs of the memories related to the following query: {query}",
            ),
        ]

        # Generate a response from the Model (includes running function calls)
        response = model.response(messages=messages_for_model, response_format=response_format)
        log_debug("Search for memories complete", center=True)

        memory_search: Optional[MemorySearchResponse] = None
        # If the model natively supports structured outputs, the parsed value is already in the structured format
        if (
            model.supports_native_structured_outputs
            and response.parsed is not None
            and isinstance(response.parsed, MemorySearchResponse)
        ):
            memory_search = response.parsed

        # Otherwise convert the response to the structured format
        if isinstance(response.content, str):
            try:
                memory_search = parse_response_model_str(response.content, MemorySearchResponse)  # type: ignore

                # Update RunOutput
                if memory_search is None:
                    log_warning("Failed to convert memory_search response to MemorySearchResponse")
                    return []
            except Exception as e:
                log_warning(f"Failed to convert memory_search response to MemorySearchResponse: {e}")
                return []

        memories_to_return = []
        if memory_search:
            for memory_id in memory_search.memory_ids:
                for memory in user_memories:
                    if memory.memory_id == memory_id:
                        memories_to_return.append(memory)
        return memories_to_return[:limit]

    def _search_user_memories_vector(self, user_id: str, query: str, limit: Optional[int] = None, **filters: Optional[Dict[str, Any]]) -> List[UserMemory]:
        """Search through user memories using vector similarity search."""
        if not self.vector_db:
            log_warning("Vector database not configured for vector search")
            return []

        try:
            log_debug("Searching memories using vector similarity", center=True)
            
            # Use vector database to search for similar memories
            # The vector_db should have memories indexed with user_id as collection_id
            search_filters = {
                **filters
            }

            workspace_id = filters.get('workspace_id')
            if workspace_id:
                del search_filters['workspace_id']
            
            # Search using vector similarity
            documents = self.vector_db.search(
                query=query,
                limit=limit or 5,
                filters=search_filters,
                collection_id=user_id,
                workspace_id=workspace_id
            )

            if not documents:
                log_debug("No similar memories found")
                return []
            
            # Convert documents back to UserMemory objects
            memories = self._process_memory_documents(documents)
            return memories
            
        except Exception as e:
            log_error(f"Error in vector search: {e}")
            return []

    def _process_memory_documents(self, documents: List[Document], user_id: str = None) -> List[UserMemory]:
        """Process the memory documents."""
        if not documents or not self.db:
            return []
        
        # Extract memory IDs from documents
        memory_ids = []
        for doc in documents:
            memory_id = doc.content_id or doc.name
            if memory_id:
                memory_ids.append(memory_id)
        
        if not memory_ids:
            log_debug("No valid memory IDs found in documents")
            return []
        
        # Fetch all memories in a single database query
        memories = self.db.get_user_memories_by_ids(memory_ids=memory_ids, user_id=user_id)
        
        log_debug(f"Found {len(memories)} similar memories", center=True)
        
        return memories


    def _search_user_memories_agentic_semantic(
        self, 
        user_id: str, 
        query: str, 
        limit: Optional[int] = None, 
        semantic_method: str = "vector",
        **filters: Optional[Dict[str, Any]]
    ) -> List[UserMemory]:
        """Search through user memories using semantic search followed by agentic filtering.
        
        This method first performs a semantic search (vector, keyword, or hybrid) to get a broader
        set of candidate memories, then uses agentic search to filter and rank them based on the
        original query for more precise results.
        
        Args:
            user_id: The user to search for
            query: The search query
            limit: Maximum number of memories to return
            semantic_method: The semantic search method to use first ("vector", "keyword", or "hybrid")
            **filters: Additional filters to apply
            
        Returns:
            A list of UserMemory objects that are both semantically similar and agentically relevant
        """
        try:
            log_debug(f"Starting agentic_{semantic_method} search", center=True)
            
            # Step 1: Perform semantic search to get candidate memories
            # We fetch more candidates than the final limit to give the agentic search better options
            semantic_limit = (limit * 3) if limit else 15  # Fetch 3x the requested limit
            
            candidate_memories = self._search_user_memories_vector(
                user_id=user_id, 
                query=query, 
                limit=semantic_limit, 
                **filters
            )
            
            if not candidate_memories:
                log_debug("No candidate memories found from semantic search")
                return []
            
            log_debug(f"Found {len(candidate_memories)} candidate memories from {semantic_method} search")
            
            # Step 2: Use agentic search to filter and rank the candidates
            # Convert candidate memories to the format expected by agentic search
            existing_memories = [
                {"memory_id": memory.memory_id, "memory": memory.memory} 
                for memory in candidate_memories
            ]
            
            # Use the agentic search logic but with the pre-filtered candidates
            model = self.get_model()
            response_format = self._get_response_format()

            log_debug("Applying agentic filtering to candidates", center=True)

            system_message_str = "Your task is to search through user memories and return the IDs of the memories that are most relevant to the query.\n"
            system_message_str += "\n<user_memories>\n"
            for memory in candidate_memories:
                system_message_str += f"ID: {memory.memory_id}\n"
                system_message_str += f"Memory: {memory.memory}\n"
                if memory.topics:
                    system_message_str += f"Topics: {','.join(memory.topics)}\n"
                system_message_str += "\n"
            system_message_str = system_message_str.strip()
            system_message_str += "\n</user_memories>\n\n"
            system_message_str += "REMEMBER: Only return the IDs of the memories that are most relevant to the query. Focus on quality over quantity."

            if response_format == {"type": "json_object"}:
                system_message_str += "\n" + get_json_output_prompt(MemorySearchResponse)  # type: ignore

            messages_for_model = [
                Message(role="system", content=system_message_str),
                Message(
                    role="user",
                    content=f"Return the IDs of the memories most relevant to the following query: {query}",
                ),
            ]

            # Generate a response from the Model
            response = model.response(messages=messages_for_model, response_format=response_format)
            log_debug("Agentic filtering complete", center=True)

            memory_search: Optional[MemorySearchResponse] = None
            # If the model natively supports structured outputs, the parsed value is already in the structured format
            if (
                model.supports_native_structured_outputs
                and response.parsed is not None
                and isinstance(response.parsed, MemorySearchResponse)
            ):
                memory_search = response.parsed

            # Otherwise convert the response to the structured format
            if isinstance(response.content, str):
                try:
                    memory_search = parse_response_model_str(response.content, MemorySearchResponse)  # type: ignore

                    # Update RunOutput
                    if memory_search is None:
                        log_warning("Failed to convert memory_search response to MemorySearchResponse")
                        return []
                except Exception as e:
                    log_warning(f"Failed to convert memory_search response to MemorySearchResponse: {e}")
                    return []

            # Step 3: Map the selected memory IDs back to UserMemory objects
            memories_to_return = []
            if memory_search:
                for memory_id in memory_search.memory_ids:
                    for memory in candidate_memories:
                        if memory.memory_id == memory_id:
                            memories_to_return.append(memory)
                            break  # Found the memory, move to next ID
            
            # Apply the final limit
            final_results = memories_to_return[:limit] if limit else memories_to_return
            
            log_debug(f"Agentic_{semantic_method} search returned {len(final_results)} memories", center=True)
            return final_results
            
        except Exception as e:
            log_error(f"Error in agentic_{semantic_method} search: {e}")
            return []

    async def _search_user_memories_agentic_semantic_async(
        self, 
        user_id: str, 
        query: str, 
        limit: Optional[int] = None, 
        semantic_method: str = "vector",
        **filters: Optional[Dict[str, Any]]
    ) -> List[UserMemory]:
        """Search through user memories using semantic search followed by agentic filtering (async version).
        
        This method first performs a semantic search (vector, keyword, or hybrid) to get a broader
        set of candidate memories, then uses agentic search to filter and rank them based on the
        original query for more precise results.
        
        Args:
            user_id: The user to search for
            query: The search query
            limit: Maximum number of memories to return
            semantic_method: The semantic search method to use first ("vector", "keyword", or "hybrid")
            **filters: Additional filters to apply
            
        Returns:
            A list of UserMemory objects that are both semantically similar and agentically relevant
        """
        try:
            log_debug(f"Starting agentic_{semantic_method} search (async)", center=True)
            
            # Step 1: Perform semantic search to get candidate memories
            # We fetch more candidates than the final limit to give the agentic search better options
            semantic_limit = (limit * 3) if limit else 15  # Fetch 3x the requested limit
            
            candidate_memories = await self._search_user_memories_vector_async(
                    user_id=user_id, 
                query=query, 
                limit=semantic_limit, 
                **filters
            )
            
            if not candidate_memories:
                log_debug("No candidate memories found from semantic search")
                return []
            
            log_debug(f"Found {len(candidate_memories)} candidate memories from {semantic_method} search")
            
            # Step 2: Use agentic search to filter and rank the candidates
            # Convert candidate memories to the format expected by agentic search
            existing_memories = [
                {"memory_id": memory.memory_id, "memory": memory.memory} 
                for memory in candidate_memories
            ]
            
            # Use the agentic search logic but with the pre-filtered candidates
            model = self.get_model()
            response_format = self._get_response_format()

            log_debug("Applying agentic filtering to candidates (async)", center=True)

            system_message_str = "Your task is to search through user memories and return the IDs of the memories that are most relevant to the query.\n"
            system_message_str += "\n<user_memories>\n"
            for memory in candidate_memories:
                system_message_str += f"ID: {memory.memory_id}\n"
                system_message_str += f"Memory: {memory.memory}\n"
                if memory.topics:
                    system_message_str += f"Topics: {','.join(memory.topics)}\n"
                system_message_str += "\n"
            system_message_str = system_message_str.strip()
            system_message_str += "\n</user_memories>\n\n"
            system_message_str += "REMEMBER: Only return the IDs of the memories that are most relevant to the query. Focus on quality over quantity."

            if response_format == {"type": "json_object"}:
                system_message_str += "\n" + get_json_output_prompt(MemorySearchResponse)  # type: ignore

            messages_for_model = [
                Message(role="system", content=system_message_str),
                Message(
                    role="user",
                    content=f"Return the IDs of the memories most relevant to the following query: {query}",
                ),
            ]

            # Generate a response from the Model
            response = await model.aresponse(messages=messages_for_model, response_format=response_format)
            log_debug("Agentic filtering complete (async)", center=True)

            memory_search: Optional[MemorySearchResponse] = None
            # If the model natively supports structured outputs, the parsed value is already in the structured format
            if (
                model.supports_native_structured_outputs
                and response.parsed is not None
                and isinstance(response.parsed, MemorySearchResponse)
            ):
                memory_search = response.parsed

            # Otherwise convert the response to the structured format
            if isinstance(response.content, str):
                try:
                    memory_search = parse_response_model_str(response.content, MemorySearchResponse)  # type: ignore

                    # Update RunOutput
                    if memory_search is None:
                        log_warning("Failed to convert memory_search response to MemorySearchResponse")
                        return []
                except Exception as e:
                    log_warning(f"Failed to convert memory_search response to MemorySearchResponse: {e}")
                    return []

            # Step 3: Map the selected memory IDs back to UserMemory objects
            memories_to_return = []
            if memory_search:
                for memory_id in memory_search.memory_ids:
                    for memory in candidate_memories:
                        if memory.memory_id == memory_id:
                            memories_to_return.append(memory)
                            break  # Found the memory, move to next ID
            
            # Apply the final limit
            final_results = memories_to_return[:limit] if limit else memories_to_return
            
            log_debug(f"Agentic_{semantic_method} search returned {len(final_results)} memories (async)", center=True)
            return final_results
            
        except Exception as e:
            log_error(f"Error in agentic_{semantic_method} search (async): {e}")
            return []

    async def _search_user_memories_vector_async(self, user_id: str, query: str, limit: Optional[int] = None, **filters: Optional[Dict[str, Any]]) -> List[UserMemory]:
        """Search through user memories using vector similarity search (async version)."""
        if not self.vector_db:
            log_warning("Vector database not configured for vector search")
            return []

        try:
            log_debug("Searching memories using vector similarity (async)", center=True)
            
            # Use vector database to search for similar memories
            search_filters = {
                **filters
            }

            workspace_id = filters.get('workspace_id')
            if workspace_id:
                del search_filters['workspace_id']
            
            # Search using async vector similarity
            documents = await self.vector_db.async_search(
                query=query,
                limit=limit or 10,
                filters=search_filters,
                collection_id=user_id,
                workspace_id=filters.get('workspace_id')
            )

            if not documents:
                log_debug("No similar memories found")
                return []
            
            # Convert documents back to UserMemory objects
            memories = self._process_memory_documents(documents)
            return memories
            
        except Exception as e:
            log_error(f"Error in async vector search: {e}")
            return []

    def _get_last_n_memories(self, user_id: str, limit: Optional[int] = 10, **filters: Optional[Dict[str, Any]]) -> List[UserMemory]:
        """Get the most recent user memories.

        Args:
            user_id: The user ID to fetch memories for
            limit: Maximum number of memories to return.
            **filters: Additional filters to apply to the memory fetch

        Returns:
            A list of the most recent UserMemory objects.
        """
        # Apply limit and sorting directly in the database query for efficiency
        db_filters = {
            **filters,
            'user_id': user_id,
            'limit': limit,
            'sort_by': 'updated_at',
            'sort_order': 'desc'  # Newest first
        }
        
        # Fetch memories with database-level sorting and limiting
        memories = self.fetch_memories(**db_filters)
        if memories is None:
            return []

        # fetch_memories returns a list, not a dictionary
        if not isinstance(memories, list):
            return []

        return memories


    def _get_first_n_memories(self, user_id: str, limit: Optional[int] = None, **filters: Optional[Dict[str, Any]]) -> List[UserMemory]:
        """Get the oldest user memories.

        Args:
            user_id: The user ID to fetch memories for
            limit: Maximum number of memories to return.
            **filters: Additional filters to apply to the memory fetch

        Returns:
            A list of the oldest UserMemory objects.
        """
        # Apply limit and sorting directly in the database query for efficiency
        db_filters = {
            **filters,
            'user_id': user_id,
            'limit': limit,
            'sort_by': 'updated_at',
            'sort_order': 'asc'  # Oldest first
        }
        
        # Fetch memories with database-level sorting and limiting
        memories = self.fetch_memories(**db_filters)
        if memories is None:
            return []

        # fetch_memories returns a list, not a dictionary
        if not isinstance(memories, list):
            return []

        return memories


    # --Memory Manager Functions--
    def determine_tools_for_model(self, tools: List[Callable]) -> None:
        # Have to reset each time, because of different user IDs
        self._tools_for_model = []
        self._functions_for_model = {}

        for tool in tools:
            try:
                function_name = tool.__name__
                if function_name not in self._functions_for_model:
                    func = Function.from_callable(tool, strict=True)  # type: ignore
                    func.strict = True
                    self._functions_for_model[func.name] = func
                    self._tools_for_model.append({"type": "function", "function": func.to_dict()})
                    log_debug(f"Added function {func.name}")
            except Exception as e:
                log_warning(f"Could not add function {tool}: {e}")

    def get_system_message(
        self,
        existing_memories: Optional[List[Dict[str, Any]]] = None,
        enable_delete_memory: bool = True,
        enable_clear_memory: bool = True,
        enable_update_memory: bool = True,
        enable_add_memory: bool = True,
    ) -> Message:
        if self.system_message is not None:
            return Message(role="system", content=self.system_message)

        memory_capture_instructions = self.memory_capture_instructions or dedent("""\
            Memories should include details that could personalize ongoing interactions with the user, such as:
              - Personal facts: name, age, occupation, location, interests, preferences, etc.
              - Significant life events or experiences shared by the user
              - Important context about the user's current situation, challenges or goals
              - What the user likes or dislikes, their opinions, beliefs, values, etc.
              - Any other details that provide valuable insights into the user's personality, perspective or needs\
        """)

        # -*- Return a system message for the memory manager
        system_prompt_lines = [
            "You are a MemoryConnector that is responsible for manging key information about the user. "
            "You will be provided with a criteria for memories to capture in the <memories_to_capture> section and a list of existing memories in the <existing_memories> section.",
            "",
            "## When to add or update memories",
            "- Your first task is to decide if a memory needs to be added, updated, or deleted based on the user's message OR if no changes are needed.",
            "- If the user's message meets the criteria in the <memories_to_capture> section and that information is not already captured in the <existing_memories> section, you should capture it as a memory.",
            "- If the users messages does not meet the criteria in the <memories_to_capture> section, no memory updates are needed.",
            "- If the existing memories in the <existing_memories> section capture all relevant information, no memory updates are needed.",
            "",
            "## How to add or update memories",
            "- If you decide to add a new memory, create memories that captures key information, as if you were storing it for future reference.",
            "- Memories should be a brief, third-person statements that encapsulate the most important aspect of the user's input, without adding any extraneous information.",
            "  - Example: If the user's message is 'I'm going to the gym', a memory could be `John Doe goes to the gym regularly`.",
            "  - Example: If the user's message is 'My name is John Doe', a memory could be `User's name is John Doe`.",
            "- Don't make a single memory too long or complex, create multiple memories if needed to capture all the information.",
            "- Don't repeat the same information in multiple memories. Rather update existing memories if needed.",
            "- If a user asks for a memory to be updated or forgotten, remove all reference to the information that should be forgotten. Don't say 'The user used to like ...`",
            "- When updating a memory, append the existing memory with new information rather than completely overwriting it.",
            "- When a user's preferences change, update the relevant memories to reflect the new preferences but also capture what the user's preferences used to be and what has changed.",
            "",
            "## Criteria for creating memories",
            "Use the following criteria to determine if a user's message should be captured as a memory.",
            "",
            "<memories_to_capture>",
            memory_capture_instructions,
            "</memories_to_capture>",
            "",
            "## Updating memories",
            "You will also be provided with a list of existing memories in the <existing_memories> section. You can:",
            "  1. Decide to make no changes.",
        ]
        if enable_add_memory:
            system_prompt_lines.append("  2. Decide to add a new memory, using the `add_memory` tool.")
        if enable_update_memory:
            system_prompt_lines.append("  3. Decide to update an existing memory, using the `update_memory` tool.")
        if enable_delete_memory:
            system_prompt_lines.append("  4. Decide to delete an existing memory, using the `delete_memory` tool.")
        if enable_clear_memory:
            system_prompt_lines.append("  5. Decide to clear all memories, using the `clear_memory` tool.")

        system_prompt_lines += [
            "You can call multiple tools in a single response if needed. ",
            "Only add or update memories if it is necessary to capture key information provided by the user.",
        ]

        if existing_memories and len(existing_memories) > 0:
            system_prompt_lines.append("\n<existing_memories>")
            for existing_memory in existing_memories:
                system_prompt_lines.append(f"ID: {existing_memory['memory_id']}")
                system_prompt_lines.append(f"Memory: {existing_memory['memory']}")
                system_prompt_lines.append("")
            system_prompt_lines.append("</existing_memories>")

        if self.additional_instructions:
            system_prompt_lines.append(self.additional_instructions)

        return Message(role="system", content="\n".join(system_prompt_lines))

    def create_or_update_memories(
        self,
        messages: List[Message],
        existing_memories: List[Dict[str, Any]],
        user_id: str,
        db: BaseDb,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        update_memories: bool = True,
        add_memories: bool = True,
    ) -> str:
        if self.model is None:
            log_error("No model provided for memory manager")
            return "No model provided for memory manager"

        log_debug("MemoryManager Start", center=True)

        if len(messages) == 1:
            input_string = messages[0].get_content_string()
        else:
            input_string = f"{', '.join([m.get_content_string() for m in messages if m.role == 'user' and m.content])}"

        model_copy = deepcopy(self.model)
        # Update the Model (set defaults, add logit etc.)
        self.determine_tools_for_model(
            self._get_db_tools(
                user_id,
                db,
                input_string,
                agent_id=agent_id,
                team_id=team_id,
                enable_add_memory=add_memories,
                enable_update_memory=update_memories,
                enable_delete_memory=False,
                enable_clear_memory=False,
                workspace_id=workspace_id,
            ),
        )

        # Prepare the List of messages to send to the Model
        messages_for_model: List[Message] = [
            self.get_system_message(
                existing_memories=existing_memories,
                enable_update_memory=update_memories,
                enable_add_memory=add_memories,
                enable_delete_memory=False,
                enable_clear_memory=False,
            ),
            *messages,
        ]

        # Generate a response from the Model (includes running function calls)
        response = model_copy.response(
            messages=messages_for_model, tools=self._tools_for_model, functions=self._functions_for_model
        )

        if response.tool_calls is not None and len(response.tool_calls) > 0:
            self.memories_updated = True
        log_debug("MemoryManager End", center=True)

        return response.content or "No response from model"

    async def acreate_or_update_memories(
        self,
        messages: List[Message],
        existing_memories: List[Dict[str, Any]],
        user_id: str,
        db: BaseDb,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        update_memories: bool = True,
        add_memories: bool = True,
        workspace_id: Optional[str] = None,
    ) -> str:
        if self.model is None:
            log_error("No model provided for memory manager")
            return "No model provided for memory manager"

        log_debug("MemoryManager Start", center=True)

        if len(messages) == 1:
            input_string = messages[0].get_content_string()
        else:
            input_string = f"{', '.join([m.get_content_string() for m in messages if m.role == 'user' and m.content])}"

        model_copy = deepcopy(self.model)
        # Update the Model (set defaults, add logit etc.)
        self.determine_tools_for_model(
            self._get_db_tools(
                user_id,
                db,
                input_string,
                agent_id=agent_id,
                team_id=team_id,
                enable_add_memory=add_memories,
                enable_update_memory=update_memories,
                enable_delete_memory=False,
                enable_clear_memory=False,
                workspace_id=workspace_id,
            ),
        )

        # Prepare the List of messages to send to the Model
        messages_for_model: List[Message] = [
            self.get_system_message(
                existing_memories=existing_memories,
                enable_update_memory=update_memories,
                enable_add_memory=add_memories,
                enable_delete_memory=False,
                enable_clear_memory=False,
            ),
            *messages,
        ]

        # Generate a response from the Model (includes running function calls)
        response = await model_copy.aresponse(
            messages=messages_for_model, tools=self._tools_for_model, functions=self._functions_for_model
        )

        if response.tool_calls is not None and len(response.tool_calls) > 0:
            self.memories_updated = True
        log_debug("MemoryManager End", center=True)

        return response.content or "No response from model"

    ## Memory Vector DB Functions

    async def _handle_vector_db_insert(self, memory: UserMemory, upsert: bool = True):
        if not self.vector_db:
            log_error("No vector database configured")
            # self._update_content(memory)
            return
        
        content_hash = generate_unique_hash(f"{memory.memory}_{memory.user_id}_{memory.workspace_id}")

        metadata = memory.metadata or {
            "source": "memory",
            "user_id": memory.user_id,
            "topics": memory.topics
        }

        if memory.topics:
            metadata["topics"] = memory.topics

        if memory.agent_id:
            metadata["agent_id"] = memory.agent_id

        if memory.team_id:
            metadata["team_id"] = memory.team_id

        if memory.user_id:
            metadata["user_id"] = memory.user_id

        if memory.workspace_id:
            metadata["workspace_id"] = memory.workspace_id
    
        documents = [
            Document(
                content=memory.memory, 
                meta_data=metadata, 
                content_id=memory.memory_id, 
                name=memory.memory_id,
                id=generate_prefix_ulid("doc"),
                content_origin="memory",
                size=int(sys.getsizeof(memory.memory))
             )
        ]

        if self.vector_db.upsert_available() and upsert:
            try:
                await self.vector_db.async_upsert(content_hash, documents, metadata, collection_id=memory.user_id, workspace_id=memory.workspace_id)
            except Exception as e:
                log_error(f"Error upserting document: {e}")
                # content.status = ContentStatus.FAILED
                # content.status_message = "Could not upsert embedding"
                # self._update_content(content)
                return
        else:
            try:
                await self.vector_db.async_insert(
                    content_hash, 
                    documents=documents, 
                    filters=metadata,
                    collection_id=memory.user_id,
                    workspace_id=memory.workspace_id
                )
            except Exception as e:
                log_error(f"Error inserting document: {e}")
                # content.status = ContentStatus.FAILED
                # content.status_message = "Could not insert embedding"
                # self._update_content(content)
                return

        # content.status = ContentStatus.COMPLETED
        # self._update_content(content)
    
    ## Memory Db Functions
    def run_memory_task(
        self,
        task: str,
        existing_memories: List[Dict[str, Any]],
        user_id: str,
        db: BaseDb,
        delete_memories: bool = True,
        update_memories: bool = True,
        add_memories: bool = True,
        clear_memories: bool = True,
    ) -> str:
        if self.model is None:
            log_error("No model provided for memory manager")
            return "No model provided for memory manager"

        log_debug("MemoryManager Start", center=True)

        model_copy = deepcopy(self.model)
        # Update the Model (set defaults, add logit etc.)
        self.determine_tools_for_model(
            self._get_db_tools(
                user_id,
                db,
                task,
                enable_delete_memory=delete_memories,
                enable_clear_memory=clear_memories,
                enable_update_memory=update_memories,
                enable_add_memory=add_memories,
            ),
        )

        # Prepare the List of messages to send to the Model
        messages_for_model: List[Message] = [
            self.get_system_message(
                existing_memories,
                enable_delete_memory=delete_memories,
                enable_clear_memory=clear_memories,
                enable_update_memory=update_memories,
                enable_add_memory=add_memories,
            ),
            # For models that require a non-system message
            Message(role="user", content=task),
        ]

        # Generate a response from the Model (includes running function calls)
        response = model_copy.response(
            messages=messages_for_model, tools=self._tools_for_model, functions=self._functions_for_model
        )

        if response.tool_calls is not None and len(response.tool_calls) > 0:
            self.memories_updated = True
        log_debug("MemoryManager End", center=True)

        return response.content or "No response from model"

    async def arun_memory_task(
        self,
        task: str,
        existing_memories: List[Dict[str, Any]],
        user_id: str,
        db: BaseDb,
        delete_memories: bool = True,
        clear_memories: bool = True,
        update_memories: bool = True,
        add_memories: bool = True,
    ) -> str:
        if self.model is None:
            log_error("No model provided for memory manager")
            return "No model provided for memory manager"

        log_debug("MemoryManager Start", center=True)

        model_copy = deepcopy(self.model)
        # Update the Model (set defaults, add logit etc.)
        self.determine_tools_for_model(
            self._get_db_tools(
                user_id,
                db,
                task,
                enable_delete_memory=delete_memories,
                enable_clear_memory=clear_memories,
                enable_update_memory=update_memories,
                enable_add_memory=add_memories,
            ),
        )

        # Prepare the List of messages to send to the Model
        messages_for_model: List[Message] = [
            self.get_system_message(
                existing_memories,
                enable_delete_memory=delete_memories,
                enable_clear_memory=clear_memories,
                enable_update_memory=update_memories,
                enable_add_memory=add_memories,
            ),
            # For models that require a non-system message
            Message(role="user", content=task),
        ]

        # Generate a response from the Model (includes running function calls)
        response = await model_copy.aresponse(
            messages=messages_for_model, tools=self._tools_for_model, functions=self._functions_for_model
        )

        if response.tool_calls is not None and len(response.tool_calls) > 0:
            self.memories_updated = True
        log_debug("MemoryManager End", center=True)

        return response.content or "No response from model"

    # -*- DB Functions
    def _get_db_tools(
        self,
        user_id: str,
        db: BaseDb,
        input_string: str,
        enable_add_memory: bool = True,
        enable_update_memory: bool = True,
        enable_delete_memory: bool = True,
        enable_clear_memory: bool = True,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Callable]:
        def add_memory(memory: str, topics: Optional[List[str]] = None) -> str:
            """Use this function to add a memory to the database.
            Args:
                memory (str): The memory to be added.
                topics (Optional[List[str]]): The topics of the memory (e.g. ["name", "hobbies", "location"]).
            Returns:
                str: A message indicating if the memory was added successfully or not.
            """
            from uuid import uuid4

            from mielto.db.base import UserMemory

            try:
                memory_id = generate_prefix_ulid("mem")
                db.upsert_user_memory(
                    UserMemory(
                        memory_id=memory_id,
                        user_id=user_id,
                        agent_id=agent_id,
                        team_id=team_id,
                        memory=memory,
                        topics=topics,
                        input=input_string,
                        workspace_id=workspace_id,
                    )
                )
                log_debug(f"Memory added: {memory_id}")
                return "Memory added successfully"
            except Exception as e:
                log_warning(f"Error storing memory in db: {e}")
                return f"Error adding memory: {e}"

        def update_memory(memory_id: str, memory: str, topics: Optional[List[str]] = None) -> str:
            """Use this function to update an existing memory in the database.
            Args:
                memory_id (str): The id of the memory to be updated.
                memory (str): The updated memory.
                topics (Optional[List[str]]): The topics of the memory (e.g. ["name", "hobbies", "location"]).
            Returns:
                str: A message indicating if the memory was updated successfully or not.
            """
            from mielto.db.base import UserMemory

            try:
                db.upsert_user_memory(
                    UserMemory(
                        memory_id=memory_id,
                        memory=memory,
                        topics=topics,
                        input=input_string,
                        workspace_id=workspace_id,
                    )
                )
                log_debug("Memory updated")
                return "Memory updated successfully"
            except Exception as e:
                log_warning(f"Error storing memory in db: {e}")
                return f"Error adding memory: {e}"

        def delete_memory(memory_id: str) -> str:
            """Use this function to delete a single memory from the database.
            Args:
                memory_id (str): The id of the memory to be deleted.
            Returns:
                str: A message indicating if the memory was deleted successfully or not.
            """
            try:
                db.delete_user_memory(memory_id=memory_id)
                log_debug("Memory deleted")
                return "Memory deleted successfully"
            except Exception as e:
                log_warning(f"Error deleting memory in db: {e}")
                return f"Error deleting memory: {e}"

        def clear_memory() -> str:
            """Use this function to remove all (or clear all) memories from the database.

            Returns:
                str: A message indicating if the memory was cleared successfully or not.
            """
            db.clear_memories()
            log_debug("Memory cleared")
            return "Memory cleared successfully"

        functions: List[Callable] = []
        if enable_add_memory:
            functions.append(add_memory)
        if enable_update_memory:
            functions.append(update_memory)
        if enable_delete_memory:
            functions.append(delete_memory)
        if enable_clear_memory:
            functions.append(clear_memory)
        return functions
