"""Output formatters for array data."""

import csv
from typing import List, Any, TextIO
from enum import Enum

from .array_extractor import ArrayInfo


class OutputFormat(Enum):
    """Supported output formats."""
    SPACE = "space"
    TSV = "tsv"
    CSV = "csv"


class ArrayFormatter:
    """Formats array data for output."""
    
    def __init__(self, format_type: OutputFormat = OutputFormat.SPACE) -> None:
        """Initialize formatter with specified format."""
        self.format_type = format_type
    
    def format_arrays(self, arrays: List[ArrayInfo], names_only: bool = False) -> str:
        """Format all arrays according to the specified format."""
        if names_only:
            return self._format_names_only(arrays)
        
        output_parts = []
        for array in arrays:
            formatted = self._format_single_array(array)
            output_parts.append(formatted)
        
        return '\n'.join(output_parts)
    
    def _format_names_only(self, arrays: List[ArrayInfo]) -> str:
        """Format array names only."""
        names = [array.declaration.variable_name for array in arrays]
        return '\n'.join(names)
    
    def _format_single_array(self, array: ArrayInfo) -> str:
        """Format a single array."""
        lines = []
        
        # Header separator
        lines.append("---")
        
        # Array declaration
        decl = array.declaration
        full_name = f"{decl.storage_class + ' ' if decl.storage_class else ''}{decl.type_name} {decl.variable_name}"
        
        # Add dimension info
        dimension_str = ''.join(f"[{dim if dim else ''}]" for dim in decl.dimensions)
        lines.append(f"Array: {full_name}{dimension_str}")
        
        # Dimension information  
        if len(array.max_dimensions) == 1:
            # For 1D arrays, show [1] if it's a single-row layout
            if isinstance(array.data, list) and len(array.data) > 0:
                lines.append(f"Dimensions: [1]")
            else:
                lines.append(f"Dimensions: [{array.max_dimensions[0]}]")
        elif len(array.max_dimensions) == 2:
            lines.append(f"Dimensions: [{array.max_dimensions[0]}][{array.max_dimensions[1]}] ({array.max_dimensions[0]} rows × {array.max_dimensions[1]} columns)")
        else:
            dims_str = ']['.join(str(d) for d in array.max_dimensions)
            lines.append(f"Dimensions: [{dims_str}] (multi-dimensional array)")
        
        lines.append("")  # Empty line
        
        # Format data based on dimensions
        if len(array.max_dimensions) <= 2:
            lines.extend(self._format_2d_data(array))
        else:
            lines.extend(self._format_multidimensional_data(array))
        
        return '\n'.join(lines)
    
    def _format_2d_data(self, array: ArrayInfo) -> List[str]:
        """Format 2D array data."""
        lines = []
        decl = array.declaration
        
        # Array name with appropriate brackets
        if len(array.max_dimensions) == 1:
            array_header = f"{decl.variable_name}[] = "
        else:
            dim_str = ']['.join(decl.dimensions[1:] if len(decl.dimensions) > 1 else [''])
            array_header = f"{decl.variable_name}[][{dim_str}] = "
        
        lines.append(array_header)
        
        # Normalize data to 2D
        from .array_extractor import ArrayExtractor
        extractor = ArrayExtractor()
        normalized_data = extractor.normalize_array_data(array)
        
        # Format based on output type
        if self.format_type == OutputFormat.SPACE:
            lines.extend(self._format_space_separated(normalized_data))
        elif self.format_type == OutputFormat.TSV:
            lines.extend(self._format_tsv(normalized_data))
        elif self.format_type == OutputFormat.CSV:
            lines.extend(self._format_csv(normalized_data))
        
        return lines
    
    def _format_multidimensional_data(self, array: ArrayInfo) -> List[str]:
        """Format multi-dimensional array data as 2D slices."""
        lines = []
        decl = array.declaration
        
        from .array_extractor import ArrayExtractor
        extractor = ArrayExtractor()
        slices = extractor._create_2d_slices(array.data, array.max_dimensions)
        
        for indices, slice_data in slices:
            # Create slice header like "a[0][1][][] ="
            indices_str = ']['.join(str(i) for i in indices)
            remaining_brackets = '[]' * (len(array.max_dimensions) - len(indices))
            slice_header = f"{decl.variable_name}[{indices_str}]{remaining_brackets} ="
            
            lines.append(slice_header)
            
            # Format slice data
            if self.format_type == OutputFormat.SPACE:
                lines.extend(self._format_space_separated(slice_data))
            elif self.format_type == OutputFormat.TSV:
                lines.extend(self._format_tsv(slice_data))
            elif self.format_type == OutputFormat.CSV:
                lines.extend(self._format_csv(slice_data))
            
            lines.append("")  # Empty line between slices
        
        return lines
    
    def _format_space_separated(self, data: List[List[Any]]) -> List[str]:
        """Format data as space-separated columns."""
        if not data:
            return []
        
        # Calculate column widths for alignment
        col_widths = []
        for row in data:
            for i, cell in enumerate(row):
                cell_str = str(cell) if cell != '' else ' '
                if i >= len(col_widths):
                    col_widths.append(len(cell_str))
                else:
                    col_widths[i] = max(col_widths[i], len(cell_str))
        
        # Format rows
        lines = []
        for row in data:
            formatted_cells = []
            for i, cell in enumerate(row):
                if cell == '':
                    # Empty cell - use spaces
                    cell_str = ' ' * col_widths[i] if i < len(col_widths) - 1 else ' '
                else:
                    cell_str = str(cell)
                    if i < len(col_widths) - 1:  # Don't pad the last column
                        cell_str = cell_str.ljust(col_widths[i])
                formatted_cells.append(cell_str)
            lines.append(' '.join(formatted_cells))
        
        return lines
    
    def _format_tsv(self, data: List[List[Any]]) -> List[str]:
        """Format data as TSV (tab-separated values)."""
        lines = []
        for row in data:
            lines.append('\t'.join(str(cell) for cell in row))
        return lines
    
    def _format_csv(self, data: List[List[Any]]) -> List[str]:
        """Format data as CSV (comma-separated values)."""
        lines = []
        for row in data:
            # Use Python's CSV module for proper escaping
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([str(cell) for cell in row])
            lines.append(output.getvalue().rstrip('\n'))
        return lines