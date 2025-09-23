#!/usr/bin/env python

from pathlib import Path
from argparse import ArgumentParser

LINE_STARTERS = {
    'plain': [
        "# solution",
        "## solution",
    ],
    'commented': [
        "# # solution",
        "# ## solution",
    ],
}

def has_line_starter(line: str):
    """
    search if line starts with one of the triggers listed in LINE_STARTERS
    returns either False, or 'plain' or 'commented'
    """
    for category, texts in LINE_STARTERS.items():
        for text in texts:
            if line.startswith(text):
                return category
    return False

def to_insert(markdown, category):
    if category == 'plain':
        return markdown
    else:
        return '\n'.join(f'# {line}' for line in markdown.split('\n'))



def trim_solution(in_filename, out_filename):
    with (open(in_filename) as reader, open(out_filename, 'w') as writer):
        for line in reader:
            if category := has_line_starter(line):
                writer.write(to_insert("solution removed here\n", category))
                break
            writer.write(line)

def output_filename(in_filename):
    result = (in_filename
                .replace("-solution", "")
                .replace("-corrige", "")
    )
    if result == in_filename:
        return None
    return result


def main():
    parser = ArgumentParser("")
    parser.add_argument("solutions", nargs="+")
    parser.add_argument("-f", "--force", default=False, action='store_true')
    parser.add_argument("-v", "--verbose", default=False, action='store_true')

    cli_args = parser.parse_args()
    solutions = cli_args.solutions

    def verbose(*args, **kwds):
        if cli_args.verbose:
            print(*args, **kwds)

    for solution in solutions:
        student = output_filename(solution)
        if not student:
            verbose(f"ignoring {solution} - does not comply with conventions")
            continue

        p1, p2 = Path(solution), Path(student)
        if not p1.exists():
            print(f"{p1} not found")
            continue
        if not cli_args.force and p2.exists() and p2.stat().st_mtime > p1.stat().st_mtime:
            verbose(f"ignoring {p1}, as {p2} is more recent")
            continue
        message = "created" if not p2.exists() else "overwritten"
        trim_solution(solution, student)
        print(f"{student} {message}")

main()