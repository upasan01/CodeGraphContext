import ast
from collections import defaultdict

# --- 1. Graph Builder Class ---
class CallGraphBuilder(ast.NodeVisitor):
    """
    Analyzes Python code to find function definitions and their calls.
    The resulting graph shows: {caller_function: [list_of_called_functions]}
    """
    def __init__(self):
        # Graph structure: {caller: [callees]}
        self.graph = defaultdict(set)
        # Stack to track the current function scope
        self.current_function = None

    # --- 2. Visitor Methods ---

    # Called when visiting a function definition
    def visit_FunctionDef(self, node):
        # 1. Store the previous function scope (if nested)
        parent_function = self.current_function
        # 2. Set the new current scope
        self.current_function = node.name
        
        # Initialize the set for this function if it doesn't exist
        if node.name not in self.graph:
             self.graph[node.name] = set()
        
        # Ensure the graph handles non-function-level calls (e.g., top-level)
        self.generic_visit(node)
        
        # 3. Restore the previous scope
        self.current_function = parent_function

    # Called when visiting a function call
    def visit_Call(self, node):
        # Check if the call is a simple Name (like 'func()')
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
            
            # If we are inside a function, record the call
            if self.current_function:
                self.graph[self.current_function].add(callee_name)
            # If at the top level, use a special key (e.g., 'TOP_LEVEL')
            else:
                self.graph['TOP_LEVEL'].add(callee_name)
        
        # Ensure we continue visiting nested calls (e.g., f(g(x)))
        self.generic_visit(node)
        

# --- 3. Example Usage ---

# The code we want to analyze
CODE_TO_ANALYZE = """
def main_entry():
    # Calls another function
    data = fetch_data("config")
    
    # Calls another function
    process_data(data)
    
    # Calls a built-in
    print("Done.") 

def fetch_data(key):
    # Calls an external library function (or built-in)
    return open(key + ".txt").read()

def process_data(d):
    # This function doesn't call others defined here
    pass

# Top-level execution call
main_entry()
"""

# --- 4. Execution ---
def analyze_code(code):
    """Parses the code and prints the resulting call graph."""
    try:
        # Parse the code into an Abstract Syntax Tree
        tree = ast.parse(code)
        
        # Create and run the visitor
        builder = CallGraphBuilder()
        builder.visit(tree)
        
        # Print the results
        print("--- Call Graph Context ---")
        for caller, callees in builder.graph.items():
            print(f"[{caller}] calls: {', '.join(sorted(list(callees)))}")
            
    except Exception as e:
        print(f"Error parsing code: {e}")

if __name__ == "__main__":
    analyze_code(CODE_TO_ANALYZE)
