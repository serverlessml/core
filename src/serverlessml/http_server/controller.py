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

"""``serverlessml.http_server.controller`` is the module
with the logic defining http server endpoints.
"""

from typing import Any, Callable, Dict, Optional

from sanic import Sanic  # type: ignore
from sanic.request import Request  # type: ignore
from sanic.response import HTTPResponse, empty  # type: ignore

from serverlessml.controllers import get_logger
from serverlessml.errors import ModelDefinitionError, PipelineConfigError, PipelineRunningError
from serverlessml.pipeline import Runner


class Endpoints:
    """``Endpoints`` defines HTTP server endpoints logic."""

    def __init__(self, runner: Runner, payload_decoder: Optional[Callable] = None) -> None:
        """Instantiates endpoints logic handlers.

        Args:
            runner: Pipeline runner.
            payload_decoder: Custom payload decoder.
        """
        self.runner = runner
        self.payload_decoder = payload_decoder
        self._logger = get_logger(name=__name__)

    def _extract_payload(self, request: Request) -> Dict[str, Any]:
        payload: Dict[str, Any] = request.json
        if not payload:
            self._logger.error("No JSON payload in request body")
            raise Exception("400")

        if self.payload_decoder:
            try:
                return self.payload_decoder(payload)
            except (KeyError, TypeError) as ex:
                self._logger.error({"error": str(ex), "payload": payload})
                raise Exception("422") from ex
        return payload

    @classmethod
    def endpoint_status(cls, request: Request) -> HTTPResponse:  # pylint: disable=unused-argument
        """Healthcheck endpoint."""
        return empty(200)

    def endpoint_train(self, request: Request) -> HTTPResponse:
        """Resolves requests for to execute train pipelines."""
        try:
            payload = self._extract_payload(request)
        except Exception as ex:
            return empty(int(str(ex)))

        try:
            self.runner.train(payload)
        except PipelineConfigError as ex:
            self._logger.error(
                {"error": str(ex), "run_id": payload.get("run_id"), "payload": payload}
            )
            return empty(422)
        except (PipelineRunningError, ModelDefinitionError) as ex:
            self._logger.error(
                {"error": str(ex), "run_id": payload.get("run_id"), "payload": payload}
            )
            return empty(500)
        return empty(200)

    def endpoint_predict(self, request: Request) -> HTTPResponse:
        """Resolves requests for to execute train pipelines."""
        try:
            payload = self._extract_payload(request)
        except Exception as ex:
            return empty(int(str(ex)))

        try:
            self.runner.predict(payload)
        except PipelineConfigError as ex:
            self._logger.error(
                {"error": str(ex), "run_id": payload.get("run_id"), "payload": payload}
            )
            return empty(422)
        except (PipelineRunningError, ModelDefinitionError) as ex:
            self._logger.error(
                {"error": str(ex), "run_id": payload.get("run_id"), "payload": payload}
            )
            return empty(500)
        return empty(200)


class Server(Endpoints):
    """``Server`` launches HTTP server."""

    def run(self, port: int = 8080) -> None:
        """Launches the http server.

        Args:
            port: Port for webserver to listen on.
        """
        app = Sanic("ServerlessML")
        app.add_route(
            self.endpoint_status,
            "/status",
            methods=[
                "GET",
            ],
        )
        app.add_route(
            self.endpoint_train,
            "/train",
            methods=[
                "POST",
            ],
        )
        app.add_route(
            self.endpoint_predict,
            "/predict",
            methods=[
                "POST",
            ],
        )
        app.run(host="0.0.0.0", port=port, access_log=False)
