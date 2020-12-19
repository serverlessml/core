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

"""Module to communicate to the local file system."""

from gzip import open as gzip_open
from os.path import exists
from typing import Callable

from serverlessml.controllers.io import AbstractClientStorage


class Client(AbstractClientStorage):
    """``Client`` loads/saves data from/to a local file."""

    def _load(self, path: str) -> bytes:
        _reader: Callable = open
        if path.endswith(".gz"):
            _reader = gzip_open
        with _reader(path, "rb") as fread:
            return fread.read()

    def _save(self, data: bytes, path: str) -> None:
        _writer: Callable = open
        if path.endswith(".gz"):
            _writer = gzip_open
        with _writer(path, "wb") as fwrite:
            fwrite.write(data)

    def _exists(self, path: str) -> bool:
        return exists(path)
