import re
import argparse
from chardet.universaldetector import UniversalDetector

"""Used to find prefixes like '&31 '"""
prefix_pattern = r"^(&[\d]*\ )"
"""Used to find all kind of line breaks"""
linebreak_pattern = r"(\r\n|\r|\n)$"


class FileData:
    name: str
    content: [str]

    def __init__(self, name: str, content: [str]):
        self.name = name
        self.content = content


def validate_lines(translation: FileData, template: FileData, interactive: bool = False) -> [[str], ValueError]:
    """
    Validates that the content of an old, outdated translation and a new translation template can be merged. For some
    inconsistencies the user will be asked for a decision.

    Parameters
    ----------
    translation : [FileData]
        All infos about the translation file, containing the original lines and translated bits
    template : [FileData]
        All infos about translation template file, missing translation bits
    interactive : bool
        If true, an error can be resolved by user input, if possible

    Returns
    -------
    [[str], ValueError]
        A list of all validated lines (including user decisions) and an Error in case of an validation error or user
        cancel. Even in case of an error the list of validated lines should be stored.
    """
    translation_lines = translation.content
    template_lines = template.content
    translation_file_name = translation.name
    template_file_name = template.name
    if len(translation_lines) != len(template_lines):
        raise ValueError(
            f'The given files have a different lines count: {len(translation_lines)} ({translation_file_name}) vs ' +
            f'{len(template_lines)} ({template_file_name}).')

    errors: [str] = []
    current_prefix = ''
    validated_lines: [str] = []
    line_no_iter = iter(range(0, len(translation_lines)))
    for line_no in line_no_iter:
        old_line = re.sub(linebreak_pattern, '', translation_lines[line_no])
        template_line = re.sub(linebreak_pattern, '', template_lines[line_no])
        if ((line_no + 1) % 2) == 1:  # even number -> English. Compare with possibly newer template version.
            found = re.search(prefix_pattern, template_line, re.MULTILINE)
            if found:
                current_prefix = found.group(1)
            else:
                current_prefix = ''
            if current_prefix + old_line == template_line or old_line == template_line:
                if len(errors) == 0:
                    validated_lines.append(template_line)
            else:
                translation_line = re.sub(linebreak_pattern, '', translation_lines[line_no + 1])
                if translation_line.startswith("//"):  # we're still in the comment section
                    translation_line_in_template = re.sub(linebreak_pattern, '', template_lines[line_no + 1])
                    if not translation_line_in_template.startswith("//"):
                        errors.append(
                            f'Line {line_no + 1} is a comment in {translation_file_name}, '
                            f'but not in {template_file_name}.')
                    else:
                        validated_lines.append(template_line)
                elif interactive and len(errors) == 0:  # if there are already unsolved errors: just find more errors
                    print(f'Line {line_no + 1} differs:\n'
                          f'{old_line} ({translation_file_name})\n'
                          f'{template_line} ({template_file_name})\n')
                    print(f'The translation is:\n'
                          f'{translation_line} ({translation_file_name})\n')
                    if len(errors) == 0:
                        choice: str = ''
                        while choice not in ['1', '2', '3']:
                            choice = input('Enter number:\n' +
                                           f'(1) Keep english line from {template_file_name} line and translation ' +
                                           f'from {translation_file_name}\n' +
                                           f'(2) Keep english line {template_file_name} and enter new custom line\n' +
                                           '(3) Abort\n')
                        if choice == '1':
                            next(line_no_iter)
                            validated_lines.append(template_line)
                            validated_lines.append(translation_line)
                            print('--------------\n')
                        elif choice == '2':
                            next(line_no_iter)
                            validated_lines.append(template_line)
                            translation = input('\nNew translation:\n')
                            validated_lines.append(re.sub(linebreak_pattern, '', translation))
                            print('--------------\n')
                        else:
                            errors.append(f'Line {line_no + 1} differs: "{old_line}" ({translation_file_name} with ' +
                                          f'interpolated prefix) vs "{template_line}" ({template_file_name}).')
                else:
                    errors.append(f'Line {line_no + 1} differs: "{old_line}" ({translation_file_name} with ' +
                                  f'interpolated prefix) vs "{template_line}" ({template_file_name}).')
        else:
            found = re.search(prefix_pattern, old_line, re.MULTILINE)
            if found is None or (found.group(1) == current_prefix):
                if len(errors) == 0: # in case there was already an error we don't append new lines
                    validated_lines.append(old_line)
            else:
                errors.append(
                    f'Line {line_no + 1} has different prefixes: "{found.group(1)}" ({translation_file_name}) vs ' +
                    f'"{current_prefix}" {template_file_name}).')

    if len(errors) == 0:
        return validated_lines, None
    else:
        return validated_lines, ValueError('Some lines don\'t match: ' + '\n'.join(errors))


def __get_adjusted_translation_line__(to_adjust: str, current_prefix: str, current_line: int) -> str:
    """
    Takes a line and adds the prefix to it (in case there isn't already one or current_prefix is empty).

    Parameters
    ----------
    to_adjust: str
        The line with or without a prefix
    current_prefix:
        The current prefix to be used - can be empty
    current_line: int
        Provides some context for reporting

    Returns
    -------
    [str]
        The given line with a prefix, if required
    """
    found_in_to_adjust = re.search(prefix_pattern, to_adjust, re.MULTILINE)
    # should never fail because of preceding validation, any prefix should match current_prefix
    if found_in_to_adjust and found_in_to_adjust.group(1) != current_prefix:
        raise ValueError(f'invalid file state around line {current_line}')
    prefix = '' if found_in_to_adjust else current_prefix
    return prefix + to_adjust


