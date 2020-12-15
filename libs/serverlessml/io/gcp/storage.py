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

from gzip import GzipFile
from io import BytesIO
from typing import Tuple

from google.cloud.storage import Client as StorageClient  # type: ignore
from serverlessml.errors import ClientFSError  # type: ignore
from serverlessml.io.controller import AbstractClientFS  # type: ignore


class Client(AbstractClientFS):
    """``Client`` loads/saves data from/to a GCS bucket."""

    def __init__(self):
        """Initiates connection to gcs using google gcs library."""
        self.client = StorageClient()

    @classmethod
    def _validate_prefix(cls, path: str) -> None:
        """Validates the path prefix.

        Args:
            path: Path to the data object.

        Raises:
            ClientFSError: When provided path is not valid.
        """
        if not path.startswith("gs://"):
            raise ClientFSError("Path must start with 'gs://'")

    @classmethod
    def _split_path(cls, path: str) -> Tuple[str, str]:
        """Splits object path into a tuple of bucket and object path.

        Args:
            path: Path to the data object.

        Returns:
            Tuple with the bucket name and the path to the object/blob in the bucket.
        """
        path_elements = path.replace("gs://", "").split("/")
        return path_elements[0], "/".join(path_elements[1:])

    def _load(self, path: str) -> bytes:
        self._validate_prefix(path)
        bucket, path = self._split_path(path)

        obj = self.client.bucket(bucket).blob(path).download_as_string()

        if path.endswith(".gz"):
            with GzipFile(fileobj=BytesIO(obj), mode="rb") as fread:
                return fread.read()
        return obj

    def _save(self, data: bytes, path: str) -> None:
        self._validate_prefix(path)
        bucket, path = self._split_path(path)
        if path.endswith(".gz"):
            out = BytesIO()
            with GzipFile(fileobj=out, mode="wb") as fwrite:
                fwrite.write(data)
            self.client.bucket(bucket).blob(path).upload_from_string(
                out.getvalue(), content_type="application/gzip"
            )
        else:
            self.client.bucket(bucket).blob(path).upload_from_string(data)

    def _exists(self, path: str) -> bool:
        self._validate_prefix(path)
        bucket, path = self._split_path(path)
        return self.client.bucket(bucket).blob(path).exists()
