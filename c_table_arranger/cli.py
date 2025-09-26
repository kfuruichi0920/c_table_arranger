"""Command line interface for C Table Arranger."""

import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__

from .array_extractor import ArrayExtractor
from .formatter import ArrayFormatter, OutputFormat

PROGRAM_NAME = "C Table Arranger"
HELP_TEXT = (
    f"{PROGRAM_NAME} v{__version__}\n\n"
    "Extract and format array data from C source files.\n\n"
    "INPUT_FILE: Path to C source file to process\n"
)


@click.command(help=HELP_TEXT)
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--format', '-f',
    'output_format',
    type=click.Choice(['space', 'tsv', 'csv'], case_sensitive=False),
    default='space',
    help='Output format (default: space)'
)
@click.option(
    '--names-only', '-n',
    is_flag=True,
    help='Output only array names'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output file (default: stdout)'
)
@click.option(
    '--transpose', '-t',
    is_flag=True,
    help='Transpose output: [N] as 1 column, [N][M] as M rows × N columns'
)
@click.option(
    '--include-comments',
    is_flag=True,
    help='Include C comments in the formatted output'
)
@click.version_option(version=__version__, prog_name=PROGRAM_NAME)
def main(
    input_file: Path,
    output_format: str,
    names_only: bool,
    output: Optional[Path],
    transpose: bool,
    include_comments: bool
) -> None:
    """Extract and format array data from C source files.
    
    INPUT_FILE: Path to C source file to process
    """
    try:
        # 入力ファイルを読み込み、必要に応じて文字コードを切り替えます。
        try:
            content = input_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # 文字コードが不明な場合は latin-1 を後退戦略として試します。
            content = input_file.read_text(encoding='latin-1')
        
        # 抽出器を用意して、対象ファイルから配列情報を収集します。
        extractor = ArrayExtractor()
        # 配列宣言と初期化子を解析し、整形に必要な情報を得ます。
        arrays = extractor.extract_arrays(content, include_comments=include_comments)
        
        if not arrays:
            click.echo("No arrays found in the input file.", err=True)
            sys.exit(1)
        
        # 出力形式に合わせて整形処理を実行します。
        format_enum = OutputFormat(output_format.lower())
        formatter = ArrayFormatter(format_enum, transpose=transpose)
        # 整形ルールに従って表示用の文字列を作成します。
        result = formatter.format_arrays(arrays, names_only)
        
        # 出力先に応じて書き出し方法を変えます。
        if output:
            # ファイル出力時は末尾の空白を整え、LF を 1 つだけ追加します。
            clean_result = result.rstrip('\n\r\t ') + '\n'
            output.write_text(clean_result, encoding='utf-8')
            click.echo(f"Output written to {output}")
        else:
            # 端末出力では末尾の不要な空白のみ除去します。
            clean_result = result.rstrip('\n\r\t ')
            click.echo(clean_result)
    
    except FileNotFoundError:
        click.echo(f"Error: File '{input_file}' not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
