"""
Extension to `jsonpointer` package to replace sub-string references.

"""
import copy
import re

import jsonpointer

BAD_OPEN_PATTERN = re.compile(r'\{{3,}')
BAD_CLOSE_PATTERN = re.compile(r'\}{3,}')
GROUP_PATTERN = re.compile(r'{{([^{^}]*)}}')
OPEN_PATTERN = re.compile(r'{{')
CLOSE_PATTERN = re.compile(r'}}')


class MaxRecursionLimit(Exception):
    pass


def string_value_generator(obj):
    """
    Returns key, value, parent triplets for all nested string values.

    :param (dict|list) obj: The object to generate values for.
    :return (generator): A generator object to iterate over.

    """
    if isinstance(obj, list):
        for index, value in enumerate(obj):
            if isinstance(value, basestring):
                yield index, value, obj
            if isinstance(value, (list, dict)):
                for item in string_value_generator(value):
                    yield item
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, basestring):
                yield key, value, obj
            if isinstance(value, (list, dict)):
                for item in string_value_generator(value):
                    yield item


def get_references(string):
    """
    Search string for embedded json pointers and return information on them.

    :param (str|unicode) string: A value from the document that may have refs.
    :raises (ValueError): For syntax errors related to formatting characters.
    :return (dict[]): Each has the form {'pointer': (str), 'indices': (list)}

    """
    if BAD_OPEN_PATTERN.search(string):
        raise ValueError('Syntax Error in {}.'.format(string))
    if BAD_CLOSE_PATTERN.search(string):
        raise ValueError('Syntax Error in {}.'.format(string))

    references = []
    search_index = 0
    while True:
        sub_string = string[search_index:]
        group_match = GROUP_PATTERN.search(sub_string)
        if not group_match:
            open_match = OPEN_PATTERN.search(sub_string)
            close_match = CLOSE_PATTERN.search(sub_string)
            if open_match or close_match:
                raise ValueError('Syntax Error in {}.'.format(string))
            break
        else:
            start = search_index + group_match.start()
            end = search_index + group_match.end()
            search_index = end
            references.append({'pointer': group_match.groups()[0],
                               'indices': [start, end]})

    return references


def resolve_string(string, document, max_recursion=100):
    """
    Resolve a string value using the given document as context.

    :param (str|unicode) string: The string to resolve pointers inside of.
    :param (dict|list) document: A loaded json document.
    :param (int) max_recursion: Prevents cyclic references. Increase if needed.
    :raises (CycleDetected): If a cycle is detected while resolving the string.
    :return: (str|unicode) The resolved string.

    """
    recursions = 0
    while True:
        if recursions > max_recursion:
            raise MaxRecursionLimit(max_recursion)
        recursions += 1
        references = get_references(string)
        if not references:
            break

        offset = 0
        for reference in references:
            pointer = reference['pointer']
            start, stop = reference['indices']
            value = jsonpointer.resolve_pointer(document, pointer)
            if not isinstance(value, basestring):
                raise ValueError('Variables must be strings.')
            string = string[:start + offset] + value + string[stop + offset:]
            offset += len(value) - (stop - start)

    return string


def dereference(document, inplace=True, max_recursion=100):
    """
    Set pointers to equal their resolved values inside a loaded json document.

    :param (dict|list) document: A loaded json document.
    :param (bool) inplace: If False, set values in a *copy* of the document.
    :param (int) max_recursion: Prevents cyclic references. Increase if needed.
    :return (dict|list): A fully-resolved document (may be a copy).

    """
    if not inplace:
        document = copy.deepcopy(document)
    for key, value, parent in string_value_generator(document):
        parent[key] = resolve_string(value, document, max_recursion)
    return document
