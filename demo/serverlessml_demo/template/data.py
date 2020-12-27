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

"""``Data`` defines the data preparation class template for serverless ML framework."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Union

from fastjsonschema import validate


class DataConfigError(Exception):
    """Data preparation configuration error."""


class DataValidationError(Exception):
    "Data validation error"


class DataProcessingError(Exception):
    """Data preparation/processing error."""


class DataPreparation(ABC):
    """``DataPreparation`` is the base class for all models implementations.
    All data preparation implementations should extend this abstract class
    and implement the methods marked as abstract.
    """

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """DataPreparation config JSON schema."""
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `schema` property"
        )

    def _get_config_defaults(self) -> Dict[str, Any]:
        """Extracts default config."""
        schema = self.schema()
        return {k: v.get("default") for k, v in schema.get("properties", {}).items()}

    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Creates an instance of the ``DataPreparation`` class.

        Args:
            config: Data preparation configuration.
        """
        self.config = self._validate_config(config) if config else self._get_config_defaults()

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validates the data preparation config.

        Args:
            config: Data preparation configuration.

        Returns:
            Config in case it's valid.

        Raises:
            DataConfigError: When data preparation config fails validation.
        """
        self._logger.debug("Validate data preparation config with %s", str(self))
        try:
            return validate(self.schema(), config)
        except Exception as ex:
            message = f"Config failed validation, the config {config} {str(self)}.\n{str(ex)}"
            raise DataConfigError(message) from ex

    def validate(self, dataset: Any) -> Any:
        """Validates the input dataset.

        Args:
            dataset: Input dataset.

        Returns:
            Dataset in case it passes validation.

        Raises:
            DataValidationError: When underlying validation method raises exception.
        """
        self._logger.debug("Validating the input dataset")
        try:
            return self._validate(dataset)
        except DataValidationError:
            raise
        except Exception as ex:
            message = f"Input data set failed validation.\n{str(ex)}"
            raise DataValidationError(message) from ex

    @abstractmethod
    def _validate(self, dataset: Any) -> Any:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``DataPreparation`` and"
            "it must implement the `_validate` method"
        )

    def process(self, dataset: Any) -> Any:
        """(Pre-)Processes the input dataset.

        Args:
            dataset: Input dataset.

        Returns:
            (Pre-)Processed dataset, e.g. scaling, hotencoding etc.

        Raises:
            DataProcessingError: When underlying processing method raises exception.
        """
        self._logger.debug("Processing the input dataset")
        try:
            return self._process(dataset)
        except DataProcessingError:
            raise
        except Exception as ex:
            message = f"Input data processing failed.\n{str(ex)}"
            raise DataProcessingError(message) from ex

    @abstractmethod
    def _process(self, dataset: Any) -> Any:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``DataPreparation`` and"
            "it must implement the `_process` method"
        )

    def train_test_split(self, dataset: Any) -> Union[Tuple[Any], Tuple[Any, Any]]:
        """Method to split processed dataset to train/test subsets.

        Args:
            dataset: (Pre-)Processed dataset.

        Returns:
            The tuple of data features and targets (X_train, X_test, y_train, y_test),
                or the tuple of (X_train, y_train).
            The results of the method are being used as the input to the ``Model`` `train` method.

        Raises:
            DataProcessingError: When underlying train_test_split method raises exception.
        """
        self._logger.debug("Run data split.")
        try:
            return self._train_test_split(dataset)
        except DataProcessingError:
            raise
        except Exception as ex:
            message = f"Processed data split failed.\n{str(ex)}"
            raise DataProcessingError(message) from ex

    @abstractmethod
    def _train_test_split(self, dataset: Any) -> Union[Tuple[Any], Tuple[Any, Any]]:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``DataPreparation`` and"
            "it must implement the `_train_test_split` method"
        )

    def run(self, dataset: Any) -> Union[Tuple[Any], Tuple[Any, Any]]:
        """Wraps methods for operations to prepare input dataset to be used for model training.

        Args:
            dataset: (Pre-)Processed dataset.

        Returns:
            The tuple of tuples of data features (X_train, X_test) and targets (y_train, y_test),
                or the tuple of (X_train, y_train).
            The results of the method are being used as the input to the ``Model`` `train` method.

        Raises:
            DataValidationError: When the input data fail validation.
            DataProcessingError: When input data processing failed.
        """
        return self.train_test_split(self.process(self.validate(dataset)))
