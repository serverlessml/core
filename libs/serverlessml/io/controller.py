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

"""``serverlessml.io.controller`` is the module
with the centralized IO clients controller.
"""

import importlib
from typing import Callable

from serverlessml.errors import InitError


def client(platform: str, service: str, **kwargs) -> Callable:
    """Instantiates ``Client`` to interface platforms e.g. local, aws, gcp.

    Example:
    ::
        >>> from serverlessml.io import client
        >>>
        >>> storage_client = client(platform="gcp", service="storage")
        >>>
        >>> data_set = storage_client.load(path="gcs://test/test.csv")
        >>> storage_client.save(data_set, path="gcs://test/test1.csv")
        >>> reloaded = storage_client.load(path="gcs://test/test1.csv")
        >>> assert data_set == reloaded
        >>>
        >>> bus_client = client(platform="gcp", service="bus")
        >>>
        >>> message = {"foo": "bar"}
        >>> bus_client.push(topic="test", data=message)

    Args:
        platform: Env platform, i.e. local, gcp, s3.
        service: The name of the service, e.g. storage, bus.
        kwargs: Additional config attributes, e.g. AWS region.

    Returns:
        Client class instance.

    Raises:
        NotImplementedError: When no client is implemeneted for the given service and/or platform.
        InitError: When a client couldn't be instantiated.
    """

    supported_platforms = ("local", "aws", "gcp")
    supported_services = ("storage", "bus")

    if platform not in supported_platforms:
        raise NotImplementedError(
            f"""{platform} is not supported. Set one of\n{", ".join(supported_platforms)}"""
        )

    if service not in supported_services:
        raise InitError(
            f"""{service} is not supported. Set one of\n{", ".join(supported_services)}"""
        )

    _config = {}
    if platform == "aws" and service == "bus":
        _config["region"] = kwargs.get("region", "")

    try:
        module = importlib.import_module(f"serverlessml.io.{platform}.{service}", "serverlessml")
        class_instance: Callable = module.Client(**_config)  # type: ignore
    except Exception as ex:
        message = f"Client init error:\n{str(ex)}"
        raise InitError(message) from ex
    return class_instance
