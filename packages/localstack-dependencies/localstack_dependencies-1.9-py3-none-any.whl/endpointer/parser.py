import ast
import json

def parse(source_code: str) -> tuple:
    """
    Analyze Python code and detect any form of dynamic code execution.
    Only safe built-in functions and safe modules are allowed.
    
    Returns:
        (has_violations: bool, report: dict)
    """
    # --- Safe built-in functions (no dynamic execution) ---
    safe_builtins = {
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
        'callable', 'chr', 'complex', 'divmod', 'enumerate', 'filter',
        'float', 'format', 'frozenset', 'hash', 'hex', 'int', 'isinstance',
        'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min', 'next',
        'oct', 'ord', 'pow', 'range', 'repr', 'reversed', 'round', 'set',
        'slice', 'sorted', 'str', 'sum', 'tuple', 'zip'
    }

    # --- Safe built-in modules ---
    safe_builtin_modules = {
        'math', 'string', 'fractions', 'decimal', 'itertools', 'functools',
        'operator', 'collections', 'heapq', 'array', 're', 'statistics',
        'time', 'datetime', 'enum', 'types',
        'requests',   # Added requests
        'endpointer',  # Added custom module
        'mysql'
    }

    # --- Internal blacklists ---
    token_blacklist = {
        "eval", "exec", "compile", "__import__",
        "getattr", "setattr", "delattr", "globals", "locals", "type", "super"
    }
    attribute_blacklist = {
        "__globals__", "__code__", "__class__", "__dict__"
    }

    tree = ast.parse(source_code)

    report = {
        "forbidden_calls": [],
        "forbidden_imports": [],
        "forbidden_from_imports": [],
        "blacklisted_tokens": [],
        "blacklisted_attributes": [],
        "forbidden_classes": [],
        "forbidden_metaclasses": [],
        "forbidden_lambdas": [],
        "forbidden_async_funcs": [],
        "forbidden_decorators": [],
        "forbidden_with_statements": [],
        "forbidden_comprehensions": [],
        "forbidden_globals_nonlocals": []
    }

    user_defined_funcs = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    for node in ast.walk(tree):
        # --- Function calls ---
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name not in user_defined_funcs and func_name not in safe_builtins:
                    report["forbidden_calls"].append((func_name, node.lineno))
            elif isinstance(node.func, ast.Attribute):
                attr_name = node.func.attr
                if attr_name in token_blacklist or attr_name in attribute_blacklist:
                    report["blacklisted_attributes"].append((attr_name, node.lineno))

        # --- Imports ---
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_root = alias.name.split('.')[0]
                if module_root not in safe_builtin_modules:
                    report["forbidden_imports"].append((module_root, node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_root = node.module.split('.')[0]
            if module_root not in safe_builtin_modules:
                report["forbidden_from_imports"].append((module_root, node.lineno))

        # --- Blacklisted identifiers ---
        if isinstance(node, ast.Name):
            if node.id in token_blacklist:
                report["blacklisted_tokens"].append((node.id, node.lineno))
        elif isinstance(node, ast.Attribute):
            if node.attr in token_blacklist or node.attr in attribute_blacklist:
                report["blacklisted_attributes"].append((node.attr, node.lineno))

        # --- Class / metaclass ---
        if isinstance(node, ast.ClassDef):
            report["forbidden_classes"].append((node.name, node.lineno))
            for kw in node.keywords:
                if kw.arg == "metaclass":
                    report["forbidden_metaclasses"].append((node.name, node.lineno))

        # --- Lambda ---
        if isinstance(node, ast.Lambda):
            report["forbidden_lambdas"].append(node.lineno)

        # --- Async functions ---
        if isinstance(node, ast.AsyncFunctionDef):
            report["forbidden_async_funcs"].append((node.name, node.lineno))

        # --- Decorators ---
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    dec_repr = dec.id
                elif isinstance(dec, ast.Attribute):
                    dec_repr = ast.unparse(dec)
                else:
                    dec_repr = ast.dump(dec)
                report["forbidden_decorators"].append((dec_repr, dec.lineno))

        # --- With statements ---
        if isinstance(node, (ast.With, ast.AsyncWith)):
            report["forbidden_with_statements"].append(node.lineno)

        # --- Comprehensions ---
        if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            report["forbidden_comprehensions"].append(node.lineno)

        # --- Global / Nonlocal ---
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            report["forbidden_globals_nonlocals"].append((node.names, node.lineno))

    has_violations = any(report[key] for key in report)

    return (has_violations, json.dumps(report))

# Example source code to analyze
# code_to_check = """
# import math
# import requests
# import os  # This should be flagged

# def safe_function(x):
#     return x + 1

# eval("2 + 2")  # This should be flagged
# """

# # Import the analyzer function (assume it's in the same file or imported)
# # from your_module import analyze_for_dynamic_code

# # Run the analysis
# has_errors, report = parse(code_to_check)

# errors = {}

# # Check the result
# if has_errors:
#     print("Unsafe code detected!")
#     for key, items in report.items():   
#         if items:  # Only show categories with violations
#             print(f"\n{key}:")
#             for item in items:
#                 print(f"  {item}")
#                 errors[key] = item


# else:
#     print("No unsafe code detected. Code is safe to execute.")

# print(errors)