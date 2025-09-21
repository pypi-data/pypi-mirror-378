# Dyngle

## Run lightweight local workflows

Dyngle is a simple workflow runner that executes sequences of commands defined in configuration files. It's like a lightweight combination of Make and a task runner, designed for automating common development and operational tasks.

## Basic usage

Create a configuration file (e.g., `.dyngle.yml`) with your workflows:

```yaml
dyngle:
  operations:
    build:
      - python -m pip install -e .
      - python -m pytest
    deploy:
      - docker build -t myapp .
      - docker push myapp
    clean:
      - rm -rf __pycache__
      - rm -rf .pytest_cache
```

Run an operation:

```bash
dyngle run build
```

## Configuration

Dyngle reads configuration from YAML files. You can specify the config file location using:

- `--config` command line option
- `DYNGLE_CONFIG` environment variable  
- `.dyngle.yml` in current directory
- `~/.dyngle.yml` in home directory

The configuration has 2 parts: `operations:` and `expressions`.

Configuration files can import other configuration files, by providing an entry `imports:` with an array of filepaths. The most obvious example is a Dyngle config in a local directory which imports the user-level configuration.

```yaml
dyngle:
  imports:
    - ~/.dyngle.yml
  expressions:
  operations:
```

In the event of item name conflicts, expressions and operations are loaded from imports in the order specified, so imports lower in the array will override those higher up. The expressions and operations defined in the main file override the imports. Imports are not recursive.

## Data

Dyngle maintains a block of data throughout operations, which is parsed from YAML in stdin.

## Operations

Operations contain steps as a YAML array. The lifecycle of an operation is:

1. Load input data if it exists from YAML on stdin (if no tty)
2. Perform template rendering on a step, using data and expressions (see below)
3. Execute the step in a subprocess
4. Continue with the next step

Note that operations in the config are _not_ full shell lines. They are passed directly to the system.

## Templates

Prior to running commands, the line containing that command is processed as a template. Entries from the data set can be substituted into the command line using Jinja-like expressions in double-curly brackets (`{{` and `}}`).

For example, if stdin contains the following data:

```yaml
name: Francis
```

And the command looks like:

``` yaml
- echo "Hello {{name}}!"
```

Then the command will output "Hello Francis!".


## Expressions

Configs can also contain expressions, written in Python, that can also be referenced in operation steps.

```yaml
dyngle:
  expressions:
    say-hello: >-
        'Hello ' + name + '!'
  operations:
    say-hello: echo {{say-hello}}
```

Expressions can use a controlled subset of the Python standard library, including:

- Built-in data types such as `str()`
- Essential built-in functions such as `len()`
- The core modules from the `datetime` package (but some methods such as `strftime()` will fail)
- A specialized function called `formatted()` to perform string formatting operations on a `datetime` object
- A restricted version of `Path()` that only operates within the current working directory
- Various other useful utilities, mostly read-only, such as the `math` module
- A special function called `resolve` which resolves data expressions using the same logic as in templates

Data keys containing hyphens are converted to valid Python names by replacing hyphens with underscores.

Expressions can reference data directly as local names in Python (using the underscore replacements)...

```yaml
dyngle:
  expressions:
    say-hello: >-
        'Hello ' + full_name + '!'
```

... or using the `resolve()` function, which also allows expressions to essentially call other expressions, using the same underlying data set.

```yaml
dyngle:
  expressions:
    hello: >-
        'Hello ' + resolve('formal-name') + '!'
    formal-name: >-
        'Ms. ' + full_name
```

Note it's also _possible_ to call other expressions by name as functions, if they only return hard-coded values (i.e. constants).

```yaml
dyngle:
  expressions:
    author-name: Francis Potter
    author-hello: >-
        'Hello ' + author_name()
``` 

## Local Expressions

Expressions can also be defined in a way that applies only to one operation - especially useful for command-line arguments.

In this case, the operation definition has a different structure. See the example below.

```yaml
dyngle:
  operations:
    name_from_arg:
      expressions:
        local_name: "args[0]"
      steps:
        - echo "Hello {{local_name}}"
```

## Security

Commands are executed using Python's `subprocess.run()` with arguments split in a shell-like fashion. The shell is not used, which reduces the likelihood of shell injection attacks. However, note that Dyngle is not robust to malicious configuration. Use with caution.

## Quick installation (MacOS)

```bash
brew install python@3.11
python3.11 -m pip install pipx
pipx install dyngle
```
