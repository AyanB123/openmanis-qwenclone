class MessageToolAdapter(ToolAdapter):
    def __init__(self, messenger):
        super().__init__("message_tool", None)
        self.messenger = messenger

    def execute(self, parameters):
        # Validate message content
        if not self._validate_message(parameters["text"]):
            raise ValidationException("Invalid message content")
        
        # Send message through messenger
        return self.messenger.send_message(
            recipient=parameters["recipient"],
            text=parameters["text"],
            attachments=parameters.get("attachments", [])
        )

    def _validate_message(self, text):
        # Content filtering and validation logic
        if len(text) > 10000:
            return False
        if contains_prohibited_content(text):
            return False
        return True
```

## File Tool Adapter
```python
class FileToolAdapter(ToolAdapter):
    def __init__(self, file_system):
        super().__init__("file_tool", None)
        self.file_system = file_system

    def execute(self, parameters):
        operation = parameters["operation"]
        
        if operation == "read":
            return self._handle_read(parameters)
        elif operation == "write":
            return self._handle_write(parameters)
        elif operation == "search":
            return self._handle_search(parameters)
        else:
            raise InvalidOperationError(f"Unsupported operation: {operation}")

    def _handle_read(self, params):
        # Security validation
        if not self._validate_path(params["path"]):
            raise SecurityException("Access denied to path")
        
        # Execute read operation
        return self.file_system.read_file(
            path=params["path"],
            start_line=params.get("start_line"),
            end_line=params.get("end_line")
        )
```

## Shell Tool Adapter
```python
class ShellToolAdapter(ToolAdapter):
    def __init__(self, sandbox):
        super().__init__("shell_tool", sandbox)

    def execute(self, parameters):
        # Command validation
        if not self._validate_command(parameters["command"]):
            raise SecurityException("Command not allowed")
        
        # Execute in sandbox
        result = self.executor.run({
            "command": parameters["command"],
            "working_dir": parameters.get("working_dir", "/sandbox")
        })
        
        # Sanitize output
        return self._sanitize_output(result)

    def _validate_command(self, command):
        # Security checks for shell commands
        prohibited_patterns = ["rm -rf", "mkfs", "dd if="]
        for pattern in prohibited_patterns:
            if pattern in command:
                return False
        return True