#!/usr/bin/env python3
import libcst as cst

def debug_try_node():
    with open('test_defensive_try.py', 'r') as f:
        source = f.read()
    
    module = cst.parse_module(source)
    
    for node in module.body:
        if isinstance(node, cst.FunctionDef) and node.name.value == 'example1':
            function_body = node.body.body
            for statement in function_body:
                if isinstance(statement, cst.Try):
                    print("Found try statement:")
                    print("Try node:", repr(statement))
                    print("\nHas handlers:", bool(statement.handlers))
                    print("Number of handlers:", len(statement.handlers))
                    print("Handler types:")
                    for handler in statement.handlers:
                        if handler.type is None:
                            print("  except: (no type)")
                        elif isinstance(handler.type, cst.Name):
                            print(f"  except {handler.type.value}:")
                    
                    print(f"\nBody has body attribute: {hasattr(statement.body, 'body')}")
                    if hasattr(statement.body, 'body'):
                        print(f"Body length: {len(statement.body.body)}")
                        print("Body elements:")
                        for i, element in enumerate(statement.body.body):
                            print(f"  {i+1}: {type(element)}")

debug_try_node()
