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

"""Tool to patch the README.md with the code coderage badde

https://shields.io/ is used to generate badges
"""

import logging
import re
from pathlib import Path

import utils  # type: ignore


def run_gocover(path: Path) -> None:
    """Run gocover."""
    utils.execute_cmd("""""")


def extract_total_coverage(raw: str) -> int:
    """Extract total coverage."""
    tail_line = raw.splitlines()[-1]
    return int(float(tail_line.split("\t")[-1][:-1]))


def generate_url(coverage_pct: float) -> str:
    """Generate badge source URL."""
    color = "yellow"
    if coverage_pct == 100:
        color = "brightgreen"
    elif coverage_pct > 90:
        color = "green"
    elif coverage_pct > 70:
        color = "yellowgreen"
    elif coverage_pct > 50:
        color = "yellow"
    else:
        color = "orange"

    return f"https://img.shields.io/badge/coverage-{coverage_pct}%25-{color}"


def main() -> None:
    """Run."""
    root = Path(__file__).absolute().parents[1]
    path_readme = root / "README.md"
    path_coverage = root / "COVERAGE"
    placeholder_tag = "Code Coverage"
    regexp_pattern = rf"\[\!\[{placeholder_tag}\]\(.*\)\]\(.*\)"

    run_gocover(path_coverage)

    coverage = utils.read(path_coverage)

    coverage_pct = extract_total_coverage(coverage)

    badge_url = generate_url(coverage_pct)

    inpt = utils.read(path_readme)

    search = re.findall(regexp_pattern, inpt)

    if not search:
        raise Exception(f"No placeholder found in README.md. Add '[![{placeholder_tag}]()]()'.")

    placeholder_inject = f"[![{placeholder_tag}]({badge_url})]({badge_url})"

    out = re.sub(regexp_pattern, placeholder_inject, inpt)

    utils.write(out, path_readme)


if __name__ == "__main__":
    log = logging.getLogger("coverage-bump")

    try:
        main()
    except Exception as ex:  # pylint: disable=broad-except
        log.error(ex)
