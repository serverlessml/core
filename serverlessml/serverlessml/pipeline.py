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

"""``serverlessml.pipeline`` is the module
with the train and predict pipeline runner definition.
"""

import importlib
import logging
from types import ModuleType
from typing import Any, Callable, Dict, Optional

from serverlessml.controllers import ControllerIO, Validator
from serverlessml.errors import (
    InitError,
    ModelDefinitionError,
    PipelineConfigError,
    PipelineRunningError,
)


class PipelineRunner:
    """``Runner`` executes ML pipeline."""

    @property
    def _logger(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(linenum)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger(__name__)

    def __init__(self, controller_io: Callable):
        """Instantiates ``Runner`` to execute training and prediction pipelines.

        Args:
            controller_io: IO controller "factory".
        """
        self.controller_io_factory = controller_io
        self.validate = Validator()
        self.controller_io: ControllerIO = None  # type: ignore

    def _instantiate_io_controller(self, run_id: str) -> None:
        """Instantiates IO controller using run_id to map artifacts to the storage location.

        Args:
            run_id: Experiment/run ID.

        Raises:
            InitError: When a client couldn't be instantiated.
        """
        try:
            self.controller_io = self.controller_io_factory(run_id=run_id)
        except Exception as ex:
            message = f"IO Controller error: {ex}"
            self._logger.error(message)
            raise InitError(message) from ex

    def _error(self, message: str) -> None:
        self._logger.error(message)
        self.controller_io.save.status(status="FAILED", error=message)
        raise PipelineRunningError(message)

    def _load_pipeline_definition_module(
        self, model_configs: Dict[str, Any]
    ) -> Optional[ModuleType]:
        """Loads module with the pipeline defintion.

        Args:
            model_configs: Model configurations.

        Returns:
            Module with the user defined pipelines definitions.

        Raises:
            ModelDefinitionError: When underlying model's class failed to be instantiated.
        """
        try:
            model_version: str = model_configs.get("version", "")
            model_package_name = ".".join(model_version.split(".")[:-1])
            udm = importlib.import_module(f"{model_version}.pipeline", model_package_name)
        except ModelDefinitionError as ex:
            message = str(ex)
            self._logger.error(message)
            self.controller_io.save.status(status="FAILED", error=message)
            raise ex
        except Exception as ex:
            self._error(f"Failed loading the model code: {ex}")
        return udm

    def train(self, config: Dict[str, Any]) -> None:
        """`train` runs training pipeline.

        Args:
            config: Pipeline configuration.

        Raises:
            PipelineConfigError: When config failed validation.
            PipelineRunningError: When pipeline failed.
            ModelDefinitionError: When underlying model's class failed to be instantiated.
        """
        self._logger.debug("Running train pipeline.")
        try:
            self.validate.train(config)
        except PipelineConfigError as ex:
            self._error(f"Faulty config submitted: {ex}")

        self._instantiate_io_controller(config.get("run_id", None))

        self.controller_io.save.status(status="RUNNING")
        self.controller_io.save.run_type(run_type="train")
        self.controller_io.save.metadata(config)

        pipeline_cfg: Dict[str, Any] = config.get("pipeline_config", {})
        model_cfg: Dict[str, Any] = pipeline_cfg.get("model", {})
        data_cfg: Dict[str, Any] = pipeline_cfg.get("data", {})

        model_module = self._load_pipeline_definition_module(model_cfg)

        try:
            path_data_source: str = data_cfg.get("location", {}).get("source", "")
            dataset = self.controller_io.load.data(path_data_source)
        except Exception as ex:
            self._error(f"Failed to load data: {ex}")

        try:
            pipeline = model_module.PipelineTrain(  # type: ignore
                model_config=model_cfg.get("hyperparameters"),
                data_config=data_cfg.get("prep_config"),
                dataset=dataset,
            )
            model, metrics = next(pipeline.run())
        except Exception as ex:
            self._error(f"Failed while running user defined pipeline: {ex}")

        self.controller_io.save.model(model)
        self.controller_io.save.metrics(metrics)
        self.controller_io.save.status(status="SUCCESS")

    def predict(self, config: Dict[str, Any]) -> None:
        """`predict` runs prediction pipeline.

        Args:
            config: Pipeline configuration.

        Raises:
            PipelineConfigError: When config failed validation.
            PipelineRunningError: When pipeline failed.
        """
        self._logger.debug("Running prediction pipeline.")
        try:
            self.validate.predict(config)
        except PipelineConfigError as ex:
            self._error(f"Faulty config submitted: {ex}")

        self._instantiate_io_controller(config.get("run_id", None))

        self.controller_io.save.status(status="RUNNING")
        self.controller_io.save.run_type(run_type="predict")
        self.controller_io.save.metadata(config)

        pipeline_cfg: Dict[str, Any] = config.get("pipeline_config", {})

        train_id: str = pipeline_cfg.get("train_id", "")
        controller_io_train = self.controller_io_factory(run_id=train_id)

        pipeline_cfg_train: Dict[str, Any] = controller_io_train.load.metadata()
        model_cfg: Dict[str, Any] = pipeline_cfg_train.get("pipeline_config", {}).get("model", {})

        model: bytes = controller_io_train.load.model()
        model_module = self._load_pipeline_definition_module(model_cfg)

        data_cfg: Dict[str, Any] = pipeline_cfg.get("data", {})
        path_data_source: str = data_cfg.get("location", {}).get("source", "")
        path_data_destination: str = data_cfg.get("location", {}).get("destination", "")

        try:
            dataset_in = self.controller_io.load.data(path_data_source)
        except Exception as ex:
            self._error(f"Failed to load data: {ex}")

        try:
            pipeline = model_module.PipelinePredict(  # type: ignore
                model=model,
                dataset=dataset_in,
            )
            dataset_out = next(pipeline.run())
        except Exception as ex:
            self._error(f"Failed while running user defined pipeline: {ex}")

        self.controller_io.save.data(dataset_out, path=path_data_destination)
        self.controller_io.save.status(status="SUCCESS")
