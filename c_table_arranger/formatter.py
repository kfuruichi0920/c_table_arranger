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
    
    def __init__(self, format_type: OutputFormat = OutputFormat.SPACE, transpose: bool = False) -> None:
        """Initialize formatter with specified format."""
        self.format_type = format_type
        self.transpose = transpose
    
    def format_arrays(self, arrays: List[ArrayInfo], names_only: bool = False) -> str:
        """Format all arrays according to the specified format."""
        if names_only:
            return self._format_names_only(arrays)
        
        # 個々の配列を整形した結果を蓄積します。
        output_parts = []
        for array in arrays:
            formatted = self._format_single_array(array)
            output_parts.append(formatted)

        # 配列ごとに空行を挟んで結合し、末尾の制御文字を取り除きます。
        result = '\n\n'.join(output_parts)
        result = result.rstrip('\n\r\t ')
        return result
    
    def _format_names_only(self, arrays: List[ArrayInfo]) -> str:
        """Format array names only."""
        names = [array.declaration.variable_name for array in arrays]
        return '\n'.join(names)
    
    def _format_single_array(self, array: ArrayInfo) -> str:
        """Format a single array."""
        lines = []

        # 出力ブロックの区切り線を追加します。
        lines.append("//----------------------------------------------------------------")

        # 元の宣言に近い形で配列情報を表示します。
        decl = array.declaration
        full_name = f"{decl.storage_class + ' ' if decl.storage_class else ''}{decl.type_name} {decl.variable_name}"
        dimension_str = ''.join(f"[{dim if dim else ''}]" for dim in decl.dimensions)
        lines.append(f"Array: {full_name}{dimension_str}")

        # 実際に解析した次元数と要素数を表示します。
        dims_str = ']['.join(str(d) for d in array.max_dimensions)
        lines.append(f"Dimensions: [{dims_str}]")

        lines.append("")  # 空行でヘッダーとデータを区切ります。

        # 次元数に応じて整形方法を切り替えます。
        if len(array.max_dimensions) <= 2:
            lines.extend(self._format_2d_data(array))
        else:
            lines.extend(self._format_multidimensional_data(array))

        # 個々の出力末尾に残った空行を除去して整えます。
        result_lines = []
        for line in lines:
            result_lines.append(line)

        # 末尾の空行があれば削除します。
        while result_lines and result_lines[-1] == "":
            result_lines.pop()

        # 行を結合し、末尾の制御文字を取り除いて返します。
        result = '\n'.join(result_lines)
        result = result.rstrip('\n\r\t ')
        return result
    
    def _format_2d_data(self, array: ArrayInfo) -> List[str]:
        """Format 2D array data."""
        lines = []
        decl = array.declaration
        
        # 元の配列宣言に合わせた添字を示します。
        if len(array.max_dimensions) == 1:
            array_header = f"{decl.variable_name}[] = "
        else:
            dim_str = ']['.join(decl.dimensions[1:] if len(decl.dimensions) > 1 else [''])
            array_header = f"{decl.variable_name}[][{dim_str}] = "

        lines.append(array_header)

        # 表示しやすい 2 次元構造に正規化します。
        from .array_extractor import ArrayExtractor
        extractor = ArrayExtractor()
        normalized_data = extractor.normalize_array_data(array)

        # 必要であれば転置して列・行を入れ替えます。
        if self.transpose:
            normalized_data = self._transpose_data(normalized_data, len(array.max_dimensions))

        # 指定されたフォーマットごとに整形関数を切り替えます。
        if self.format_type == OutputFormat.SPACE:
            formatted_lines = self._format_space_separated(normalized_data)
        elif self.format_type == OutputFormat.TSV:
            formatted_lines = self._format_tsv(normalized_data)
        elif self.format_type == OutputFormat.CSV:
            formatted_lines = self._format_csv(normalized_data)

        # 完全に空の行は出力から外して、見通しを保ちます。
        non_empty_lines = [line for line in formatted_lines if line.strip()]
        lines.extend(non_empty_lines)

        return lines
    
    def _format_multidimensional_data(self, array: ArrayInfo) -> List[str]:
        """Format multi-dimensional array data as 2D slices."""
        # 多次元配列は 2 次元の断面の集合として整形します。
        lines = []
        decl = array.declaration

        from .array_extractor import ArrayExtractor
        extractor = ArrayExtractor()
        slices = extractor._create_2d_slices(array.data, array.max_dimensions)
        
        for indices, slice_data in slices:
            # 例: "a[0][1][][] =" のようにスライス位置を明示します。
            indices_str = ']['.join(str(i) for i in indices)
            remaining_brackets = '[]' * (len(array.max_dimensions) - len(indices))
            slice_header = f"{decl.variable_name}[{indices_str}]{remaining_brackets} ="
            
            lines.append(slice_header)
            
            # スライス内のデータも選択された形式で整形します。
            if self.format_type == OutputFormat.SPACE:
                lines.extend(self._format_space_separated(slice_data))
            elif self.format_type == OutputFormat.TSV:
                lines.extend(self._format_tsv(slice_data))
            elif self.format_type == OutputFormat.CSV:
                lines.extend(self._format_csv(slice_data))
            
            # スライス間は空行を挟まず、緊密なレイアウトを保ちます。
        
        return lines
    
    def _transpose_data(self, data: List[List[Any]], dimensions: int) -> List[List[Any]]:
        """Transpose data based on dimension count."""
        if not data:
            return data
            
        if dimensions == 1:
            # 1 次元配列は 1 行を縦持ちに変換し、各要素を 1 行として表示します。
            if len(data) == 1:
                row_data = data[0]
                return [[item] for item in row_data]
            else:
                return data
        elif dimensions == 2:
            # 2 次元配列では M×N を N×M に転置します。
            if not data or not data[0]:
                return data
            
            # 列数の最大値を求めて、欠損列の補完に利用します。
            max_cols = max(len(row) for row in data)
            
            # 転置処理で列を行へと入れ替えます。
            transposed = []
            for col_idx in range(max_cols):
                new_row = []
                for row in data:
                    if col_idx < len(row):
                        new_row.append(row[col_idx])
                    else:
                        new_row.append('x')  # 欠損値は 'x' で補います。
                transposed.append(new_row)
            
            return transposed
        else:
            # それ以上の次元では転置を行わずにそのまま返します。
            return data
    
    def _format_space_separated(self, data: List[List[Any]]) -> List[str]:
        """Format data as space-separated columns."""
        if not data:
            return []
        
        # 各列の幅を計算して整列を保ちます。
        col_widths = []
        for row in data:
            for i, cell in enumerate(row):
                cell_str = str(cell) if cell != '' else ' '
                # セル内の改行コードを削除して 1 行表示に整えます。
                cell_str = cell_str.replace('\r', '').replace('\n', ' ')
                if i >= len(col_widths):
                    col_widths.append(len(cell_str))
                else:
                    col_widths[i] = max(col_widths[i], len(cell_str))

        # 各行を整形し、右側の余白を整えます。
        lines = []
        for row in data:
            formatted_cells = []
            for i, cell in enumerate(row):
                if cell == '':
                    # 空セルはスペースで埋め、列の配置を崩さないようにします。
                    cell_str = ' ' * col_widths[i] if i < len(col_widths) - 1 else ' '
                else:
                    cell_str = str(cell)
                    # セル内の改行コードを削除して 1 行表示に整えます。
                    cell_str = cell_str.replace('\r', '').replace('\n', ' ')
                    if i < len(col_widths) - 1:  # 最終列以外は桁数を揃えます。
                        cell_str = cell_str.ljust(col_widths[i])
                formatted_cells.append(cell_str)
            # 各行の末尾に残った余分なスペースを削除します。
            line = ' '.join(formatted_cells).rstrip()
            lines.append(line)
        
        return lines
    
    def _format_tsv(self, data: List[List[Any]]) -> List[str]:
        """Format data as TSV (tab-separated values)."""
        # タブ区切りに整形したテキストを 1 行ずつ蓄積します。
        lines = []
        for row in data:
            lines.append('\t'.join(str(cell) for cell in row))
        return lines

    def _format_csv(self, data: List[List[Any]]) -> List[str]:
        """Format data as CSV (comma-separated values)."""
        # CSV のエスケープ処理は標準ライブラリに委ねます。
        lines = []
        for row in data:
            # Python の CSV モジュールを利用して適切にエスケープします。
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([str(cell) for cell in row])
            lines.append(output.getvalue().rstrip('\n'))
        return lines
