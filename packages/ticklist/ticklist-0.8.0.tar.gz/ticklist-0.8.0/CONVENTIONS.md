# general guidance

- no whitespace changes

# python

- source code is inside the src folder.
- you are an expert python developer. you write straightforward easy to read code.
- use types everywhere possible.
- do not make changes that have nothing to do with the current goal.


## workspaces

This is a monorepo containing multiple packages. These packages live inside the `packages` folder.
each subfolder inside the `packages` folder represents a `workspace-package`.
inside each `workspace-package` is a `src` folder. The `src` folder contains the python source code grouped inside a python module, called `workspace-module`

## writing tests

- write your test using pytest framework. make use of fixtures and parameterization where appropriate.
- tests are put inside the tests folder.
- When creating a new test file use the same folder structure as defined inside the source code folder. The name of the testfile is identical to the file under test, but
  prefixed with `test_`.
    for example, when the code I want to test lives in: `src/mypackage/constants.py`, I want the test file to be located here: `tests/mypackage/test_constants.py`

## writing python docstrings:

- Use the google docstring convention.
- Do not include types of the arguments or the return objects.


