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
import time

from supervisor.client.python.orchestrators import gke_callbacks
from supervisor.core.python import utils as core_utils
import supervisor_core


class BaseController:
  """Base implementation of the Python wrapper for the Supervisor controller.

  Subclasses can implement the event_policy method to handle events
  reported by the Controller process in a custom way.

  Controller provides a series of primitive to trigger different types of
  orchestrator level commands. These include:
  - trigger_in_job_reset: Triggers a reset for all hosts currently tracked by
  the controller.
  - trigger_workload_reset: Triggers a reset of all pods for the workload
  running on the specified host.
  - trigger_workload_recreation: Triggers a job recreation for the workload
  running on the specified host.
  - trigger_hot_swap: Triggers a hot-swap for the specified host.
  - trigger_scale_down: Triggers a data parallel scale down for the
  jobset running on the specified host.
  - trigger_scale_up: Triggers a data parallel scale up for the jobset
  running on the specified host.

  Stores all metadata related to the Controller process and provides an
  interface to interact with the Controller process. The Controller process is
  responsible for computing new cluster states given events reported by the
  Controller.
  """

  def __init__(
      self,
      port: int,
      num_grpc_threads: int,
      supervisor_config: supervisor_core.SupervisorConfig | None = None,
      orchestrator: str = "GKE",
  ):
    """Constructs the Controller object.

    Args:
        port: The port on which to run the controller communication.
        num_grpc_threads: The number of gRPC threads to initialize for
          communication.
        supervisor_config: The config object for Supervisor components.
        orchestrator: The orchestrator to use for the controller.
    """
    self.logger = core_utils.setup_logger()

    if not supervisor_config:
      supervisor_config = supervisor_core.SupervisorConfig.from_environment()

    self._controller = supervisor_core.Controller(
        port=port,
        num_grpc_threads=num_grpc_threads,
        config=supervisor_config,
        command_handle_fn=self._command_handler,
        update_handle_fn=self._update_handler,
        event_handle_fn=self._event_handler,
    )

    self._controller.start()
    while not self._controller.is_ready():
      continue

    self._controller_address = supervisor_config.controller_address
    self.logger.info(
        f"Successfully started controller process at address: {self.address}"
    )

    if orchestrator == "GKE":
      self._orchestrator = gke_callbacks.KubernetesCallbacks(
          supervisor_config.workload_namespace
      )
      self._orchestrator_callbacks = {
          "uncordon_host": self._orchestrator.uncordon_host,
          "delete_pod": self._orchestrator.delete_pod,
          "restart_jobset": self._orchestrator.restart_jobset,
          "reset_gpu": self._orchestrator.reset_gpu,
          "poll_workload_status": self._orchestrator.poll_jobset_status,
          "get_cordoned_nodes": self._orchestrator.get_cordoned_nodes,
          "drain_host": self._orchestrator.drain_host,
      }
    else:
      raise ValueError(f"Unsupported orchestrator type: {orchestrator}")

    self._failure_counter = collections.Counter()
    self._in_job_restarts = collections.Counter()

  def __repr__(self) -> str:
    return f"{self.name}@{self.address}"

  @property
  def name(self) -> str:
    """Returns the name of the Controller process."""
    return "controller"

  @property
  def address(self) -> str:
    """Returns the address of the Controller process."""
    return self._controller_address

  @property
  def num_hosts(self) -> str:
    """Returns the total number of hosts currently tracked by the controller."""
    return self._controller.num_hosts()

  @property
  def num_workers(self) -> str:
    """Returns the number of workers participating in training currently tracked by the controller."""
    return self._controller.num_workers()

  @property
  def num_running_hosts(self) -> str:
    """Returns the number of hosts participating in training currently tracked by the controller."""
    return self._controller.num_running_hosts()

  @property
  def num_spare_hosts(self) -> str:
    """Returns the number of idle hosts currently tracked by the controller."""
    return self._controller.num_spare_hosts()

  @property
  def failure_counter(self) -> dict[str, int]:
    """Returns the failure counter for each host currently tracked by the controller."""
    return self._failure_counter

  def trigger_in_job_reset(self, host_info: supervisor_core.HostInfo):
    """Reset host daemon state in preparation for a NVRX in-job reset."""
    self._controller.trigger_in_job_reset(host_info)

  def trigger_workload_reset(self, host_info: supervisor_core.HostInfo):
    """Recreates all workload Pods for the workload with the GKE failure policy.

    Triggers recreation of all workload Pods for the workload running on the
    specified host by deleting a workload podand resets all corresponding host
    daemons.

    Args:
        host_info: The host info of the host to reset.
    """
    self._controller.trigger_workload_reset(host_info)

  def trigger_workload_recreation(self, host_info: supervisor_core.HostInfo):
    """Deletes and recreates the Jobset running on the specified host.

    Triggers deletion of the Jobset running on the specified host and recreates
    it. Also resets the state of all corresponding host daemons.

    Args:
        host_info: The host info of the host to recreate.
    """
    self._controller.trigger_workload_recreation(host_info)

  def trigger_hot_swap(self, host_info: supervisor_core.HostInfo):
    """Replaces the specified host with a spare host.

    Triggers replacement of the specified host with a spare host. The workload
    state running on the specified host will be migrated to the spare host. Also
    recreates all workload Pods for the workload using its GKE failure policy
    and resets all corresponding host daemon states.

    Args:
        host_info: The host info of the host to hot-swap.
    """
    self._controller.trigger_hot_swap(host_info)

  def trigger_scale_down(self, host_info: supervisor_core.HostInfo):
    """Scale down the data parallel dimension of the workload.

    Triggers scaling down the data parallel dimension of the workload running
    on the specified host. The workload will be scaled down by one data parallel
    replica and will be recreated with the new replica count.

    Args:
        host_info: The host info of the host to scale down.
    """
    self._controller.trigger_scale_down(host_info)

  def trigger_scale_up(self, host_info: supervisor_core.HostInfo):
    """Scale up the data parallel dimension of the workload.

    Triggers scaling up the data parallel dimension of the workload running
    on the specified host. The workload will be scaled up by one data parallel
    replica and will be recreated with the new replica count.

    Args:
        host_info: The host info of the host to scale up.
    """
    self._controller.trigger_scale_up(host_info)

  def trigger_cordon_host(self, host_name: str):
    """Notify the corresponding host daemon that its node is cordoned.

    Args:
        host_name: The name of the host to cordon.
    """
    self._controller.trigger_cordon_host(host_name)

  def shutdown(self):
    """Shuts down the controller process and child threads."""
    if hasattr(self._orchestrator, "shutdown"):
      self._orchestrator.shutdown()

    self._controller.shutdown()

  def wait_for_completion(self):
    """Waits for all hosts registered to controller to finish their workloads."""
    while not self._controller.is_complete():
      time.sleep(10)

  def event_policy(self, event_reports: supervisor_core.EventReports):
    """Default event policy for the Controller process."""

    self.logger.info(
        f"Received {len(event_reports.event_reports)} event reports from"
        " controller."
    )
    # Cache num_spare_hosts to avoid race conditions for simulaneous events
    num_spare_hosts = self.num_spare_hosts

    for event_report in event_reports.event_reports:
      event_type = event_report.event_type
      host_info = event_report.host_info
      workload_info = host_info.workload

      if workload_info.workload_name not in self._in_job_restarts:
        self._in_job_restarts[workload_info.workload_name] = 0

      if (
          event_type == supervisor_core.EventType.WORKER_HB
          and self._in_job_restarts[workload_info.workload_name]
          < workload_info.max_in_job_restarts
      ):
        # Only Reset Hosts in preparation for NVRX in-job reset
        self.trigger_in_job_reset(host_info)
        self._in_job_restarts[workload_info.workload_name] += 1

      elif event_type == supervisor_core.EventType.WORKER_HB:
        # Reset workload if a worker timeout is detected.
        self.trigger_workload_reset(host_info)
        self._in_job_restarts[workload_info.workload_name] = 0

      elif (
          event_type == supervisor_core.EventType.HOST_HB
          or event_type == supervisor_core.EventType.XID
          or event_type == supervisor_core.EventType.ECC
      ):

        self.failure_counter[host_info.host_name] += 1

        if num_spare_hosts > 0:
          # Attempt workload reset first, escalate to hot-swap if unsuccessful
          if (
              self.failure_counter[host_info.host_name]
              <= workload_info.max_workload_restarts
          ):
            self.trigger_workload_reset(host_info)

          else:
            self.trigger_hot_swap(host_info)
            self.failure_counter[host_info.host_name] = 0
            num_spare_hosts -= 1

        elif num_spare_hosts == 0 and workload_info.workload_scaling_enabled:
          # Scale down the jobset if there are no spare hosts available
          if (
              self.failure_counter[host_info.host_name]
              <= workload_info.max_workload_restarts
          ):
            self.trigger_workload_reset(host_info)

          else:
            self.trigger_scale_down(host_info)
            self.failure_counter[host_info.host_name] = 0
            num_spare_hosts += workload_info.num_nodes_per_data_replica

        else:
          # Restart the workload if hot-swap and scaling are not feasible
          self.logger.info(
              "Conditions not met for hot-swap and scaling, resetting"
              " workload..."
          )
          self.trigger_workload_reset(host_info)

      elif (
          event_type == supervisor_core.EventType.SCALE_UP
          and workload_info.workload_scaling_enabled
      ):
        self.trigger_scale_up(host_info)
        num_spare_hosts -= workload_info.num_nodes_per_data_replica

  def _update_handler(self, state: supervisor_core.SupervisorState):
    """Handle update requests to synchronize C++ and Python Supervisor state.

    Args:
        state: The current supervisor state coming from the C++ controller.
    """
    if not isinstance(state, supervisor_core.SupervisorState):
      raise ValueError((
          f"Invalid callback argument type: {type(state)}. "
          "The callback argument must be of type SupervisorState."
      ))

  def _event_handler(self, event_reports: supervisor_core.EventReports):
    """Handle event reports from the C++ controller.

    Args:
        event_reports: The event reports received from the C++ controller.
    """
    if not isinstance(event_reports, supervisor_core.EventReports):
      raise ValueError((
          f"Invalid callback argument type: {type(event_reports)}. "
          "The callback argument must be of type EventReports."
      ))
    self.event_policy(event_reports)

  def _command_handler(self, command: supervisor_core.Command):
    """Handle orchestrator level command issued by C++ controller.

    Args:
        command: The command received from the C++ controller.
    """
    if not isinstance(command, supervisor_core.Command):
      raise ValueError((
          f"Invalid callback argument type: {type(command)}. "
          "The callback argument must be of type Command."
      ))
    for callback, kwargs in zip(
        command.callback_names, command.callback_kwargs
    ):
      kwargs = core_utils.destringify_kwargs(kwargs)
      workload_info = command.host_info.workload
      if callback not in self._orchestrator_callbacks:
        raise ValueError(f"Unexpected callback {callback} received.")

      if callback == "get_cordoned_nodes":
        for node in self._orchestrator_callbacks[callback](**kwargs):
          self.trigger_cordon_host(node)
      else:
        self._orchestrator_callbacks[callback](
            workload_info=workload_info, **kwargs
        )
