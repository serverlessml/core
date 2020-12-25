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

"""``serverlessml.controllers.config_validator`` is the module
with the logic to validate pipelines invocation config.
"""

from typing import Any, Dict

from fastjsonschema import JsonSchemaException
from fastjsonschema import compile as JsonValidatorCompile

from serverlessml.errors import PipelineConfigError

config_path = {
    "type": "string",
    "description": "Path to a data object.",
    "oneOf": [
        {"description": "File on file system.", "pattern": "^fs://.*?$"},
        {
            "description": "Object in a GCS (GCP) bucket.",
            "pattern": "^gcs://[a-zA-Z0-9_\\-.]{3,63}/.*?$",
        },
        {
            "description": "Object in a s3 bucket.",
            "pattern": "^s3://[a-zA-Z0-9-.]{3,63}/.*?$",
        },
    ],
}

config_uuid4 = {
    "type": "string",
    "pattern": (
        "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$"
    ),
}

schema_train = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "uuid4": config_uuid4,
        "path": config_path,
        "data_location": {
            "type": "object",
            "description": "Data location.",
            "additionalProperties": False,
            "required": ["source"],
            "properties": {"source": {"$ref": "#/definitions/path"}},
        },
        "data_config": {
            "type": "object",
            "description": "Data prep config.",
            "additionalProperties": False,
            "required": ["location", "prep_config"],
            "properties": {
                "location": {"$ref": "#/definitions/data_location"},
                "prep_config": {
                    "type": "object",
                    "description": "Config to prepare data set for model training.",
                },
            },
        },
        "model_config": {
            "type": "object",
            "description": "Model train config.",
            "additionalProperties": False,
            "required": ["hyperparameters", "version"],
            "properties": {
                "hyperparameters": {
                    "type": "object",
                    "description": "Model's hyperparameters configuration.",
                },
                "version": {
                    "type": "string",
                    "description": "Model's version name.",
                    "pattern": "^[a-zA-Z0-9_\\-.|]{1,40}$",
                },
            },
        },
        "item": {
            "type": "object",
            "description": "Pipeline config.",
            "additionalProperties": False,
            "required": ["data", "model"],
            "properties": {
                "data": {"$ref": "#/definitions/data_config"},
                "model": {"$ref": "#/definitions/model_config"},
            },
        },
    },
    "type": "object",
    "title": "Train trigger config schema.",
    "additionalProperties": False,
    "required": ["run_id", "project_id", "code_hash", "pipeline_config"],
    "properties": {
        "project_id": {"description": "ML project ID.", "$ref": "#/definitions/uuid4"},
        "run_id": {"description": "Modelling run ID.", "$ref": "#/definitions/uuid4"},
        "code_hash": {
            "description": "Codebase (git commit) SHA1 hash value.",
            "type": "string",
            "pattern": "^[a-fA-F0-9]{40}$",
        },
        "pipeline_config": {"$ref": "#/definitions/item"},
    },
}


schema_predict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "uuid4": config_uuid4,
        "path": config_path,
        "data_location": {
            "type": "object",
            "description": "Data location.",
            "additionalProperties": False,
            "required": ["source", "destination"],
            "properties": {
                "source": {"$ref": "#/definitions/path"},
                "destination": {"$ref": "#/definitions/path"},
            },
        },
        "data_config": {
            "type": "object",
            "description": "Data prep config.",
            "additionalProperties": False,
            "required": ["location"],
            "properties": {"location": {"$ref": "#/definitions/data_location"}},
        },
        "pipeline_config_item": {
            "type": "object",
            "description": "Data prep config.",
            "additionalProperties": False,
            "required": ["train_id", "data"],
            "properties": {
                "train_id": {
                    "description": "Train experiment/run ID.",
                    "$ref": "#/definitions/uuid4",
                },
                "data": {"$ref": "#/definitions/data_config"},
            },
        },
    },
    "type": "object",
    "title": "Prediction trigger config schema.",
    "additionalProperties": False,
    "required": ["project_id", "run_id", "pipeline_config"],
    "properties": {
        "project_id": {"description": "ML project ID.", "$ref": "#/definitions/uuid4"},
        "run_id": {"description": "Modelling run ID.", "$ref": "#/definitions/uuid4"},
        "pipeline_config": {
            "description": "ML pipeline configuration for prediction.",
            "$ref": "#/definitions/pipeline_config_item",
        },
    },
}


class Validator:
    """``Validator`` defines JSON schema validators for train and predict pipeliens config."""

    def __init__(self):
        """Instantiates the validator."""
        self.validator_train = JsonValidatorCompile(schema_train)
        self.validator_predict = JsonValidatorCompile(schema_predict)

    def train(self, config: Dict[str, Any]) -> None:
        """`train` validates train pipeline's config.

        Args:
            config: Pipeline configuration.

        Raises:
            PipelineConfigError: When config failed validation.
        """
        try:
            _ = self.validator_train(config)
        except JsonSchemaException as ex:
            raise PipelineConfigError(ex.message) from ex

    def predict(self, config: Dict[str, Any]) -> None:
        """`predict` validates predict pipeline's config.

        Args:
            config: Pipeline configuration.

        Raises:
            PipelineConfigError: When config failed validation.
        """
        try:
            _ = self.validator_predict(config)
        except JsonSchemaException as ex:
            raise PipelineConfigError(ex.message) from ex
