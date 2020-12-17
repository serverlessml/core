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
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

from serverlessml.errors import ClientBusError, ClientStorageError, InitError


class AbstractClientBus(ABC):
    """``AbstractClientBus`` is the base class for all message bus clients implementations.
    All storage message brokers/bus clients implementations should extend this abstract class
    and implement the methods marked as abstract.
    """

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    def push(self, topic: str, payload: Dict[str, Any]) -> None:
        """Publishes a message by delegation to the provided publish method.

        Args:
            topic: Message broker topic name to publish.
            payload: Message content.

        Raises:
            ClientBusError: When underlying method raises exception.
        """
        self._logger.debug("Pushing message to to a topic %s with %s", topic, str(self))

        if payload is None:
            raise ClientBusError("Pushing `None` is not allowed")

        try:
            self._push(topic=topic, payload=payload)
        except ClientBusError:
            raise
        except Exception as ex:
            message = f"Failed to publish {json.dumps(payload)} to {topic} {str(self)}.\n{str(ex)}"
            raise ClientBusError(message) from ex

    @abstractmethod
    def _push(self, topic: str, payload: Dict[str, Any]) -> None:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractClientBus and"
            "it must implement the `_push` method"
        )

    def get_topic_path(self, topic: str) -> str:
        """Requests the full topic by delegation to the provided get_topic_path method..

        Args:
            topic: Message broker topic name to publish.

        Returns:
            Topic path.

        Raises:
            ClientBusError: When underlying method raises exception.
        """
        self._logger.debug("Requesting path to the topic %s with %s", topic, str(self))

        try:
            return self._get_topic_path(topic=topic)
        except Exception as ex:
            message = f"Failed to return path to the topic {topic} {str(self)}.\n{str(ex)}"
            raise ClientBusError(message) from ex

    @abstractmethod
    def _get_topic_path(self, topic: str) -> str:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractClientBus and"
            "it must implement the `_get_topic_path` method"
        )


class AbstractClientStorage(ABC):
    """``AbstractClientStorage`` is the base class for all storage clients implementations.
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
            ClientStorageError: When underlying load method raises exception.
        """
        self._logger.debug("Loading with %s", str(self))

        try:
            return self._load(path)
        except ClientStorageError:
            raise
        except Exception as ex:
            message = f"Failed while loading data from data set {str(self)}.\n{str(ex)}"
            raise ClientStorageError(message) from ex

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
            ClientStorageError: When arguments don't compline with the client requirements.
        """
        self._logger.debug("Saving %s", str(self))

        if data is None:
            raise ClientStorageError("Saving `None` is not allowed")

        try:
            self._save(data, path)
        except ClientStorageError:
            raise
        except Exception as ex:
            message = f"Failed while saving data to data set {str(self)}.\n{str(ex)}"
            raise ClientStorageError(message) from ex

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
            ClientStorageError: When underlying exists method raises exception.
        """
        try:
            self._logger.debug("Checking whether target of %s exists", str(self))
            return self._exists(path)
        except Exception as ex:
            message = f"Failed during exists check for data set {str(self)}.\n{str(ex)}"
            raise ClientStorageError(message) from ex

    @abstractmethod
    def _exists(self, path: str) -> bool:
        raise NotImplementedError(
            f"`{self.__class__.__name__}` is a subclass of AbstractClientFS and"
            "it must implement the `_exists` method"
        )


def client(platform: str, service: str, **kwargs) -> Callable:
    """Instantiates ``Client`` to interface platforms e.g. local, aws, gcp.

    Example:
    ::
        >>> from serverlessml.io import client
        >>>
        >>> storage_client = client(platform="gcp", service="storage")
        >>>
        >>> data_set = storage_client.load(path="gcs://test/test.csv")
        >>> storage_client.save(data_set, path="gcs://test/test1.csv")
        >>> reloaded = storage_client.load(path="gcs://test/test1.csv")
        >>> assert data_set == reloaded
        >>>
        >>> bus_client = client(platform="gcp", service="bus")
        >>>
        >>> message = {"foo": "bar"}
        >>> bus_client.push(topic="test", data=message)

    Args:
        platform: Env platform, i.e. local, gcp, s3.
        service: The name of the service, e.g. storage, bus.
        kwargs: Additional config attributes, e.g. AWS region.

    Returns:
        Client class instance.

    Raises:
        NotImplementedError: When no client is implemeneted for the given service and/or platform.
        InitError: When a client couldn't be instantiated.
    """

    supported_platforms = ("local", "aws", "gcp")
    supported_services = ("storage", "bus")

    if platform not in supported_platforms:
        raise NotImplementedError(
            f"""{platform} is not supported. Set one of\n{", ".join(supported_platforms)}"""
        )

    if service not in supported_services:
        raise InitError(
            f"""{service} is not supported. Set one of\n{", ".join(supported_services)}"""
        )

    _config = {}
    if platform == "aws" and service == "bus":
        _config["region"] = kwargs.get("region", "")

    try:
        module = importlib.import_module(f"serverlessml.io.{platform}.{service}", "serverlessml")
        class_instance: Callable = module.Client(**_config)  # type: ignore
    except Exception as ex:
        message = f"Client init error:\n{str(ex)}"
        raise InitError(message) from ex
    return class_instance
