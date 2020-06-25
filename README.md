<h1 align="center">todotxt2notion</h1>

A simple Python script to migrate your `.todo.txt` files to `.csv` format that can be imported to Notion.

## Usage
```
py todotxt2notion -i <input file path> \
                  [-r <replacements file path>] \
                  [-o <output file path>] \
                  [-v <verbosity level>]
```
Verbosity levels:
| Argument value | Explanation         |
|--------|-----------------------------|
| `-v d` | print all debug information |
| `-v e` | errors only (silent mode)   |
| `-v i` | informational messages only |

`replacements.yml` file is used if you don't specify a file with custom replacement rules.

`regex-patterns-todotxt.yml` is required for script to work.<br>
That file contains regex patterns to extract `todo.txt` task's properties.
