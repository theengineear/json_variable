JSON Variables
==============

Install
-------

.. code:: sh

    pip install json_variable

Nutshell
--------

This is a non-standard implementation extending JSON pointers:

https://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-04

It allows you to reference parts of a JSON document from within the same
document *from within a sub-string*.

In other words, JSON Pointers can handle resolving things like:

::

    {
        "a": "foo",
        "b": "/a"
    }

However, this proposes a new *variable* spec requiring an additional
template:

::

    {
        "a": "foo",
        "b": "{{/a}}"
    }

By using a template, we can replace sub-strings:

::

    {
        "a": "foo",
        "b": "{{/a}}, bar!"
    }

Example
-------

The motivation for this is to try and share settings between the
front-end and back-end of an application, settings within the same JSON
document can reference each other to prevent repetition. Consider the
following document:

::

    {
        "USERNAME_REGEX": "[a-zA-Z0-9._-]{3,30}",
        "USERNAMES_REGEX": "{{/USERNAME_REGEX}}(?:,{{/USERNAME_REGEX}})*",
        "FILE_ID_REGEX": "{{/USERNAME_REGEX}}:\\d+"
    }

After de-referencing the variables, you get:

::

    {
        "USERNAME_REGEX": "[a-zA-Z0-9._-]{3,30}",
        "USERNAMES_REGEX": "[a-zA-Z0-9._-]{3,30}(?:,[a-zA-Z0-9._-]{3,30})*",
        "FILE_ID_REGEX": "[a-zA-Z0-9._-]{3,30}:\\d+"
    }

The original document is more readable and revisions to the first value
only require changing *one* line.
