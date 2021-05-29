import re
import sys

"""Used to find prefixes like '&31 '"""
prefix_pattern = r"^(&[\d]*\ )"
"""Used to find all kind of line breaks"""
linebreak_pattern = r"(\r\n|\r|\n)$"


def validate_lines(old_lines: [str], new_lines: [str], file_name_old: str = 'old file',
                   file_name_new: str = 'new file'):
    """
    Validates that the content of an old, outdated translation and a new translation template can be merged.
    In case the validation fails, a ValueError will be raised.

    Parameters
    ----------
    old_lines : [str]
        All lines of the outdated translation file, containing translation bits
    new_lines : [str]
        All lines of the current translation template file, missing translation bits
    file_name_old : str
        Name of the outdated translation file, for more expressive error messages
    file_name_new : str
        Name of the current translation file template, for more expressive error messages
    """
    if len(old_lines) != len(new_lines):
        raise ValueError(f'The given files have a different lines count: {len(old_lines)} ({file_name_old}) vs ' +
                         f'{len(new_lines)} ({file_name_new}).')

    errors: [str] = []
    current_prefix = ''
    for line_no in range(0, len(old_lines)):
        old_line = old_lines[line_no]
        new_line = new_lines[line_no]
        if ((line_no + 1) % 2) == 1:  # even number -> English. Compare old with new version.
            found = re.search(prefix_pattern, new_line, re.MULTILINE)
            if found:
                current_prefix = found.group(1)
            else:
                current_prefix = ''
            if current_prefix + old_line != new_line and old_line != new_line:
                errors.append(f'Line {line_no + 1} differs: "{old_line}" ({file_name_old} with ' +
                              f'interpolated prefix) vs "{new_line}" ({file_name_new}).')
        else:
            found = re.search(prefix_pattern, old_line, re.MULTILINE)
            if found and found.group(1) != current_prefix:
                errors.append(f'Line {line_no + 1} has different prefixes: "{found.group(1)}" ({file_name_old}) vs ' +
                              f'"{current_prefix}" {file_name_new}).')

    if len(errors) != 0:
        raise ValueError('Some lines don\'t match: ' + '\n'.join(errors))


def __get_adjusted_translation_line__(to_adjust: str, current_prefix: str) -> str:
    """
    Takes a line and adds the prefix to it (in case there isn't already one or current_prefix is empty).

    Parameters
    ----------
    to_adjust: str
        The line with or without a prefix
    current_prefix:
        The current prefix to be used - can be empty

    Returns
    -------
    [str]
        The given line with a prefix, if required
    """
    found_in_to_adjust = re.search(prefix_pattern, to_adjust, re.MULTILINE)
    # should never fail because of preceding validation, any prefix should match current_prefix
    if found_in_to_adjust and found_in_to_adjust.group(1) != current_prefix:
        raise ValueError("invalid state")
    prefix = '' if found_in_to_adjust else current_prefix
    return prefix + to_adjust


def merge_lines(old_lines: [str], new_lines: [str]) -> [str]:
    """
    Merges the given old and new lines. See the test for details.

    Parameters
    ----------
    old_lines : [str]
        All lines of the outdated old file, containing translation bits
    new_lines : [str]
        All lines of the current translation template file, missing translation bits

    Returns
    -------
    [str]
        A merged version of the files
    """
    merged: [str] = []
    current_prefix: str = ''
    for line_no in range(0, len(old_lines)):
        old_line = re.sub(linebreak_pattern, '', old_lines[line_no])
        new_line = re.sub(linebreak_pattern, '', new_lines[line_no])
        if ((line_no + 1) % 2) == 1:  # even number -> English. We've got to store the prefix, if any
            found = re.search(prefix_pattern, new_line, re.MULTILINE)
            if found:
                current_prefix = found.group(1)
            else:
                current_prefix = ''
            merged.append(new_line)
        else:
            old_line_adjusted = __get_adjusted_translation_line__(old_line, current_prefix)
            new_line_adjusted = __get_adjusted_translation_line__(new_line, current_prefix)

            if old_line_adjusted == current_prefix:  # old line is empty except for the prefix: take new one
                merged.append(new_line_adjusted)
            else:  # else take the old one
                merged.append(old_line_adjusted)

    return merged


def run(args: [str]):
    if len(args) != 3 and len(args) != 4:
        raise ValueError(f'Argument missing: run the script with the location of the old file as first and with the ' +
                         f'location of the new file as second argument. A third argument for the target file is ' +
                         'optional and defaults to "merged.trs", e.g.:\n old.trs new.trs merged.trs')
    file_name_old = args[1]
    file_name_new = args[2]
    file_name_merged = args[3] if len(args) == 4 else 'merged.trs'

    old_lines: [str]
    new_lines: [str]

    with open(file_name_old, 'r') as file_old, open(file_name_new, 'r') as file_new:
        old_lines = file_old.readlines()
        new_lines = file_new.readlines()

    validate_lines(old_lines, new_lines, file_name_old, file_name_new)
    merged = merge_lines(old_lines, new_lines)
    with open(file_name_merged, 'w', "utf-8-sig") as file_merged:
        file_merged.writelines(merged)


if __name__ == '__main__':
    run(sys.argv)
