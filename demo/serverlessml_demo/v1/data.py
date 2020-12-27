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

"""The module defines the v1 of the ``DataPreparation`` class."""

from typing import Any, Dict, Tuple

from pandas import DataFrame, Series
from serverlessml_demo.template.data import DataPreparation as DataPreparationTemplate
from serverlessml_demo.template.data import DataValidationError
from sklearn.model_selection import train_test_split


class DataPreparation(DataPreparationTemplate):
    def schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "test_size": {
                    "type": "number",
                    "default": 0.25,
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
                "seed": {
                    "type": "integer",
                    "default": 2020,
                    "exclusiveMinimum": 0,
                },
            },
            "additionalProperties": False,
        }

    def _validate(self, dataset: DataFrame) -> DataFrame:
        required_columns = {
            "sepal_length_cm",
            "sepal_width_cm",
            "petal_length_cm",
            "petal_width_cm",
            "class",
        }

        missing_columns = required_columns.difference(set(dataset.columns))
        if missing_columns:
            missing = ",\n".join(missing_columns)
            raise DataValidationError(f"Data set is missing the columns:\n{missing}")

        return dataset

    def _process(self, dataset: DataFrame) -> Tuple[DataFrame, Series]:
        target = dataset["class"]
        data = dataset.drop(["class"], axis=1)
        return data, target

    def _train_test_split(self, dataset: Tuple[DataFrame, Series]) -> Tuple[DataFrame, DataFrame]:
        X_train, X_test, y_train, y_test = train_test_split(
            dataset[0],
            dataset[1],
            test_size=self.config.get("test_size"),
            random_state=self.config.get("seed"),
        )
        return (X_train.reset_index(drop=True), X_test.reset_index(drop=True)), (
            y_train.reset_index(drop=True),
            y_test.reset_index(drop=True),
        )
