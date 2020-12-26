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

"""``Model`` defines the model template for serverless ML framework."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union

from serverlessml.errors import (
    ModelDefinitionError,
    ModelDeserializationError,
    ModelPredictionError,
    ModelSerializationError,
    ModelTrainError,
)


class Model(ABC):
    """``Model`` is the base class for all models implementations.
    All model implementations should extend this abstract class
    and implement the methods marked as abstract.
    """

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    def __init__(self, config: Dict[str, Any], model_obj: bytes = None) -> None:
        """Creates an instance of the ``Model`` class.

        Args:
            config: Model configuration.
            model_obj: Serialized model bytes object.
        """
        self.config: Dict[str, Any] = config
        self.model: Model = self.load(model_obj) if model_obj else self.model_definition(config)

    @abstractmethod
    def model_definition(self, config: Dict[str, Any]) -> "Model":
        """Function to define and compile the model.

        Args:
            config: Model configuration.

        Returns:
            Model object.

        Raises:
            ModelDefinitionError: When underlying model definition method raises exception.
        """
        self._logger.debug("Define the model with %s", str(self))
        try:
            return self._model_definition(config)
        except ModelDefinitionError:
            raise
        except Exception as ex:
            message = f"Failed to define the model, the config {config} {str(self)}.\n{str(ex)}"
            raise ModelDefinitionError(message) from ex

    @abstractmethod
    def _model_definition(self, config: Dict[str, Any]) -> "Model":
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of Model and"
            "it must implement the `_model_definition` method"
        )

    def fit(self, data: Union[Any, Tuple[Any]]) -> None:
        """Trains the model.

        Args:
            data: Data object(s), shall match the output of the ``DataPreparation`` `run` method.
                E.g. it can be the result of the train_test_split method
                from `sklearn.model_selection.train_test_split`.

        Raises:
            ModelTrainError: When underlying fit method raises exception.
        """
        self._logger.debug("Train the model with %s", str(self))
        try:
            self._fit(data)
        except ModelTrainError:
            raise
        except Exception as ex:
            message = f"Model training error {str(self)}.\n{str(ex)}"
            raise ModelTrainError(message) from ex

    @abstractmethod
    def _fit(self, data: Union[Any, Tuple[Any]]) -> None:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of Model and"
            "it must implement the `_train` method"
        )

    def score(self, X: Any, y: List[Any]) -> Dict[str, Any]:
        """Performs calculation of the model's performance metrics.

        Args:
            X: Data features.
            y: List of target values.
        """
        self._logger.debug("Performs model's performance evaluation with %s", str(self))
        y_pred = self.predict(X)
        return self.evaluate(y, y_pred)

    def evaluate(self, y_true: List[Any], y_pred: List[Any]) -> Dict[str, Any]:
        """Calculates metrics.

        Args:
            y_true: True values.
            y_pred: Prediction results.

        Returns:
            Dict of the metrics values.

        Raises:
            ModelTrainError: When underlying evaluate method raises exception.
        """
        try:
            return self._evaluate(y_true, y_pred)
        except ModelTrainError:
            raise
        except Exception as ex:
            message = f"Model evaluation error {str(self)}.\n{str(ex)}"
            raise ModelTrainError(message) from ex

    @abstractmethod
    def _evaluate(self, y_true: List[Any], y_pred: List[Any]) -> Dict[str, Any]:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of Model and"
            "it must implement the `_evaluate` method"
        )

    def predict(self, X: Any) -> Any:
        """Runs prediction with the trained model.

        Args:
            X: Data features.

        Returns:
            Prediction results.

        Raises:
            ModelPredictionError: When underlying predict method raises exception.
        """
        self._logger.debug("Run prediction with the model with %s", str(self))
        try:
            return self._predict(X)
        except ModelPredictionError:
            raise
        except Exception as ex:
            message = f"Model prediction error {str(self)}.\n{str(ex)}"
            raise ModelPredictionError(message) from ex

    @abstractmethod
    def _predict(self, X: Any) -> Any:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of Model and"
            "it must implement the `_predict` method"
        )

    @abstractmethod
    def save(self) -> bytes:
        """Model serialization/saving method.

        Returns:
            Serialized model bytes object.
        """
        self._logger.debug("Saves/serializes the model with %s", str(self))
        try:
            return self._save()
        except ModelSerializationError:
            raise
        except Exception as ex:
            message = f"Model serialization error {str(self)}.\n{str(ex)}"
            raise ModelSerializationError(message) from ex

    @abstractmethod
    def _save(self) -> bytes:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of Model and"
            "it must implement the `_save` method"
        )

    def load(self, model_obj: bytes) -> "Model":
        """Model deserialization/loading method.

        Args:
            model_obj: Serialized model bytes object.
        """
        self._logger.debug("Loads/deserializes the model bytes object with %s", str(self))
        try:
            return self._load(model_obj)
        except ModelDeserializationError:
            raise
        except Exception as ex:
            message = f"Model deserialization error {str(self)}.\n{str(ex)}"
            raise ModelDeserializationError(message) from ex

    @abstractmethod
    def _load(self, model_obj: bytes) -> "Model":
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of Model and"
            "it must implement the `_load` method"
        )
