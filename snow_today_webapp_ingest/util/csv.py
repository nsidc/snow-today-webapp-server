from pathlib import Path


def read_csv_and_strip_before_header(
    *,
    fp: Path,
    header: str,
) -> tuple[str, str]:
    """Read input `fp` and strip all lines above the `header` line.

    `header` is meant to represent the column header of a CSV file. We look for an
    exact match to this string to identify the header, so functionally this can be any
    line in the file; if you provide a non-header line though, your output may not be
    readable as CSV!

    Return a tuple including two strings: The first is the CSV data, and the
    second is the stripped data from above the header.
    """
    with open(fp) as input_file:
        input_csv_lines = input_file.readlines()

    header_row_indices = [
        i for i, val in enumerate(input_csv_lines) if val == f'{header}\n'
    ]
    if len(header_row_indices) == 0:
        raise RuntimeError(f'Found no header row in {fp}. Expected "{header}"')
    if len(header_row_indices) > 1:
        raise RuntimeError(
            f'Found multiple header rows in {fp} on lines: {header_row_indices}'
        )
    header_row_index = header_row_indices[0]

    csv_str = "".join(input_csv_lines[header_row_index:])
    stripped_str = "".join(input_csv_lines[:header_row_index])
    return csv_str, stripped_str
