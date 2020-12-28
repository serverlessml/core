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

"""Module with integration/e2e tests.

Requires:
- requests
- fastjsonschema
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

DIR = Path(__file__).parent

PORT = os.getenv("PORT", "8080")
SOCKET = f"http://0.0.0.0:{PORT}"

BUCKET_BASE = "serverlessml"

PROJECT_ID = "0cba82ff-9790-454d-b7b9-22570e7ba28c"
RUN_ID = {
    "train": "c77d0a32-2b29-47f6-9ac5-67a21f7953b9",
    "predict": "9a3a8c44-da7a-4e42-9232-2fd1af91fb3e",
}

DIR_META = os.path.join(DIR, f"""{BUCKET_BASE}-{PROJECT_ID}""")

CONFIG: Dict[str, Any] = {
    "project_id": PROJECT_ID,
    "train": {
        "payload": {
            "project_id": PROJECT_ID,
            "code_hash": "8c2f3d3c5dd853231c7429b099347d13c8bb2c37",
            "run_id": RUN_ID["train"],
            "pipeline_config": {
                "data": {
                    "location": {"source": "storage/data/input/iris.csv"},
                    "prep_config": {"test_size": 0.33, "seed": 42},
                },
                "model": {
                    "hyperparameters": {"n_neighbors": 3, "seed": 42},
                    "version": "serverlessml_demo.v1",
                },
            },
        },
        "ls": {
            "": ["runs", "status", "train"],
            "status": ["last.json"],
            "train": [RUN_ID["train"]],
            f"""runs/{RUN_ID["train"]}""": [
                "status",
                "model",
                f"""metadata_{RUN_ID["train"]}.json""",
                f"""metrics_{RUN_ID["train"]}.json""",
            ],
            f"""runs/{RUN_ID["train"]}/model""": [f"""model_{RUN_ID["train"]}.bin"""],
        },
        "metrics_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": {"elapsed_time": {"type": "number", "minimum": 0.0}},
            "type": "object",
            "required": ["elapsed", "user_defined_metrics"],
            "properties": {
                "elapsed": {
                    "type": "object",
                    "required": ["data_read", "data_prep", "logic_execution"],
                    "properties": {
                        "data_read": {"$ref": "#/definitions/elapsed_time"},
                        "data_prep": {"$ref": "#/definitions/elapsed_time"},
                        "logic_execution": {"$ref": "#/definitions/elapsed_time"},
                    },
                    "additionalProperties": False,
                },
                "user_defined_metrics": {"type": "array"},
            },
            "additionalProperties": False,
        },
    },
    "predict": {
        "payload": {
            "project_id": PROJECT_ID,
            "run_id": RUN_ID["predict"],
            "pipeline_config": {
                "train_id": RUN_ID["train"],
                "data": {
                    "location": {
                        "source": "storage/data/input/prediction_input.csv",
                        "destination": "storage/data/output/prediction_output.csv",
                    }
                },
            },
        },
        "ls": {
            "": ["runs", "status", "predict"],
            "status": ["last.json"],
            "predict": [RUN_ID["predict"]],
            f"""runs/{RUN_ID["predict"]}""": [
                "status",
                f"""metadata_{RUN_ID["predict"]}.json""",
                f"""metrics_{RUN_ID["predict"]}.json""",
            ],
            "../storage/data/output/": ["prediction_output.csv"],
        },
        "metrics_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": {"elapsed_time": {"type": "number", "minimum": 0.0}},
            "type": "object",
            "required": ["elapsed"],
            "properties": {
                "elapsed": {
                    "type": "object",
                    "required": ["data_read", "logic_execution", "data_write"],
                    "properties": {
                        "data_read": {"$ref": "#/definitions/elapsed_time"},
                        "logic_execution": {"$ref": "#/definitions/elapsed_time"},
                        "data_write": {"$ref": "#/definitions/elapsed_time"},
                    },
                    "additionalProperties": False,
                }
            },
        },
    },
}


def test_status() -> None:
    resp = get(f"{SOCKET}/status")
    assert resp.status_code == 200, "status endpoint"


def test_post(endpoint: str) -> None:
    resp = post(url=f"{SOCKET}/{endpoint}", json=CONFIG[endpoint]["payload"])
    assert resp.status_code == 200, f"[{endpoint}] failed run"


def test_metadata_storage(endpoint: str) -> None:
    for suff, lst_expected in CONFIG[endpoint]["ls"].items():
        path = os.path.join(DIR_META, suff)
        dirs_list = set(os.listdir(path))
        missing = set(lst_expected).difference(dirs_list)
        assert missing == set(), f"[{endpoint}] dir {path} failed meta storage"


def test_metadata(endpoint: str) -> None:
    payload = CONFIG[endpoint]["payload"]
    with open(
        f"""{DIR_META}/runs/{RUN_ID[endpoint]}/metadata_{RUN_ID[endpoint]}.json""", "r"
    ) as fread:
        assert payload == json.load(fread), f"[{endpoint}] wrong metadata"


def test_last_status_happy(endpoint: str) -> None:
    want = {
        "project_id": PROJECT_ID,
        "run_id": RUN_ID[endpoint],
        "status": "SUCCESS",
    }
    with open(f"{DIR_META}/status/last.json", "r") as fread:
        got = json.load(fread)
        for k, v in want.items():
            assert got.get(k) == v, f"[{endpoint}] wrong last status"


def test_metrics(endpoint: str):
    with open(
        f"""{DIR_META}/runs/{RUN_ID[endpoint]}/metrics_{RUN_ID[endpoint]}.json""", "r"
    ) as fread:
        try:
            validate(CONFIG[endpoint]["metrics_schema"], json.load(fread))
        except Exception as ex:
            raise Exception("Wrong metrics content") from ex


def happy_path():
    test_status()

    for endpoint in ["train", "predict"]:
        test_post(endpoint)
        test_metadata_storage(endpoint)
        test_metadata(endpoint)
        test_last_status_happy(endpoint)
        test_metrics(endpoint)

    os.system(f"rm -r {DIR_META}")


def unhappy_path():
    pass


if __name__ == "__main__":
    try:
        from fastjsonschema import validate
        from requests import get, post
    except ImportError:
        os.system("pip install -r ./../requirements-test.txt")
        from fastjsonschema import validate
        from requests import get, post

    happy_path()
    unhappy_path()
