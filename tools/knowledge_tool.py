"""
Knowledge tool adapter for Manus AI Clone
Implements secure knowledge management operations
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union

from tools.tool_interface import ToolAdapter, ToolType, ToolMetadata, ExecutionResult, SecurityContext, PermissionLevel

class KnowledgeOperationType(Enum):
    """Supported knowledge operations"""
    SEARCH = "search"
    RETRIEVE = "retrieve"
    STORE = "store"
    DELETE = "delete"
    UPDATE = "update"


class KnowledgeTool(ToolAdapter):
    """
    Adapter for knowledge management operations
    """
    def __init__(self):
        # Knowledge storage
        self.knowledge_store = {}  # type: Dict[str, Dict[str, Any]]
        
        # Configuration
        self.default_permission = PermissionLevel.READ
        self.max_document_size = 5 * 1024 * 1024  # bytes (5MB)
        
        # Security settings
        self.restricted_topics = []  # type: List[str]
        
        # Component references
        self.tool_adapter = None  # type: Optional[ToolAdapter]
        
        # Statistics
        self.usage_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "last_reset": datetime.now().isoformat()
        }

    def _validate_input(self, command: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate command and parameters
        
        Args:
            command: Command to validate
            parameters: Parameters to validate
            
        Returns:
            True if valid
        """
        # Basic validation
        if not command or not isinstance(command, str):
            return False
            
        # Parameter validation varies by command
        if command == "search_knowledge":
            return "query" in parameters
        elif command == "retrieve_document":
            return "document_id" in parameters
        elif command == "store_document":
            return "content" in parameters and "metadata" in parameters
        elif command == "update_document":
            return "document_id" in parameters and "content" in parameters
        elif command == "delete_document":
            return "document_id" in parameters
            
        return False

    def execute(self, 
               command: str,
               parameters: Dict[str, Any],
               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a knowledge operation
        
        Args:
            command: Type of knowledge operation
            parameters: Operation parameters
            context: Security context
            
        Returns:
            Operation result
        """
        # Validate input
        if not self._validate_input(command, parameters):
            return self._create_error_response("Invalid input")
            
        # Check security permissions
        if not self._check_permissions(context, command):
            return self._create_error_response("Access denied")
            
        # Handle different commands
        try:
            if command == "search_knowledge":
                return self._handle_search(parameters)
            elif command == "retrieve_document":
                return self._handle_retrieve(parameters)
            elif command == "store_document":
                return self._handle_store(parameters)
            elif command == "update_document":
                return self._handle_update(parameters)
            elif command == "delete_document":
                return self._handle_delete(parameters)
            else:
                return self._create_error_response(f"Unknown command: {command}")
        except Exception as e:
            # Log error
            self._log_operation(
                command=command,
                parameters=parameters,
                success=False,
                error=str(e)
            )
            return self._create_error_response(str(e))

    def _handle_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle knowledge search operation
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        query = parameters.get("query")
        
        # Check query restrictions
        if not self._is_query_allowed(query):
            return self._create_error_response("Query restricted")
            
        # Would implement actual search logic
        return {
            "status": "success",
            "query": query,
            "results": [],
            "timestamp": datetime.now().isoformat()
        }

    def _handle_retrieve(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle document retrieval
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        document_id = params["document_id"]
        
        # Simulate retrieving document
        content = f"// ... content of {document_id} ..."
        
        # Return result
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "document_id": document_id,
                "content": content,
                "size": len(content)
            }
        )

    def _handle_store(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle document storage operation
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        content = parameters.get("content")
        metadata = parameters.get("metadata", {})
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Add timestamp to metadata
        metadata["created_at"] = datetime.now().isoformat()
        
        # Store document
        self.knowledge_store[document_id] = {
            "content": content,
            "metadata": metadata
        }
        
        # Update statistics
        self.usage_stats["total_queries"] += 1
        self.usage_stats["successful_queries"] += 1
        
        return {
            "status": "success",
            "document_id": document_id,
            "action": "stored",
            "timestamp": datetime.now().isoformat()
        }

    def _handle_delete(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle document deletion
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        document_id = params["document_id"]
        
        # Simulate deletion
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "document_id": document_id,
                "deleted_at": datetime.now().isoformat()
            }
        )

    def _handle_update(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle document update operation
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        document_id = parameters.get("document_id")
        content = parameters.get("content")
        
        # Check if document exists
        if document_id not in self.knowledge_store:
            return self._create_error_response("Document not found")
            
        # Update document
        self.knowledge_store[document_id]["content"] = content
        
        # Update metadata
        self.knowledge_store[document_id]["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Update statistics
        self.usage_stats["total_queries"] += 1
        self.usage_stats["successful_queries"] += 1
        
        return {
            "status": "success",
            "document_id": document_id,
            "action": "updated",
            "timestamp": datetime.now().isoformat()
        }

    def search_knowledge(self, 
                       query: str,
                       source_type: Optional[str] = None,
                       max_results: int = 5,
                       context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for searching knowledge
        
        Args:
            query: Search query
            source_type: Type of knowledge source
            max_results: Maximum number of results to return
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "operation": KnowledgeOperation.SEARCH.value,
            "query": query,
            "max_results": max_results
        }
        
        if source_type:
            parameters["source_type"] = source_type
            
        # Execute through main execution path
        return self.execute(parameters, context)

    def retrieve_document(self, 
                        document_id: str,
                        context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for retrieving documents
        
        Args:
            document_id: ID of document to retrieve
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "operation": KnowledgeOperation.RETRIEVE.value,
            "document_id": document_id
        }
        
        # Execute through main execution path
        return self.execute(parameters, context)

    def store_document(self, 
                     content: str,
                     source_type: str,
                     document_id: Optional[str] = None,
                     context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for storing documents
        
        Args:
            content: Content to store
            source_type: Type of knowledge source
            document_id: Optional document ID
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "operation": KnowledgeOperation.STORE.value,
            "content": content,
            "source_type": source_type
        }
        
        if document_id:
            parameters["document_id"] = document_id
            
        # Execute through main execution path
        return self.execute(parameters, context)

    def delete_document(self, 
                      document_id: str,
                      context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for deleting documents
        
        Args:
            document_id: ID of document to delete
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "operation": KnowledgeOperation.DELETE.value,
            "document_id": document_id
        }
        
        # Execute through main execution path
        return self.execute(parameters, context)

    def update_document(self, 
                      document_id: str,
                      content: str,
                      context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for updating documents
        
        Args:
            document_id: ID of document to update
            content: New content
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "operation": KnowledgeOperation.UPDATE.value,
            "document_id": document_id,
            "content": content
        }
        
        # Execute through main execution path
        return self.execute(parameters, context)

    def set_max_query_length(self, length: int) -> None:
        """
        Set maximum allowed query length
        
        Args:
            length: Maximum length in characters
        """
        self.max_query_length = length

    def set_max_result_size(self, size: int) -> None:
        """
        Set maximum allowed result size
        
        Args:
            size: Maximum size in characters
        """
        self.max_result_size = size

    def add_indexed_source(self, source: str) -> None:
        """
        Add a new indexed source
        
        Args:
            source: Source name to add
        """
        self.indexed_sources.append(source)

    def remove_indexed_source(self, source: str) -> None:
        """
        Remove an indexed source
        
        Args:
            source: Source name to remove
        """
        if source in self.indexed_sources:
            self.indexed_sources.remove(source)