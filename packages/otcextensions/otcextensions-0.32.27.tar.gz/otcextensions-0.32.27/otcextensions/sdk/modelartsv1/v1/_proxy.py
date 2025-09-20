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
import time

from openstack import exceptions
from openstack import proxy
from otcextensions.sdk.modelartsv1.v1 import builtin_model as _builtin_model
from otcextensions.sdk.modelartsv1.v1 import devenv as _devenv
from otcextensions.sdk.modelartsv1.v1 import job_engine as _job_engine
from otcextensions.sdk.modelartsv1.v1 import job_flavor as _job_flavor
from otcextensions.sdk.modelartsv1.v1 import model as _model
from otcextensions.sdk.modelartsv1.v1 import service as _service
from otcextensions.sdk.modelartsv1.v1 import \
    service_cluster as _service_cluster
from otcextensions.sdk.modelartsv1.v1 import service_event as _service_event
from otcextensions.sdk.modelartsv1.v1 import service_flavor as _service_flavor
from otcextensions.sdk.modelartsv1.v1 import service_log as _service_log
from otcextensions.sdk.modelartsv1.v1 import \
    service_monitor as _service_monitor
from otcextensions.sdk.modelartsv1.v1 import training_job as _training_job
from otcextensions.sdk.modelartsv1.v1 import \
    training_job_config as _training_job_config
from otcextensions.sdk.modelartsv1.v1 import \
    training_job_version as _training_job_version
from otcextensions.sdk.modelartsv1.v1 import \
    visualization_job as _visualization_job


