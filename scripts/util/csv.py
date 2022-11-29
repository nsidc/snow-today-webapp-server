from pathlib import Path


def read_and_strip_before_header(*, fp: Path, header: str) -> list[str]:
    """Read input `fp` and strip all lines above the `header` line.

    Header is a string exactly matching the header line in the file.

    Return a list of strings.
    """
    with open(fp, 'r') as input_file:
        input_csv_lines = input_file.readlines()

    header_rows = [i for i, val in enumerate(input_csv_lines) if val == f'{header}\n']
    if len(header_rows) == 0:
        raise RuntimeError(f'Found no header row in {fp}. Expected "{header}"')
    if len(header_rows) > 1:
        raise RuntimeError(f'Found multiple header rows in {fp} on lines: {header_rows}')

    header_row = header_rows[0]
    stripped_csv_rows = input_csv_lines[header_row:]
    return stripped_csv_rows
