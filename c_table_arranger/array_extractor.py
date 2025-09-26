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
        # 解析ロジックを担当する CParser を初期化して保持します。
        self.parser = CParser()
    
    def extract_arrays(self, content: str, include_comments: bool = False) -> List[ArrayInfo]:
        """Extract all arrays from C source code."""
        # ソースコードから配列宣言の一覧を抽出します。
        declarations = self.parser.extract_array_declarations(content)
        arrays = []
        
        for decl in declarations:
            # 宣言に対応する初期化データを取得します。コメントも保持されます。
            data = self.parser.extract_array_data(
                content,
                decl.variable_name,
                include_comments=include_comments
            )
            if data is not None:
                # 次元解析はコメントを除いたデータで行い、配列構造を正確に把握します。
                analysis_target = (
                    data if not include_comments else self.parser.strip_comments_from_data(data)
                )
                if analysis_target is None:
                    analysis_target = []
                actual_dims, max_dims = self._analyze_dimensions(analysis_target)
                
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
            # スカラ値の場合は一次元として扱います。
            return [1], [1]
        
        # 入れ子構造を再帰的に調べて、実寸と最大寸法を求めます。
        actual_dims = self._get_actual_dimensions(data)
        max_dims = self._get_max_dimensions(data)
        
        return actual_dims, max_dims
    
    def _get_actual_dimensions(self, data: Any, level: int = 0) -> List[int]:
        """Get the actual dimensions at each level."""
        if not isinstance(data, list):
            return []
        
        # 現在の深さで観測された要素数を記録します。
        dims = [len(data)]
        
        # 最初に空でない要素を見つけて、その配列構造を採用します。
        for item in data:
            if isinstance(item, list):
                # 最初に現れる入れ子配列の形状のみを採用して、実際の構造を推定します。
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
        
        # 現在の段の最大要素数を格納します。
        dims = [len(data)]
        
        # すべての部分配列を走査して、各段での最大の長さを調べます。
        sub_dims_list = []
        for item in data:
            if isinstance(item, list):
                sub_dims = self._get_max_dimensions(item)
                sub_dims_list.append(sub_dims)
        
        if sub_dims_list:
            # 各段について最大値を選び、最大全体サイズを算出します。
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
            # 1 次元・2 次元はそのまま（1 次元は行としてラップして）返します。
            if len(max_dims) == 1:
                return [data if isinstance(data, list) else [data]]
            else:
                return self._normalize_2d(data, max_dims[1])
        
        # 3 次元以上は 2 次元断面の集合に変換して扱います。
        return self._create_2d_slices(data, max_dims)
    
    def _normalize_2d(self, data: Any, max_cols: int) -> List[List[Any]]:
        """Normalize 2D data to have consistent column count."""
        if not isinstance(data, list):
            return [[data]]
        
        result = []
        for row in data:
            if isinstance(row, list):
                normalized_row = []
                for cell in row:
                    normalized_row.append(cell)

                non_comment_count = sum(
                    0 if self._is_comment_string(cell) else 1
                    for cell in normalized_row
                )

                if non_comment_count == 0:
                    # コメントのみの行はそのまま出力します。
                    result.append(normalized_row if normalized_row else [''])
                    continue

                # 列数が不足する場合は 'x' でダミー値を補います。
                while non_comment_count < max_cols:
                    normalized_row.append('x')
                    non_comment_count += 1

                result.append(normalized_row)
            else:
                # コメント行はそのまま出力に残し、余分な充填は行いません。
                if self._is_comment_string(row):
                    result.append([row])
                    continue

                # スカラ要素のみの行は 1 要素のリストとして扱います。
                normalized_row = [row]
                while len(normalized_row) < max_cols:
                    normalized_row.append('x')
                result.append(normalized_row)
        
        return result
    
    def _create_2d_slices(self, data: Any, max_dims: List[int]) -> List[Tuple[List[int], List[List[Any]]]]:
        """Create 2D slices from multi-dimensional data."""
        if len(max_dims) < 3:
            return []
        
        # 2 次元スライスの一覧を蓄積します。
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
            # ここまで到達すると 2 次元断面を切り出す準備が整います。
            slice_data = self._normalize_2d(data, max_dims[-1])
            slices.append((indices[:], slice_data))
            return

        if not isinstance(data, list):
            # 想定された構造が欠けている場合は、空配列で埋めて整形を継続します。
            for i in range(max_dims[len(indices)]):
                new_indices = indices + [i]
                self._extract_slices_recursive([], new_indices, max_dims, slices)
            return

        # 残りの入れ子構造を再帰的に追跡します。
        for i, item in enumerate(data):
            new_indices = indices + [i]
            self._extract_slices_recursive(item, new_indices, max_dims, slices)

        # 構造上不足している要素を空配列で補完します。
        for i in range(len(data), max_dims[len(indices)]):
            new_indices = indices + [i]
            self._extract_slices_recursive([], new_indices, max_dims, slices)

    def _is_comment_string(self, value: Any) -> bool:
        """コメント行かどうかを判定します。"""
        if not isinstance(value, str):
            return False
        stripped = value.strip()
        return stripped.startswith('//') or stripped.startswith('/*')
