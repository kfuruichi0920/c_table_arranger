"""C language parser for array declarations and data extraction."""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ArrayDeclaration:
    """Represents a C array declaration."""
    
    type_name: str
    variable_name: str  
    dimensions: List[str]
    storage_class: Optional[str] = None
    full_declaration: str = ""


class CParser:
    """Parser for C language array declarations and data."""
    
    def __init__(self) -> None:
        """Initialize the parser."""
        # Pattern to match array declarations
        self.array_pattern = re.compile(
            r'(?P<storage>(?:static|const|extern|volatile)\s+)?'
            r'(?P<type>\w+(?:_t)?)\s+'
            r'(?P<name>\w+)'
            r'(?P<dimensions>(?:\[[^\]]*\])+)\s*='
        )
        
        # Pattern to remove comments
        self.comment_patterns = [
            re.compile(r'/\*.*?\*/', re.DOTALL),  # Multi-line comments
            re.compile(r'//.*?$', re.MULTILINE),  # Single-line comments
        ]
        
    def remove_comments(self, content: str) -> str:
        """Remove C-style comments from content."""
        for pattern in self.comment_patterns:
            content = pattern.sub('', content)
        return content
    
    def extract_array_declarations(self, content: str) -> List[ArrayDeclaration]:
        """Extract array declarations from C source code."""
        # Remove comments first
        clean_content = self.remove_comments(content)
        
        declarations = []
        matches = self.array_pattern.finditer(clean_content)
        
        for match in matches:
            storage = match.group('storage')
            if storage:
                storage = storage.strip()
            
            type_name = match.group('type')
            name = match.group('name')
            dims_str = match.group('dimensions')
            
            # Parse dimensions
            dimensions = self._parse_dimensions(dims_str)
            
            # Create full declaration string
            full_decl = f"{storage + ' ' if storage else ''}{type_name} {name}{dims_str}"
            
            declaration = ArrayDeclaration(
                type_name=type_name,
                variable_name=name,
                dimensions=dimensions,
                storage_class=storage,
                full_declaration=full_decl
            )
            
            declarations.append(declaration)
            
        return declarations
    
    def _parse_dimensions(self, dims_str: str) -> List[str]:
        """Parse dimension string like [AA][BB] into list."""
        # Find all [content] patterns
        dim_pattern = re.compile(r'\[([^\]]*)\]')
        matches = dim_pattern.findall(dims_str)
        return matches
    
    def extract_array_data(self, content: str, array_name: str) -> Optional[Any]:
        """Extract array initialization data for a specific array."""
        # Remove comments first
        clean_content = self.remove_comments(content)
        
        # Find the array declaration and its data
        pattern = re.compile(
            rf'{re.escape(array_name)}\s*(?:\[[^\]]*\])*\s*=\s*'
            r'(\{.*?\});',
            re.DOTALL
        )
        
        match = pattern.search(clean_content)
        if not match:
            return None
            
        data_str = match.group(1)
        return self._parse_array_data(data_str)
    
    def _parse_array_data(self, data_str: str) -> Any:
        """Parse array initialization data recursively."""
        data_str = data_str.strip()
        
        if not data_str.startswith('{'):
            # Single value - remove trailing comma and whitespace
            return data_str.rstrip(',').strip()
        
        # Remove outer braces
        inner = data_str[1:-1].strip()
        
        if not inner:
            return []
        
        # Parse nested structure
        result = []
        brace_count = 0
        current_item = ""
        
        i = 0
        while i < len(inner):
            char = inner[i]
            
            if char == '{':
                brace_count += 1
                current_item += char
            elif char == '}':
                brace_count -= 1
                current_item += char
            elif char == ',' and brace_count == 0:
                # End of current item
                item = current_item.strip()
                if item:
                    if item.startswith('{'):
                        result.append(self._parse_array_data(item))
                    else:
                        # Clean up the item - remove extra whitespace but preserve content
                        cleaned = re.sub(r'\s+', ' ', item).strip()
                        if cleaned and cleaned != ',' and cleaned:
                            result.append(cleaned)
                        elif not cleaned or cleaned == ',':
                            # Empty element - preserve as placeholder
                            result.append('')
                else:
                    # Empty between commas
                    result.append('')
                current_item = ""
            else:
                current_item += char
                
            i += 1
        
        # Handle last item
        item = current_item.strip()
        if item:
            if item.startswith('{'):
                result.append(self._parse_array_data(item))
            else:
                cleaned = re.sub(r'\s+', ' ', item).strip()
                if cleaned and cleaned != ',' and cleaned:
                    result.append(cleaned)
        
        return result