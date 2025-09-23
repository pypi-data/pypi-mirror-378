from __future__ import annotations

import pytest

import os, tempfile
from pathlib import Path

from baseprinter import __main__


BASEPRINT_CASE = Path(__file__).parent / "cases" / "baseprint"


def _run(args) -> int:
    if isinstance(args, str):
        args = args.split()
    return __main__.main(args)


@pytest.mark.parametrize("case", os.listdir(BASEPRINT_CASE))
def test_baseprint_output(case):
    expect_xml = BASEPRINT_CASE / case / "expect/article.xml"
    src_dir = BASEPRINT_CASE / case / "src"
    src_files = os.listdir(src_dir)
    if len(src_files) == 1:
        args = src_files[0]
    else:
        args = "-d pandocin.yaml"
    os.chdir(src_dir)
    with tempfile.TemporaryDirectory() as tmp:
        assert 0 == _run(f"{args} -b {tmp}/baseprint")
        got = Path(f"{tmp}/baseprint/article.xml").read_text()
    assert got == expect_xml.read_text()
