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

"""Module to communicate to GCP GCS."""

from serverlessml.errors import ClientFSError  # type: ignore
from serverlessml.io.controller import AbstractClientFS  # type: ignore


class Client(AbstractClientFS):
    """``Client`` loads/saves data from/to a GCS bucket."""

    @classmethod
    def _validate_prefix(cls, path: str) -> None:
        """Validates the path prefix.

        Args:
            path: Path to the data object.

        Raises:
            ClientFSError: When provided path is not valid.
        """
        if not path.startswith("gcs://"):
            raise ClientFSError("Path must start with 'gcs://'")

    def _load(self, path: str) -> bytes:
        Client._validate_prefix(path)
        return b""

    def _save(self, data: bytes, path: str) -> None:
        self._validate_prefix(path)

    def _exists(self, path: str) -> bool:
        self._validate_prefix(path)
        return False
