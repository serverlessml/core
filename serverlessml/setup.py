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

"""ServerlessML package."""
from pathlib import Path

from setuptools import find_namespace_packages, setup  # type: ignore

DIR = Path(__file__).parent
VERSION = DIR.parent / "VERSION"

REQUIREMENTS_BASE = (DIR / "requirements.txt").read_text().split("\n")[:-1]

REQUIREMENTS = {
    "aws": [*REQUIREMENTS_BASE, "boto3==1.16.36"],
    "gcp": [*REQUIREMENTS_BASE, "google-cloud-pubsub==1.7.0", "google-cloud-storage==1.30.0"],
}


def do_setup():
    """Performs ServerlessML setup."""
    setup(
        name="serverlessml",
        version=VERSION,
        description="ServerlessML core package.",
        url="https://www.serverless.org",
        author="Dmitry Kisler",
        author_email="admin@dkisler.com",
        license="Apache 2.0 License",
        classifiers=[
            "Development Status :: 2 - Alpha",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "License :: OSI Approved :: Apache 2.0 License",
            "Operating System :: OS Independent",
        ],
        packages=find_namespace_packages(where=".", exclude=("test",)),
        extras_require=REQUIREMENTS,
    )


if __name__ == "__main__":
    do_setup()
