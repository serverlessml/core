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

"""``serverlessml.controllers.logs`` is the module
with the logic defining logger.
"""

import logging
from collections import OrderedDict
from typing import Any, Dict, Optional

from pythonjsonlogger.jsonlogger import JsonFormatter


class LogsFormatter(JsonFormatter):
    """``LogsFormatter`` defines the logs formatter class."""

    def __init__(self, request_id: Optional[str] = None) -> None:
        """Instantiates `LogsFormatter`.

        Args:
            request_id: Trigger message ID.
        """
        fmt = "%(asctime)s %(levelname)s %(run_id)s %(lineno)d %(message)s"
        if not request_id:
            fmt = "%(asctime)s %(levelname)s %(request_id)s %(run_id)s %(lineno)d %(message)s"

        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")

        self.request_id = request_id

    def add_fields(
        self, log_record: OrderedDict, record: logging.LogRecord, message_dict: Dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["request_id"] = self.request_id

        if isinstance(message_dict.get("message"), dict):
            log_record.pop("message")
            log_record.update(message_dict)

        if not message_dict.get("run_id"):
            log_record.pop("run_id")


def get_logger(name: Optional[str] = __name__, request_id: Optional[str] = None) -> logging.Logger:
    """Sets up the logger.

    Args:
        name: Logger instance name.
        request_id: Trigger message ID.

    Returns:
        Logger.
    """
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(LogsFormatter(request_id=request_id))
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    for hdl in logger.handlers:
        logger.removeHandler(hdl)

    logger.addHandler(json_handler)
    return logger
