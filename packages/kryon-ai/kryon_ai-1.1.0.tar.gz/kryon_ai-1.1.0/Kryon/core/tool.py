def tool(func):
    """Decorator to mark functions as agent tools."""
    func.is_tool = True
    return func
