# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
from openstack import resource
from otcextensions.sdk.modelartsv2.v2.dataset import DatasetVersionSpec


class DatasetVersion(DatasetVersionSpec):
    base_path = "/datasets/%(dataset_id)s/versions"

    resources_key = "versions"

    # capabilities
    allow_create = True
    allow_list = True
    allow_delete = True
    allow_fetch = True

    _query_mapping = resource.QueryParameters(
        "status",
        "train_evaluate_ratio",
        "version_format",
    )

    #: Dataset Version ID.
    version_id = resource.Body("version_id", alternate_id=True)
    #: Dataset ID.
    dataset_id = resource.URI("dataset_id")
