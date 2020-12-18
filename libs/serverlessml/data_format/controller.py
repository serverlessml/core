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

"""``serverlessml.data_file.controller`` is the module
with the centralized data encoders controller.
"""

import importlib
from typing import Callable

from serverlessml.errors import InitError


def dataset_encoder(dataset_filename: str) -> Callable:
    """``dataset_encoder`` dynamically loads a data encoder based on the file extention.

    Args:
        dataset_filename: Dataset filename.

    Returns:
        Instance of an ``AbstractDataSet``'s child-class.

    Raises:
        NotImplementedError: When no encoder is implemeneted for the given file extention.
        InitError: When underlying class couldn't be instantiated.
    """
    supported_ext = {"csv": "pandas", "json": "pandas"}

    if dataset_filename.endswith(".gz"):
        dataset_filename = dataset_filename.replace(".gz", "")

    file_ext = dataset_filename.split(".")[-1]

    submodule = supported_ext.get(file_ext)
    if not submodule:
        raise NotImplementedError(
            f"""{file_ext} is not supported. Set one of\n{", ".join(supported_ext)}"""
        )

    try:
        module = importlib.import_module(
            f"serverlessml.data_format.{submodule}.{file_ext}_encoder", "serverlessml"
        )
        cls_def: Callable = getattr(module, f"{file_ext.upper()}Encoder")  # type: ignore
    except Exception as ex:
        message = f"Init error:\n{str(ex)}."
        raise InitError(message) from ex
    return cls_def
