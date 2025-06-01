"""
Knowledge tool adapter for Manus AI Clone
Implements secure knowledge management operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from core.event_processor import EventType
from tools.tool_interface import ToolAdapter, ToolType, ToolMetadata, ExecutionResult, SecurityContext, PermissionLevel

class KnowledgeOperation(Enum):
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
        # Create tool metadata
        metadata = ToolMetadata(
            name="knowledge_tool",
            description="Secure knowledge management with access control",
            version="1.0.0",
            author="Manus AI Clone Team",
            license_type="MIT"
        )
        
        # Initialize base class
        super().__init__(
            tool_type=ToolType.KNOWLEDGE,
            metadata=metadata,
            permission_level=PermissionLevel.READ
        )
        
        # Knowledge-specific configuration
        self.max_query_length = 1000
        self.max_result_size = 10 * 1024 * 1024  # bytes (10MB)
        self.indexed_sources = ["internal_knowledge", "external_docs", "research_papers"]

    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate knowledge operation parameters
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameter
        if "operation" not in parameters:
            return False
            
        # Validate operation type
        try:
            operation = KnowledgeOperation(parameters["operation"])
        except ValueError:
            return False
            
        # Operation-specific validation
        if operation == KnowledgeOperation.SEARCH:
            return "query" in parameters
            
        elif operation == KnowledgeOperation.RETRIEVE:
            return "document_id" in parameters
            
        elif operation == KnowledgeOperation.STORE:
            return all(key in parameters for key in ["content", "source_type"])
            
        elif operation == KnowledgeOperation.DELETE:
            return "document_id" in parameters
            
        elif operation == KnowledgeOperation.UPDATE:
            return all(key in parameters for key in ["document_id", "content"])
            
        return True

    def _execute_direct(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Execute knowledge operation based on parameters
        
        Args:
            parameters: Dictionary containing operation details
            
        Returns:
            Execution result
        """
        try:
            # Parse operation
            operation = KnowledgeOperation(parameters["operation"])
            
            # Execute operation
            if operation == KnowledgeOperation.SEARCH:
                return self._handle_search(parameters)
                
            elif operation == KnowledgeOperation.RETRIEVE:
                return self._handle_retrieve(parameters)
                
            elif operation == KnowledgeOperation.STORE:
                return self._handle_store(parameters)
                
            elif operation == KnowledgeOperation.DELETE:
                return self._handle_delete(parameters)
                
            elif operation == KnowledgeOperation.UPDATE:
                return self._handle_update(parameters)
                
            # Unknown operation
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=False,
                output=None,
                error=f"Unsupported operation: {operation.value}"
            )
            
        except Exception as e:
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=False,
                output=None,
                error=str(e)
            )

    def _handle_search(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle knowledge search operation
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        query = params["query"]
        source = params.get("source_type")
        max_results = params.get("max_results", 5)
        
        # Validate query length
        if len(query) > self.max_query_length:
            raise ValueError(f"Query exceeds maximum length ({self.max_query_length} characters)")
            
        # Simulate search results
        results = [
            {
                "document_id": f"doc_{i}",
                "title": f"Document {i} Title",
                "score": 1.0 - (i * 0.1),
                "preview": f"... document {i} preview ..."
            } for i in range(max_results)
        ]
        
        # Return result
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "query": query,
                "source": source or "all",
                "results": results,
                "total": len(results)
            }
        )

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

    def _handle_store(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle document storage
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        content = params["content"]
        source_type = params["source_type"]
        document_id = params.get("document_id", str(uuid.uuid4()))
        
        # Validate content size
        if len(content) > self.max_result_size:
            raise ValueError(f"Content exceeds maximum size ({self.max_result_size} characters)")
            
        # Validate source type
        if source_type not in self.indexed_sources:
            raise ValueError(f"Source type {source_type} not allowed")
            
        # Simulate storing document
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "document_id": document_id,
                "stored_chars": len(content),
                "source_type": source_type
            }
        )

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

    def _handle_update(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle document update
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        document_id = params["document_id"]
        content = params["content"]
        
        # Validate content size
        if len(content) > self.max_result_size:
            raise ValueError(f"Content exceeds maximum size ({self.max_result_size} characters)")
            
        # Simulate update
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "document_id": document_id,
                "updated_chars": len(content),
                "timestamp": datetime.now().isoformat()
            }
        )

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