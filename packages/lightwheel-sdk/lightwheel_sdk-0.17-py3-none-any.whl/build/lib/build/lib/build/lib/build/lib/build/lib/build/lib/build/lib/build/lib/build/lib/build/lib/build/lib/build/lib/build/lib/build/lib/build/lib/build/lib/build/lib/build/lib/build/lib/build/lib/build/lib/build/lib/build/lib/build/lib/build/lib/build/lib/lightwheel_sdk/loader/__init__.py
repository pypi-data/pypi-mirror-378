# Copyright 2025 Lightwheel Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

ENDPOINT = os.environ.get("LW_API_ENDPOINT", "https://api.lightwheel.net")

from .login import Login

login_client = Login(ENDPOINT)
from .object import ObjectLoader

object_loader = ObjectLoader(ENDPOINT)
from .floorplan import FloorplanLoader

floorplan_loader = FloorplanLoader(ENDPOINT)
