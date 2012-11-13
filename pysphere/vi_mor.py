#--
# Copyright (c) 2012, Sebastian Tello
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

from pysphere.resources.VimService_services_types import ns0

class VIMor(str):
    """str subclass representing a Managed Object Reference"""
    
    def __new__(self, value, mor_type):
        return str.__new__(self, value)
    
    def __init__(self, value, mor_type):
        self._mor_type = mor_type
        self.typecode = ns0.ManagedObjectReference_Def(value)
        
    def get_attribute_type(self):
        return self._mor_type
    
    def set_attribute_type(self, mor_type):
        self._mor_type = mor_type
    
    @staticmethod
    def is_mor(obj):
        return hasattr(obj, "get_attribute_type")
    
    
class MORTypes(object):
    Alarm = "Alarm"
    AlarmManager = "AlarmManager"
    AuthorizationManager = "AuthorizationManager"
    ClusterComputeResource = "ClusterComputeResource"
    ClusterProfile = "ClusterProfile"
    ClusterProfileManager = "ClusterProfileManager"
    ComputeResource = "ComputeResource"
    ContainerView = "ContainerView"
    CustomFieldsManager = "CustomFieldsManager"
    CustomizationSpecManager = "CustomizationSpecManager"
    Datacenter = "Datacenter"
    Datastore = "Datastore"
    DiagnosticManager = "DiagnosticManager"
    DistributedVirtualPortgroup = "DistributedVirtualPortgroup"
    DistributedVirtualSwitch = "DistributedVirtualSwitch"
    DistributedVirtualSwitchManager = "DistributedVirtualSwitchManager"
    EnvironmentBrowser = "EnvironmentBrowser"
    EventHistoryCollector = "EventHistoryCollector"
    EventManager = "EventManager"
    ExtensibleManagedObject = "ExtensibleManagedObject"
    ExtensionManager = "ExtensionManager"
    FileManager = "FileManager"
    Folder = "Folder"
    GuestAuthManager = "GuestAuthManager"
    GuestFileManager = "GuestFileManager"
    GuestOperationsManager = "GuestOperationsManager"
    GuestProcessManager = "GuestProcessManager"
    HistoryCollector = "HistoryCollector"
    HostActiveDirectoryAuthentication = "HostActiveDirectoryAuthentication"
    HostAuthenticationManager = "HostAuthenticationManager"
    HostAuthenticationStore = "HostAuthenticationStore"
    HostAutoStartManager = "HostAutoStartManager"
    HostBootDeviceSystem = "HostBootDeviceSystem"
    HostCacheConfigurationManager = "HostCacheConfigurationManager"
    HostCpuSchedulerSystem = "HostCpuSchedulerSystem"
    HostDatastoreBrowser = "HostDatastoreBrowser"
    HostDatastoreSystem = "HostDatastoreSystem"
    HostDateTimeSystem = "HostDateTimeSystem"
    HostDiagnosticSystem = "HostDiagnosticSystem"
    HostDirectoryStore = "HostDirectoryStore"
    HostEsxAgentHostManager = "HostEsxAgentHostManager"
    HostFirewallSystem = "HostFirewallSystem"
    HostFirmwareSystem = "HostFirmwareSystem"
    HostHealthStatusSystem = "HostHealthStatusSystem"
    HostImageConfigManager = "HostImageConfigManager"
    HostKernelModuleSystem = "HostKernelModuleSystem"
    HostLocalAccountManager = "HostLocalAccountManager"
    HostLocalAuthentication = "HostLocalAuthentication"
    HostMemorySystem = "HostMemorySystem"
    HostNetworkSystem = "HostNetworkSystem"
    HostPatchManager = "HostPatchManager"
    HostPciPassthruSystem = "HostPciPassthruSystem"
    HostPowerSystem = "HostPowerSystem"
    HostProfile = "HostProfile"
    HostProfileManager = "HostProfileManager"
    HostServiceSystem = "HostServiceSystem"
    HostSnmpSystem = "HostSnmpSystem"
    HostStorageSystem = "HostStorageSystem"
    HostSystem = "HostSystem"
    HostVirtualNicManager = "HostVirtualNicManager"
    HostVMotionSystem = "HostVMotionSystem"
    HttpNfcLease = "HttpNfcLease"
    InventoryView = "InventoryView"
    IpPoolManager = "IpPoolManager"
    IscsiManager = "IscsiManager"
    LicenseAssignmentManager = "LicenseAssignmentManager"
    LicenseManager = "LicenseManager"
    ListView = "ListView"
    LocalizationManager = "LocalizationManager"
    ManagedEntity = "ManagedEntity"
    ManagedObjectView = "ManagedObjectView"
    Network = "Network"
    OptionManager = "OptionManager"
    OvfManager = "OvfManager"
    PerformanceManager = "PerformanceManager"
    Profile = "Profile"
    ProfileComplianceManager = "ProfileComplianceManager"
    ProfileManager = "ProfileManager"
    PropertyCollector = "PropertyCollector"
    PropertyFilter = "PropertyFilter"
    ResourcePlanningManager = "ResourcePlanningManager"
    ResourcePool = "ResourcePool"
    ScheduledTask = "ScheduledTask"
    ScheduledTaskManager = "ScheduledTaskManager"
    SearchIndex = "SearchIndex"
    ServiceInstance = "ServiceInstance"
    SessionManager = "SessionManager"
    StoragePod = "StoragePod"
    StorageResourceManager = "StorageResourceManager"
    Task = "Task"
    TaskHistoryCollector = "TaskHistoryCollector"
    TaskManager = "TaskManager"
    UserDirectory = "UserDirectory"
    View = "View"
    ViewManager = "ViewManager"
    VirtualApp = "VirtualApp"
    VirtualDiskManager = "VirtualDiskManager"
    VirtualizationManager = "VirtualizationManager"
    VirtualMachine = "VirtualMachine"
    VirtualMachineCompatibilityChecker = "VirtualMachineCompatibilityChecker"
    VirtualMachineProvisioningChecker = "VirtualMachineProvisioningChecker"
    VirtualMachineSnapshot = "VirtualMachineSnapshot"
    VmwareDistributedVirtualSwitch = "VmwareDistributedVirtualSwitch"