class Proxy(proxy.Proxy):
    skip_discovery = True

    def __init__(self, session, *args, **kwargs):
        super(Proxy, self).__init__(session=session, *args, **kwargs)
        self.additional_headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }

    # ======== BuiltIn Model Management ========
    def builtin_models(self, **params):
        """List all BuiltIn Models.

        :param dict params: Optional query parameters to be sent to limit
            the built-in models being returned.

        :returns: a generator of :class:`~otcextensions.sdk.modelartsv1.v1.
            built_in_model.BuiltInModel` instances.
        """
        return self._list(_builtin_model.BuiltInModel, **params)

    def find_builtin_model(self, name_or_id, ignore_missing=True):
        """Find a single built-in model.

        :param name_or_id: The name or ID of a built-in model
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            if the model does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent built-in model.

        :returns: One :class:`~otcextensions.sdk.modelartsv1.v1.
            built_in_model.BuiltInModel` or ``None``.
        """
        return self._find(
            _builtin_model.BuiltInModel,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    # ======== Model Management ========

    def models(self, **params):
        """List all Models.

        :param dict params: Optional query parameters to be sent to limit
            the models being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.model.Model` instances.
        """
        params["paginated"] = False
        return self._list(_model.Model, **params)

    def create_model(self, **attrs):
        """Create a model from attributes.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~otcextensions.sdk.modelartsv1.v1.models.Model`,
            comprised of the properties on the Model class.

        :returns: The results of model creation.
        :rtype: :class:`~otcextensions.modelartsv1.v1.model.Model`
        """
        return self._create(_model.Model, prepend_key=False, **attrs)

    def get_model(self, model):
        """Get details of a model by Id.

        :param model: model id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.model.Model`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.model.Model`
        """
        return self._get(_model.Model, model)

    def find_model(self, name_or_id, ignore_missing=True):
        """Find a single model.

        :param name_or_id: The name or ID of a model.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            if the model does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent model.

        :returns:
            One :class:`~otcextensions.sdk.modelartsv1.v1.model.Model`
            or ``None``.
        """
        return self._find(
            _model.Model, name_or_id, ignore_missing=ignore_missing
        )

    def delete_model(self, model, ignore_missing=False):
        """Delete a model.

        :param model: model id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.model.Model`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the model does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent model.

        :returns: ``None``
        """
        return self._delete(_model.Model, model, ignore_missing=ignore_missing)

    # ======== DevEnviron Management ========

    def devenv_instances(self, **params):
        """List all Devenv Instances.

        :param dict params: Optional query parameters to be sent to limit
            the instances being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv` instances.
        """
        if not params.get("dev_env_type"):
            params.update(dev_env_type="Notebook")
        if params.get("limit"):
            params.update(paginated=False)
        return self._list(_devenv.Devenv, **params)

    def create_devenv_instance(self, **attrs):
        """Create a devenv instance from attributes.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`,
            comprised of the properties on the Devenv class.

        :returns: The results of devenv instance creation.
        :rtype: :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`
        """
        return self._create(_devenv.Devenv, prepend_key=False, **attrs)

    def get_devenv_instance(self, instance):
        """Get details of a Devenv Instance.

        :param instance: devenv instance id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`.

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`.
        """
        return self._get(_devenv.Devenv, instance)

    def find_devenv_instance(self, name_or_id, ignore_missing=False):
        """Find a single Devenv instance by name or Id.

        :param name_or_id: The name or ID of a Devenv instance.

        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            if the devenv does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent devenv.

        :returns:
            One :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`
            or ``None``
        """
        return self._find(
            _devenv.Devenv,
            name_or_id,
            ignore_missing=ignore_missing,
            de_type="Notebook",
        )

    def update_devenv_instance(self, instance, **attrs):
        """Update a Devenv Instance Configurations.

        :param instance: devenv instance id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`,
            comprised of the properties on the Devenv class.

        """
        return self._update(_devenv.Devenv, instance, **attrs)

    def start_devenv_instance(self, instance):
        """Start a Devenv instance.

        :param instance: devenv instance id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`
        """
        devenv = self._get_resource(_devenv.Devenv, instance)
        return devenv.start(self)

    def stop_devenv_instance(self, instance):
        """Stop a Devenv instance.

        :param instance: devenv instance id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`
        """
        devenv = self._get_resource(_devenv.Devenv, instance)
        return devenv.stop(self)

    def delete_devenv_instance(self, instance, ignore_missing=False):
        """Delete a Devenv instance.

        :param instance: devenv instance id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.devenv.Devenv`.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the group does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent devenv.

        :returns: ``None``
        """
        return self._delete(
            _devenv.Devenv, instance, ignore_missing=ignore_missing
        )

    # Service Management

    def services(self, **params):
        """List all Services.

        :param dict params: Optional query parameters to be sent to limit
            the services being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
            instances
        """
        params["paginated"] = False
        return self._list(_service.Service, **params)

    def create_service(self, **attrs):
        """Deploy a modelarts service from attributes.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`,
            comprised of the properties on the Service class.

        :returns: The result of service creation.
        :rtype: :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        """
        return self._create(_service.Service, **attrs)

    def delete_service(self, service, ignore_missing=False):
        """Delete a modelarts service.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the service does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent service.

        :returns: ``None``
        """
        return self._delete(
            _service.Service, service, ignore_missing=ignore_missing
        )

    def get_service(self, service):
        """Get details of a modelarts service.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        """
        return self._get(_service.Service, service)

    def find_service(self, name_or_id, ignore_missing=True):
        """Find a single service

        :param name_or_id: The name or ID of a ModelArts service
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            if the service does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent service.

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        """
        return self._find(
            _service.Service, name_or_id, ignore_missing=ignore_missing
        )

    def update_service(self, service, **attrs):
        """Update a Service Configurations.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`,
            comprised of the properties on the Service class.

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        """
        return self._update(_service.Service, service, **attrs)

    def start_service(self, service):
        """Start a Service.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        """
        return self._update(_service.Service, service, status="running")

    def stop_service(self, service):
        """Stop a Service.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        """
        return self._update(_service.Service, service, status="stopped")

    def wait_for_service(self, service, timeout=1200, wait=5):
        while timeout > 0:
            obj = self.get_service(service)
            status = obj.status.lower()
            if status == "deploying":
                pass
            elif status in ["running", "finished"]:
                return True
            else:
                raise exceptions.SDKException(obj.error_msg)
            timeout = timeout - wait
            time.sleep(wait)
        raise exceptions.SDKException(
            f"Wait Timed Out. service status is: {status}"
        )

    def service_logs(self, service, **params):
        """List update logs of a real-time service.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        :param dict params: Optional query parameters to be sent to limit
            the service logs being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.service_log.ServiceLog`
            instances
        """
        service = self._get_resource(_service.Service, service)
        return self._list(
            _service_log.ServiceLog, service_id=service.id, **params
        )

    def service_events(self, service, **params):
        """List events logs of a service.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`
        :param dict params: Optional query parameters to be sent to limit
            the service events being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.service_event.ServiceEvent`
            instances
        """
        service = self._get_resource(_service.Service, service)
        return self._list(
            _service_event.ServiceEvent,
            service_id=service.id,
            paginated=False,
            **params,
        )

    def service_monitor(self, service, **params):
        """List a service monitoring informations.

        :param service: service id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.service.Service`

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.service_monitor.ServiceMonitor`
            instances
        """
        service = self._get_resource(_service.Service, service)
        return self._list(
            _service_monitor.ServiceMonitor, service_id=service.id, **params
        )

    def service_flavors(self, **params):
        """List all flavors for a service deployment.

        :param dict params: Optional query parameters to be sent to limit
            the service flavors being returned.
        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.service_flavor.ServiceFlavor`
            instances
        """
        return self._list(_service_flavor.ServiceFlavor, **params)

    def service_clusters(self, **params):
        """List all dedicated resource pools (clusters) available
        for a service deployment.

        :param dict params: Optional query parameters to be sent to limit
            the service clusters being returned.
        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.service_cluster.ServiceCluster`
            instances
        """
        return self._list(_service_cluster.ServiceCluster, **params)

    # Training Job Management

    def training_jobs(self, **params):
        """List all training jobs.

        :param dict params: Optional query parameters to be sent to limit
            the training jobs being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
            instances
        """
        return self._list(_training_job.TrainingJob, **params)

    def create_training_job(self, **attrs):
        """Create a training job from attributes.

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`,
            comprised of the properties on the TrainingJob class.

        :returns: The results of training job creation.
        :rtype:
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
        """
        return self._create(_training_job.TrainingJob, **attrs)

    def find_training_job(self, name_or_id, ignore_missing=True):
        """Find a single training job by name or Id.

        :param name_or_id: The name or ID of a modelarts training job
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            if the trainjob does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent trainjob.

        :returns: instance of
            :class:`~otcextensions.sdk.modelarts.v1.training_job.TrainingJob`
            or ``None``
        """
        return self._find(
            _training_job.TrainingJob,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def update_training_job(self, training_job, description):
        """Update training job description.

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelarts.v1.training_job.TrainingJob`
        :param description: Description of a training job.

        :returns: instance of
            :class:`~otcextensions.sdk.modelarts.v1.training_job.TrainingJob`
        """
        return self._update(
            _training_job.TrainingJob,
            training_job,
            job_desc=description,
        )

    def delete_training_job(self, training_job, ignore_missing=False):
        """Delete a training job

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelarts.v1.training_job.TrainingJob`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the training_job does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent training job.

        returns: ``None``
        """
        return self._delete(
            _training_job.TrainingJob,
            training_job,
            ignore_missing=ignore_missing,
        )

    def job_flavors(self, **params):
        """List all flavors available for running a job.

        :param dict params: Optional query parameters to be sent to limit
            the job flavors being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.job_flavor.JobFlavor`
            instances.
        """
        return self._list(_job_flavor.JobFlavor, **params)

    def job_engines(self, **params):
        """List all engines available for running a job.

        :param dict params: Optional query parameters to be sent to limit
            the job engines being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.job_engine.JobEngine`
            instances.
        """
        return self._list(_job_engine.JobEngine, **params)

    # Training Job Version Management

    def training_job_versions(self, training_job, **attrs):
        """List versions of a training job.

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
        :param dict params: Optional query parameters to be sent to limit
            the training job versions being returned.

        :returns: a generator of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion` instances.
        """
        training_job = self._get_resource(
            _training_job.TrainingJob, training_job
        )
        return self._list(
            _training_job_version.TrainingJobVersion,
            job_id=training_job.id,
            **attrs,
        )

    def get_training_job_version(self, training_job, version):
        """Get details of a training job by version id.

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
        :param version: training job version id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion`

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion`
        """
        training_job = self._get_resource(
            _training_job.TrainingJob, training_job
        )
        return self._get(
            _training_job_version.TrainingJobVersion,
            version,
            job_id=training_job.id,
        )

    def create_training_job_version(self, training_job, **attrs):
        """Create a training job from attributes

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~otcextensions.sdk.modelartsv1.v1.trainjob.Trainjob`,
            comprised of the properties on the Trainjob class.

        :returns: The results of trainjobs creation
        :rtype: :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion`
        """
        training_job = self._get_resource(
            _training_job.TrainingJob, training_job
        )
        return self._create(
            _training_job_version.TrainingJobVersion,
            job_id=training_job.id,
            **attrs,
        )

    def delete_training_job_version(
        self, training_job, version, ignore_missing=False
    ):
        """Delete a training job version.

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
        :param version: training job version id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the training job version does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent training job version.

        returns: ``None``
        """
        training_job = self._get_resource(
            _training_job.TrainingJob, training_job
        )
        return self._delete(
            _training_job_version.TrainingJobVersion,
            version,
            job_id=training_job.id,
            ignore_missing=ignore_missing,
        )

    def stop_training_job_version(self, training_job, version):
        """Stop a training job version.

        :param training_job: training job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.training_job.TrainingJob`
        :param version: training job version id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion`

        :rtype: :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobVersion`
        """
        training_job = self._get_resource(
            _training_job.TrainingJob, training_job
        )
        training_job_version = self._get_resource(
            _training_job_version.TrainingJobVersion,
            version,
            job_id=training_job.id,
        )
        return training_job_version.stop(self)

    # Training Job Config Management

    def training_job_configs(self, **params):
        """List all training job configurations.

        :param dict params: Optional query parameters to be sent to limit
            the training job configs being returned.

        :returns: a generator of
            (:class:`~otcextensions.sdk.modelartsv1.v1.
            training_job_config.TrainingjobConfig`) instances.
        """
        return self._list(_training_job_config.TrainingJobConfig, **params)

    def create_training_job_config(self, **attrs):
        """Create a Training Job Configuration from attributes.

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job_config.TrainingjobConfig`,
            comprised of the properties on the TrainingJobConfig class.

        :returns: The results of Training Job Configuration creation.
        :rtype: :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job.TrainingJobConfig`
        """
        return self._create(_training_job_config.TrainingJobConfig, **attrs)

    def get_training_job_config(self, name):
        """Get the Training Job Configuration by config name.

        :param name: Name of a training job configuration.

        :returns: instance of :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job_config.TrainingJobConfig`.
        """
        return self._get(_training_job_config.TrainingJobConfig, name)

    def update_training_job_config(self, name, **attrs):
        """Update training job configuration.

        :param name: Name of a training job configuration.
        :param dict attrs: Keyword arguments which will be used to update a
            :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job_config.TrainingJobConfig`,
            comprised of the properties on the class.

        :returns: instance of :class:`~otcextensions.sdk.modelartsv1.v1.
            training_job_config.TrainingJobConfig`.
        """
        return self._update(
            _training_job_config.TrainingJobConfig, name, **attrs
        )

    def delete_training_job_config(self, name, ignore_missing=False):
        """Delete Training Job Configuration.

        :param name: Name of a training job configuration.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the config does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent Training Job Configuration.

        returns: ``None``
        """
        return self._delete(
            _training_job_config.TrainingJobConfig,
            name,
            ignore_missing=ignore_missing,
        )

    # Visualization Job Management

    def visualization_jobs(self, **params):
        """List all Visualization Jobs.

        :param dict params: Optional query parameters to be sent to limit
            the visualization jobs  being returned.

        :returns: a generator of :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob` instances.
        """
        return self._list(_visualization_job.VisualizationJob, **params)

    def create_visualization_job(self, **attrs):
        """Create a Visualization Job from attributes.

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`
            comprised of the properties on the Visualization Job class.

        :returns: The results of Visualization Job creation.

        :rtype:
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.
        """
        return self._create(_visualization_job.VisualizationJob, **attrs)

    def get_visualization_job(self, visualization_job):
        """Get details of a Visualization Job.

        :param visualization_job: visualization job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.
        """
        return self._get(
            _visualization_job.VisualizationJob, visualization_job
        )

    def update_visualization_job(self, visualization_job, description):
        """Update visualization job description.

        :param visualization_job: visualization job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.
        :param description: Description of a visualization job to update.

        :returns: instance of :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`
        """
        return self._update(
            _visualization_job.VisualizationJob,
            visualization_job,
            job_desc=description,
        )

    def delete_visualization_job(
        self, visualization_job, ignore_missing=False
    ):
        """Delete a Visualization Job

        :param visualization_job: visualization job id or an instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the group does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent Visualization Job.

        returns: ``None``
        """
        return self._delete(
            _visualization_job.VisualizationJob,
            visualization_job,
            ignore_missing=ignore_missing,
        )

    def stop_visualization_job(self, visualization_job):
        """Stop a Visualization Job.

        :param visualization_job: visualization job id or an instance of
            :class:`~otcextensions.sdk.modelarts.v1.
            visualization_job.VisualizationJob`.

        :returns: instance of :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.
        """
        visualization_job = self._get_resource(
            _visualization_job.VisualizationJob, visualization_job
        )
        return visualization_job.stop(self)

    def restart_visualization_job(self, visualization_job):
        """Restart a Visualization Job.

        :param visualization_job: visualization job id or an instance of
            :class:`~otcextensions.sdk.modelarts.v1.
            visualization_job.VisualizationJob`.

        :returns: instance of
            :class:`~otcextensions.sdk.modelartsv1.v1.
            visualization_job.VisualizationJob`.
        """
        visualization_job = self._get_resource(
            _visualization_job.VisualizationJob, visualization_job
        )
        return visualization_job.restart(self)
