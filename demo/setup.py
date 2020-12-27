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

"""ServerlessML Model package."""

from pathlib import Path

from setuptools import find_namespace_packages, setup  # type: ignore

DIR = Path(__file__).parent
REQUIREMENTS = ["fastjsonschema==2.14.5"]
REQUIREMENTS_USER_DEFINED = (DIR / "requirements.txt").read_text().split("\n")[:-1]
REQUIREMENTS.extend(REQUIREMENTS_USER_DEFINED)


def do_setup():
    """Performs ServerlessML Demo Model setup."""
    setup(
        name="serverlessml_demo",
        version="1.0",
        description="ServerlessML Model package.",
        url="https://www.serverless.org",
        license="Apache 2.0 License",
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "License :: OSI Approved :: Apache 2.0 License",
            "Operating System :: OS Independent",
        ],
        packages=find_namespace_packages(where=".", exclude=("test",)),
        install_requires=REQUIREMENTS,
    )


if __name__ == "__main__":
    do_setup()
