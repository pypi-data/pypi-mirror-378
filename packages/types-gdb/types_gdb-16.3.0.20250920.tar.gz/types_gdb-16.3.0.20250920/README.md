## Typing stubs for gdb

This is a [type stub package](https://typing.python.org/en/latest/tutorials/external_libraries.html)
for the [`gdb`](https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=tree) package. It can be used by type checkers
to check code that uses `gdb`. This version of
`types-gdb` aims to provide accurate annotations for
`gdb==16.3.*`.

Type hints for GDB's [Python API](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html). Note that this API is available only when running Python scripts under GDB: it is not possible to install the `gdb` package separately, for instance using `pip`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/gdb`](https://github.com/python/typeshed/tree/main/stubs/gdb)
directory.

This package was tested with the following type checkers:
* [mypy](https://github.com/python/mypy/) 1.18.1
* [pyright](https://github.com/microsoft/pyright) 1.1.405

It was generated from typeshed commit
[`b158ccd3c1b204b2379f898425724d82e7234337`](https://github.com/python/typeshed/commit/b158ccd3c1b204b2379f898425724d82e7234337).