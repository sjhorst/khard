# -*- coding: utf-8 -*-

import os
import random
import string
from datetime import datetime
from textwrap import dedent

from .object_type import ObjectType


def pretty_print(table, justify="L"):
    import os 
    from math import ceil

    console_size = os.popen('stty size', 'r').read().split()
    console_width = int(console_size[1])

    # get width for every column
    column_widths = [0] * table[0].__len__()
    offset = 3
    for row in table:
        for index, col in enumerate(row):
            width = len(str(col))
            if width > column_widths[index]:
                column_widths[index] = width
    while sum(column_widths)+(offset+1)*(len(column_widths)-1) > console_width:
        # First narrow the offset to 0
        offset = 0
        if table[0][-1] == 'UID':
            # Second drop the UID column altogether if present
            for row in table:
                row.pop()
            column_widths.pop()
            continue
        # Third narrow down the columns proportionally to their total width
        overage = sum(column_widths)+(offset+1)*(len(column_widths)-1) - console_width
        column_sum = sum(column_widths)
        for index, width in enumerate(column_widths):
            pct = width/column_sum
            trim = ceil(overage*pct)
            column_widths[index] -= trim
    table_row_list = []
    for row in table:
        single_row_list = []
        for col_index, col in enumerate(row):
            text = str(col)
            if len(text) > column_widths[col_index]:
                text = text[:column_widths[col_index]-1]+'…'
            if justify == "R":  # justify right
                formated_column = text.rjust(column_widths[col_index] +
                                                 offset)
            elif justify == "L":  # justify left
                formated_column = text.ljust(column_widths[col_index] +
                                                 offset)
            elif justify == "C":  # justify center
                formated_column = text.center(column_widths[col_index] +
                                                  offset)
            single_row_list.append(formated_column)
        table_row_list.append(' '.join(single_row_list))
    return '\n'.join(table_row_list)


def list_to_string(input, delimiter):
    """converts list to string recursively so that nested lists are supported

    :param input: a list of strings and lists of strings (and so on recursive)
    :type input: list
    :param delimiter: the deimiter to use when joining the items
    :type delimiter: str
    :returns: the recursively joined list
    :rtype: str
    """
    if isinstance(input, list):
        return delimiter.join(
            list_to_string(item, delimiter) for item in input)
    return input


def string_to_list(input, delimiter):
    if isinstance(input, list):
        return input
    return [x.strip() for x in input.split(delimiter)]


