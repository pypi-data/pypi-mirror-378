#!/usr/bin/python3
"""
Copyright (c) 2025 Penterep Security s.r.o.

ptvulns is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptvulns is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptvulns.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import importlib
import os
import threading
import subprocess
import shutil
import itertools
import time
import json
import hashlib
import sys; sys.path.append(__file__.rsplit("/", 1)[0])

from types import ModuleType
from urllib.parse import urlparse, urlunparse
from ptlibs import ptjsonlib, ptmisclib, ptnethelper
from ptlibs.ptprinthelper import ptprint, print_banner, help_print, get_colored_text
from ptlibs.threads import ptthreads, printlock
from ptlibs.http.http_client import HttpClient
from ptlibs.app_dirs import AppDirs


from _version import __version__

class PtVulns:
    def __init__(self, args):
        self.args        = args
        self.ptjsonlib   = ptjsonlib.PtJsonLib()
        self.http_client = HttpClient(args=self.args, ptjsonlib=self.ptjsonlib)
        self.app_dirs    = AppDirs("ptvulns")

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
    def run(self) -> None:
        """Main method"""

        cpe = self.args.search
        if not self.is_cpe(cpe):
            # call string to automat that creates cpe and return the cpe string
            cpe_search_path = os.path.join(self.current_dir, '3rd_party', 'cpe_search', 'cpe_search.py')
            ptprint(f"Running CPE search:", "TITLE", (not self.args.json) and self.args.verbose, colortext=True)
            result = self.call_external_script([sys.executable, cpe_search_path, "-q", self.args.search, "--verbose"])
            cpe = self.parse_cpe_from_result(result)


        ptprint(f"Running CVE Finder:", "TITLE", (not self.args.json) and self.args.verbose, colortext=True, newline_above=True, clear_to_eol=True)
        cve_search_path = os.path.join(self.current_dir, '3rd_party', 'cve_finder', '__main__.py')
        result = self.call_external_script([sys.executable, cve_search_path, "--cpe", cpe, "--no-ssl-verify"])

        path = self.get_latest_combined_report_path()

        ptprint(f"CVE report:", "TITLE", (not self.args.json) and self.args.verbose, colortext=True, newline_above=True, clear_to_eol=True)
        self.print_cve_report(path)


        self.ptjsonlib.set_status("finished")
        ptprint(self.ptjsonlib.get_result_json(), "", self.args.json)

    def print_cve_report(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cpe_list = data.get("cpe_list", [])
        for cpe in cpe_list:
            entries = data.get(cpe, [])
            if entries:
                self.ptjsonlib.add_vulnerability("PTV-WEB-SW-KNOWNVULN")

            for entry in entries:
                cve_id = entry["id"]["selected"]
                date = entry["date_published"]["selected"]
                score = entry["score"]["average"]
                desc = entry["desc"]["selected"]

                ptprint(f"CVE: {cve_id}", "TEXT", not self.args.json, indent=0)
                ptprint(f"Published: {date}", "TEXT", not self.args.json, indent=0)
                ptprint(f"Score: {score}", "TEXT", not self.args.json, indent=0)
                ptprint(f"Description: {desc}\n", "TEXT", not self.args.json, indent=0)

                node = self.ptjsonlib.create_node_object(node_type="cve", properties={"cve": cve_id, "published": date, "score": score, "description": desc})
                self.ptjsonlib.add_node(node)

        #os.remove(file_path) # remove the file

    def get_latest_combined_report_path(self):
        # list all files starting with "combined_report_"
        reports_folder = self.app_dirs.get_path("json_reports")
        files = [f for f in os.listdir(reports_folder) if f.startswith("combined_report_")]

        if not files:
            raise FileNotFoundError("No combined_report_ files found in json_reports folder.")

        # select the oldest file based on the lexicographical order of the date part
        oldest_file = min(files, key=lambda f: f[len("combined_report_"):])
        path = os.path.join(reports_folder, oldest_file)

        return path

    def parse_cpe_from_result(self, result: str):
        if result:
            if "could not find software for query:" in result.lower():
                self.ptjsonlib.end_error(f"No CPE found for query: {self.args.search}", condition=self.args.json)
            cpe = result.strip().split("\n")[0]
            return cpe
        else:
            self.ptjsonlib.end_error(f"Error parsing CPE from query: {self.args.search}", condition=self.args.json)

    def is_cpe(self, string: str) -> bool:
        """Check if string is a valid CPE 2.3 formatted string"""
        if not string.startswith("cpe:2.3:"):
            return False

        parts = string.split(":")
        # cpe:2.3:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>
        if len(parts) != 13:
            return False

        part = parts[2]
        if part not in ("a", "o", "h"):  # a = application, o = OS, h = hardware
            return False

        return True


    def call_external_script(self, subprocess_args: list) -> None:
        def spinner_func(stop_event):
            spinner = itertools.cycle(["|", "/", "-", "\\"])
            spinner_dots = itertools.cycle(["."] * 5 + [".."] * 6 + ["..."] * 7)
            if not self.args.json:
                sys.stdout.write("\033[?25l")  # Hide cursor
                sys.stdout.flush()
            while not stop_event.is_set():
                ptprint(get_colored_text(f"[{next(spinner)}] Running ptvulns {next(spinner_dots)}", "TITLE"), "TEXT", not self.args.json, end="\r", flush=True, clear_to_eol=True)
                time.sleep(0.1)
            ptprint(" ", "TEXT", not self.args.json, end="\r", flush=True, clear_to_eol=True)

        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=spinner_func, args=(stop_spinner,))
        spinner_thread.start()
        try:
            # Start the subprocess
            proc = subprocess.Popen(
                subprocess_args,
                stdout=subprocess.PIPE,   # capture stdout
                stderr=subprocess.STDOUT, # merge stderr into stdout
                text=True,                # get strings instead of bytes
                bufsize=1                 # line-buffered
            )

            output_lines = []

            # Read output line by line
            for line in proc.stdout:
                if self.args.verbose and not self.args.json:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                output_lines.append(line)

            # wait for the process to finish
            proc.wait()

            full_output = ''.join(output_lines)
            return full_output

        except subprocess.CalledProcessError as e:
            self.ptjsonlib.end_error("Raised exception:", details=e, condition=self.args.json)

        finally:
            stop_spinner.set()
            spinner_thread.join()
            if not self.args.json:
                sys.stdout.write("\033[?25h")  # Show cursor

    def _check_if_db_loaded(self):
        """Check if cpe .db file is loaded with data"""
        db_file = os.path.join(self.current_dir, '3rd_party', 'cpe_search', 'cpe-search-dictionary.db3')

        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file not found: {db_file}")

        file_size = os.path.getsize(db_file)  # velikost v bajtech
        size_mb = file_size / (1024 * 1024)

        if size_mb < 300:
            print(f"Loading DB ({size_mb:.2f} MB) gonna take a while...")


def get_help():
    """
    Generate structured help content for the CLI tool.

    Returns:
        list: A list of dictionaries, where each dictionary represents a section of help
              content (e.g., description, usage, options). The 'options' section includes
              available command-line flags and dynamically discovered test modules.
    """

    return [
        #{"description": ["ptvulns"]},
        {"usage": ["ptvulns <options>"]},
        {"usage_example": [
            "ptvulns -s \"Apache 2.3\"",
            "ptvulns -s cpe:2.3:a:apache:camel:2.3.0:*:*:*:*:*:*:*  ",
        ]},
        {"options": [
            ["-s",  "--search",                 "<search>",        "Search string for vulns"],
            ["-vv", "--verbose",                "",                 "Show verbose output"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                 "Output in JSON format"],
        ]
        }]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help="False", description=f"{SCRIPTNAME} <options>")
    parser.add_argument("-s",  "--search",         type=str, required=True)
    parser.add_argument("-vv", "--verbose",        action="store_true")
    parser.add_argument("-j",  "--json",           action="store_true")
    parser.add_argument("-v",  "--version",        action='version', version=f'{SCRIPTNAME} {__version__}')

    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprint(help_print(get_help(), SCRIPTNAME, __version__))
        sys.exit(0)

    args = parser.parse_args()

    print_banner(SCRIPTNAME, __version__, args.json, 0)
    return args

def main():
    global SCRIPTNAME
    SCRIPTNAME = os.path.splitext(os.path.basename(__file__))[0]
    args = parse_args()
    script = PtVulns(args)
    script.run()

if __name__ == "__main__":
    main()
