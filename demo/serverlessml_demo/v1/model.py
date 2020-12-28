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

"""The module defines the v1 of the ``Model`` class."""

import pickle
from typing import Any, Dict, Tuple

from numpy.random import randint, seed
from pandas import DataFrame, Series
from serverlessml_demo.template.model import Model as ModelTemplate
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsClassifier


class Model(ModelTemplate):
    def schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["n_neighbors"],
            "properties": {
                "n_neighbors": {
                    "type": "integer",
                    "default": 5,
                    "exclusiveMinimum": 0,
                },
                "weights": {
                    "type": "string",
                    "default": "uniform",
                    "enum": ["uniform", "distance"],
                },
                "algorithm": {
                    "type": "string",
                    "default": "auto",
                    "enum": ["auto", "ball_tree", "kd_tree", "brute"],
                },
                "leaf_size": {
                    "type": "integer",
                    "default": 10,
                    "exclusiveMinimum": 0,
                },
                "seed": {
                    "type": "integer",
                    "default": 2020,
                    "exclusiveMinimum": 0,
                },
            },
            "additionalProperties": True,
        }

    def _model_definition(self, config: Dict[str, Any]) -> "Model":
        seed(config.get("seed", randint(1, 10000, 1)))
        if config.get("seed"):
            config.pop("seed")

        return KNeighborsClassifier(n_jobs=-1, **config)

    def _fit(self, data: Tuple[DataFrame], target: Tuple[Series]) -> None:
        self.model.fit(data, target)

    def _evaluate(self, y_true: Series, y_pred: Series) -> Dict[str, Any]:
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "f1_score": f1_score(y_true, y_pred, average="macro"),
        }

    def _predict(self, X: DataFrame) -> DataFrame:
        return DataFrame({"class": self.model.predict(X)})

    def _save(self) -> bytes:
        return pickle.dumps(self.model)

    def _load(self, model_obj: bytes) -> "Model":
        return pickle.loads(model_obj)
