from collections import OrderedDict
from collections.abc import Mapping
from typing import List, Dict
from pathlib import Path


# =====FROM
# 2020-06-17 due:2020-06-21 @cn +lab 9.1.2.8 9.2.3.6 9.2.4.4
# =====TO
# Name,Status,Subjects,Contexts,Links,Completion Date,Creation Date,Due Date
# 9.1.2.8 9.2.3.6 9.2.4.4,To Do,Computer Networks,Laboratory work,,,"Jun 17, 2020","Jun 21, 2020"


def parse_todo_txt(
    file_path: Path, patterns: Dict[str, str], replacements: Dict[str, str]
) -> List[Dict[str, str]]:
    import re

    content = ""
    with open(file_path, encoding="utf-8") as todo_txt_file:
        content = todo_txt_file.readlines()

    lines = [x.strip() for x in content]
    tasks: List[Dict[str, str]] = []
    for line in lines:
        # skip empty lines
        if not line:
            continue

        # priority = re.match(patterns["PRIORITY_RX_PATTERN"], line)
        completed = bool(re.match(patterns["COMPLETED_RX_PATTERN"], line))

        # substitute subj/proj with readable expanded forms
        subjects = re.findall(patterns["SUBJECT_RX_PATTERN"], line)
        projects = re.findall(patterns["PROJECT_RX_PATTERN"], line)
        for k, v in replacements.items():
            for idx, s in enumerate(subjects):
                subjects[idx] = re.sub(k, v, s)
            for idx, p in enumerate(projects):
                projects[idx] = re.sub(k, v, p)

        # capitalize subj/proj first letters
        for idx, s in enumerate(subjects):
            subjects[idx] = s[0].upper() + s[1:]
        for idx, p in enumerate(projects):
            projects[idx] = p[0].upper() + p[1:]

        # fill dates
        creation_date_parts = re.findall(patterns["CREATION_DATE_RX_PATTERN"], line)
        creation_date = (
            format_date(*creation_date_parts[0][::-1]) if creation_date_parts else ""
        )

        completion_date_parts = re.findall(patterns["COMPLETION_DATE_RX_PATTERN"], line)
        completion_date = (
            format_date(*completion_date_parts[0][::-1])
            if completion_date_parts
            else ""
        )

        due_date_parts = re.findall(patterns["DUE_DATE_RX_PATTERN"], line)
        due_date = format_date(*due_date_parts[0][::-1]) if due_date_parts else ""

        tasks.append(
            OrderedDict(
                {
                    "Name": str(
                        re.match(patterns["CONTENT_RX_PATTERN"], line, re.S)
                        .group(1)
                        .strip()
                        .capitalize()
                    ),
                    "Status": "Done" if completed else "To Do",
                    "Subjects": ", ".join(subjects),
                    "Contexts": ", ".join(projects),
                    "Links": " ".join(
                        [
                            s.strip()
                            for s in re.findall(patterns["URL_RX_PATTERN"], line)
                        ]
                    ),
                    "Completion Date": completion_date,
                    "Creation Date": creation_date,
                    "Due Date": due_date,
                }.items()
            )
        )
    return tasks


def format_date(day: str, month: str, year: str) -> str:
    import datetime

    # e.g. "Jun 18, 2020"
    return f"""{
        datetime.date(1900, int(month), 1).strftime('%b')
    } {
        int(day)
    }, {
        year
    }"""


def write_notion_csv(file_path: Path, rows: List[Dict[str, str]]):
    import csv

    with open(file_path, "w", newline="") as csv_file:
        wr = csv.writer(
            csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        # Write csv header
        wr.writerow(list(rows[0].keys()))
        for row in rows:
            wr.writerow(list(row.values()))


def print_help():
    print("usage: py todotxt2notion <options>")
    print("options:")
    print(" -i | --input     | Path to file with todo.txt format.")
    print(" -o | --output    | Path to resulting Notion database file.")
    print(" -v | --verbosity | Verbosity level: d=debug e=errors i=info (default)")
    print(" -h | --help      | Shows this help screen.")


def main():
    import sys
    import logging
    import yaml
    from getopt import getopt, GetoptError

    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        opts, args = getopt(
            sys.argv[1:],
            "hi:r:o:v:",
            ["help", "input=", "replacements=" "output=", "verbosity="],
        )
    except GetoptError as err:
        print(err)
        print_help()
        exit(2)

    input_path = None
    replacements_path = None
    output_path = None

    for key, value in opts:
        if key in ("-v", "--verbosity"):
            if value == "e":
                logging.getLogger().setLevel(logging.ERROR)
            elif value == "d":
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                logging.getLogger().setLevel(logging.INFO)
        elif key in ("-h", "--help"):
            print_help()
            exit()
        elif key in ("-i", "--input"):
            input_path = Path(value)
        elif key in ("-r", "--replacements"):
            replacements_path = Path(value)
        elif key in ("-o", "--output"):
            output_path = Path(value)
        else:
            pass

    patterns_path = Path("regex-patterns-todotxt.yml")
    if patterns_path is None:
        logging.error("Fatal: regex-patterns-todotxt.yml doesn't exists.")
        print_help()
        exit(2)

    patterns = {}
    with open(patterns_path, "r") as f:
        patterns = yaml.safe_load(f.read())

    if input_path is None:
        logging.error("Input file path is not specified.")
        print_help()
        exit(1)
    elif not input_path.exists():
        logging.error("Specified todo.txt file path does not exists.")
        exit(1)

    logging.info("Todo.txt file to Notion CSV database converter | by @f1uctus")

    if replacements_path is None:
        logging.debug(
            "D: Replacements path is not specified. "
            "Trying to use 'replacements.yml' in script directory."
        )
        if Path("replacements.yml").exists():
            replacements_path = Path("replacements.yml")
        else:
            logging.debug(
                "D: 'replacements.yml' doesn't exists. " "No replacements will be made."
            )

    replacements = {}
    if replacements_path is not None and replacements_path.exists():
        with open(replacements_path, "r") as f:
            replacements = yaml.safe_load(f.read())
    if not isinstance(replacements, Mapping):
        logging.debug(
            "D: Replacements file contents is not a dictionary. "
            "No replacements will be made."
        )
        replacements = {}

    if output_path is None:
        logging.debug(
            "D: Output path is not specified. "
            "Result will be saved as input file with .csv extension."
        )
        output_path = Path(str(input_path) + ".csv")

    logging.info("Parsing " + str(input_path))
    tasks = parse_todo_txt(input_path, patterns, replacements)

    for task in tasks:
        logging.debug(yaml.dump(task, allow_unicode=True))

    logging.info("Writing tasks to " + str(output_path))
    write_notion_csv(output_path, tasks)

    logging.info("All done ;)")


if __name__ == "__main__":
    main()
