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

"""``CSVEncoder`` encodes/decodes bytes encoded data of CSV format to/from ``pandas.DataFrame``.
"""
from io import BytesIO, StringIO
from typing import Any, Dict, Optional, Union

from pandas import DataFrame, read_csv  # type: ignore

from serverlessml.data_format.template import AbstractEncoder


class CSVEncoder(AbstractEncoder, DataFrame):
    """``CSVEncoder`` encodes/decides from/to bytes data following CSV definition format.
    It relies on the `read_csv` and `to_csv` methods of the ``pandas.DataFrame`` class.

    Example:
    ::

        >>> import pandas
        >>> from serverlessml.data_format import CSVDataSet
        >>>
        >>> data_set = CSVEncoder({"col1": [1, 2], "col2": [4, 5], "col3": [5, 6]})
        >>>
        >>> data_bytes = data_set.to_raw()
        >>> reloaded = CSVEncoder.from_raw(data_bytes)
        >>> assert data_set.equals(reloaded)
    """

    def __init__(self, data: Optional[Union[DataFrame, Dict[str, Any]]] = None):
        """Creates a new instance of ``CSVEncoder``.

        Args:
            data: Data object.
        """
        super().__init__(data=data)

    @classmethod
    def _from_raw(cls, data: bytes) -> DataFrame:
        return cls(read_csv(BytesIO(data)))

    def _to_raw(self) -> bytes:
        out = StringIO()
        self.to_csv(out, index=False)
        return out.getvalue().encode("UTF-8")
