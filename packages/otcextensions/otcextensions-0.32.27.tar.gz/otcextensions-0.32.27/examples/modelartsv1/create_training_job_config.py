#!/usr/bin/env python3
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
"""Create a training job configuration from attributes."""
import openstack

openstack.enable_logging(True)
conn = openstack.connect(cloud="otc")

attrs = {
    "config_name": "testConfig",
    "config_desc": "This is config",
    "worker_server_num": 1,
    "app_url": "/usr/app/",
    "boot_file_url": "/usr/app/boot.py",
    "parameter": [
        {
            "label": "learning_rate",
            "value": "0.01",
        },
        {
            "label": "batch_size",
            "value": "32",
        },
    ],
    "spec_id": 1,
    "dataset_id": "38277e62-9e59-48f4-8d89-c8cf41622c24",
    "dataset_version_id": "2ff0d6ba-c480-45ae-be41-09a8369bfc90",
    "engine_id": 1,
    "train_url": "/usr/train/",
    "log_url": "/usr/log/",
}

trainingjob_conf = conn.modelartsv1.create_training_job_config(**attrs)
print(trainingjob_conf)
