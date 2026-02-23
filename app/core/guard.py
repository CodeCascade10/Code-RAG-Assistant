def is_code_related(query: str) -> bool:
    """
    Determines if a query is programming-related
    using expanded keyword matching.
    """

    keywords = [
        # Languages
        "python", "java", "c++", "c", "sql", "javascript",
        "typescript", "go", "rust", "kotlin", "swift",
        "html", "css", "bash",

        # OOP
        "class", "object", "inheritance", "polymorphism",
        "encapsulation", "abstraction", "constructor",
        "destructor", "interface", "abstract",

        # Core concepts
        "function", "method", "variable", "loop",
        "array", "list", "dictionary", "map",
        "set", "tuple", "string", "pointer",
        "reference", "recursion",

        # Data structures
        "stack", "queue", "linked list", "tree",
        "binary tree", "bst", "graph", "heap",
        "hashmap", "hash table",

        # Algorithms
        "algorithm", "sorting", "searching",
        "binary search", "merge sort",
        "quick sort", "dynamic programming",
        "greedy", "dfs", "bfs",

        # Errors & debugging
        "error", "exception", "bug",
        "compile", "runtime", "syntax",
        "debug", "traceback",

        # Databases
        "database", "query", "select",
        "insert", "update", "delete",
        "join", "index",

        # Web/backend
        "api", "backend", "frontend",
        "framework", "library",
        "fastapi", "django", "flask",
        "react", "node",

        # Complexity
        "time complexity", "space complexity",
        "big o", "o(n)", "o(log n)"
    ]

    query_lower = query.lower()

    return any(keyword in query_lower for keyword in keywords)