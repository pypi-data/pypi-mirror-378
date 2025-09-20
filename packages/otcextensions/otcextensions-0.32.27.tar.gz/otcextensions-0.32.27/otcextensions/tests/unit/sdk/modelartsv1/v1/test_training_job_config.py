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
from otcextensions.sdk.modelartsv1.v1 import training_job_config
from otcextensions.tests.unit.sdk.modelartsv1.v1 import examples
from otcextensions.tests.unit.sdk.utils import assert_attributes_equal

EXAMPLE = examples.TRAINING_JOB_CONFIG


class TestTrainingjobConfig(base.TestCase):
    def setUp(self):
        super(TestTrainingjobConfig, self).setUp()

    def test_basic(self):
        sot = training_job_config.TrainingJobConfig()

        self.assertEqual("/training-job-configs", sot.base_path)
        self.assertEqual("configs", sot.resources_key)
        self.assertEqual(None, sot.resource_key)

        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_commit)

    def test_make_it(self):
        sot = training_job_config.TrainingJobConfig(**EXAMPLE)

        for key, value in EXAMPLE.items():
            if key == "create_time":
                self.assertEqual(sot.created_at, EXAMPLE[key])
            else:
                assert_attributes_equal(self, getattr(sot, key), value)
