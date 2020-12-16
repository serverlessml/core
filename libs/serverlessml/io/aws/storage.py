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

"""Module to communicate to AWS S3."""

from gzip import GzipFile
from io import BytesIO
from typing import Tuple

import boto3  # type: ignore

from ...errors import ClientStorageError  # type: ignore; type: ignore
from ..controller import AbstractClientStorage  # type: ignore


class Client(AbstractClientStorage):
    """``Client`` loads/saves data from/to a S3 bucket."""

    def __init__(self):
        """Initiates connection to S3 using google boto3 library."""
        self.client = boto3.client("s3")

    @classmethod
    def _validate_prefix(cls, path: str) -> None:
        """Validates the path prefix.

        Args:
            path: Path to the data object.

        Raises:
            ClientStorageError: When provided path is not valid.
        """
        if not path.startswith("s3://"):
            raise ClientStorageError("Path must start with 's3://'")

    @classmethod
    def _split_path(cls, path: str) -> Tuple[str, str]:
        """Splits object path into a tuple of bucket and object path.

        Args:
            path: Path to the data object.

        Returns:
            Tuple with the bucket name and the path to the object/blob in the bucket.
        """
        path_elements = path.replace("s3://", "").split("/")
        return path_elements[0], "/".join(path_elements[1:])

    def _load(self, path: str) -> bytes:
        self._validate_prefix(path)
        bucket, path = self._split_path(path)

        obj = self.client.get_object(Bucket=bucket, Key=path).get("Body")
        if not obj:
            raise ClientStorageError(f"No object {path} found")

        if path.endswith(".gz"):
            with GzipFile(fileobj=obj, mode="rb") as fread:
                return fread.read()
        return obj.read()

    def _save(self, data: bytes, path: str) -> None:
        self._validate_prefix(path)
        bucket, path = self._split_path(path)

        if path.endswith(".gz"):
            out = BytesIO()
            with GzipFile(fileobj=out, mode="wb") as fwrite:
                fwrite.write(data)
            self.client.put_object(Body=out.getvalue(), Bucket=bucket, Key=path)
        else:
            self.client.put_object(Body=data, Bucket=bucket, Key=path)

    def _exists(self, path: str) -> bool:
        self._validate_prefix(path)
        bucket, path = self._split_path(path)
        resp = self.client.list_objects(Bucket=bucket, Prefix=path)
        return resp.get("Contents") is not None
