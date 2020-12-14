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

"""Module with the definition of abstract IO controllers"""

import importlib
import logging
from abc import ABC, abstractmethod  # type: ignore
from typing import Callable

from serverlessml.errors import InitError  # type: ignore
from serverlessml.errors import ClientFSError, ReadingError, WritingError


class AbstractClientFS(ABC):
    """``AbstractClientFS`` is the base class for all storage clients implementations.
    All storage IO implementations should extend this abstract class
    and implement the methods marked as abstract.
    """

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    def load(self, path: str) -> bytes:
        """Loads data by delegation to the provided load method.

        Args:
            path: Path to file to read data.

        Returns:
            Bytes data returned by the provided load method.

        Raises:
            ReadingError: When underlying load method raises error.
        """
        self._logger.debug("Loading with %s", str(self))

        try:
            return self._load(path)
        except ReadingError:
            raise
        except Exception as ex:
            message = f"Failed while loading data from data set {str(self)}.\n{str(ex)}"
            raise ReadingError(message) from ex

    @abstractmethod
    def _load(self, path: str) -> bytes:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractClientFS and"
            "it must implement the `_load` method"
        )

    def save(self, data: bytes, path: str) -> None:
        """Saves data by delegation to the provided save method.

        Args:
            data: The data to be saved by provided save method.
            path: Path to the file destination to store into.

        Raises:
            ClientFSError: When arguments don't compline with the client requirements.
            WritingError: When underlying save method raises error.
        """

        if data is None:
            raise ClientFSError("Saving `None` is not allowed")

        try:
            self._logger.debug("Saving %s", str(self))
            self._save(data, path)
        except WritingError:
            raise
        except Exception as ex:
            message = f"Failed while saving data to data set {str(self)}.\n{str(ex)}"
            raise WritingError(message) from ex

    @abstractmethod
    def _save(self, data: bytes, path: str) -> None:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractClientFS and"
            "it must implement the `_save` method"
        )

    def exists(self, path: str) -> bool:
        """Checks whether the file exists by calling the provided _exists() method.

        Args:
            path: Path to file to check.

        Returns:
            Flag indicating whether the file exists.

        Raises:
            ClientFSError: When underlying exists method raises error.
        """
        try:
            self._logger.debug("Checking whether target of %s exists", str(self))
            return self._exists(path)
        except Exception as ex:
            message = f"Failed during exists check for data set {str(self)}.\n{str(ex)}"
            raise ClientFSError(message) from ex

    @abstractmethod
    def _exists(self, path: str) -> bool:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractClientFS and"
            "it must implement the `_exists` method"
        )


def get_client_storage(storage_type: str) -> Callable:
    """Instantiates ``Client`` to load/save data from/to the storage e.g. local, aws, gcp.

    Example:
    ::
        >>> from serverlessml.io import get_client_storage
        >>>
        >>> storage_client = get_client_storage(storage_type="gcp")
        >>>
        >>> data_set = storage_client.load(path="gcs://test/test.csv")
        >>> storage_client.save(data_set, path="gcs://test/test1.csv")
        >>> reloaded = storage_client.load(path="gcs://test/test1.csv")
        >>> assert data_set == reloaded

    Args:
        storage_type: Data storage type, i.e. local, gcp, s3.

    Returns:
        Client class instance.

    Raises:
        ClientFSError: Raised when client is not found.
        InitError: Raised when a client couldn't be instantiated.
    """
    try:
        module = importlib.import_module(f"serverlessml.io.{storage_type}.storage", "serverlessml")
    except ModuleNotFoundError as ex:
        raise ClientFSError(f"Client for the '{storage_type}' storage is not implemented") from ex

    try:
        client: Callable = module.Client()  # type: ignore
    except Exception as ex:
        message = f"Client init error:.\n{str(ex)}"
        raise InitError(message) from ex
    return client
