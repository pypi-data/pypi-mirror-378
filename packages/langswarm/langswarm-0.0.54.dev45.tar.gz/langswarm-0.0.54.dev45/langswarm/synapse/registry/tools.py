
class ToolRegistry:
    """
    A registry for managing agent-specific tools.
    """

    def __init__(self):
        """
        Initialize the ToolRegistry.
        """
        self.tools = {}

    def register_tool(self, tool):
        """
        Register a new tool.

        :param tool_name: Name of the tool to register.
        :param tool: A callable object or function representing the tool. 
                           It must have a `description` attribute.
        :raises ValueError: If the tool is already registered or lacks a description.
        """
        tool_name = tool.identifier
        if tool_name in self.tools:
            raise ValueError(f"Tool '{tool_name}' is already registered.")
        if not hasattr(tool, "description"):
            raise ValueError(f"Tool '{tool_name}' must have a 'description' attribute.")
        
        self.tools[tool_name] = tool

    def get_tool(self, tool_name: str):
        """
        Retrieve a tool by its name.

        :param tool_name: Name of the tool to retrieve.
        :return: The registered tool if found, otherwise None.
        """
        return self.tools.get(tool_name)

    def count_tools(self):
        """
        Count all registered tools.

        :return: A count of tools.
        """
        return len(self.tools)

    def list_tools(self):
        """
        List all registered tools.

        :return: A list of tool names and briefs.
        """
        return [f"{k} - {v.brief}" for k, v in self.tools.items()]

    def get_tools(self):
        """
        Get all registered tools in a format suitable for function calling.
        
        :return: A list of tool schemas for function calling.
        """
        tools_list = []
        for tool_name, tool in self.tools.items():
            # Try to get the tool schema for function calling
            if hasattr(tool, 'get_schema'):
                try:
                    schema = tool.get_schema()
                    tools_list.append(schema)
                except Exception:
                    # Fallback to basic schema
                    tools_list.append(self._create_basic_tool_schema(tool_name, tool))
            elif hasattr(tool, 'description'):
                # Create schema from tool attributes
                tools_list.append(self._create_basic_tool_schema(tool_name, tool))
        
        return tools_list
    
    def _create_basic_tool_schema(self, tool_name, tool):
        """Create a basic tool schema for function calling"""
        return {
            "tool": tool_name,
            "description": getattr(tool, 'description', f"Tool: {tool_name}"),
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string", 
                        "description": "Input for the tool"
                    }
                },
                "required": ["input"]
            }
        }

    def remove_tool(self, tool_name: str):
        """
        Remove a tool by its name.

        :param tool_name: Name of the tool to remove.
        :raises ValueError: If the tool does not exist.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered.")
        del self.tools[tool_name]