def string_to_date(input):
    """Convert string to date object.

    :param input: the date string to parse
    :type input: str
    :returns: the parsed datetime object
    :rtype: datetime.datetime
    """
    # try date formats --mmdd, --mm-dd, yyyymmdd, yyyy-mm-dd and datetime
    # formats yyyymmddThhmmss, yyyy-mm-ddThh:mm:ss, yyyymmddThhmmssZ,
    # yyyy-mm-ddThh:mm:ssZ.
    for format_string in ("--%m%d", "--%m-%d", "%Y%m%d", "%Y-%m-%d",
                          "%Y%m%dT%H%M%S", "%Y-%m-%dT%H:%M:%S",
                          "%Y%m%dT%H%M%SZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(input, format_string)
        except ValueError:
            pass
    # try datetime formats yyyymmddThhmmsstz and yyyy-mm-ddThh:mm:sstz where tz
    # may look like -06:00.
    for format_string in ("%Y%m%dT%H%M%S%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(''.join(input.rsplit(":", 1)),
                                     format_string)
        except ValueError:
            pass
    raise ValueError


def get_random_uid():
    return ''.join([random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(36)])


def file_modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def convert_to_yaml(
        name, value, indentation, indexOfColon, show_multi_line_character):
    """converts a value list into yaml syntax
    :param name: name of object (example: phone)
    :type name: str
    :param value: object contents
    :type value: str, list(str), list(list(str))
    :param indentation: indent all by number of spaces
    :type indentation: int
    :param indexOfColon: use to position : at the name string (-1 for no space)
    :type indexOfColon: int
    :param show_multi_line_character: option to hide "|"
    :type show_multi_line_character: boolean
    :returns: yaml formatted string array of name, value pair
    :rtype: list(str)
    """
    strings = []
    if isinstance(value, list):
        # special case for single item lists:
        if len(value) == 1 \
                and isinstance(value[0], str):
            # value = ["string"] should not be converted to
            # name:
            #   - string
            # but to "name: string" instead
            value = value[0]
        elif len(value) == 1 \
                and isinstance(value[0], list) \
                and len(value[0]) == 1 \
                and isinstance(value[0][0], str):
            # same applies to value = [["string"]]
            value = value[0][0]
    if isinstance(value, str):
        strings.append("%s%s%s: %s" % (
            ' ' * indentation, name, ' ' * (indexOfColon-len(name)),
            indent_multiline_string(value, indentation+4,
                                    show_multi_line_character)))
    elif isinstance(value, list):
        strings.append("%s%s%s: " % (
            ' ' * indentation, name, ' ' * (indexOfColon-len(name))))
        for outer in value:
            # special case for single item sublists
            if isinstance(outer, list) \
                    and len(outer) == 1 \
                    and isinstance(outer[0], str):
                # outer = ["string"] should not be converted to
                # -
                #   - string
                # but to "- string" instead
                outer = outer[0]
            if isinstance(outer, str):
                strings.append("%s- %s" % (
                    ' ' * (indentation+4), indent_multiline_string(
                        outer, indentation+8, show_multi_line_character)))
            elif isinstance(outer, list):
                strings.append("%s- " % (' ' * (indentation+4)))
                for inner in outer:
                    if isinstance(inner, str):
                        strings.append("%s- %s" % (
                            ' ' * (indentation+8), indent_multiline_string(
                                inner, indentation+12,
                                show_multi_line_character)))
    return strings


def convert_to_vcard(name, value, allowed_object_type):
    """converts user input into vcard compatible data structures
    :param name: object name, only required for error messages
    :type name: str
    :param value: user input
    :type value: str or list(str)
    :param allowed_object_type: set the accepted return type for vcard
        attribute
    :type allowed_object_type: enum of type ObjectType
    :returns: cleaned user input, ready for vcard or a ValueError
    :rtype: str or list(str)
    """
    if isinstance(value, str):
        if allowed_object_type == ObjectType.list_with_strings:
            raise ValueError(
                "Error: " + name + " must not contain a single string.")
        else:
            return value.strip()
    elif isinstance(value, list):
        if allowed_object_type == ObjectType.string:
            raise ValueError(
                "Error: " + name + " must not contain a list.")
        else:
            for entry in value:
                if not isinstance(entry, str):
                    raise ValueError(
                        "Error: " + name + " must not contain a nested list")
            # filter out empty list items and strip leading and trailing space
            return [x.strip() for x in value if x]
    else:
        if allowed_object_type == ObjectType.string:
            raise ValueError(
                "Error: " + name + " must be a string.")
        elif allowed_object_type == ObjectType.list_with_strings:
            raise ValueError(
                "Error: " + name + " must be a list with strings.")
        else:
            raise ValueError(
                "Error: " + name + " must be a string or a list with strings.")


def indent_multiline_string(input, indentation, show_multi_line_character):
    # if input is a list, convert to string first
    if isinstance(input, list):
        input = list_to_string(input, "")
    # format multiline string
    if "\n" in input:
        lines = ["|"] if show_multi_line_character else [""]
        for line in input.split("\n"):
            lines.append("%s%s" % (' ' * indentation, line.strip()))
        return '\n'.join(lines)
    return input.strip()


def get_new_contact_template():
    from .config import Config
    from os.path import join, dirname
    import sys

    formats = {'default': 'default_contact_template.yaml',
               'compact': 'compact_contact_template.yaml'
               }

    config = Config()
    supported_private_objects = config.get_supported_private_objects()
    contact_template = config.config['contact table']['contact_format'].lower()

    try:
        with open(join(dirname(__file__), 'data', formats[contact_template]), 'r') as fid:
            contact_text = fid.read()
    except IOError:
        print('Contact template file not found.')
        sys.exit()

    formatted_private_objects = []
    if supported_private_objects:
        formatted_private_objects.append("")
        longest_key = max(supported_private_objects, key=len)
        for object in supported_private_objects:
            formatted_private_objects += convert_to_yaml(
                object, "", 4, len(longest_key)+1, True)

    # create template
    return contact_text.format('\n'.join(formatted_private_objects))

