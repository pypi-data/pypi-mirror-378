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
from openstack.tests.unit import base
from otcextensions.sdk.modelartsv2.v2 import dataset_statistics
from otcextensions.tests.unit.sdk.modelartsv2.v2 import examples

EXAMPLE = examples.DATASET_STATISTICS


class TestDatasetStatistics(base.TestCase):
    def setUp(self):
        super(TestDatasetStatistics, self).setUp()

    def test_basic(self):
        sot = dataset_statistics.DatasetStatistics()

        self.assertEqual(
            "/datasets/%(dataset_id)s/data-annotations/stats", sot.base_path
        )
        self.assertEqual(None, sot.resource_key)
        self.assertEqual(None, sot.resources_key)

        self.assertFalse(sot.allow_list)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_commit)

        self.assertDictEqual(
            {
                "email": "email",
                "limit": "limit",
                "locale": "locale",
                "marker": "marker",
                "sample_state": "sample_state",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = dataset_statistics.DatasetStatistics(**EXAMPLE)

        for key, value in EXAMPLE.items():
            if key == "data_spliting_enable":
                self.assertEqual(
                    EXAMPLE["data_spliting_enable"],
                    sot.is_data_spliting_enabled,
                )
            else:
                self.assertEqual(getattr(sot, key), value)
