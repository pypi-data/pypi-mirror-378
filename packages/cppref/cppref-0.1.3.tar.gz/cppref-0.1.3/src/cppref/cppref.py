#!/usr/bin/env python3

import asyncio
import sys
from subprocess import Popen

from tqdm import tqdm

from cppref import Record, Source
from cppref.conf import ConfContext
from cppref.fzf import FzfContext
from cppref.utils import Utils


class CppRef:
    """A cli cpp manual pages for Linux/MacOS!"""

    def switch(self, source: Source):
        """Switch the manual source.

        Args:
            source: data source.
        """
        if source != "cppreference":
            return "Only cppreference is supported currently."
        with ConfContext() as conf:
            conf.source = source

    def list(self):
        """List titles of current source."""
        source = ConfContext.read_source()
        try:
            records = Utils.query(source, ConfContext.dbfile())
            print("\n".join(map(str, records)))
        except AssertionError as e:
            print(str(e), file=sys.stderr)
        except BrokenPipeError:
            pass  # the process piped to has been closed.

    def man(self, *, timeout: float = 10000):
        """Lookup a manual page interactively.

        Args:
            timeout: timeout of requesting webpage.
        """
        source = ConfContext.read_source()
        dbfile = ConfContext.dbfile()
        man3 = ConfContext.man3_root()
        html = ConfContext.html_root()

        try:
            records = Utils.query(source, dbfile)
        except AssertionError as e:
            return print(str(e), file=sys.stderr)

        with FzfContext("+m") as fzf:
            assert fzf.add_option(*records)
            selected = fzf.get_selection()
            if len(selected) == 0:
                return print("Canceled.")
            record = records[Record.parse_id(selected[0]) - 1]

        filename = man3.joinpath(f"{source}{record.id}.3.gz")
        filename.parent.mkdir(parents=True, exist_ok=True)

        if not filename.exists():
            htmlname = html.joinpath(f"{source}{record.id}.html")
            if htmlname.exists():
                webpage = Utils.read_file(htmlname)
            else:
                webpage = Utils.fetch(record, timeout)

            Utils.write_file(filename, Utils.html_handler(source)(webpage, record))

        process = Popen(f"man {filename}", shell=True)
        process.wait()

    def fetch(self, *, force: bool = False, timeout: float = 10000, limit: int = 5):
        """Fetch web pages from source and save it to the cache.

        Args:
            force: whether or not overwrite the existing web pages
            timeout: timeout of single url.
            limit: number of concurrent requests
        """
        source = ConfContext.read_source()
        html = ConfContext.html_root()

        # Get required records
        try:
            records = Utils.query(source, ConfContext.dbfile())
        except AssertionError as e:
            return print(f"Unexpected Error: {e}", file=sys.stderr)
        if not force:
            records = list(filter(lambda r: not html.joinpath(f"{source}{r.id}.html").exists(), records))  # fmt: off
            records = list(records)
        records = list(records)
        if (length := len(records)) == 0:
            return print("Nothing to fetch.", file=sys.stderr)

        pbar = tqdm(total=length)

        def on_success(record: Record, resp: str):
            Utils.write_file(html.joinpath(f"{source}{record.id}.html"), resp)
            pbar.update()

        def on_failed(record: Record, exec: Exception):
            print(f"Error={type(exec).__name__}({exec}): {record}", file=sys.stderr)
            pbar.update()

        html.mkdir(parents=True, exist_ok=True)
        asyncio.run(Utils.afetch(*records, timeout=timeout, limit=limit, on_success=on_success, on_failed=on_failed))  # fmt: off

    def parse(self, force: bool = False, interact: bool = False):
        """Parse the fetched pages in the cache, and save the results to manual directory.

        Args:
            force: whether or not overwrite the existing manual pages.
            interact: select the manual pages to parse interactively.
        """
        source = ConfContext.read_source()
        html = ConfContext.html_root()
        man3 = ConfContext.man3_root()
        if not html.exists():
            return f"{html} is not eixst, run cache command first."
        if not html.is_dir():
            return f"{html} is not a directory"

        # Get required records
        try:
            records = Utils.query(source, ConfContext.dbfile())
        except AssertionError as e:
            return print(str(e), file=sys.stderr)
        records = list(filter(lambda r: html.joinpath(f"{source}{r.id}.html").exists(), records))  # fmt: off
        if interact:
            with FzfContext("-m") as fzf:
                assert fzf.add_option(*records)
                selected = fzf.get_selection()
                records = [records[Record.parse_id(s) - 1] for s in selected]
        elif not force:
            records = list(filter(lambda r: not man3.joinpath(f"{source}{r.id}.3.gz").exists(), records))  # fmt: off
        if len(records) == 0:
            return print("Nothing to parse.")

        # Parse
        man3.mkdir(parents=True, exist_ok=True)
        total, process = len(records), Utils.html_handler(source)
        for r in tqdm(records, desc="Processing", total=total, file=sys.stdout):
            document = Utils.read_file(html.joinpath(f"{source}{r.id}.html"))
            try:
                document = process(document, r)
            except AssertionError as e:
                print(f"{e}, record={r}", file=sys.stderr)
            except Exception as e:
                print(f"record={r}, Unexpected error {e}", file=sys.stderr)
            else:
                Utils.write_man3(man3.joinpath(f"{source}{r.id}.3.gz"), document)

    def cache(self, force: bool = False, timeout: float = 10000, limit: int = 5):
        """Basically the combination of fetch and parse, except for save the webpages to the cache.

        Args:
            force: whether or not overwrite the existing manual pages
            timeout: timeout of single url
            limit: number of concurrent requests
        """
        source = ConfContext.read_source()
        man3 = ConfContext.man3_root()
        try:
            records = Utils.query(source, ConfContext.dbfile())
        except AssertionError as e:
            return print(f"Unexpected Error: {e}", file=sys.stderr)
        if not force:
            records = list(filter(lambda r: not man3.joinpath(f"{source}{r.id}.3.gz").exists(), records))  # fmt: off
            records = list(records)
        records = list(records)
        if (length := len(records)) == 0:
            return print("Nothing to fetch.", file=sys.stderr)

        pbar, process = tqdm(total=length), Utils.html_handler(source)

        def on_success(record: Record, resp: str):
            document = process(resp, record)
            Utils.write_man3(man3.joinpath(f"{source}{record.id}.3.gz"), document)
            pbar.update()

        def on_failed(record: Record, exec: Exception):
            print(f"Error={type(exec).__name__}({exec}): {record}", file=sys.stderr)
            pbar.update()

        man3.mkdir(parents=True, exist_ok=True)
        asyncio.run(Utils.afetch(*records, timeout=timeout, limit=limit, on_success=on_success, on_failed=on_failed))  # fmt: off


def main():
    import fire

    fire.Fire(CppRef, name="cppref")
