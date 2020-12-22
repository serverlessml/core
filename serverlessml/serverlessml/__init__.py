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

"""ServerlessML is a framework that makes it easy to build robust and scalable
ML pipelines to train and serve models in public clouds.
"""

import logging
from contextlib import suppress

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "1.0"

__all__ = [
    "InitError",
    "ClientStorageError",
    "ClientBusError",
    "DataDecodingError",
    "DataEncodingError",
    "DataProcessingError",
    "ModelDefinitionError",
    "PipelineRunningError",
    "PipelineConfigError",
    "ControllerIO",
    "Runner",
]

with suppress(ImportError):
    from .controllers import ControllerIO
    from .errors import (
        ClientBusError,
        ClientStorageError,
        DataDecodingError,
        DataEncodingError,
        DataProcessingError,
        InitError,
        ModelDefinitionError,
        PipelineConfigError,
        PipelineRunningError,
    )
    from .pipeline import PipelineRunner as Runner
