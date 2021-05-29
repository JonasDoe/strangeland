import re
import sys

"""Used to find prefixes like '&31 '"""
prefix_pattern = r"^(&[\d]*\ )"
"""Used to find all kind of line breaks"""
linebreak_pattern = r"(\r\n|\r|\n)$"


def validate_lines(old_lines: [str], new_lines: [str], file_name_old: str = 'old file',
                   file_name_new: str = 'new file', interactive: bool = False) -> [[str], ValueError]:
    """
    Validates that the content of an old, outdated translation and a new translation template can be merged. For some
    inconsistencies the user will be asked for a decision.

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
    interactive : bool
        If true, an error can be resolved by user input, if possible

    Returns
    -------
    [[str], ValueError]
        A list of all validated lines (including user decisions) and an Error in case of an validation error or user
        cancel. Even in case of an error the list of validated lines should be stored.
    """
    if len(old_lines) != len(new_lines):
        raise ValueError(f'The given files have a different lines count: {len(old_lines)} ({file_name_old}) vs ' +
                         f'{len(new_lines)} ({file_name_new}).')

    errors: [str] = []
    current_prefix = ''
    validated_lines: [str] = []
    line_no_iter = iter(range(0, len(old_lines)))
    for line_no in line_no_iter:
        old_line = re.sub(linebreak_pattern, '', old_lines[line_no])
        new_line = re.sub(linebreak_pattern, '', new_lines[line_no])
        if ((line_no + 1) % 2) == 1:  # even number -> English. Compare old with new version.
            found = re.search(prefix_pattern, new_line, re.MULTILINE)
            if found:
                current_prefix = found.group(1)
            else:
                current_prefix = ''
            if current_prefix + old_line == new_line or old_line == new_line:
                if len(errors) == 0:
                    validated_lines.append(new_line)
            else:
                old_line_translation = re.sub(linebreak_pattern, '', old_lines[line_no + 1])
                new_line_translation = re.sub(linebreak_pattern, '', new_lines[line_no + 1])
                if old_line_translation.startswith("//"):  # we're still in the comment section
                    if not new_line_translation.startswith("//"):
                        errors.append(
                            f'Line {line_no + 1} is a comment in {file_name_old}, but not in {file_name_new}.')
                    else:
                        validated_lines.append(new_line)
                elif interactive and len(errors) == 0:  # if there are already unsolved errors: just find more errors
                    print(f'Line {line_no + 1} differs:\n'
                          f'{old_line} ({file_name_old})\n'
                          f'{new_line} ({file_name_new})\n')
                    print(f'The translation is:\n'
                          f'{old_line_translation} ({file_name_old})\n')
                    if len(errors) == 0:
                        choice: str = ''
                        while choice not in ['1', '2', '3']:
                            choice = input('Enter number:\n'
                                           '(1) Keep new english line and old translation line\n'
                                           '(2) Keep new english line and enter new custom line\n'
                                           '(3) Abort\n')
                        if choice == '1':
                            next(line_no_iter)
                            validated_lines.append(new_line)
                            validated_lines.append(old_line_translation)
                            print('--------------\n')
                        elif choice == '2':
                            next(line_no_iter)
                            validated_lines.append(new_line)
                            translation = input('\nNew translation:\n')
                            validated_lines.append(re.sub(linebreak_pattern, '', translation))
                            print('--------------\n')
                        else:
                            errors.append(f'Line {line_no + 1} differs: "{old_line}" ({file_name_old} with ' +
                                          f'interpolated prefix) vs "{new_line}" ({file_name_new}).')
                else:
                    errors.append(f'Line {line_no + 1} differs: "{old_line}" ({file_name_old} with ' +
                                  f'interpolated prefix) vs "{new_line}" ({file_name_new}).')
        else:
            found = re.search(prefix_pattern, old_line, re.MULTILINE)
            if found is None or (found.group(1) == current_prefix):
                if len(errors) == 0:
                    validated_lines.append(old_line)
            else:
                errors.append(f'Line {line_no + 1} has different prefixes: "{found.group(1)}" ({file_name_old}) vs ' +
                              f'"{current_prefix}" {file_name_new}).')

    if len(errors) == 0:
        return validated_lines, None
    else:
        return validated_lines, ValueError('Some lines don\'t match: ' + '\n'.join(errors))


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
    if len(args) < 3 or len(args) > 5:
        raise ValueError('Invalid argument count. This script takes two to four arguments:\n' +
                         '1.) location of the old file with the translation data (required)\n'
                         '2.) location of the new file (required)\n'
                         '3.) the encoding of the input and output files (e.g. utf-8 or cp1252), default = utf-8\n' +
                         '4.) output file, default = merged.trs\n"'
                         'So run the script with something like:'
                         'python add_prefixes.py german.trs english.trs utf-8 merged.trs')
    file_name_old: str = args[1]
    file_name_new: str = args[2]
    encoding: str = args[3] if len(args) == 4 else 'utf-8'
    file_name_merged: str = args[4] if len(args) == 5 else 'merged.trs'
    sys.stdout.reconfigure(encoding=encoding)
    sys.stdin.reconfigure(encoding=encoding)

    old_lines: [str]
    new_lines: [str]

    with open(file_name_old, 'r', encoding=encoding) as file_old, open(file_name_new, 'r',
                                                                       encoding=encoding) as file_new:
        old_lines = file_old.readlines()
        new_lines = file_new.readlines()

    [validated_lines, error] = validate_lines(old_lines, new_lines, file_name_old, file_name_new, True)
    if error is not None:
        print(f'{str(error)}\n'
            f'--------------\n'
            f'Canceled operation due to an error.\n'
            f'The state until the line causing this error has been stored in {file_name_merged}.\n'
            f'You might want to backup this results or replace regarding lines in {file_name_old} with them.')
        with open(file_name_merged, 'w', encoding=encoding) as file_merged:
            file_merged.writelines('\n'.join(validated_lines))
        exit(1)
    else:
        merged = merge_lines(validated_lines, new_lines)
        with open(file_name_merged, 'w', encoding=encoding) as file_merged:
            file_merged.writelines('\n'.join(merged))


if __name__ == '__main__':
    run(sys.argv)
