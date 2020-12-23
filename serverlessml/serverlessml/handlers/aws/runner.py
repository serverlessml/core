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

"""``serverlessml.handlers.aws.runner`` is the module
with the runner's logic to be executed on AWS.
"""

import json
import logging
import sys
from functools import partial
from typing import Any, Dict

from serverlessml import ControllerIO, Runner
from serverlessml.errors import ModelDefinitionError, PipelineConfigError, PipelineRunningError


def run(event: Dict[str, Any], context: Any) -> None:  # pylint: disable=unused-argument
    """Contains the end-to-end logic to run pipelines.

    Args:
        event: AWS lambda event object.
        context: AWS lambda context.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(linenum)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger(__name__)
    log.debug("Invoke serverlessML pipeline with %s", __name__)

    record: Dict[str, Any] = event["Records"][0]["Sns"]
    topic: str = record["TopicArn"]

    try:
        payload: Dict[str, Any] = json.loads(record["Message"])
    except json.JSONDecodeError as ex:
        log.error(ex)
        sys.exit(1)

    try:
        runner = Runner(partial(ControllerIO, platform="aws"))
        if topic.endswith("train"):
            runner.train(payload)
        elif topic.endswith("predict"):
            runner.predict(payload)
        else:
            log.error("Triggered by the wrong topic.")
            sys.exit(1)
    except (ModelDefinitionError, PipelineConfigError, PipelineRunningError) as ex:
        log.error(ex)
        sys.exit(1)

    log.debug("Done")
