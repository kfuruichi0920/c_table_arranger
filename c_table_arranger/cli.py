"""Command line interface for C Table Arranger."""

import sys
from pathlib import Path
from typing import Optional

import click

from .array_extractor import ArrayExtractor
from .formatter import ArrayFormatter, OutputFormat


@click.command()
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
@click.version_option()
def main(
    input_file: Path,
    output_format: str,
    names_only: bool,
    output: Optional[Path]
) -> None:
    """Extract and format array data from C source files.
    
    INPUT_FILE: Path to C source file to process
    """
    try:
        # Read input file
        try:
            content = input_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            content = input_file.read_text(encoding='latin-1')
        
        # Extract arrays
        extractor = ArrayExtractor()
        arrays = extractor.extract_arrays(content)
        
        if not arrays:
            click.echo("No arrays found in the input file.", err=True)
            sys.exit(1)
        
        # Format output
        format_enum = OutputFormat(output_format.lower())
        formatter = ArrayFormatter(format_enum)
        result = formatter.format_arrays(arrays, names_only)
        
        # Write output
        if output:
            output.write_text(result, encoding='utf-8')
            click.echo(f"Output written to {output}")
        else:
            click.echo(result)
    
    except FileNotFoundError:
        click.echo(f"Error: File '{input_file}' not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()