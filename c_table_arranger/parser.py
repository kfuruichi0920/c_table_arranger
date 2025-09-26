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
        # 配列宣言を検出するための正規表現です。
        self.array_pattern = re.compile(
            r'(?P<storage>(?:static|const|extern|volatile)\s+)?'
            r'(?P<type>\w+(?:_t)?)\s+'
            r'(?P<name>\w+)'
            r'(?P<dimensions>(?:\[[^\]]*\])+)\s*='
        )
        
        # コメントを除去するためのパターンを準備しておきます。
        self.comment_patterns = [
            re.compile(r'/\*.*?\*/', re.DOTALL),  # 複数行コメント
            re.compile(r'//.*?$', re.MULTILINE),  # 行コメント
        ]
    
    def remove_comments(self, content: str) -> str:
        """Remove C-style comments from content."""
        for pattern in self.comment_patterns:
            content = pattern.sub('', content)
        return content
    
    def extract_array_declarations(self, content: str) -> List[ArrayDeclaration]:
        """Extract array declarations from C source code."""
        # 宣言抽出ではコメントを除去して誤検出を防ぎます。
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
            
            # 次元情報を個別の文字列に分割します。
            dimensions = self._parse_dimensions(dims_str)
        
            # 元の宣言を再構成して保管します。
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
        # 波括弧内の数値や記号をすべて抜き出します。
        dim_pattern = re.compile(r'\[([^\]]*)\]')
        matches = dim_pattern.findall(dims_str)
        return matches
    
    def extract_array_data(
        self,
        content: str,
        array_name: str,
        include_comments: bool = False
    ) -> Optional[Any]:
        """Extract array initialization data for a specific array."""
        # 宣言と初期化子の間にコメントや空白が現れても対応できるよう、パターンを柔軟にします。
        comment_ws = (
            r'(?:'
            r'\s+'
            r'|/\*.*?\*/'
            r'|//[^\n]*?(?:\n|$)'
            r')'
        )

        # コメントを挟みながら続く宣言でも初期化子を取得できるようにマッチさせます。
        pattern = re.compile(
            rf'{re.escape(array_name)}{comment_ws}*'
            r'(?:\[[^\]]*\]' + comment_ws + r'*)*'
            r'=' + comment_ws + r'*'
            r'(\{.*?\});',
            re.DOTALL
        )

        match = pattern.search(content)
        if not match:
            return None
            
        data_str = match.group(1)
        parsed = self._parse_array_data(data_str)

        if include_comments:
            return parsed

        return self.strip_comments_from_data(parsed)
    
    def _parse_array_data(self, data_str: str) -> Any:
        """Parse array initialization data recursively."""
        data_str = data_str.strip()
        
        if not data_str.startswith('{'):
            # スカラ値で初期化されている場合は末尾のコンマ等を取り除きます。
            return data_str.rstrip(',').strip()
        
        # 最外周の波括弧を取り除き、実データ部分に絞り込みます。
        inner = data_str[1:-1].strip()
        
        if not inner:
            return []
        
        # 分割結果を保持するリストです。
        result = []
        brace_count = 0
        current_item = ""
        
        i = 0
        while i < len(inner):
            # コメントは形を保ったまま出力したいので、専用処理で回収します。
            if inner[i:i + 2] == '/*':
                end = inner.find('*/', i + 2)
                if end == -1:
                    comment = inner[i:]
                    if not current_item.strip():
                        current_item = ""
                        result.append(comment.strip())
                    else:
                        current_item += comment
                    i = len(inner)
                    break
                comment = inner[i:end + 2]
                if not current_item.strip():
                    current_item = ""
                    comment_text = comment.strip()
                    if comment_text:
                        result.append(comment_text)
                else:
                    current_item += comment
                i = end + 2
                continue
            if inner[i:i + 2] == '//':
                end = inner.find('\n', i + 2)
                if end == -1:
                    comment = inner[i:]
                    if not current_item.strip():
                        current_item = ""
                        comment_text = comment.strip()
                        if comment_text:
                            result.append(comment_text)
                    else:
                        current_item += comment
                    i = len(inner)
                    break
                comment = inner[i:end]
                if not current_item.strip():
                    current_item = ""
                    comment_text = comment.strip()
                    if comment_text:
                        result.append(comment_text)
                else:
                    current_item += comment
                i = end
                continue

            char = inner[i]
            
            if char == '{':
                # 入れ子の開始を検出したら深さを 1 増やします。
                brace_count += 1
                current_item += char
            elif char == '}':
                # 入れ子が終了したら深さを 1 減らします。
                brace_count -= 1
                current_item += char
            elif char == ',' and brace_count == 0:
                # カンマが最外層で現れたら 1 要素の終端です。
                item = current_item.strip()
                if item:
                    if item.startswith('{'):
                        result.append(self._parse_array_data(item))
                    else:
                        # 余計な前後空白だけを落として元の記述を尊重します。
                        cleaned = item.strip()
                        if cleaned and cleaned != ',':
                            result.append(cleaned)
                        else:
                            result.append('')
                else:
                    result.append('')
                current_item = ""
            else:
                current_item += char
                
            i += 1
        
        # 最後に蓄積された要素を忘れずに評価します。
        item = current_item.strip()
        if item:
            if item.startswith('{'):
                result.append(self._parse_array_data(item))
            else:
                cleaned = item.strip()
                if cleaned and cleaned != ',':
                    result.append(cleaned)

        return result

    def strip_comments_from_data(self, data: Any) -> Any:
        """コメント要素を取り除いた配列データを再帰的に生成します。"""
        if isinstance(data, list):
            stripped_list: List[Any] = []
            for item in data:
                cleaned = self.strip_comments_from_data(item)
                if cleaned is None:
                    continue
                stripped_list.append(cleaned)
            return stripped_list

        if isinstance(data, str):
            # 行コメントとブロックコメントを削除し、値だけを残します。
            without_block = re.sub(r'/\*.*?\*/', '', data, flags=re.DOTALL)
            without_line = re.sub(r'//.*', '', without_block)
            cleaned = without_line.strip()
            if not cleaned:
                return None
            return cleaned

        return data
