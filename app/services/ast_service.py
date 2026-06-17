import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser
from app.utils.logger import logger

# Inisialisasi Language & Parser (Menggunakan API tree-sitter modern >= 0.21)
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

# Daftarkan parser berdasarkan ekstensi file
parsers = {
    ".py": Parser(PY_LANGUAGE),
    ".js": Parser(JS_LANGUAGE),
    ".jsx": Parser(JS_LANGUAGE),
}

def parse_code(file_name: str, code_bytes: bytes) -> dict:
    """Parse kode menggunakan Tree-sitter dan ekstrak metrik dasar."""
    ext = "." + file_name.split(".")[-1].lower()
    parser = parsers.get(ext)
    
    if not parser:
        return {"supported": False, "reason": "Unsupported extension"}
        
    tree = parser.parse(code_bytes)
    root_node = tree.root_node
    
    functions = []
    classes = []
    
    # AST Walker: Menelusuri node demi node
    def walk_tree(node):
        # Deteksi Function / Method
        if node.type in ("function_definition", "method_definition", "function_declaration"):
            for child in node.children:
                if child.type in ("identifier", "property_identifier"):
                    functions.append(child.text.decode('utf-8', errors='replace'))
                    break
        # Deteksi Class
        elif node.type in ("class_definition", "class_declaration"):
            for child in node.children:
                if child.type in ("identifier", "type_identifier"):
                    classes.append(child.text.decode('utf-8', errors='replace'))
                    break
                    
        for child in node.children:
            walk_tree(child)
            
    walk_tree(root_node)
    
    return {
        "supported": True,
        "functions": functions,
        "classes": classes,
        "lines_of_code": code_bytes.count(b'\n') + 1,
        "ast_nodes": root_node.child_count
    }