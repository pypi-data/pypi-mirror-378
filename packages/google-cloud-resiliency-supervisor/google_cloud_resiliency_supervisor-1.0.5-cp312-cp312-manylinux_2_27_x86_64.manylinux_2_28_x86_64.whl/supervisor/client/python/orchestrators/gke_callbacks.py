"""Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import collections
import copy
import datetime
import logging
import subprocess
import threading
import time
import typing

from kubernetes import client
from kubernetes import config
from kubernetes import watch
from supervisor.core.python import utils as core_utils
import supervisor_core


class KubernetesCallbacks:
  """Kubernetes-specific implementation of OrchestratorCallbacks.

  This class provides methods for interacting with a Kubernetes cluster,
  such as resetting hosts, draining hosts, and restarting jobsets.
  """

  def __init__(self, namespace: str = "default"):
    """Initializes the KubernetesCallbacks class.

    This method loads the Kubernetes configuration and initializes the
    necessary API clients. It also sets the namespace based on the
    JOB_NAMESPACE environment variable or defaults to "default".

    Args:
        namespace: The namespace to use for the Kubernetes cluster.
    """
    try:
      config.load_incluster_config()
    except:
      config.load_kube_config()

    # Required Kubernetes API clients
    self.core_api = client.CoreV1Api()
    self.custom_api = client.CustomObjectsApi()

    # Workload related configuration
    self.namespace = namespace

    # Workload related state
    self.workload_downtime = collections.defaultdict(None)

    self.logger = core_utils.setup_logger()

    # For watching cordoned nodes
    self._cordon_lock = threading.Lock()
    self._cordoned_nodes = set(self._get_initially_cordoned_nodes())
    self._stop_cordon_watch = threading.Event()
    self._cordon_watch_thread = threading.Thread(
        target=self._watch_cordoned_nodes
    )
    self._cordon_watch_thread.daemon = True
    self._cordon_watch_thread.start()

    # For watching jobset pods
    self._pod_lock = threading.Lock()
    self.jobset_pods = collections.defaultdict(dict)
    self.jobset_pod_statuses = collections.defaultdict(
        lambda: {
            "total_pods": 0,
            "running_pods": 0,
            "pending_pods": [],
            "other_state_pods": [],
            "all_running": False,
        }
    )
    self._stop_pod_watch = threading.Event()
    self._pod_watch_thread = threading.Thread(target=self._watch_all_pods)
    self._pod_watch_thread.daemon = True
    self._pod_watch_thread.start()

  def shutdown(self):
    """Shuts down the watcher threads."""
    self.logger.info("Shutting down Kubernetes callbacks watcher threads.")
    self._stop_cordon_watch.set()
    self._stop_pod_watch.set()
    self._cordon_watch_thread.join()
    self._pod_watch_thread.join()

  def _get_initially_cordoned_nodes(self) -> list[str]:
    """Returns a list of cordoned nodes in the cluster."""
    try:
      nodes = self.core_api.list_node(field_selector="spec.unschedulable=true")
      return [node.metadata.name for node in nodes.items]
    except client.ApiException:
      self.logger.warning("Failed to get cordoned nodes during initialization.")
      return []

  def _watch_cordoned_nodes(self):
    """Watches for node events and updates the list of cordoned nodes."""
    w = watch.Watch()
    while not self._stop_cordon_watch.is_set():
      try:
        resource_version = self.core_api.list_node(
            _request_timeout=60
        ).metadata.resource_version
        for event in w.stream(
            self.core_api.list_node,
            resource_version=resource_version,
            timeout_seconds=60,
        ):
          if self._stop_cordon_watch.is_set():
            break
          node = event["object"]
          node_name = node.metadata.name
          is_cordoned = node.spec.unschedulable

          with self._cordon_lock:
            if is_cordoned:
              if node_name not in self._cordoned_nodes:
                self.logger.info(f"Node {node_name} is now cordoned.")
                self._cordoned_nodes.add(node_name)
            else:
              if node_name in self._cordoned_nodes:
                self.logger.info(f"Node {node_name} is now uncordoned.")
                self._cordoned_nodes.discard(node_name)
      except client.ApiException as e:
        if e.status == 410:  # Gone
          self.logger.warning(
              "Resource version for node watch is too old. Resyncing."
          )
          with self._cordon_lock:
            self._cordoned_nodes = set(self._get_initially_cordoned_nodes())
        else:
          self.logger.warning(f"API error watching nodes: {e}. Retrying...")
          time.sleep(5)
      except Exception as e:
        self.logger.warning(
            f"Unexpected error watching nodes: {e}. Retrying..."
        )
        time.sleep(5)
    w.stop()
    self.logger.info("Cordoned node watcher stopped.")

  def _watch_all_pods(self):
    """Watches all pod events and dispatches them to the correct jobset."""
    w = watch.Watch()
    jobset_label = "jobset.sigs.k8s.io/jobset-name"

    while not self._stop_pod_watch.is_set():
      try:
        # Initial population
        with self._pod_lock:
          self.jobset_pods.clear()
          pods = self.core_api.list_namespaced_pod(
              namespace=self.namespace, label_selector=jobset_label
          )
          for pod in pods.items:
            if jobset_label in pod.metadata.labels:
              jobset_name = pod.metadata.labels[jobset_label]
              self.jobset_pods[jobset_name][pod.metadata.name] = pod

          # Recalculate for all jobsets after initial load
          for jobset_name in self.jobset_pods:
            self._recalculate_jobset_pod_status(jobset_name)

        resource_version = pods.metadata.resource_version

        for event in w.stream(
            self.core_api.list_namespaced_pod,
            namespace=self.namespace,
            label_selector=jobset_label,
            resource_version=resource_version,
            timeout_seconds=60,
        ):
          if self._stop_pod_watch.is_set():
            break

          pod = event["object"]
          if pod.metadata.labels and jobset_label in pod.metadata.labels:
            with self._pod_lock:
              jobset_name = pod.metadata.labels[jobset_label]
              pod_name = pod.metadata.name

              if event["type"] in ("ADDED", "MODIFIED"):
                self.jobset_pods[jobset_name][pod_name] = pod

              elif event["type"] == "DELETED":
                self.jobset_pods[jobset_name].pop(pod_name, None)

              self._recalculate_jobset_pod_status(jobset_name)

      except client.ApiException as e:
        if e.status == 410:  # Gone
          self.logger.warning(
              "Resource version for pod watch is too old. Resyncing."
          )
        else:
          self.logger.warning(f"API error watching pods: {e}. Retrying...")
          time.sleep(5)

      except Exception as e:
        self.logger.warning(f"Unexpected error watching pods: {e}. Retrying...")
        time.sleep(5)

    w.stop()
    self.logger.info("Jobset pod watcher stopped.")

  def _recalculate_jobset_pod_status(self, jobset_name: str):
    """Recalculates the aggregated pod status for a jobset."""
    status: dict[str, typing.Any] = {
        "total_pods": 0,
        "running_pods": 0,
        "pending_pods": [],
        "other_state_pods": [],
        "all_running": False,
    }
    pods = self.jobset_pods.get(jobset_name, {}).values()

    for pod in pods:
      status["total_pods"] += 1

      if pod.status.phase == "Running":
        # Check if all containers in pod are running
        all_containers_running = all(
            container.state.running is not None
            for container in pod.status.container_statuses
            if container.state is not None
        )

        if all_containers_running:
          status["running_pods"] += 1
        else:
          status["other_state_pods"].append({
              "name": pod.metadata.name,
              "phase": pod.status.phase,
              "containers": [
                  {
                      "name": container.name,
                      "state": (
                          next(iter(container.state.to_dict().keys()))
                          if container.state
                          else "unknown"
                      ),
                  }
                  for container in pod.status.container_statuses
              ],
          })
      elif pod.status.phase == "Pending":
        status["pending_pods"].append(
            {"name": pod.metadata.name, "start_time": pod.status.start_time}
        )
      else:
        status["other_state_pods"].append(
            {"name": pod.metadata.name, "phase": pod.status.phase}
        )

    status["all_running"] = (
        status["running_pods"] == status["total_pods"]
        and status["total_pods"] > 0
    )
    self.jobset_pod_statuses[jobset_name] = status

  def reset_host(
      self, workload_info: supervisor_core.WorkloadInfo, host_name: str
  ) -> None:
    """Resets the specified host in Kubernetes.

    Args:
        host_name: The host name (node name) of the host to reboot.
    """
    pass

  def drain_host(
      self,
      workload_info: supervisor_core.WorkloadInfo,
      host_name: str,
  ) -> None:
    """Cordons and drains the specified host in a Kubernetes cluster.

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.
        host_name: The host name (node name) of the machine to quarantine.
    """
    self.cordon_host(workload_info, host_name)
    self.delete_pod(workload_info, host_name)

  def cordon_host(
      self,
      workload_info: supervisor_core.WorkloadInfo,
      host_name: str,
  ) -> None:
    """Cordons the specified host in a Kubernetes cluster.

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.
        host_name: The host name (node name) of the machine to quarantine.
    """
    self.logger.info(
        f"Cordoning host {host_name} for workload"
        f" {workload_info.workload_name}."
    )

    try:
      node = self.core_api.read_node(name=host_name)
      if (
          node.metadata.labels
          and "cloud.google.com/perform-reboot" in node.metadata.labels
          and node.metadata.labels["cloud.google.com/perform-reboot"] == "true"
      ):
        self.logger.info(
            f"Node {host_name} is pending reboot. Skipping cordoning."
        )
        return

    except client.ApiException:
      self.logger.exception(f"Failed to read node {host_name}.")
      return

    cordon_result = subprocess.run(
        ["kubectl", "cordon", host_name],
        check=True,
        capture_output=True,
        shell=False,
    )

    if cordon_result.returncode == 0:
      self.logger.info(f"Successfully cordoned node {host_name}.")
    else:
      self.logger.exception(f"Failed to cordon node {host_name}.")

  def uncordon_host(
      self,
      workload_info: supervisor_core.WorkloadInfo,
      host_name: str,
  ) -> None:
    """Uncordons the specified host in a Kubernetes cluster.

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.
        host_name: The host name (node name) of the machine to quarantine.
    """
    self.logger.info(
        f"Uncordoning host {host_name} for workload"
        f" {workload_info.workload_name}."
    )
    uncordon_result = subprocess.run(
        ["kubectl", "uncordon", host_name],
        check=True,
        capture_output=True,
        shell=False,
    )

    if uncordon_result.returncode == 0:
      self.logger.info(f"Successfully uncordoned node {host_name}.")
    else:
      self.logger.exception(f"Failed to uncordon node {host_name}.")

  def delete_pod(
      self, workload_info: supervisor_core.WorkloadInfo, host_name: str
  ) -> None:
    """Deletes the pod running on the specified host.

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.
        host_name: The host name (node name) of the machine.
    """
    self.logger.info(
        f"Deleting pod on host {host_name} for workload"
        f" {workload_info.workload_name}."
    )

    pod_name = self._get_pod_on_host(host_name)

    if not pod_name:
      self.logger.warning(
          f"No workload pod found on host {host_name}. Skipping pod deletion."
      )
      return

    self._force_delete_pod(pod_name)

  def restart_jobset(
      self,
      workload_info: supervisor_core.WorkloadInfo,
      host_name: str,
      scale_direction: str | None = None,
      cordon_host: bool = True,
  ) -> bool:
    """Restarts a jobset running on the specified host.

    This method can handle a jobset with hanging pods by:
    1. Getting the current jobset spec
    2. Deleting the hanging jobset
    3. Creating a new jobset

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.
        host_name: The host name (node name) associated with the jobset.
        scale_direction: Optional argument to scale the jobset replicas up or
          down. Valid values are "up", "down", or None (no scaling).
        cordon_host: Optional argument to cordon the host after scaling down.

    Returns:
        True if the jobset was successfully restarted, False otherwise.

    Raises:
        ValueError: If the scale_direction is invalid.
    """
    try:
      if scale_direction not in ["up", "down", None]:
        raise ValueError(f"Invalid scale direction: {scale_direction}")

      if scale_direction is not None and (
          workload_info.num_nodes_per_data_replica < 1
      ):
        raise ValueError(
            "Cannot scale jobset if num_nodes_per_data_replica is invalid."
        )

      self.logger.info(
          f"Retrieving jobset spec for {workload_info.workload_name} before"
          " deletion."
      )
      new_spec = self._get_jobset_spec(workload_info.workload_name)
      if not new_spec:
        return False

      self.logger.info(f"Deleting jobset {workload_info.workload_name}.")
      if not self._delete_jobset(workload_info.workload_name):
        return False

      # Wait for the pod termination threshold to ensure that all pods are terminated
      self.logger.info(
          f"Waiting {workload_info.container_termination_threshold_s} seconds"
          " for pods to terminate."
      )
      time.sleep(workload_info.container_termination_threshold_s)

      # Scale the number of replicas if necessary
      if scale_direction == "up" and self._can_scale_up(workload_info):
        self.logger.info(
            f"Scaling jobset {workload_info.workload_name} up by"
            f" {workload_info.num_nodes_per_data_replica} nodes."
        )
        new_spec = self._scale_jobset_spec(
            workload_info, new_spec, scale_direction
        )

      elif scale_direction == "down" and self._can_scale_down(workload_info):
        self.logger.info(
            f"Scaling jobset {workload_info.workload_name} down by"
            f" {workload_info.num_nodes_per_data_replica} nodes."
        )
        new_spec = self._scale_jobset_spec(
            workload_info, new_spec, scale_direction
        )

        # Cordon faulty host to avoid rescheduling post-scale down
        if cordon_host:
          self.cordon_host(workload_info, host_name)

      # Check for stuck pods and force delete them
      stuck_pods = self._get_stuck_pods(workload_info)
      if stuck_pods:
        self.logger.warning(
            f"Found {len(stuck_pods)} pods stuck in terminating state in Jobset"
            f" {workload_info.workload_name}. Force deleting pods..."
        )
        for pod in stuck_pods:
          self._force_delete_pod(pod["name"])

      # Remove Kueue annotation from the jobset spec if it exists
      self._remove_kueue_annotation(workload_info.job_name, new_spec)

      # Create new Jobset with updated spec
      if self._create_jobset(new_spec):
        self.logger.info(
            f"Successfully restarted jobset {workload_info.workload_name} as"
            f" {new_spec['metadata']['name']}"
        )
        return True

      return False

    except RuntimeError:
      self.logger.exception(
          "An error occurred while restarting jobset"
          f" {workload_info.workload_name}."
      )
      return False

  def reset_gpu(
      self,
      host_name: str,
      gpu_local_rank: str,
  ) -> None:
    """Resets a specific GPU on a given host.

    Args: host name: The host name (node name) of the host.
        gpu_local_rank: The local rank of the GPU to reset.
    """
    pass

  def get_cordoned_nodes(self) -> list[str]:
    """Returns a list of cordoned nodes in the cluster."""
    with self._cordon_lock:
      return list(self._cordoned_nodes)

  def poll_jobset_status(
      self, workload_info: supervisor_core.WorkloadInfo, host_name: str
  ):
    """Polls the status of a Jobset and initiates resubmission if needed.

    This method checks for stuck pods and non-running pods in the jobset.
    If stuck pods are found, it restarts the jobset. If non-running pods
    persist for longer than the configured threshold, it also restarts the
    jobset.

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.
        host_name: The host name (node name) associated with the jobset.
    """
    workload_name = workload_info.workload_name

    try:
      if not workload_name:
        self.logger.warning(
            "Workload name is empty. Skipping jobset status polling."
        )
        return

      if not self._check_jobset_exists(workload_name):
        return

      with self._pod_lock:
        pod_status = self.jobset_pod_statuses.get(workload_name)
      self.logger.info(f"Jobset {workload_name} pod status: {pod_status}")

      if workload_name not in self.workload_downtime:
        self.workload_downtime[workload_name] = None

      if pod_status and not pod_status["all_running"]:
        if self.workload_downtime[workload_name] is None:
          self.workload_downtime[workload_name] = time.time()
          self.logger.warning(
              f"Jobset {workload_name} has non-running pods. "
              f"Pending: {len(pod_status['pending_pods'])}, "
              f"Other states: {len(pod_status['other_state_pods'])}. "
              "Will check again in"
              f" {workload_info.workload_downtime_threshold_s} seconds."
          )
        else:
          if (
              time.time() - self.workload_downtime[workload_name]
              > workload_info.workload_downtime_threshold_s
          ):
            self.logger.warning(
                f"Jobset {workload_name} pods not running for more than"
                f" {workload_info.workload_downtime_threshold_s} seconds."
            )

            if (
                pod_status["pending_pods"]
                and workload_info.workload_scaling_enabled
            ):
              self.logger.warning(
                  f"Jobset {workload_name} has pending pods. Will scale down."
              )
              if self.restart_jobset(workload_info, host_name, "down", False):
                self.logger.info(
                    "Successfully scaled down jobset"
                    f" {workload_info.workload_name} after detecting pending"
                    " pods."
                )
                self.workload_downtime[workload_name] = None
              else:
                self.logger.exception(
                    "Failed to scale down jobset"
                    f" {workload_info.workload_name} after detecting pending"
                    " pods."
                )
            else:
              self.logger.warning(
                  f"Jobset {workload_name} has non-running pods. Will restart."
              )
              if self.restart_jobset(workload_info, host_name):
                self.logger.info(
                    "Successfully restarted jobset"
                    f" {workload_info.workload_name} after detecting"
                    " non-running pods."
                )
                self.workload_downtime[workload_name] = None
              else:
                self.logger.exception(
                    "Failed to restart jobset"
                    f" {workload_info.workload_name} after detecting"
                    " non-running pods."
                )

      elif pod_status and pod_status["all_running"]:
        self.workload_downtime[workload_name] = None
        self.logger.info(f"All pods in jobset {workload_name} are running.")

      else:
        self.logger.warning(
            f"Could not retrieve pod status for pods in jobset {workload_name}."
        )

    except RuntimeError:
      self.logger.exception(
          f"Error while polling jobset {workload_name} status."
      )

  def _get_pod_on_host(self, host_name: str):
    """Gets the name of the GPU requesting running pod on the specified host.

    Args:
        host_name: The name of the host (node).

    Returns:
        The name of the running GPU requesting pod found on the node, or None if
        no such pod is found.

    Raises:
        client.rest.ApiException: If there is an error getting the pod list.
    """
    try:
      pods = self.core_api.list_namespaced_pod(
          namespace=self.namespace, field_selector=f"spec.nodeName={host_name}"
      )
      for pod in pods.items:
        if pod.status.phase == "Running" and "daemon" not in pod.metadata.name:
          for container_spec in pod.spec.containers:
            if (
                container_spec.resources
                and container_spec.resources.limits
                and "nvidia.com/gpu" in container_spec.resources.limits
            ):
              return pod.metadata.name

      return None

    except client.rest.ApiException:
      self.logger.exception(f"Error getting pods on node {host_name}.")
      return None

  def _force_delete_pod(self, pod_name: str) -> bool:
    """Force deletes a pod.

    Args:
        pod_name: The name of the pod to delete.
    """
    try:
      self.core_api.delete_namespaced_pod(
          name=pod_name,
          namespace=self.namespace,
          propagation_policy="Background",
          grace_period_seconds=0,
      )
      self.logger.info(f"Successfully deleted workload pod {pod_name}.")
    except client.ApiException:
      self.logger.exception(f"Failed to delete workload pod {pod_name}.")

  def _create_jobset(self, jobset_spec: dict) -> bool:
    """Creates a new jobset from the given spec.

    Args:
        jobset_spec: A dictionary representing the jobset specification.

    Returns:
        True if the jobset was successfully created, False otherwise.

    Raises:
        RuntimeError: If there is an error creating the jobset.
    """
    try:
      self.custom_api.create_namespaced_custom_object(
          group="jobset.x-k8s.io",
          version="v1alpha2",
          namespace=self.namespace,
          plural="jobsets",
          body=jobset_spec,
      )
      return True

    except RuntimeError:
      self.logger.exception(
          f"Error creating new jobset {jobset_spec['metadata']['name']}."
      )
      return False

  def _delete_jobset(self, jobset_name: str) -> bool:
    """Deletes the entire jobset.

    Args:
        jobset_name: The name of the jobset to delete.

    Returns:
        True if the jobset was successfully deleted, False otherwise.

    Raises:
        RuntimeError: If there is an error deleting the jobset.
    """
    try:
      self.custom_api.delete_namespaced_custom_object(
          group="jobset.x-k8s.io",
          version="v1alpha2",
          namespace=self.namespace,
          plural="jobsets",
          name=jobset_name,
          body=client.V1DeleteOptions(
              grace_period_seconds=0, propagation_policy="Background"
          ),
      )
      return True

    except RuntimeError:
      self.logger.exception(f"Error deleting jobset {jobset_name}.")
      return False

  def _check_jobset_exists(self, jobset_name: str) -> bool:
    """Checks if a jobset exists."""
    try:
      self.custom_api.get_namespaced_custom_object(
          group="jobset.x-k8s.io",
          version="v1alpha2",
          namespace=self.namespace,
          plural="jobsets",
          name=jobset_name,
      )
      return True

    except client.ApiException:
      self.logger.warning(
          f"Jobset {jobset_name} does not exist. This usually means the Jobset"
          " was already deleted. Cleaning up state."
      )
      if jobset_name in self.jobset_pods:
        del self.jobset_pods[jobset_name]
      if jobset_name in self.jobset_pod_statuses:
        del self.jobset_pod_statuses[jobset_name]
      return False

  def get_workload_info(
      self, host_name: str
  ) -> supervisor_core.WorkloadInfo | None:
    """Gets the name of a JobSet running on the specified host.

    Args:
        host_name: The name of the host (node).

    Returns:
        The name of the JobSet running on the host, or None if no JobSet is
        found.

    Raises:
        client.rest.ApiException: If there is an error getting the jobset list.
    """
    try:
      pod_name = self._get_pod_on_host(host_name)

      if not pod_name:
        self.logger.info(
            f"No workload pod found on host {host_name}. Cannot determine"
            " Jobset name."
        )
        return None

      jobsets = self.custom_api.list_namespaced_custom_object(
          group="jobset.x-k8s.io",
          version="v1alpha2",
          namespace=self.namespace,
          plural="jobsets",
          field_selector=(
              "status.terminalState!=Failed,status.terminalState!=Completed"
          ),
      )
      jobset_name = None
      jobset_spec = None
      for jobset in jobsets.get("items", []):
        if jobset["metadata"]["name"] in pod_name:
          jobset_name = jobset["metadata"]["name"]
          jobset_spec = jobset

      if not jobset_name or not jobset_spec:
        self.logger.warning(
            f"No Jobset found on host {host_name} matching pod name {pod_name}."
        )
        return None

      workload_info = supervisor_core.WorkloadInfo()
      workload_info.workload_name = jobset_name

      jobset_annotations = (
          jobset_spec["metadata"]["annotations"]
          if "annotations" in jobset_spec["metadata"]
          else None
      )
      if jobset_annotations is None:
        self.logger.warning(f"Jobset {jobset_name} does not have annotations.")
        return None

      if "supervisor/container-name" in jobset_annotations:
        workload_info.container_name = jobset_annotations[
            "supervisor/container-name"
        ]
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a container name annotation."
        )
      if "supervisor/job-name" in jobset_annotations:
        workload_info.job_name = jobset_annotations["supervisor/job-name"]
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a job name annotation."
        )
      if "supervisor/max-workload-restarts" in jobset_annotations:
        workload_info.max_workload_restarts = int(
            jobset_annotations["supervisor/max-workload-restarts"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a max workload restarts"
            " annotation."
        )
      if "supervisor/max-in-job-restarts" in jobset_annotations:
        workload_info.max_in_job_restarts = int(
            jobset_annotations["supervisor/max-in-job-restarts"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a max in job restarts"
            " annotation."
        )
      if "supervisor/workload-downtime-threshold-s" in jobset_annotations:
        workload_info.workload_downtime_threshold_s = int(
            jobset_annotations["supervisor/workload-downtime-threshold-s"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a workload downtime threshold"
            " annotation."
        )
      if "supervisor/enable-workload-scaling" in jobset_annotations:
        workload_info.workload_scaling_enabled = (
            jobset_annotations["supervisor/enable-workload-scaling"] == "true"
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a workload scaling enabled"
            " annotation."
        )
      if "supervisor/container-termination-threshold-s" in jobset_annotations:
        workload_info.container_termination_threshold_s = int(
            jobset_annotations["supervisor/container-termination-threshold-s"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a container termination"
            " threshold annotation."
        )
      if "supervisor/num-nodes-per-dp" in jobset_annotations:
        workload_info.num_nodes_per_data_replica = int(
            jobset_annotations["supervisor/num-nodes-per-dp"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a num nodes per dp annotation."
        )
      if "supervisor/min-num-dp-replicas" in jobset_annotations:
        workload_info.min_num_data_replicas = int(
            jobset_annotations["supervisor/min-num-dp-replicas"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a min num dp replicas"
            " annotation."
        )
      if "supervisor/max-num-dp-replicas" in jobset_annotations:
        workload_info.max_num_data_replicas = int(
            jobset_annotations["supervisor/max-num-dp-replicas"]
        )
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a max num dp replicas"
            " annotation."
        )

      if not workload_info.job_name or not workload_info.container_name:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a job name or container name"
            " annotation."
        )
        return workload_info

      replicated_job_index = self._find_replicated_job_index(
          workload_info.job_name, jobset_spec
      )
      container_index = self._find_container_index(
          workload_info.container_name, jobset_spec, replicated_job_index
      )

      env_vars = jobset_spec["spec"]["replicatedJobs"][replicated_job_index][
          "template"
      ]["spec"]["template"]["spec"]["containers"][container_index]["env"]
      for env_var in env_vars:
        if env_var["name"] == "NNODES":
          workload_info.num_data_replicas = (
              int(env_var["value"]) // workload_info.num_nodes_per_data_replica
          )
          break
      else:
        self.logger.warning(
            f"Jobset {jobset_name} does not have a NNODES environment variable."
        )

      return workload_info

    except client.ApiException:
      self.logger.exception(
          "A Kubernetes API error occurred while retrieving Jobsets on node"
          f" {host_name}."
      )
      return None

  def _get_jobset_spec(self, jobset_name: str) -> dict | None:
    """Gets the current JobSet spec for resubmission.

    Args:
        jobset_name: The name of the jobset.

    Returns:
        A dictionary representing the jobset specification, or None if
        there is an error getting the spec.

    Raises:
        RuntimeError: If there is an error getting the jobset spec.
    """
    try:
      jobset = self.custom_api.get_namespaced_custom_object(
          group="jobset.x-k8s.io",
          version="v1alpha2",
          namespace=self.namespace,
          plural="jobsets",
          name=jobset_name,
      )

      # Create a clean copy for resubmission
      new_spec = copy.deepcopy(jobset)

      # Remove metadata that shouldn"t be reused
      new_spec["metadata"].pop("resourceVersion", None)
      new_spec["metadata"].pop("uid", None)
      new_spec["metadata"].pop("creationTimestamp", None)
      new_spec["metadata"].pop("generation", None)

      return new_spec

    except client.ApiException:
      self.logger.warning(
          f"Jobset {jobset_name} does not exist. This usually means the Jobset"
          " was already deleted. Cleaning up state."
      )
      with self._pod_lock:
        if jobset_name in self.jobset_pods:
          del self.jobset_pods[jobset_name]
        if jobset_name in self.jobset_pod_statuses:
          del self.jobset_pod_statuses[jobset_name]
      return None

    except RuntimeError:
      self.logger.exception(
          "An unexpected error occurred while retrieving Jobset spec for"
          f" {jobset_name}."
      )
      return None

  def _get_stuck_pods(
      self, workload_info: supervisor_core.WorkloadInfo
  ) -> list[dict[str, typing.Any]]:
    """Find pods in the jobset that are stuck in Terminating state.

    Args:
        workload_info: The WorkloadInfo object containing information about the
          workload running on the host.

    Returns:
        A list of stuck pods with their details.
    """
    stuck_pods = []

    try:
      # Get all pods for this jobset
      pods = self.core_api.list_namespaced_pod(
          namespace=self.namespace,
          label_selector=(
              f"jobset.sigs.k8s.io/jobset-name={workload_info.workload_name}"
          ),
      )

      current_time = datetime.datetime.now()

      for pod in pods.items:
        # Check if pod is terminating
        if pod.metadata.deletion_timestamp:
          # Calculate how long it"s been terminating
          deletion_time = pod.metadata.deletion_timestamp.replace(tzinfo=None)
          terminating_duration = (current_time - deletion_time).total_seconds()
          threshold = max(
              pod.spec.termination_grace_period_seconds,
              workload_info.container_termination_threshold_s,
          )

          if terminating_duration > threshold:
            stuck_pods.append({
                "name": pod.metadata.name,
                "node": pod.spec.node_name,
                "terminating_duration": terminating_duration,
                "pod": pod,
            })

    except RuntimeError:
      self.logger.exception(
          "An error occurred while checking for stuck pods in Jobset"
          f" {workload_info.workload_name}."
      )

    return stuck_pods

  def _can_scale_up(self, workload_info: supervisor_core.WorkloadInfo) -> bool:
    """Returns if the jobset can scale up one data parallel replica."""
    if (
        workload_info.num_data_replicas is None
        or workload_info.num_nodes_per_data_replica < 1
    ):
      self.logger.warning(
          "Skipping jobset scale up due to missing NUM_DP_REPLICAS or"
          " NUM_NODES_PER_DP environment variables."
      )
      return False

    can_scale_up = (
        workload_info.num_data_replicas + 1
        <= workload_info.max_num_data_replicas
    )
    if not can_scale_up:
      self.logger.warning(
          f"Cannot scale up jobset {workload_info.workload_name} to"
          f" {workload_info.num_data_replicas + 1} data parallel replicas."
      )

    return can_scale_up

  def _can_scale_down(
      self, workload_info: supervisor_core.WorkloadInfo
  ) -> bool:
    """Returns if the jobset can scale down one data parallel replica."""
    if (
        workload_info.num_data_replicas is None
        or workload_info.num_nodes_per_data_replica is None
    ):
      self.logger.warning(
          "Skipping jobset scale down due to missing NUM_DP_REPLICAS or"
          " NUM_NODES_PER_DP environment variables."
      )
      return False

    can_scale_down = (
        workload_info.num_data_replicas - 1
        >= workload_info.min_num_data_replicas
    )
    if not can_scale_down:
      self.logger.warning(
          f"Cannot scale down jobset {workload_info.workload_name} to"
          f" {workload_info.num_data_replicas - 1} data parallel replicas."
      )

    return can_scale_down

  def _scale_jobset_spec(
      self,
      workload_info: supervisor_core.WorkloadInfo,
      jobset_spec: dict[str, typing.Any],
      scale_direction: str,
  ) -> dict:
    """Scales the jobset spec replicas up or down."""

    if scale_direction not in ["up", "down"]:
      raise ValueError(f"Invalid scale direction: {scale_direction}")

    if not workload_info.job_name:
      raise ValueError("Cannot scale jobset if job_name is not provided.")

    if not workload_info.container_name:
      raise ValueError("Cannot scale jobset if container_name is not provided.")

    if workload_info.num_nodes_per_data_replica < 1:
      raise ValueError(
          "Cannot scale jobset if num_nodes_per_data_replica is not provided."
      )

    if workload_info.num_data_replicas is None:
      raise ValueError("Cannot scale jobset if num_dp is not provided.")

    jobset_name = jobset_spec["metadata"]["name"]
    nodes_to_add = 0

    if scale_direction == "up":
      nodes_to_add = workload_info.num_nodes_per_data_replica
      logging.info(
          f"Scaling jobset {jobset_name} replicas up by {nodes_to_add} nodes."
      )
    elif scale_direction == "down":
      nodes_to_add = -workload_info.num_nodes_per_data_replica
      logging.info(
          f"Scaling jobset {jobset_name} replicas down by"
          f" {-nodes_to_add} nodes."
      )

    # Get the index of the replicated job and container in the spec
    replicated_job_index = self._find_replicated_job_index(
        workload_info.job_name, jobset_spec
    )
    container_index = self._find_container_index(
        workload_info.container_name, jobset_spec, replicated_job_index
    )

    # Update the parallelism and completions
    jobset_spec["spec"]["replicatedJobs"][replicated_job_index]["template"][
        "spec"
    ]["parallelism"] += nodes_to_add
    jobset_spec["spec"]["replicatedJobs"][replicated_job_index]["template"][
        "spec"
    ]["completions"] += nodes_to_add

    # Update the NNODES env var
    env_vars = jobset_spec["spec"]["replicatedJobs"][replicated_job_index][
        "template"
    ]["spec"]["template"]["spec"]["containers"][container_index]["env"]
    env_vars = [
        {"name": var["name"], "value": str(int(var["value"]) + nodes_to_add)}
        if var["name"] == "NNODES"
        else var
        for var in env_vars
    ]
    jobset_spec["spec"]["replicatedJobs"][replicated_job_index]["template"][
        "spec"
    ]["template"]["spec"]["containers"][container_index]["env"] = env_vars

    return jobset_spec

  def _find_replicated_job_index(
      self, job_name: str, jobset_spec: dict[str, typing.Any]
  ) -> int:
    """Finds the index of the replicated job in the jobset spec."""
    for i, job_spec in enumerate(jobset_spec["spec"]["replicatedJobs"]):
      if job_spec["name"] == job_name:
        return i
    raise ValueError(f"Replicated job {job_name} not found in jobset spec.")

  def _find_container_index(
      self,
      container_name: str,
      jobset_spec: dict[str, typing.Any],
      replicated_job_index: int,
  ) -> int:
    """Finds the index of the workload container in the jobset spec."""
    for i, container_spec in enumerate(
        jobset_spec["spec"]["replicatedJobs"][replicated_job_index]["template"][
            "spec"
        ]["template"]["spec"]["containers"]
    ):
      if container_spec["name"] == container_name:
        return i
    raise ValueError(f"Container {container_name} not found in jobset spec.")

  def _remove_kueue_annotation(
      self, job_name: str, jobset_spec: dict[str, typing.Any]
  ):
    """Removes the Kueue annotations from the jobset spec."""
    replicated_job_index = self._find_replicated_job_index(
        job_name, jobset_spec
    )
    if (
        "metadata"
        not in jobset_spec["spec"]["replicatedJobs"][replicated_job_index][
            "template"
        ]["spec"]["template"]
    ):
      return

    if (
        "annotations"
        not in jobset_spec["spec"]["replicatedJobs"][replicated_job_index][
            "template"
        ]["spec"]["template"]["metadata"]
    ):
      return

    if (
        "kueue.x-k8s.io/workload"
        in jobset_spec["spec"]["replicatedJobs"][replicated_job_index][
            "template"
        ]["spec"]["template"]["metadata"]["annotations"]
    ):
      self.logger.info(
          "Removing Kueue annotation from jobset"
          f" {jobset_spec['metadata']['name']}."
      )
      jobset_spec["spec"]["replicatedJobs"][replicated_job_index]["template"][
          "spec"
      ]["template"]["metadata"]["annotations"].pop(
          "kueue.x-k8s.io/workload", None
      )
