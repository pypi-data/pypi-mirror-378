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
import mock
from openstackclient.tests.unit import utils as tests_utils
from osc_lib import exceptions

from otcextensions.osclient.modelartsv2.v2 import dataset_sync
from otcextensions.tests.unit.osclient.modelartsv2.v2 import fakes


class TestDatasetSyncStatus(fakes.TestModelartsv2):
    _dataset = fakes.FakeDataset.create_one()

    columns = ("dataset_id", "status")
    object = fakes.FakeDatasetSync.create_one()

    data = fakes.gen_data(
        object,
        columns,
    )

    def setUp(self):
        super(TestDatasetSyncStatus, self).setUp()

        self.cmd = dataset_sync.DatasetSyncStatus(self.app, None)

        self.client.find_dataset = mock.Mock(return_value=self._dataset)
        self.client.get_dataset_sync_status = mock.Mock(
            return_value=self.object
        )

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Testing that a call without the required argument will fail and
        # throw a "ParserExecption"
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show(self):
        arglist = [
            "dataset-id",
        ]

        verifylist = [
            ("dataset", "dataset-id"),
        ]

        # Verify cm is triggered with default parameters
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Trigger the action
        columns, data = self.cmd.take_action(parsed_args)
        self.client.get_dataset_sync_status.assert_called_with(self._dataset)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_show_non_existent(self):
        arglist = [
            "nonexisting-dataset-id",
        ]

        verifylist = [
            ("dataset", "nonexisting-dataset-id"),
        ]

        # Verify cm is triggered with default parameters
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        get_mock_result = exceptions.CommandError("Resource Not Found")
        self.client.find_dataset = mock.Mock(side_effect=get_mock_result)

        # Trigger the action
        try:
            self.cmd.take_action(parsed_args)
        except Exception as e:
            self.assertEqual("Resource Not Found", str(e))
        self.client.find_dataset.assert_called_with(
            "nonexisting-dataset-id", ignore_missing=False
        )


class TestDatasetSync(fakes.TestModelartsv2):
    _dataset = fakes.FakeDataset.create_one()

    def setUp(self):
        super(TestDatasetSync, self).setUp()

        self.client.find_dataset = mock.Mock(return_value=self._dataset)
        self.client.dataset_sync = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = dataset_sync.DatasetSync(self.app, None)

    def test_sync(self):
        arglist = [
            "dataset-id",
        ]

        verifylist = [
            ("dataset", "dataset-id"),
        ]

        # Verify cm is triggered with default parameters
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Trigger the action
        result = self.cmd.take_action(parsed_args)
        self.client.dataset_sync.assert_called_with(self._dataset)
        self.assertIsNone(result)
