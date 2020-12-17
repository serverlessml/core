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

"""Dataset abstraction module."""

import importlib
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable

from serverlessml.errors import DataDecodingError, DataEncodingError, InitError


class AbstractDataSet(ABC):
    """``AbstractDataSet`` is the base class for all data structure formats implementations.
    All data formats implementations should extend this abstract class
    and implement the methods marked as abstract.
    """

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @classmethod
    def from_raw(cls, data: bytes) -> Any:
        """Decodes raw bytes data into a desired data structure format by delegation
        to the provided decode method.

        Args:
            data: Raw bytes data.

        Returns:
            Data set decoded from raw bytes data.

        Raises:
            DataDecodingError: When underlying decore method raises exception.
        """
        logging.getLogger(__name__).debug("Decoding data with %s", str(cls))

        try:
            return cls._from_raw(data=data)
        except DataDecodingError:
            raise
        except Exception as ex:
            message = f"Failed to decode {str(data)}.\n{str(ex)}"
            raise DataDecodingError(message) from ex

    @classmethod
    @abstractmethod
    def _from_raw(cls, data: bytes) -> Any:
        raise NotImplementedError(
            f"`{cls.__class__.__name__}` is a subclass of AbstractDataSet and"
            "it must implement the `_from_raw` method"
        )

    def to_raw(self) -> bytes:
        """Encodes from a desired data structure format to bytes data by delegation
        to the provided encode method.

        Returns:
            Bytes data returned by the provided decode method.

        Raises:
            DataEncodingError: When underlying encode method raises exception.
        """
        self._logger.debug("Encoding data with %s", str(self))

        try:
            return self._to_raw()
        except DataEncodingError:
            raise
        except Exception as ex:
            message = f"Failed to encode.\n{str(ex)}"
            raise DataEncodingError(message) from ex

    @abstractmethod
    def _to_raw(self) -> bytes:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractDataSet and"
            "it must implement the `_to_raw` method"
        )


def dataset_encoder(dataset_filename: str) -> Callable:
    """``dataset_encoder`` dynamically loads a data encoder based on the file extention.

    Args:
        dataset_filename: Dataset filename.

    Returns:
        Instance of an ``AbstractDataSet``'s child-class.

    Raises:
        NotImplementedError: When no encoder is implemeneted for the given file extention.
        InitError: When underlying class couldn't be instantiated.
    """
    supported_ext = {"csv": "pandas", "json": "pandas"}

    if dataset_filename.endswith(".gz"):
        dataset_filename.replace(".gz", "")

    file_ext = dataset_filename.split(".")[-1]

    submodule = supported_ext.get(file_ext)
    if not submodule:
        raise NotImplementedError(
            f"""{file_ext} is not supported. Set one of\n{", ".join(supported_ext)}"""
        )

    try:
        module = importlib.import_module(
            f"serverlessml.data_format.{submodule}.{file_ext}_file", "serverlessml"
        )
        cls_def: Callable = getattr(module, f"{file_ext.upper()}DataSet")  # type: ignore
    except Exception as ex:
        message = f"Init error:\n{str(ex)}."
        raise InitError(message) from ex
    return cls_def
