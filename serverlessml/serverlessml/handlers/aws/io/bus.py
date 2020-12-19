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

"""Module to communicate to AWS SQS."""

import json
from typing import Any, Dict

import boto3

from serverlessml.controllers.io import AbstractClientBus


class Client(AbstractClientBus):
    """Client to publish a message to AWS a SNS topic.

    Args:
        project_id: AWS account ID.
        region: AWS region.
    """

    @classmethod
    def _get_caller_account_id(cls) -> str:
        """Requests the AWS account ID by calling AWS STS."""
        return boto3.client("sts").get_caller_identity().get("Account")

    def __init__(self, project_id: str = None, region: str = "us-east-1") -> None:
        self.region = region
        self.client = boto3.client("sns", region_name=self.region)
        self.project_id = project_id if project_id else self._get_caller_account_id()

    def _get_topic_path(self, topic: str) -> str:
        return f"arn:aws:sns:{self.region}:{self.project_id}:{topic}"

    def _push(self, topic: str, payload: Dict[str, Any]) -> None:
        topic_arn = self.get_topic_path(topic=topic)
        self.client.publish(TopicArn=topic_arn, Message=json.dumps(payload))
