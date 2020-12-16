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

"""Module to communicate to GCP PubSub."""

import json
from typing import Any, Dict

from google.auth import default as default_project  # type: ignore
from google.cloud.pubsub_v1.publisher import Client as PubSubClient  # type: ignore

from .. import AbstractClientBus


class Client(AbstractClientBus):
    """Client to publish a message to a GCP PubSub topic.

    Args:
        project_id: GCP project.
    """

    @classmethod
    def _get_caller_account_id(cls) -> str:
        """Requests the AWS account ID by calling AWS STS."""
        _, project_id = default_project()
        return project_id

    def __init__(self, project_id: str = None) -> None:
        self.client = PubSubClient()
        self.project_id = project_id if project_id else self._get_caller_account_id()

    def _get_topic_path(self, topic: str) -> str:
        return self.client.topic_path(self.project_id, topic)

    def _push(self, topic: str, payload: Dict[str, Any]) -> None:
        topic = self.get_topic_path(topic)
        self.client.publish(topic, data=json.dumps(payload).encode("UTF-8"))
