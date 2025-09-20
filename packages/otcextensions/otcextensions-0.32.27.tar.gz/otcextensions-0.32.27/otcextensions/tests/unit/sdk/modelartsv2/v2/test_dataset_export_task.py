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
from otcextensions.sdk.modelartsv2.v2 import dataset_export_task
from otcextensions.tests.unit.sdk.modelartsv2.v2 import examples
from otcextensions.tests.unit.sdk.utils import assert_attributes_equal

EXAMPLE = examples.DATASET_EXPORT_TASK


class TestDatasetExportTask(base.TestCase):
    def setUp(self):
        super(TestDatasetExportTask, self).setUp()

    def test_basic(self):
        sot = dataset_export_task.DatasetExportTask()

        self.assertEqual(
            "/datasets/%(uri_dataset_id)s/export-tasks", sot.base_path
        )
        self.assertEqual(None, sot.resource_key)
        self.assertEqual("export_tasks", sot.resources_key)

        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_commit)

        self.assertDictEqual(
            {
                "export_type": "export_type",
                "limit": "limit",
                "marker": "marker",
                "offset": "offset",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = dataset_export_task.DatasetExportTask(**EXAMPLE)
        for key, value in EXAMPLE.items():
            if key == 'task_id':
                self.assertEqual(sot.id, value)
            elif key == 'update_time':
                self.assertEqual(sot.updated_at, value)
            elif key == 'create_time':
                self.assertEqual(sot.created_at, value)
            else:
                assert_attributes_equal(self, getattr(sot, key), value)
