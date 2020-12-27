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

from fastjsonschema import validate


class ModelConfigError(Exception):
    """Model configuration error."""


class ModelDefinitionError(Exception):
    """Model instantiation error."""


class ModelDeserializationError(Exception):
    """Model deserialization/loading error."""


class ModelSerializationError(Exception):
    """Model serialization/saving error."""


class ModelTrainError(Exception):
    """Model training error."""


class ModelPredictionError(Exception):
    """Model prediction error."""


class Model(ABC):
    """``Model`` is the base class for all models implementations.
    All model implementations should extend this abstract class
    and implement the methods marked as abstract.
    """

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """Model config JSON schema."""
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `schema` property"
        )

    def _get_config_defaults(self) -> Dict[str, Any]:
        """Extracts default config."""
        schema = self.schema()
        return {k: v.get("default") for k, v in schema.get("properties", {}).items()}

    def __init__(self, config: Dict[str, Any] = None, model_obj: bytes = None) -> None:
        """Creates an instance of the ``Model`` class.

        Args:
            config: Model configuration.
            model_obj: Serialized model bytes object.

        Raises:
            ModelConfigError: When config failed validatation.
            ModelDefinitionError: When underlying model definition method raises exception.
            ModelDeserializationError: When underlying method fails
                to deserialize the model bytes object.
        """
        config = config if config else self._get_config_defaults()

        self.model: "Model" = (
            self.load(model_obj)
            if model_obj
            else self.model_definition(self._validate_config(config))
        )

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validates the model config.

        Args:
            config: Model configuration.

        Returns:
            Config in case it's valid.

        Raises:
            ModelConfigError: When model config fails validation.
        """
        self._logger.debug("Validate model's config with %s", str(self))
        try:
            return validate(self.schema(), config)
        except Exception as ex:
            message = f"Config failed validation, the config {config} {str(self)}.\n{str(ex)}"
            raise ModelConfigError(message) from ex

    def model_definition(self, config: Dict[str, Any]) -> "Model":
        """Defines and compiles the model.

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
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `_model_definition` method"
        )

    def fit(self, data: Union[Any, Tuple[Any]], target: Union[Any, Tuple[Any]]) -> None:
        """Trains the model.

        Args:
            data: Dataset of features object(s), i.e. train and test datasets.
            target: Vector(s) of the target values, i.e. Y for train and for test.

            Note! `data` and `target` hall match the output of the ``DataPreparation`` `run` method.
                E.g. it can be the result of the train_test_split method
                from `sklearn.model_selection.train_test_split`.

        Raises:
            ModelTrainError: When underlying fit method raises exception.
        """
        self._logger.debug("Train the model with %s", str(self))
        try:
            self._fit(data, target)
        except ModelTrainError:
            raise
        except Exception as ex:
            message = f"Model training error {str(self)}.\n{str(ex)}"
            raise ModelTrainError(message) from ex

    @abstractmethod
    def _fit(self, data: Union[Any, Tuple[Any]], target: Union[Any, Tuple[Any]]) -> None:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `_train` method"
        )

    def score(self, X: Any, y: List[Any]) -> Dict[str, Any]:
        """Performs calculation of the model's performance metrics.

        Returns:
            Dict of the metrics values.

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
    def _evaluate(self, y_true: Any, y_pred: Any) -> Dict[str, Any]:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
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
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `_predict` method"
        )

    def train(
        self, data: Union[Any, Tuple[Any]], target: Union[Any, Tuple[Any]]
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """Method to perform model training cycle.

        Args:
            data: Data object(s), shall match the output of the ``DataPreparation`` `run` method.
                E.g. it can be the result of the train_test_split method
                from `sklearn.model_selection.train_test_split`.

        Returns:
            Tuple of the model bytes object and the metrics dict.

        Raises:
            ModelTrainError: When underlying fit method raises exception.
        """
        if not isinstance(data, tuple):
            data, target = (data,), (target,)

        data_train, target_train = data[0], target[0]
        self.fit(data_train, target_train)

        # it's assumed that data is a tuple of object
        # with the element 0 being "train", 1 being "test" data sets
        score: List[Dict[str, Any]] = list(self.score(d, t) for d, t in zip(data, target))
        return self.save(), score

    def save(self) -> bytes:
        """Model serialization/saving method.

        Returns:
            Serialized model bytes object.

        Raises:
            ModelSerializationError: When underlying method fails
                to serialize the model bytes object.
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
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `_save` method"
        )

    def load(self, model_obj: bytes) -> "Model":
        """Model deserialization/loading method.

        Args:
            model_obj: Serialized model bytes object.

        Returns:
            Model object.

        Raises:
            ModelDeserializationError: When underlying method fails
                to deserialize the model bytes object.
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
            f"`{self.__class__.__name__}` is a subclass of ``Model`` and"
            "it must implement the `_load` method"
        )
