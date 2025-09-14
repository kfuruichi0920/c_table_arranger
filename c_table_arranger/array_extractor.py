"""Array data extractor and processor."""

from typing import List, Any, Tuple, Dict, Optional
from dataclasses import dataclass

from .parser import CParser, ArrayDeclaration


@dataclass
class ArrayInfo:
    """Complete information about an extracted array."""
    
    declaration: ArrayDeclaration
    data: Any
    actual_dimensions: List[int]
    max_dimensions: List[int]


class ArrayExtractor:
    """Extracts and processes array data from C source code."""
    
    def __init__(self) -> None:
        """Initialize the extractor."""
        self.parser = CParser()
    
    def extract_arrays(self, content: str) -> List[ArrayInfo]:
        """Extract all arrays from C source code."""
        declarations = self.parser.extract_array_declarations(content)
        arrays = []
        
        for decl in declarations:
            data = self.parser.extract_array_data(content, decl.variable_name)
            if data is not None:
                actual_dims, max_dims = self._analyze_dimensions(data)
                
                array_info = ArrayInfo(
                    declaration=decl,
                    data=data,
                    actual_dimensions=actual_dims,
                    max_dimensions=max_dims
                )
                arrays.append(array_info)
        
        return arrays
    
    def _analyze_dimensions(self, data: Any) -> Tuple[List[int], List[int]]:
        """Analyze the actual dimensions and maximum dimensions of nested data."""
        if not isinstance(data, list):
            return [1], [1]
        
        # Get the structure recursively
        actual_dims = self._get_actual_dimensions(data)
        max_dims = self._get_max_dimensions(data)
        
        return actual_dims, max_dims
    
    def _get_actual_dimensions(self, data: Any, level: int = 0) -> List[int]:
        """Get the actual dimensions at each level."""
        if not isinstance(data, list):
            return []
        
        dims = [len(data)]
        
        # Find dimensions of first non-empty element
        for item in data:
            if isinstance(item, list):
                sub_dims = self._get_actual_dimensions(item, level + 1)
                dims.extend(sub_dims)
                break
                
        return dims
    
    def _get_max_dimensions(self, data: Any) -> List[int]:
        """Get the maximum dimensions at each level."""
        if not isinstance(data, list):
            return []
        
        if not data:
            return [0]
        
        dims = [len(data)]
        
        # Get max dimensions from all sub-arrays
        sub_dims_list = []
        for item in data:
            if isinstance(item, list):
                sub_dims = self._get_max_dimensions(item)
                sub_dims_list.append(sub_dims)
        
        if sub_dims_list:
            # Find maximum at each level
            max_levels = max(len(sub) for sub in sub_dims_list)
            for level in range(max_levels):
                max_at_level = max(
                    (sub[level] if level < len(sub) else 0)
                    for sub in sub_dims_list
                )
                dims.append(max_at_level)
        
        return dims
    
    def normalize_array_data(self, array_info: ArrayInfo) -> List[List[Any]]:
        """Normalize array data to 2D slices for display."""
        data = array_info.data
        max_dims = array_info.max_dimensions
        
        if len(max_dims) <= 2:
            # 1D or 2D array - return as is (wrapped in list if 1D)
            if len(max_dims) == 1:
                return [data if isinstance(data, list) else [data]]
            else:
                return self._normalize_2d(data, max_dims[1])
        
        # 3D or higher - create 2D slices
        return self._create_2d_slices(data, max_dims)
    
    def _normalize_2d(self, data: Any, max_cols: int) -> List[List[Any]]:
        """Normalize 2D data to have consistent column count."""
        if not isinstance(data, list):
            return [[data]]
        
        result = []
        for row in data:
            if isinstance(row, list):
                normalized_row = row[:]
                # Pad with 'x' if needed
                while len(normalized_row) < max_cols:
                    normalized_row.append('x')
                result.append(normalized_row)
            else:
                # Single element row
                normalized_row = [row]
                while len(normalized_row) < max_cols:
                    normalized_row.append('x')
                result.append(normalized_row)
        
        return result
    
    def _create_2d_slices(self, data: Any, max_dims: List[int]) -> List[Tuple[List[int], List[List[Any]]]]:
        """Create 2D slices from multi-dimensional data."""
        if len(max_dims) < 3:
            return []
        
        slices = []
        self._extract_slices_recursive(data, [], max_dims, slices)
        return slices
    
    def _extract_slices_recursive(
        self, 
        data: Any, 
        indices: List[int], 
        max_dims: List[int], 
        slices: List[Tuple[List[int], List[List[Any]]]]
    ) -> None:
        """Recursively extract 2D slices."""
        if len(indices) == len(max_dims) - 2:
            # We've reached the level where we extract 2D slices
            slice_data = self._normalize_2d(data, max_dims[-1])
            slices.append((indices[:], slice_data))
            return
        
        if not isinstance(data, list):
            # Pad with empty data if structure is incomplete
            for i in range(max_dims[len(indices)]):
                new_indices = indices + [i]
                self._extract_slices_recursive([], new_indices, max_dims, slices)
            return
        
        # Continue recursively
        for i, item in enumerate(data):
            new_indices = indices + [i]
            self._extract_slices_recursive(item, new_indices, max_dims, slices)
        
        # Handle missing elements
        for i in range(len(data), max_dims[len(indices)]):
            new_indices = indices + [i]
            self._extract_slices_recursive([], new_indices, max_dims, slices)