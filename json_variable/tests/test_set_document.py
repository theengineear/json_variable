from copy import deepcopy
from unittest import TestCase

from json_variable import dereference

from json_variable.dereferencing import (
    MaxRecursionLimit, get_references, resolve_string, string_value_generator
)


class TestStringValueGenerator(TestCase):

    def test_string_value_generator(self):

        # should generate a (key, value, parent) pair for all string values.

        object_1 = {'g': '6'}
        array_1 = ['5', object_1]
        object_2 = {'f': array_1}
        object_3 = {'e': object_2}
        object_4 = {'c': '4'}
        array_2 = ['2', '3', object_4]

        document = {
            'a': '1',
            'b': array_2,
            'd': object_3
        }

        expected_items = [
            ('a', '1', document),
            (0, '2', array_2),
            (1, '3', array_2),
            ('c', '4', object_4),
            (0, '5', array_1),
            ('g', '6', object_1)
        ]

        items = list(string_value_generator(document))
        self.assertEqual(items, expected_items)


class TestGetReferences(TestCase):

    def test_raises_for_unbalanced_groupings(self):

        # Make sure we proactively catch syntax problems.

        strings = ['{{foo', 'foo}}', '{{{bar}}', '{{bar}}}']
        for string in strings:
            with self.assertRaises(ValueError):
                get_references(string)

    def test_returns_references_list(self):

        # We should get an array of all the matches in a string.

        string = "This references {{/one}}, {{/two}}, and {{/three}}!"
        expected_references = [
            {'indices': [16, 24], 'pointer': '/one'},
            {'indices': [26, 34], 'pointer': '/two'},
            {'indices': [40, 50], 'pointer': '/three'}
        ]
        references = get_references(string)
        self.assertEqual(references, expected_references)


class TestResolveString(TestCase):

    def test_cyclic_reference(self):

        # Currently just a simple limit on depth of reference recursion.

        document = {
            'a': 'I point to {{/b}}.',
            'b': 'And "/b" points to {{/c}}.',
            'c': 'But "/c" points {{/a}}!'
        }

        for key in document.keys():
            with self.assertRaises(MaxRecursionLimit):
                resolve_string(document[key], document)

    def test_max_recursion(self):

        # Test that we can just increase the limit if we need more depth.

        document = {
            'a': 'I point to {{/b}}.',
            'b': 'And "/b" points to {{/c}}.',
            'c': '\o/'
        }

        # We need two recursions, but we're limited to one --> error.
        with self.assertRaises(MaxRecursionLimit):
            resolve_string(document['a'], document, 1)

        # We have a built-in workaround though...
        resolve_string(document['a'], document, 2)

    def test_resolved_string(self):

        # Test that we get the expected value.

        document = {
            'a': 'A {{/b/0/a}} value and a {{/c}} value.',
            'b': [{'a': 'nested'}],
            'c': 'top-level'
        }

        resolved_string = resolve_string(document['a'], document)
        expected_resolved_string = 'A nested value and a top-level value.'
        self.assertEqual(resolved_string, expected_resolved_string)

    def test_reference_must_be_string(self):

        # Until we need this, it's a simplification to prevent non-string vars.

        with self.assertRaises(ValueError):
            resolve_string('{{/a}}', {'a': 5})


class TestDereferenceVariables(TestCase):

    maxDiff = None

    def setUp(self):
        self.document = {
            'a': 'beep {{/b}}',
            'b': 'boop',
            'c': [{'a': '{{/a}}', 'b': '{{/b}}'}, {'a': 'foo', 'b': 'bar'}],
            'e': '{{/c/0/b}} and {{/c/1/b}}',
            'f': ['{{/b}}']
        }
        self.dereferenced_document = {
            'a': 'beep boop',
            'c': [{'a': 'beep boop', 'b': 'boop'}, {'a': 'foo', 'b': 'bar'}],
            'b': 'boop',
            'e': 'boop and bar',
            'f': ['boop']
        }

    def test_inplace(self):

        # By default, we should set the document inplace.

        dereference(self.document)
        self.assertEqual(self.document, self.dereferenced_document)

    def test_not_inplace(self):

        # We should also be able to prevent setting the document in place.

        document_copy = deepcopy(self.document)
        dereferenced_document = dereference(self.document, inplace=False)
        self.assertNotEqual(self.document, dereferenced_document)
        self.assertEqual(self.document, document_copy)
        self.assertEqual(dereferenced_document, self.dereferenced_document)
