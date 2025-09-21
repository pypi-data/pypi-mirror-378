"""Collect tests and run them on supplied code."""

import os

from tempfile import NamedTemporaryFile
import sys


from check_pfda.utils import get_current_assignment, get_tests

from click import echo, secho

import pytest


def check_student_code(verbosity: int = 2, debug: bool = False) -> None:
    """Check student code."""
    try:
        current = get_current_assignment()
    except TypeError:
        echo("Unable to match chapter and assignment against cwd. Contact your TA.")
        return
    chapter = current["chapter"]
    assignment = current["assignment"]
    echo(f"Checking assignment {assignment} at verbosity {verbosity}...")
    cwd_src = os.path.join(os.getcwd(), "src")
    if cwd_src not in sys.path:
        sys.path.insert(0, cwd_src)
    if debug:
        secho("\nIN DEBUG MODE\n", fg="blue", bold=True)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_path = os.path.join(base_dir, "check_pfda",
                                 ".test_static_imports",
                                 f"test_{assignment}.py")
        args = [test_path]
        if verbosity > 0:
            args.append(f"-{'v' * verbosity}")
        exit_code = pytest.main(args)
        echo(f"Pytest finished with exit code {exit_code}")
        return
    tests = get_tests(chapter, assignment)

    temp_file = NamedTemporaryFile(suffix=".py", delete=False)
    try:
        temp_file.write(tests.encode("utf-8"))
        temp_file.flush()
        temp_file.close()

        args = [temp_file.name]
        if verbosity > 0:
            args.append(f"-{'v' * verbosity}")
        exit_code = pytest.main(args)
    finally:
        os.remove(temp_file.name)
    if cwd_src in sys.path:
        sys.path.remove(cwd_src)
