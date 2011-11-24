#--
# Copyright (c) 2011, Sebastian Tello
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of copyright holders nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#--

import time

from resources import VimService_services as VI
from resources.vi_exception import VIException, VIApiException, FaultTypes
from vi_task import VITask
from vi_snapshot import VISnapshot
from vi_property import VIProperty

class VIVirtualMachine:

    def __init__(self, server, mor):
        self._server = server
        self._mor = mor
        self._properties = {}
        self._root_snapshots = []
        self._snapshot_list = []
        self._disks = []
        self._files = {}
        self._devices = {}
        self.__current_snapshot = None
        self._resource_pool = None
        self.properties = None
        self._properties = {}
        self.__update_properties()
        self._mor_vm_task_collector = None
        

    def power_on(self, sync_run=True, host=None):
        """Attemps to power on the VM. If @sync_run is True (default) waits for
        the task to finish, and returns (raises an exception if the task didn't
        succeed). If sync_run is set to False the task is started an a VITask
        instance is returned. You may additionally provided a managed object
        reference to a host where the VM should be powered on at."""
        try:
            request = VI.PowerOnVM_TaskRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)
            if host:
                mor_host = request.new_host(host)
                mor_host.set_attribute_type(host.get_attribute_type())
                request.set_element_host(mor_host)

            task = self._server._proxy.PowerOnVM_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def power_off(self, sync_run=True):
        """Attemps to power off the VM. If @sync_run is True (default) waits for
        the task to finish, and returns (raises an exception if the task didn't
        succeed). If sync_run is set to False the task is started an a VITask
        instance is returned. """
        try:
            request = VI.PowerOffVM_TaskRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)

            task = self._server._proxy.PowerOffVM_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def reset(self, sync_run=True):
        """Attempts to reset the VM. If @sync_run is True (default) waits for the
        task to finish, and returns (raises an exception if the task didn't
        succeed). If sync_run is set to False the task is started an a VITask
        instance is returned. """
        try:
            request = VI.ResetVM_TaskRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)

            task = self._server._proxy.ResetVM_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def suspend(self, sync_run=True):
        """Attempts to suspend the VM (it must be powered on)"""
        try:
            request = VI.SuspendVM_TaskRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)

            task = self._server._proxy.SuspendVM_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def reboot_guest(self):
        """Issues a command to the guest operating system asking it to perform
        a reboot. Returns immediately and does not wait for the guest operating
        system to complete the operation."""
        try:
            request = VI.RebootGuestRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)

            self._server._proxy.RebootGuest(request)

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)


    def shutdown_guest(self):
        """Issues a command to the guest operating system asking it to perform
        a clean shutdown of all services. Returns immediately and does not wait
        for the guest operating system to complete the operation. """
        try:
            request = VI.ShutdownGuestRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)

            self._server._proxy.ShutdownGuest(request)

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def standby_guest(self):
        """Issues a command to the guest operating system asking it to prepare
        for a suspend operation. Returns immediately and does not wait for the
        guest operating system to complete the operation.  """
        try:
            request = VI.StandbyGuestRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)

            self._server._proxy.StandbyGuest(request)

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def revert_to_snapshot(self, sync_run=True, host=None):
        """Attemps to revert the VM to the current snapshot. If @sync_run is
        True (default) waits for the task to finish, and returns (raises an
        exception if the task didn't succeed). If sync_run is set to False the
        task is started an a VITask instance is returned. You may additionally
        provided a managed object reference to a host where the VM should be
        reverted at."""
        try:
            request = VI.RevertToCurrentSnapshot_TaskRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)
            if host:
                mor_host = request.new_host(host)
                mor_host.set_attribute_type(host.get_attribute_type())
                request.set_element_host(mor_host)

            task = self._server._proxy.RevertToCurrentSnapshot_Task(request) \
                                                                    ._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def revert_to_named_snapshot(self, name, sync_run=True, host=None):
        """Attemps to revert the VM to the snapshot of the given name (the first
        match found). If @sync_run is True (default) waits for the task to
        finish, and returns (raises an exception if the task didn't succeed).
        If sync_run is set to False the task is started an a VITask instance is
        returned. You may additionally provided a managed object reference to a
        host where the VM should be reverted at."""

        mor = None
        for snap in self._snapshot_list:
            if snap._name == name:
                mor = snap._mor
                break
        if not mor:
            raise VIException("Could not find snapshot '%s'" % name,
                              FaultTypes.SNAPSHOT_NOT_FOUND)

        try:
            request = VI.RevertToSnapshot_TaskRequestMsg()

            mor_snap = request.new__this(mor)
            mor_snap.set_attribute_type(mor.get_attribute_type())
            request.set_element__this(mor_snap)
            if host:
                mor_host = request.new_host(host)
                mor_host.set_attribute_type(host.get_attribute_type())
                request.set_element_host(mor_host)

            task = self._server._proxy.RevertToSnapshot_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def revert_to_path(self, path, index=0, sync_run=True, host=None):
        """Attemps to revert the VM to the snapshot of the given path and index
        (to disambiguate among snapshots with the same path, default 0)
        If @sync_run is True (default) waits for the task to finish, and returns
        (raises an exception if the task didn't succeed).
        If sync_run is set to False the task is started an a VITask instance is
        returned. You may additionally provided a managed object reference to a
        host where the VM should be reverted at."""

        mor = None
        for snap in self._snapshot_list:
            if snap.get_path() == path and snap._index == index:
                mor = snap._mor
                break
        if not mor:
            raise VIException(
                           "Could not find snapshot with path '%s' (index %d)" %
                                   (path, index), FaultTypes.SNAPSHOT_NOT_FOUND)

        try:
            request = VI.RevertToSnapshot_TaskRequestMsg()

            mor_snap = request.new__this(mor)
            mor_snap.set_attribute_type(mor.get_attribute_type())
            request.set_element__this(mor_snap)
            if host:
                mor_host = request.new_host(host)
                mor_host.set_attribute_type(host.get_attribute_type())
                request.set_element_host(mor_host)

            task = self._server._proxy.RevertToSnapshot_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def create_snapshot(self, name, description=None, sync_run=True):
        """Takes a snapshot of this VM
        If @sync_run is True (default) waits for the task to finish, and returns
        (raises an exception if the task didn't succeed).
        If sync_run is set to False the task is started an a VITask instance is
        returned."""
        try:
            request = VI.CreateSnapshot_TaskRequestMsg()
            mor_vm = request.new__this  (self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)
            request.set_element_name(name)
            if description:
                request.set_element_description(description)
            request.set_element_memory(True)
            request.set_element_quiesce(True)

            task = self._server._proxy.CreateSnapshot_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                self.refresh_snapshot_list()
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def delete_current_snapshot(self, remove_children=False, sync_run=True):
        """Removes the current snapshot. If @remove_children is True, removes
        all the snapshots in the subtree as well. If @sync_run is True (default)
        waits for the task to finish, and returns (raises an exception if the
        task didn't succeed). If sync_run is set to False the task is started a
        VITask instance is returned."""
        self.refresh_snapshot_list()
        if not self.__current_snapshot:
            raise VIException("There is no current snapshot",
                              FaultTypes.SNAPSHOT_NOT_FOUND)

        return self.__delete_snapshot(self.__current_snapshot, remove_children,
                                                                       sync_run)

    def delete_named_snapshot(self, name, remove_children=False, sync_run=True):
        """Removes the first snapshot found in this VM named after @name
        If @remove_children is True, removes all the snapshots in the subtree as
        well. If @sync_run is True (default) waits for the task to finish, and
        returns (raises an exception if the task didn't succeed). If sync_run is
        set to False the task is started an a VITask instance is returned."""

        mor = None
        for snap in self._snapshot_list:
            if snap._name == name:
                mor = snap._mor
                break
        if mor is None:
            raise VIException("Could not find snapshot '%s'" % name,
                              FaultTypes.SNAPSHOT_NOT_FOUND)

        return self.__delete_snapshot(mor, remove_children, sync_run)


    def delete_snapshot_by_path(self, path, index=0, remove_children=False,
                                                                 sync_run=True):
        """Removes the VM snapshot of the given path and index (to disambiguate
        among snapshots with the same path, default 0). If @remove_children is
        True, removes all the snapshots in the subtree as well. If @sync_run is
        True (default) waits for the task to finish,and returns (raises an
        exception if the task didn't succeed). If sync_run is set to False the
        task is started an a VITask instance is returned.
        """

        mor = None
        for snap in self._snapshot_list:
            if snap.get_path() == path and snap._index == index:
                mor = snap._mor
                break
        if not mor:
            raise VIException(
                           "Could not find snapshot with path '%s' (index %d)" %
                                   (path, index), FaultTypes.SNAPSHOT_NOT_FOUND)

        self.__delete_snapshot(mor, remove_children, sync_run)


    def refresh_snapshot_list(self):
        """Refreshes the internal list of snapshots of this VM"""
        self.__update_properties()

    def get_property(self, name='', from_cache=True):
        """"Returns the VM property with the given @name or None if the property
        doesn't exist or have not been set. The property is looked in the cached
        info obtained from the last time the server was requested.
        If you expect to get a volatile property (that might have changed since
        the last time the properties were queried), you may set @from_cache to
        True to refresh all the properties.
        The properties you may get are:
            name: Name of this entity, unique relative to its parent.
            path: Path name to the configuration file for the virtual machine
                  e.g., the .vmx file.
            guest_id:
            guest_full_name:
            hostname:
            ip_address:
            mac_address
            net: [{connected, mac_address, ip_addresses, network},...]
        """
        if not from_cache:
            self.__update_properties()
        return self._properties.get(name)

    def get_properties(self, from_cache=True):
        """Returns a dictionary of property of this VM.
        If you expect to get a volatile property (that might have changed since
        the last time the properties were queried), you may set @from_cache to
        True to refresh all the properties before retrieve them."""
        if not from_cache:
            self.__update_properties()
        return self._properties.copy()

    def get_snapshots(self):
        """Returns a list of VISnapshot instances of this VM"""
        return self._snapshot_list[:]

    def upgrade_tools(self, sync_run=True, params=None):
        """Attemps to upgrade the VMWare tools in the guest.
        If @sync_run is True (default) waits for the task to finish, and returns
        (raises an exception if the task didn't succeed)
        If sync_run is set to False the task is started an a VITask instance is
        returned.
        You may additionally provided a string (@params) with parameters to the
        tool upgrade executable."""
        try:
            request = VI.UpgradeTools_TaskRequestMsg()
            mor_vm = request.new__this(self._mor)
            mor_vm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_vm)
            if params:
                request.set_element_installerOptions(str(params))

            task = self._server._proxy.UpgradeTools_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)


    def get_status(self, basic_status=False):
        """Returns any of the status strings defined in VMPowerState:
        'POWERED ON', 'POWERED OFF', 'SUSPENDED', 'POWERING ON', 'POWERING OFF',
        'SUSPENDING', 'RESETTING', 'BLOCKED ON MSG', 'REVERTING TO SNAPSHOT',
        'UNKNOWN'
        """
        #we can't check tasks in a VMWare Server
        if self._server.get_server_type()!='VMware Server' and not basic_status:
            if not self._mor_vm_task_collector:
                self.__create_pendant_task_collector()

        #get the VM current power state, and messages blocking if any
        vi_power_states = {'poweredOn':VMPowerState.POWERED_ON,
                           'poweredOff': VMPowerState.POWERED_OFF,
                           'suspended': VMPowerState.SUSPENDED}

        vm_has_question = False
        power_state = None

        oc_vm_status_msg = self._server._get_object_properties(
                      self._mor,
                      property_names=['runtime.question', 'runtime.powerState']
                      )
        oc_vm_status_msg = oc_vm_status_msg[0]
        properties = oc_vm_status_msg.PropSet
        for prop in properties:
            if prop.Name == 'runtime.powerState':
                power_state = prop.Val
            if prop.Name == 'runtime.question':
                return VMPowerState.BLOCKED_ON_MSG

        #we can't check tasks in a VMWare Server
        if self._server.get_server_type() == 'VMware Server' or basic_status:
            return vi_power_states.get(power_state, VMPowerState.UNKNOWN)

        #on the other hand, get the current task running or queued for this VM
        oc_task_history = self._server._get_object_properties(
                      self._mor_vm_task_collector,
                      property_names=['latestPage']
                      )
        oc_task_history = oc_task_history[0]
        properties = oc_task_history.PropSet
        if len(properties) == 0:
            return vi_power_states.get(power_state, VMPowerState.UNKNOWN)
        for prop in properties:
            if prop.Name == 'latestPage':
                tasks_info_array = prop.Val.TaskInfo
                if len(tasks_info_array) == 0:
                    return vi_power_states.get(power_state,VMPowerState.UNKNOWN)
                for task_info in tasks_info_array:
                    desc = task_info.DescriptionId
                    if task_info.State in ['success', 'error']:
                        continue

                    if desc == 'VirtualMachine.powerOff' and power_state in [
                                                      'poweredOn', 'suspended']:
                        return VMPowerState.POWERING_OFF
                    if desc in ['VirtualMachine.revertToCurrentSnapshot',
                                'vm.Snapshot.revert']:
                        return VMPowerState.REVERTING_TO_SNAPSHOT
                    if desc == 'VirtualMachine.reset' and power_state in [
                                                      'poweredOn', 'suspended']:
                        return VMPowerState.RESETTING
                    if desc == 'VirtualMachine.suspend' and power_state in [
                                                                   'poweredOn']:
                        return VMPowerState.SUSPENDING
                    if desc in ['Drm.ExecuteVmPowerOnLRO',
                                'VirtualMachine.powerOn'] and power_state in [
                                                     'poweredOff', 'suspended']:
                        return VMPowerState.POWERING_ON
                return vi_power_states.get(power_state, VMPowerState.UNKNOWN)

    def get_tools_status(self):
        """Returns any of the status described in class ToolsStatus.
        'NOT INSTALLED': VMware Tools has never been installed or has not run
                         in the virtual machine.
        'NOT RUNNING': VMware Tools is not running.
        'RUNNING': VMware Tools is running and the version is current.
        'RUNNING OLD': VMware Tools is running, but the version is not current.
        'UNKNOWN': Couldn't obtain the status of the VMwareTools.
        """

        statuses = {'toolsNotInstalled':ToolsStatus.NOT_INSTALLED,
                    'toolsNotRunning':ToolsStatus.NOT_RUNNING,
                    'toolsOk':ToolsStatus.RUNNING,
                    'toolsOld':ToolsStatus.RUNNING_OLD}

        do_object_content = self._server._get_object_properties(self._mor,
                                           property_names=['guest.toolsStatus'])
        oc = do_object_content[0]
        if not hasattr(oc, 'PropSet'):
            return ToolsStatus.UNKNOWN
        prop_set = oc.PropSet
        if len(prop_set) == 0:
            return ToolsStatus.UNKNOWN
        for prop in prop_set:
            if prop.Name == 'guest.toolsStatus':
                return statuses.get(prop.Val, ToolsStatus.UNKNOWN)


    def wait_for_tools(self, timeout=15):
        """Waits for the VMWare tools to be running in the guest. Or for the
        timeout in seconds to expire. If timed out a VIException is thrown"""
        timeout = abs(int(timeout))
        start_time = time.clock()
        while True:
            cur_state = self.get_tools_status()
            if cur_state in [ToolsStatus.RUNNING, ToolsStatus.RUNNING_OLD]:
                return True

            if (time.clock() - start_time) > timeout:
                raise VIException(
                              "Timed out waiting for VMware Tools to be ready.",
                              FaultTypes.TIME_OUT)
            time.sleep(1.5)

    def is_powering_off(self):
        """Returns True if the VM is being powered off"""
        return self.get_status() == VMPowerState.POWERING_OFF

    def is_powered_off(self):
        """Returns True if the VM is powered off"""
        return self.get_status() == VMPowerState.POWERED_OFF

    def is_powering_on(self):
        """Returns True if the VM is being powered on"""
        return self.get_status() == VMPowerState.POWERING_ON

    def is_powered_on(self):
        """Returns True if the VM is powered off"""
        return self.get_status() == VMPowerState.POWERED_ON

    def is_suspending(self):
        """Returns True if the VM is being suspended"""
        return self.get_status() == VMPowerState.SUSPENDING

    def is_suspended(self):
        """Returns True if the VM is suspended"""
        return self.get_status() == VMPowerState.SUSPENDED

    def is_resetting(self):
        """Returns True if the VM is being resetted"""
        return self.get_status() == VMPowerState.RESETTING

    def is_blocked_on_msg(self):
        """Returns True if the VM is blocked because of a question message"""
        return self.get_status() == VMPowerState.BLOCKED_ON_MSG

    def is_reverting(self):
        """Returns True if the VM is being reverted to a snapshot"""
        return self.get_status() == VMPowerState.REVERTING_TO_SNAPSHOT

    def get_resource_pool_name(self):
        """Returns the name of the resource pool where this VM belongs to. Or
        None if there isn't any or it can't be retrieved"""
        if self._resource_pool:
            do_object_content = self._server._get_object_properties(
                                   self._resource_pool, property_names=['name'])
            oc = do_object_content[0]
            if not hasattr(oc, 'PropSet'):
                return None
            prop_set = oc.PropSet
            if len(prop_set) == 0:
                return None
            for prop in prop_set:
                if prop.Name == 'name':
                    return prop.Val

    def get_current_snapshot_name(self):
        """Returns the name of the current snapshot (if any)."""
        self.__update_properties()
        if not self.__current_snapshot:
            return None
        for snap in self._snapshot_list:
            if str(self.__current_snapshot) == str(snap._mor):
                return snap._name
        return None

    def __create_snapshot_list(self):
        """Creates a VISnapshot list with the snapshots this VM has. Stores that
        list in self._snapshot_list"""

        def create_list(snap_list=[], cur_node=None):
            #first create the trees of snapshots
            if not cur_node:
                children = self._root_snapshots
            else:
                children = cur_node.get_children()

            for snap in children:
                    snap_list.append(snap)
                    create_list(snap_list, snap)

            return snap_list

        self._snapshot_list = create_list()

        path_list = []
        for snap in self._snapshot_list:
            path_list.append(snap.get_path())

        path_list = list(set(filter(lambda x: path_list.count(x) > 1,
                                                                    path_list)))

        for snap_path in path_list:
            v = 0
            for snap in self._snapshot_list:
                if(snap.get_path() == snap_path):
                    snap._index = v
                    v += 1

    def __create_pendant_task_collector(self):
        """sets the MOR of a TaskHistoryCollector which will retrieve
        the lasts task info related to this VM (or any suboject as snapshots)
        for those task in 'running' or 'queued' states"""
        try:
            mor_task_manager = self._server._do_service_content.TaskManager

            request = VI.CreateCollectorForTasksRequestMsg()
            mor_tm = request.new__this(mor_task_manager)
            mor_tm.set_attribute_type(mor_task_manager.get_attribute_type())
            request.set_element__this(mor_tm)

            do_task_filter_spec = request.new_filter()
            do_task_filter_spec.set_element_state(['running', 'queued'])

            do_tfs_by_entity = do_task_filter_spec.new_entity()
            mor_entity = do_tfs_by_entity.new_entity(self._mor)
            mor_entity.set_attribute_type(self._mor.get_attribute_type())
            do_tfs_by_entity.set_element_entity(mor_entity)
            do_tfs_by_entity.set_element_recursion('all')

            do_task_filter_spec.set_element_entity(do_tfs_by_entity)

            request.set_element_filter(do_task_filter_spec)
            ret = self._server._proxy.CreateCollectorForTasks(request) \
                                                                     ._returnval
            self._mor_vm_task_collector = ret

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def __delete_snapshot(self, mor, remove_children, sync_run):
        """Deletes the snapshot of the given MOR. If remove_children is True,
        deletes all the snapshots in the subtree as well. If @sync_run is True
        (default) waits for the task to finish, and returns
        (raises an exception if the task didn't succeed). If sync_run is set to
        False the task is started an a VITask instance is returned."""
        try:
            request = VI.RemoveSnapshot_TaskRequestMsg()
            mor_snap = request.new__this(mor)
            mor_snap.set_attribute_type(mor.get_attribute_type())
            request.set_element__this(mor_snap)
            request.set_element_removeChildren(remove_children)

            task = self._server._proxy.RemoveSnapshot_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                self.refresh_snapshot_list()
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                                          FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def __update_properties(self):
        """Refreshes the properties retrieved from the virtual machine
        (i.e. name, path, snapshot tree, etc). To reduce traffic, all the
        properties are retrieved from one shot, if you expect changes, then you
        should call this method before other"""
        
        def update_devices(devices):
            for dev in devices:
                d = {
                     'key': dev.key,
                     'type': dev._type,
                     'unitNumber': getattr(dev,'unitNumber',None),
                     'label': getattr(getattr(dev,'deviceInfo',None),
                                      'label',None),
                     'summary': getattr(getattr(dev,'deviceInfo',None),
                                        'summary',None),
                     '_obj': dev
                     }
                # Network Device
                if hasattr(dev,'macAddress'):
                    d['macAddress'] = dev.macAddress
                    d['addressType'] = getattr(dev,'addressType',None)
                # Video Card
                if hasattr(dev,'videoRamSizeInKB'):
                    d['videoRamSizeInKB'] = dev.videoRamSizeInKB
                # Disk
                if hasattr(dev,'capacityInKB'):
                    d['capacityInKB'] = dev.capacityInKB
                # Controller
                if hasattr(dev,'busNumber'):
                    d['busNumber'] = dev.busNumber
                    d['devices'] = getattr(dev,'device',[])
                    
                self._devices[dev.key] = d
        
        def update_disks(disks):
            for disk in disks:
                files = []
                committed = 0
                store = None
                for c in getattr(disk, "chain", []):
                    for k in c.fileKey:
                        f = self._files[k]
                        files.append(f)
                        if f['type'] == 'diskExtent':
                            committed += f['size']
                        if f['type'] == 'diskDescriptor':
                            store = f['name']
                dev = self._devices[disk.key]
                
                self._disks.append({
                                   'device': dev,
                                   'files': files,
                                   'capacity': dev['capacityInKB'],
                                   'committed': committed/1024,
                                   'descriptor': store,
                                   'label': dev['label'],
                                   })
        
        def update_files(files):
            for file in files:
                self._files[file.key] = {
                                        'key': file.key,
                                        'name': file.name,
                                        'size': file.size,
                                        'type': file.type
                                        }
                
        
        try:
            self.properties = VIProperty(self._server, self._mor)
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)      
        
        p = {}
        p['name'] = self.properties.name
        
        #------------------------#
        #-- UPDATE CONFIG INFO --#
        if hasattr(self.properties, "config"):
            p['guest_id'] = self.properties.config.guestId
            p['guest_full_name'] = self.properties.config.guestFullName
            if hasattr(self.properties.config.files, "vmPathName"):
                p['path'] = self.properties.config.files.vmPathName
            p['memory_mb'] = self.properties.config.hardware.memoryMB
            p['num_cpu'] = self.properties.config.hardware.numCPU
        
            if hasattr(self.properties.config.hardware, "device"):
                update_devices(self.properties.config.hardware.device)
                p['devices'] = self._devices
        
        #-----------------------#
        #-- UPDATE GUEST INFO --#
        
        if hasattr(self.properties, "guest"):
            if hasattr(self.properties.guest, "hostName"):
                p['hostname'] = self.properties.guest.hostName
            if hasattr(self.properties.guest, "ipAddress"):
                p['ip_address'] = self.properties.guest.ipAddress
            nics = []
            if hasattr(self.properties.guest, "net"):
                for nic in self.properties.guest.net:
                    nics.append({
                                 'connected':getattr(nic, "connected", None),
                                 'mac_address':getattr(nic, "macAddress", None),
                                 'ip_addresses':getattr(nic, "ipAddress", []),
                                 'network':getattr(nic, "network", None)
                                })
           
                p['net'] = nics
        
        #------------------------#
        #-- UPDATE LAYOUT INFO --#
        
        if hasattr(self.properties, "layoutEx"):
            if hasattr(self.properties.layoutEx, "file"):
                update_files(self.properties.layoutEx.file)
                p['files'] = self._files
            if hasattr(self.properties.layoutEx, "disk"):
                update_disks(self.properties.layoutEx.disk)
                p['disks'] = self._disks
            
        self._properties = p
        
        #----------------------#
        #-- UPDATE SNAPSHOTS --#
        
        if hasattr(self.properties, "snapshot"):
            if hasattr(self.properties.snapshot, "currentSnapshot"):
                self.__current_snapshot = \
                                   self.properties.snapshot.currentSnapshot._obj
            
            for root_snap in self.properties.snapshot.rootSnapshotList:
                root = VISnapshot(root_snap)
                self._root_snapshots.append(root)
            self.__create_snapshot_list()

        #-----------------------#
        #-- SET RESOURCE POOL --#
        if hasattr(self.properties, "resourcePool"):
            self._resource_pool = self.properties.resourcePool._obj
            

class VMPowerState:
    POWERED_ON              = 'POWERED ON'
    POWERED_OFF             = 'POWERED OFF'
    SUSPENDED               = 'SUSPENDED'
    POWERING_ON             = 'POWERING ON'
    POWERING_OFF            = 'POWERING OFF'
    SUSPENDING              = 'SUSPENDING'
    RESETTING               = 'RESETTING'
    BLOCKED_ON_MSG          = 'BLOCKED ON MSG'
    REVERTING_TO_SNAPSHOT   = 'REVERTING TO SNAPSHOT'
    UNKNOWN                 = 'UNKNOWN'

class ToolsStatus:
    #VMware Tools has never been installed or has not run in the virtual machine
    NOT_INSTALLED   = 'NOT INSTALLED'

    #VMware Tools is not running.
    NOT_RUNNING     = 'NOT RUNNING'

    #VMware Tools is running and the version is current.
    RUNNING         = 'RUNNING'

    #VMware Tools is running, but the version is not current.
    RUNNING_OLD     = 'RUNNING OLD'

    #Couldn't obtain the status of the VMwareTools.
    UNKNOWN         = 'UNKNOWN'