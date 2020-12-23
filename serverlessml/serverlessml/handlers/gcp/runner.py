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

"""``serverlessml.handlers.gcp.runner`` is the module
with the runner's logic to be executed on GCP.
"""

import base64
import json
from functools import partial
from typing import Any, Dict

from serverlessml import ControllerIO, Runner
from serverlessml.http_server import Server


def extract_pubsub_payload(event: dict) -> Dict[str, Any]:
    """Extracts payload from the PubSub event body.

    Args:
        event: PubSub event body, e.g.
            {
                "message": {
                    "data": <base64 encoded object>
                }
            }

    Returns:
        Dict with PubSub event body payload.

    Raises:
        KeyError: Raised when the payload doesn't contain required key(s).
        TypeError: Raised when payload message has wrong dataype.
    """
    if not event.get("message"):
        raise KeyError("Payload doesn't contain the 'message' key")

    pubsub_message = event["message"]

    if not isinstance(pubsub_message, dict):
        raise TypeError("Event payload's message is of wrong data type.")

    if not pubsub_message.get("data"):
        raise KeyError("Payload's 'message' doesn't contain the 'data' key")

    return json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8"))


def run(port: int) -> None:
    """Contains the end-to-end logic to run pipelines.

    Args:
        port: Port for the web-server to listen.
    """
    Server(
        runner=Runner(partial(ControllerIO, platform="gcp")),
        payload_decoder=extract_pubsub_payload,
    ).run(port=port)
