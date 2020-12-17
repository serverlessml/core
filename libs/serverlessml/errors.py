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

"""``serverlessml.error`` is the module with the errors definitions."""


class InitError(Exception):
    """Client instantiation error."""


class ClientStorageError(Exception):
    """Filesystem IO client's error."""


class ClientBusError(Exception):
    """Message bus client's error."""


class DataDecodingError(Exception):
    """Error when decoding raw bytedata into desidered data structure format."""


class DataEncodingError(Exception):
    """Error when encoding data from desired structure format into raw bytedata."""


class ModelDefinitionError(Exception):
    """Model instantiation error."""


class ModelTrainError(Exception):
    """Model training error."""


class ModelPredictionError(Exception):
    """Model prediction error."""
