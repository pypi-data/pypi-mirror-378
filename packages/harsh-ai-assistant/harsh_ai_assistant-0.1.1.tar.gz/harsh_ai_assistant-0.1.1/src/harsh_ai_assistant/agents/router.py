def router_node(state):
    query = state["query"].lower()
    if "explain" in query:
        return "explain"
    elif "fix" in query or "debug" in query:
        return "debug"
    return "codegen"
