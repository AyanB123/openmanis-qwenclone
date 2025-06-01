class MessageRouter:
    def route_message(self, message: UserMessage) -> Response:
        """
        Route user messages through the system
        
        Args:
            message: User message containing text and metadata
            
        Returns:
            Response object with result and optional attachments
            
        Raises:
            SecurityException: If message content is prohibited
            ProcessingError: If message cannot be processed
        """
        
    def send_response(self, response: Response) -> None:
        """
        Send response to user interface
        
        Args:
            response: Response object containing text and attachments
        """
```

## Event Processor Interface
```python
class EventProcessor:
    def process_event(self, event: SystemEvent) -> List[Action]:
        """
        Process system events and generate actions
        
        Args:
            event: System event containing type and data
            
        Returns:
            List of actions to execute
            
        Raises:
            InvalidEventError: If event format is invalid
            ProcessingError: If event cannot be processed
        """
```

## Tool Interface Specification
```python
class ToolInterface:
    def execute(self, tool_name: str, parameters: Dict) -> Any:
        """
        Execute a tool with given parameters
        
        Args:
            tool_name: Name of tool to execute
            parameters: Dictionary of tool-specific parameters
            
        Returns:
            Tool-specific execution result
            
        Raises:
            ToolNotFoundError: If requested tool doesn't exist
            SecurityException: If operation violates security policy
            ExecutionError: If tool execution fails
        """
```

## Planner Module Interface
```python
class Planner:
    def generate_plan(self, task: str) -> ExecutionPlan:
        """
        Generate execution plan for given task
        
        Args:
            task: Description of task to accomplish
            
        Returns:
            Execution plan with pseudocode steps
            
        Raises:
            PlanningError: If plan cannot be generated
        """
```

## Security Manager Interface
```python
class SecurityManager:
    def validate_operation(self, operation: Operation) -> bool:
        """
        Validate if operation should be allowed
        
        Args:
            operation: Operation details including type and parameters
            
        Returns:
            True if operation is allowed, False otherwise
        """
```

## State Management Interface
```python
class StateManager:
    def get_state(self, component_id: str) -> Dict:
        """
        Get current state for component
        
        Args:
            component_id: Unique identifier for component
            
        Returns:
            Dictionary containing component state
        """
        
    def save_state(self, component_id: str, state: Dict) -> None:
        """
        Save state for component
        
        Args:
            component_id: Unique identifier for component
            state: Dictionary containing new state
        """