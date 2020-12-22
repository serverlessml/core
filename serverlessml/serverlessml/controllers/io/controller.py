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

"""``serverlessml.io.controller`` is the module
with the centralized IO clients controller.
"""

import importlib
import json
import os
from datetime import datetime
from typing import Any, Callable, Dict

from serverlessml.data_format import dataset_encoder  # type: ignore
from serverlessml.errors import InitError  # type: ignore


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
        module = importlib.import_module(
            f"serverlessml.handlers.{platform}.io.{service}", "serverlessml"
        )
        class_instance: Callable = module.Client(**_config)  # type: ignore
    except Exception as ex:
        message = f"Client init error:\n{str(ex)}"
        raise InitError(message) from ex
    return class_instance


class _ControllerGeneric:
    """``_ControllerGeneric`` controlls IO interactions.

    Raises:
        ClientStorageError: When underlying storage client fails.
        NotImplementedError: When no encoder is implemeneted for the given file extention.
        InitError: When underlying class couldn't be instantiated.
    """

    BUCKET = "serverlessml-pipeline"
    PATH_PREFIX = {
        "aws": "s3://",
        "gcp": "gs://",
        "local": "",
    }

    def __init__(self, project_id: str, run_id: str, platform: str, **kwargs):
        """Instantiates ``_ControllerGeneric`` to interface platforms e.g. local, aws, gcp.

        Args:
            project_id: Model project ID.
            run_id: Experiment/run ID.
            platform: Env platform, i.e. local, gcp, s3.
            kwargs: Additional config attributes, e.g. AWS region.

        Raises:
            NotImplementedError: When no controller is implemeneted for the given platform.
            InitError: When a client couldn't be instantiated.
        """

        self.project_id = project_id
        self.run_id = run_id
        self.uri_prefix = self.PATH_PREFIX[platform]
        self.storage_client = client(platform=platform, service="storage", **kwargs)

        self.prefix = os.path.join(
            self.uri_prefix,
            self.BUCKET,
            project_id,
        )

        self.prefix_per_run = os.path.join(
            self.prefix,
            "runs",
            run_id,
        )

        self.path = {
            "metadata": f"{self.prefix_per_run}/metadata_{run_id}.json",
            "metrics": f"{self.prefix_per_run}/metrics_{run_id}.json",
            "model": f"{self.prefix_per_run}/model/model_{run_id}.bin",
        }

    @classmethod
    def get_object_name(cls, path: str) -> str:
        """Returns object name.

        Args:
            path: Location of the data file.

        Returns:
            Object name.
        """
        return os.path.basename(path)


class _Load(_ControllerGeneric):
    """``_Load`` controlls reading IO interactions."""

    @classmethod
    def _from_json(cls, obj: bytes) -> Dict[str, Any]:
        """Decodes JSON to dict.

        Args:
            obj: Dict to dencode.

        Returns:
            Decoded JSON.
        """
        return json.loads(obj)

    def data(self, path: str) -> Any:
        """Reads the dataset.

        Args:
            path: Location of the data file.

        Returns:
            Dataset object.
        """
        data_bytes = self.storage_client.load(path)  # type: ignore
        data_encoder = dataset_encoder(self.get_object_name(path))
        return data_encoder.from_raw(data_bytes)  # type: ignore

    def metadata(self) -> Dict[str, Any]:
        """Reads the metadata.

        Returns:
            Metadata dict.
        """
        data_bytes = self.storage_client.load(self.path["metadata"])  # type: ignore
        return self._from_json(data_bytes)

    def model(self) -> bytes:
        """Reads the model bytes encoded file.

        Returns:
            Model bytes encoded object.
        """
        return self.storage_client.load(self.path["model"])  # type: ignore


class _Save(_ControllerGeneric):
    """``_Save`` controlls writing IO interactions."""

    @classmethod
    def _to_json(cls, obj: Dict[str, Any]) -> bytes:
        """Encodes dict to JSON.

        Args:
            obj: Dict to encode.

        Returns:
            Bytes encoded JSON.
        """
        return json.dumps(obj).encode("UTF-8")

    def data(self, data: Any, path: str) -> None:
        """Writes the dataset.

        Args:
            data: Dataset object to store.
            path: Location of the data file.
        """
        data_encoder = dataset_encoder(self.get_object_name(path))(data)
        data_bytes = data_encoder.to_raw()
        self.storage_client.save(data_bytes, path)  # type: ignore

    def metadata(self, data: Dict[str, Any]) -> None:
        """Writes the metadata.

        Args:
            data: Metadata dict.
        """
        data_bytes = self._to_json(data)
        self.storage_client.save(data_bytes, self.path["metadata"])  # type: ignore

    def metrics(self, data: Dict[str, Any]) -> None:
        """Writes the metrics.

        Args:
            data: Metics dict.
        """
        data_bytes = self._to_json(data)
        self.storage_client.save(data_bytes, self.path["metrics"])  # type: ignore

    def run_type(self, run_type: str) -> None:
        """Writes the pipeline experiement's type, i.e. train, or predict.

        Args:
            run_type: ML pipeline: train, or predict.
        """
        self.storage_client.save(b"", f"{self.prefix}/{run_type}/{self.run_id}")  # type: ignore

    def model(self, model: bytes) -> None:
        """Writes the model bytes encoded file.

        Args:
            model: Model bytes encoded object.
        """
        self.storage_client.save(model, self.path["model"])  # type: ignore

    def status(self, status: str, **kwargs) -> None:
        """Writes a pipeline status.

        Args:
            status: Pipeline status.
            kwargs: Additional status attributes.
        """
        now = datetime.utcnow()
        epoch = int(now.timestamp())
        data = {
            **{
                "project_id": self.project_id,
                "run_id": self.run_id,
                "timestamp": now.isoformat(),
                "status": status,
            },
            **kwargs,
        }

        paths = [
            f"{self.prefix_per_run}/status/{self.run_id}_{epoch}.json",
            f"{self.prefix}/status/last.json",
        ]

        for path in paths:
            self.storage_client.save(self._to_json(data), path)  # type: ignore


class Controller:  # pylint: disable=too-few-public-methods
    """``Controller`` controlls IO interactions."""

    def __init__(self, project_id: str, run_id: str, platform: str, **kwargs):
        """Instantiates ``Controller`` to interface platforms e.g. local, aws, gcp.

        Example:
        ::
            >>> from serverlessml.io import Controller
            >>>
            >>> controller = Controller(
            >>>     platform="gcp", run_id="d0c5857d-59d2-44b0-ba1d-341e4971e15d",
            >>> )

        Args:
            project_id: Model project ID.
            run_id: Experiment/run ID.
            platform: Env platform, i.e. local, gcp, aws.
            kwargs: Additional config attributes, e.g. AWS region.

        Raises:
            NotImplementedError: When no controller is implemeneted for the given platform.
            InitError: When a client couldn't be instantiated.
        """
        self.load = _Load(project_id, run_id, platform, **kwargs)
        self.save = _Save(project_id, run_id, platform, **kwargs)
