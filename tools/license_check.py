#! /usr/local/bin/python3

# Copyright 2020 dkisler.com Dmitry Kisler
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""License header check and patch."""

import logging
import os
import sys
from pathlib import Path
from typing import List

import utils  # type: ignore

ROOT = Path(__file__).absolute().parents[1]
PATH_LICENSE_HEADER = "LICENSE_HEADER.md"


def files_at_path(path: str) -> List[str]:
    """Gets the list of file paths to codebase modules."""
    output = []
    for i in os.listdir(path):
        path_deep = f"{path}/{i}"
        if os.path.isdir(path_deep):
            output.extend(files_at_path(path_deep))
        elif path_deep.endswith(".py"):
            output.append(path_deep)
    return output


def adds_comment_sign(data: str, comment_sign: str) -> str:
    """Adds comment signs to the string."""
    return "\n".join(list(f"{comment_sign} {line}".strip() for line in data.split("\n")[:-1]))


def throw_missing_license(header: str, files_list: List[str]) -> None:
    """Throw error with the list of files with missing license header."""
    red_color = "\033[0;31m"
    no_color = "\033[0m"
    sys.exit(
        red_color
        + "The legal header is missing in the files:\n- "
        + "\n- ".join(files_list)
        + no_color
        + "\nPlease add it by copy-pasting the below:\n\n"
        + header
        + "\n"
    )


def main() -> None:
    """Run."""
    header = utils.read(ROOT / PATH_LICENSE_HEADER)
    header = adds_comment_sign(header, "#")

    files_codebase = files_at_path(str(ROOT))

    files_missing_header = [
        ifile for ifile in files_codebase if header not in utils.read(ifile).strip()
    ]
    if files_missing_header:
        throw_missing_license(header, files_missing_header)


if __name__ == "__main__":
    log = logging.getLogger("license-fix")

    try:
        main()
    except Exception as ex:  # pylint: disable=broad-except
        log.error(ex)