def merge_lines(translation_lines: [str], template_lines: [str] = None) -> [str]:
    """
    Merges the given old and new lines. See the test for details.

    Parameters
    ----------
    translation_lines : [str]
        All lines of the outdated old file, containing translation bits
    template_lines : [str]
        All lines of the current translation template file, missing translation bits. None in case only the translation
         file shall be used.

    Returns
    -------
    [str]
        A merged version of the files
    """
    merged: [str] = []
    current_prefix: str = ''
    for line_no in range(0, len(translation_lines)):
        translation_line = re.sub(linebreak_pattern, '', translation_lines[line_no])
        template_line = translation_line if template_lines is None else re.sub(linebreak_pattern, '',
                                                                               template_lines[line_no])
        if ((line_no + 1) % 2) == 1:  # even number -> English. We've got to store the prefix, if any
            found = re.search(prefix_pattern, template_line, re.MULTILINE)
            if found:
                current_prefix = found.group(1)
            else:
                current_prefix = ''
            merged.append(template_line)
        else:
            adjusted_translation_line = __get_adjusted_translation_line__(translation_line, current_prefix, line_no + 1)
            adjusted_template_line = __get_adjusted_translation_line__(template_line, current_prefix, line_no + 1)

            if adjusted_translation_line == current_prefix:  # old line is empty except for the prefix: take new one
                merged.append(adjusted_template_line)
            else:  # else take the old one
                merged.append(adjusted_translation_line)

    return merged


def run():
    translation_file_key = 'translation'
    template_file_key = 'template'
    output_file_key = 'output'
    encoding_key = 'encoding'
    parser = argparse.ArgumentParser(description='Validate and merge translation files')
    parser.add_argument(translation_file_key, help='Location of the old file with the translation data')
    parser.add_argument('--' + template_file_key,
                        help='Location of the template file, preferably without any translated lines. Required for ' +
                             'better validation and prefix determination.')
    parser.add_argument('--' + output_file_key,
                        help='Location of the output file', default='merged.trs')
    parser.add_argument('--' + encoding_key,
                        help='The encoding of the input and output files. If not set,'
                             'auto-detection will be applied (which might slow down the progress) ',
                        default=None,
                        choices=['utf-8', 'cp1252'])
    parsed_args = parser.parse_args()

    file_name_translation: str = getattr(parsed_args, translation_file_key)
    file_name_template: str = getattr(parsed_args, template_file_key)
    encoding_from_arg: str = getattr(parsed_args, encoding_key)
    output_file: str = getattr(parsed_args, output_file_key)
    # sys.stdout.reconfigure(encoding='cp1252')
    # sys.stdin.reconfigure(encoding=encoding)

    old_lines: [str]
    new_lines: [str]

    translation, encoding = read_file_lines(file_name_translation, encoding_from_arg)
    if file_name_template is None:
        process_without_template(FileData(file_name_translation, translation), output_file, encoding)
    else:
        template, _ = read_file_lines(file_name_template, encoding_from_arg)
        process_with_template(FileData(file_name_translation, translation), FileData(file_name_template, template),
                              output_file, encoding)


def process_with_template(translation: FileData, template: FileData, output_file: str, output_encoding: str):
    [validated_lines, error] = validate_lines(translation, template, True)
    if error is not None:
        print(f'{str(error)}\n'
              f'--------------\n'
              f'Canceled operation due to an error.\n'
              f'The state until the line causing this error has been stored in {output_file}.\n'
              f'You might want to backup this results or replace regarding lines in {translation.name} with them.')
        with open(output_file, 'w', encoding=output_encoding) as file_merged:
            file_merged.writelines('\n'.join(validated_lines))
        exit(1)
    else:
        merged = merge_lines(validated_lines, template.content)
        with open(output_file, 'w', encoding=output_encoding) as file_merged:
            file_merged.writelines('\n'.join(merged))


def process_without_template(translation: FileData, output_file: str, output_encoding: str):
    lines = translation.content
    merged = merge_lines(lines)
    with open(output_file, 'w', encoding=output_encoding) as file_merged:
        file_merged.writelines('\n'.join(merged))


def read_file_lines(file_name: str, encoding: str = None) -> ([str], str):
    if encoding is None:
        with open(file_name, 'rb') as file:
            file_bytes = file.read()
            detector = UniversalDetector()
            detector.feed(file_bytes)
            result = detector.close()
            if result['confidence'] >= .9:
                encoding = result['encoding']
                return file_bytes.decode(encoding).splitlines(), encoding
            else:
                raise ValueError(
                    f'couldn\'t detect encoding of {file_name} - '
                    f'please set an encoding and make sure all files comply with that one')
    else:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.read().splitlines(), encoding


if __name__ == '__main__':
    import sys

    if int(sys.version[0]) != 3:
        print('Aborted: Python 3.x required')
        sys.exit(1)
    run()
