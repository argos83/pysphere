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

from resources import VimService_services as VI

from resources.vi_exception import *
from vi_virtual_machine import VIVirtualMachine
from vi_performance_manager import PerformanceManager
from vi_mor import VIMor, MORTypes

class VIServer:

    def __init__(self):
        self.__logged = False
        self.__server_type = None
        self.__api_version = None
        self.__session = None
        self.__user = None
        self.__password = None
        #By default impersonate the VI Client to be accepted by Virtual Server
        self.__initial_headers = {"User-Agent":"VMware VI Client/5.0.0"}

    def connect(self, host, user, password, trace_file=None):
        """Opens a session to a VC/ESX server with the given credentials. You
        might provide a file name to write the soap conversation for debuging"""

        self.__user = user
        self.__password = password
        #Generate server's URL
        if not isinstance(host, basestring):
            raise VIException("'host' should be a string with the ESX/VC url."
                             ,FaultTypes.PARAMETER_ERROR)

        elif (host.lower().startswith('http://')
        or host.lower().startswith('https://')):
            server_url = host.lower()

        else:
            server_url = 'https://%s/sdk' % host

        try:
            #get the server's proxy
            locator = VI.VimServiceLocator()
            if not trace_file:
                self._proxy = locator.getVimPortType(url=server_url)
            else:
                trace=open(trace_file, 'w')
                self._proxy = locator.getVimPortType(url=server_url,
                                                     tracefile=trace)
            for header, value in self.__initial_headers.items():
                self._proxy.binding.AddHeader(header, value)
                
            #get service content from service instance
            request = VI.RetrieveServiceContentRequestMsg()
            mor_service_instance = request.new__this('ServiceInstance')
            mor_service_instance.set_attribute_type(MORTypes.ServiceInstance)
            request.set_element__this(mor_service_instance)
            self._do_service_content = self._proxy.RetrieveServiceContent(
                                                             request)._returnval
            self.__server_type = self._do_service_content.About.Name
            self.__api_version = self._do_service_content.About.ApiVersion

            #login
            request = VI.LoginRequestMsg()
            mor_session_manager = request.new__this(
                                        self._do_service_content.SessionManager)
            mor_session_manager.set_attribute_type(MORTypes.SessionManager)
            request.set_element__this(mor_session_manager)
            request.set_element_userName(user)
            request.set_element_password(password)
            self.__session = self._proxy.Login(request)._returnval
            self.__logged = True

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def keep_session_alive(self):
        """Asks sever time, usefull for keeping alive a session. Returns
        False if the session expired"""
        if not self.__logged:
            raise VIException("Must call 'connect' before invoking this method",
                            FaultTypes.NOT_CONNECTED)
        request = VI.CurrentTimeRequestMsg()
        mor_service_instance = request.new__this("ServiceInstance")
        mor_service_instance.set_attribute_type(MORTypes.ServiceInstance)
        request.set_element__this(mor_service_instance)
        try:
            self._proxy.CurrentTime(request)
            return True
        except(VI.ZSI.FaultException):
            return False

    def is_connected(self):
        """True if the user has successfuly logged in. False otherwise"""
        return self.__logged

    def disconnect(self):
        """Closes the open session with the VC/ESX Server."""
        if self.__logged:
            try:
                self.__logged = False
                request = VI.LogoutRequestMsg()
                mor_session_manager = request.new__this(
                                        self._do_service_content.SessionManager)
                mor_session_manager.set_attribute_type(MORTypes.SessionManager)
                request.set_element__this(mor_session_manager)
                self._proxy.Logout(request)
            except (VI.ZSI.FaultException), e:
                raise VIApiException(e)

    def get_performance_manager(self):
        """Returns a Performance Manager entity"""
        return PerformanceManager(self, self._do_service_content.PerfManager)

    def get_hosts(self, from_mor=None):
        """
        Returns a dictionary of the existing hosts keys are their names
        and values their ManagedObjectReference object.
        @from_mor: if given, retrieves the hosts contained within the specified 
            managed entity.
        """
        return self._get_managed_objects(MORTypes.HostSystem, from_mor)
    

    def get_datastores(self, from_mor=None):
        """
        Returns a dictionary of the existing datastores. Keys are
        ManagedObjectReference and values datastore names.
        @from_mor: if given, retrieves the datastores contained within the 
            specified managed entity.
        """
        return self._get_managed_objects(MORTypes.Datastore, from_mor)
        
    def get_clusters(self, from_mor=None):
        """
        Returns a dictionary of the existing clusters. Keys are their 
        ManagedObjectReference objects and values their names.
        @from_mor: if given, retrieves the clusters contained within the 
            specified managed entity.
        """
        return self._get_managed_objects(MORTypes.ClusterComputeResource,
                                               from_mor)

    def get_datacenters(self, from_mor=None):
        """
        Returns a dictionary of the existing datacenters. keys are their
        ManagedObjectReference objects and values their names.
        @from_mor: if given, retrieves the datacenters contained within the 
            specified managed entity.
        """
        return self._get_managed_objects(MORTypes.Datacenter, from_mor)           

    def get_resource_pools(self, from_mor=None):
        """
        Returns a dictionary of the existing ResourcePools. keys are their
        ManagedObjectReference objects and values their full path names.
        @from_mor: if given, retrieves the resource pools contained within the
            specified managed entity.
        """

        def get_path(nodes, node):
            if 'parent' in node:
                return get_path(nodes, rps[node['parent']]) + '/' + node['name']
            else:
                return '/' + node['name']
        rps = {}
        prop = self._retrieve_properties_traversal(
                                      property_names=["name", "resourcePool"],
                                      from_node=from_mor,
                                      obj_type=MORTypes.ResourcePool)
        for oc in prop:
            this_rp = {}
            this_rp["children"] = []
            this_rp["mor"] = oc.get_element_obj()
            mor_str = str(this_rp["mor"])
            properties = oc.PropSet
            if not properties:
                continue
            for prop in properties:
                if prop.Name == "name":
                    this_rp["name"] = prop.Val
                elif prop.Name == "resourcePool":
                    for rp in prop.Val.ManagedObjectReference:
                        this_rp["children"].append(str(rp))
            rps[mor_str] = this_rp
        for _id, rp in rps.items():
            for child in rp["children"]:
                rps[child]["parent"] = _id
        ret = {}
        for rp in rps.values():
            ret[rp["mor"]] = get_path(rps, rp) 
        
        return ret

    def get_vm_by_path(self, path, datacenter=None):
        """Returns an instance of VIVirtualMachine. Where its path matches
        @path. The VM is searched througout all the datacenters, unless the
        name or MOR of the datacenter the VM belongs to is provided."""
        if not self.__logged:
            raise VIException("Must call 'connect' before invoking this method",
                            FaultTypes.NOT_CONNECTED)
        try:
            dc_list = []
            if datacenter and VIMor.is_mor(datacenter):
                dc_list.append(datacenter)
            else:
                dc = self.get_datacenters()
                if datacenter:
                    dc_list = [k for k,v in dc.items() if v==datacenter]
                else:
                    dc_list = dc.keys()

            for mor_dc in dc_list:
                request = VI.FindByDatastorePathRequestMsg()
                mor_search_index = request.new__this(
                                           self._do_service_content.SearchIndex)
                mor_search_index.set_attribute_type(MORTypes.SearchIndex)
                request.set_element__this(mor_search_index)
                mor_datacenter = request.new_datacenter(mor_dc)
                mor_datacenter.set_attribute_type(MORTypes.Datacenter)
                request.set_element_datacenter(mor_datacenter)
                request.set_element_path(path)
                try:
                    vm = self._proxy.FindByDatastorePath(request)._returnval
                except VI.ZSI.FaultException:
                    pass
                else:
                    if vm:
                        return VIVirtualMachine(self, vm)
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

        raise VIException("Could not find a VM with path '%s'" % path, 
                          FaultTypes.OBJECT_NOT_FOUND)

    def get_vm_by_name(self, name, datacenter=None):
        """
        Returns an instance of VIVirtualMachine. Where its name matches @name.
        The VM is searched throughout all the datacenters, unless the name or 
        MOR of the datacenter the VM belongs to is provided. The first instance
        matching @name is returned.
        NOTE: As names might be duplicated is recommended to use get_vm_by_path
        instead.
        """
        if not self.__logged:
            raise VIException("Must call 'connect' before invoking this method",
                              FaultTypes.NOT_CONNECTED)
        try:
            nodes = [None]
            if datacenter and VIMor.is_mor(datacenter):
                nodes = [datacenter]
            elif datacenter:
                dc = self.get_datacenters()
                nodes = [k for k,v in dc.items() if v==datacenter]
                
            for node in nodes:
                vms = self._get_managed_objects(MORTypes.VirtualMachine,
                                                      from_mor=node)
                for k,v in vms.items():
                    if v == name:
                        return VIVirtualMachine(self, k)
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

        raise VIException("Could not find a VM named '%s'" % name, 
                          FaultTypes.OBJECT_NOT_FOUND)

    def get_server_type(self):
        """Returns a string containing a the server type name: E.g:
        'VirtualCenter', 'VMware Server' """
        return self.__server_type

    def get_api_version(self):
        """Returns a string containing a the vSphere API version: E.g: '4.1' """
        return self.__api_version

    def get_registered_vms(self, datacenter=None, cluster=None, 
                           resource_pool=None, status=None):
        """Returns a list of VM Paths. You might also filter by datacenter,
        cluster, or resource pool by providing their name or MORs. 
        if  cluster is set, datacenter is ignored, and if resource pool is set
        both, datacenter and cluster are ignored.
        You can also filter by VM power state, by setting status to one of this
        values: 'poweredOn', 'poweredOff', 'suspended'
        """

        if not self.__logged:
            raise VIException("Must call 'connect' before invoking this method",
                              FaultTypes.NOT_CONNECTED)
        try:
            property_filter= ['config.files.vmPathName']
            if status:
                property_filter.append('runtime.powerState')
            ret = []
            nodes = [None]
            if resource_pool and VIMor.is_mor(resource_pool):
                nodes = [resource_pool]
            elif resource_pool:
                nodes = [k for k,v in self.get_resource_pools().items()
                         if v==resource_pool]
            elif cluster and VIMor.is_mor(cluster):
                nodes = [cluster]
            elif cluster:
                nodes = [k for k,v in self.get_clusters().items() 
                        if v==cluster]
            elif datacenter and VIMor.is_mor(datacenter):
                nodes = [datacenter]
            elif datacenter:
                nodes = [k for k,v in self.get_datacenters().items()
                        if v==datacenter]

            for node in nodes:
                obj_content = self._retrieve_properties_traversal(
                                            property_names=property_filter,
                                            from_node=node,
                                            obj_type=MORTypes.VirtualMachine)
                if not obj_content:
                    continue
                for obj in obj_content:
                    try:
                        prop_set = obj.PropSet
                    except AttributeError:
                        continue
                    ppath = None
                    pstatus = None
                    for item in prop_set:
                        if item.Name == 'config.files.vmPathName':
                            ppath = item.Val
                        elif item.Name == 'runtime.powerState':
                            pstatus = item.Val
                    if (status and status==pstatus) or not status:
                        ret.append(ppath)
            return ret

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def _get_object_properties(self, mor, property_names=[], get_all=False):
        """Returns the properties defined in property_names (or all if get_all
        is set to True) of the managed object reference given in @mor.
        Returns the corresponding objectContent data object."""
        if not self.__logged:
            raise VIException("Must call 'connect' before invoking this method",
                              FaultTypes.NOT_CONNECTED)
        try:

            request, request_call = self._retrieve_property_request()

            _this = request.new__this(
                                     self._do_service_content.PropertyCollector)
            _this.set_attribute_type(MORTypes.PropertyCollector)
            request.set_element__this(_this)

            do_PropertyFilterSpec_specSet = request.new_specSet()

            props_set = []
            do_PropertySpec_propSet =do_PropertyFilterSpec_specSet.new_propSet()
            do_PropertySpec_propSet.set_element_type(mor.get_attribute_type())
            if not get_all:
                do_PropertySpec_propSet.set_element_pathSet(property_names)
            else:
                do_PropertySpec_propSet.set_element_all(True)
            props_set.append(do_PropertySpec_propSet)

            objects_set = []
            do_ObjectSpec_objSet = do_PropertyFilterSpec_specSet.new_objectSet()
            obj = do_ObjectSpec_objSet.new_obj(mor)
            obj.set_attribute_type(mor.get_attribute_type())
            do_ObjectSpec_objSet.set_element_obj(obj)
            do_ObjectSpec_objSet.set_element_skip(False)
            objects_set.append(do_ObjectSpec_objSet)

            do_PropertyFilterSpec_specSet.set_element_propSet(props_set)
            do_PropertyFilterSpec_specSet.set_element_objectSet(objects_set)
            request.set_element_specSet([do_PropertyFilterSpec_specSet])

            ret = request_call(request)
            if ret and isinstance(ret, list):
                return ret[0]

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def _get_object_properties_bulk(self, mor_list, properties):
        """Similar to _get_object_properties but you can retrieve different sets
        of properties for many managed object of different types. @mor_list is a
        list of the managed object references you want to retrieve properties
        from, @properties is a dictionary where keys are managed object types
        and values are a list of the properties you want to retrieve for that
        type of object (or an empty list if you want to retrieve all). E.g.
        _get_object_properties_bulk( [mor_obj_1, mor_obj_2,...,mor_obj_3],
                                  {'VirtualMachine':['guest.toolStatus', 'name],
                                   'ResourcePool':['summary'],
                                   'VirtualMachineSnapthot':[]}

        Returns the corresponding objectContent data object array."""
        if not self.__logged:
            raise VIException("Must call 'connect' before invoking this method",
                              FaultTypes.NOT_CONNECTED)
        try:

            request, request_call = self._retrieve_property_request()

            pc = request.new__this(self._do_service_content.PropertyCollector)
            pc.set_attribute_type(
                self._do_service_content.PropertyCollector.get_attribute_type())
            request.set_element__this(pc)

            spec_sets = []
            spec_set = request.new_specSet()

            prop_sets = []
            for mo_type, path_set in properties.items():
                prop_set = spec_set.new_propSet()
                prop_set.set_element_type(mo_type)
                if path_set:
                    prop_set.set_element_pathSet(path_set)
                    prop_set.set_element_all(False)
                else:
                    prop_set.set_element_all(True)
                prop_sets.append(prop_set)
            spec_set.set_element_propSet(prop_sets)

            object_sets = []
            for mo in mor_list:
                object_set = spec_set.new_objectSet()
                obj = object_set.new_obj(mo)
                obj.set_attribute_type(mo.get_attribute_type())
                object_set.set_element_obj(obj)
                object_set.set_element_skip(False)
                object_sets.append(object_set)
            spec_set.set_element_objectSet(object_sets)

            spec_sets.append(spec_set)

            request.set_element_specSet(spec_sets)

            return request_call(request)

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)                 


    def _retrieve_properties_traversal(self, property_names=[],
                                      from_node=None, obj_type='ManagedEntity'):
        """Uses VI API's property collector to retrieve the properties defined
        in @property_names of Managed Objects of type @obj_type ('ManagedEntity'
        by default). Starts the search from the managed object reference
        @from_node (RootFolder by default). Returns the corresponding
        objectContent data object."""
        try:
            if not from_node:
                from_node = self._do_service_content.RootFolder
            
            elif isinstance(from_node, tuple) and len(from_node) == 2:
                from_node = VIMor(from_node[0], from_node[1])
            elif not VIMor.is_mor(from_node):
                raise VIException("from_node must be a MOR object or a "
                                  "(<str> mor_id, <str> mor_type) tuple",
                                  FaultTypes.PARAMETER_ERROR)
            
            request, request_call = self._retrieve_property_request()


            _this = request.new__this(
                                     self._do_service_content.PropertyCollector)
            _this.set_attribute_type(MORTypes.PropertyCollector)

            request.set_element__this(_this)
            do_PropertyFilterSpec_specSet = request.new_specSet()

            props_set = []
            do_PropertySpec_propSet =do_PropertyFilterSpec_specSet.new_propSet()
            do_PropertySpec_propSet.set_element_type(obj_type)
            do_PropertySpec_propSet.set_element_pathSet(property_names)
            props_set.append(do_PropertySpec_propSet)

            objects_set = []
            do_ObjectSpec_objSet = do_PropertyFilterSpec_specSet.new_objectSet()
            mor_obj = do_ObjectSpec_objSet.new_obj(from_node)
            mor_obj.set_attribute_type(from_node.get_attribute_type())
            do_ObjectSpec_objSet.set_element_obj(mor_obj)
            do_ObjectSpec_objSet.set_element_skip(False)

            #Recurse through all ResourcePools
            rp_to_rp = VI.ns0.TraversalSpec_Def('rpToRp').pyclass()
            rp_to_rp.set_element_name('rpToRp')
            rp_to_rp.set_element_type(MORTypes.ResourcePool)
            rp_to_rp.set_element_path('resourcePool')
            rp_to_rp.set_element_skip(False)
            rp_to_vm= VI.ns0.TraversalSpec_Def('rpToVm').pyclass()
            rp_to_vm.set_element_name('rpToVm')
            rp_to_vm.set_element_type(MORTypes.ResourcePool)
            rp_to_vm.set_element_path('vm')
            rp_to_vm.set_element_skip(False)

            spec_array_resource_pool = [do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet()]
            spec_array_resource_pool[0].set_element_name('rpToRp')
            spec_array_resource_pool[1].set_element_name('rpToVm')

            rp_to_rp.set_element_selectSet(spec_array_resource_pool)

            #Traversal through resource pool branch
            cr_to_rp = VI.ns0.TraversalSpec_Def('crToRp').pyclass()
            cr_to_rp.set_element_name('crToRp')
            cr_to_rp.set_element_type(MORTypes.ComputeResource)
            cr_to_rp.set_element_path('resourcePool')
            cr_to_rp.set_element_skip(False)
            spec_array_computer_resource =[do_ObjectSpec_objSet.new_selectSet(),
                                           do_ObjectSpec_objSet.new_selectSet()]
            spec_array_computer_resource[0].set_element_name('rpToRp');
            spec_array_computer_resource[1].set_element_name('rpToVm');
            cr_to_rp.set_element_selectSet(spec_array_computer_resource)

            #Traversal through host branch
            cr_to_h = VI.ns0.TraversalSpec_Def('crToH').pyclass()
            cr_to_h.set_element_name('crToH')
            cr_to_h.set_element_type(MORTypes.ComputeResource)
            cr_to_h.set_element_path('host')
            cr_to_h.set_element_skip(False)

            #Traversal through hostFolder branch
            dc_to_hf = VI.ns0.TraversalSpec_Def('dcToHf').pyclass()
            dc_to_hf.set_element_name('dcToHf')
            dc_to_hf.set_element_type(MORTypes.Datacenter)
            dc_to_hf.set_element_path('hostFolder')
            dc_to_hf.set_element_skip(False)
            spec_array_datacenter_host = [do_ObjectSpec_objSet.new_selectSet()]
            spec_array_datacenter_host[0].set_element_name('visitFolders')
            dc_to_hf.set_element_selectSet(spec_array_datacenter_host)

            #Traversal through vmFolder branch
            dc_to_vmf = VI.ns0.TraversalSpec_Def('dcToVmf').pyclass()
            dc_to_vmf.set_element_name('dcToVmf')
            dc_to_vmf.set_element_type(MORTypes.Datacenter)
            dc_to_vmf.set_element_path('vmFolder')
            dc_to_vmf.set_element_skip(False)
            spec_array_datacenter_vm = [do_ObjectSpec_objSet.new_selectSet()]
            spec_array_datacenter_vm[0].set_element_name('visitFolders')
            dc_to_vmf.set_element_selectSet(spec_array_datacenter_vm)

            #Traversal through datastore branch
            dc_to_ds = VI.ns0.TraversalSpec_Def('dcToDs').pyclass()
            dc_to_ds.set_element_name('dcToDs')
            dc_to_ds.set_element_type(MORTypes.Datacenter)
            dc_to_ds.set_element_path('datastore')
            dc_to_ds.set_element_skip(False)
            spec_array_datacenter_ds = [do_ObjectSpec_objSet.new_selectSet()]
            spec_array_datacenter_ds[0].set_element_name('visitFolders')
            dc_to_ds.set_element_selectSet(spec_array_datacenter_ds)

            #Recurse through all hosts
            h_to_vm = VI.ns0.TraversalSpec_Def('hToVm').pyclass()
            h_to_vm.set_element_name('hToVm')
            h_to_vm.set_element_type(MORTypes.HostSystem)
            h_to_vm.set_element_path('vm')
            h_to_vm.set_element_skip(False)
            spec_array_host_vm = [do_ObjectSpec_objSet.new_selectSet()]
            spec_array_host_vm[0].set_element_name('visitFolders')
            h_to_vm.set_element_selectSet(spec_array_host_vm)

            #Recurse through the folders
            visit_folders = VI.ns0.TraversalSpec_Def('visitFolders').pyclass()
            visit_folders.set_element_name('visitFolders')
            visit_folders.set_element_type(MORTypes.Folder)
            visit_folders.set_element_path('childEntity')
            visit_folders.set_element_skip(False)
            spec_array_visit_folders = [do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet(),
                                        do_ObjectSpec_objSet.new_selectSet()]
            spec_array_visit_folders[0].set_element_name('visitFolders')
            spec_array_visit_folders[1].set_element_name('dcToHf')
            spec_array_visit_folders[2].set_element_name('dcToVmf')
            spec_array_visit_folders[3].set_element_name('crToH')
            spec_array_visit_folders[4].set_element_name('crToRp')
            spec_array_visit_folders[5].set_element_name('dcToDs')
            spec_array_visit_folders[6].set_element_name('hToVm')
            spec_array_visit_folders[7].set_element_name('rpToVm')
            visit_folders.set_element_selectSet(spec_array_visit_folders)

            #Add all of them here
            spec_array = [visit_folders, dc_to_vmf, dc_to_ds, dc_to_hf, cr_to_h,
                          cr_to_rp, rp_to_rp, h_to_vm, rp_to_vm]

            do_ObjectSpec_objSet.set_element_selectSet(spec_array)
            objects_set.append(do_ObjectSpec_objSet)

            do_PropertyFilterSpec_specSet.set_element_propSet(props_set)
            do_PropertyFilterSpec_specSet.set_element_objectSet(objects_set)
            request.set_element_specSet([do_PropertyFilterSpec_specSet])

            return request_call(request)

        except (VI.ZSI.FaultException), e:
                raise VIApiException(e)


    def _retrieve_property_request(self):
        """Returns a base request object an call request method pointer for
        either RetrieveProperties or RetrievePropertiesEx depending on
        RetrievePropertiesEx being supported or not"""

        def call_retrieve_properties(request):
            return self._proxy.RetrieveProperties(request)._returnval

        def call_retrieve_properties_ex(request):
            retval = self._proxy.RetrievePropertiesEx(
                                                 request)._returnval
            if not retval:
                return None
            ret = retval.Objects
            while hasattr(retval, "Token"):
                token = retval.Token
                request = VI.ContinueRetrievePropertiesExRequestMsg()

                _this = request.new__this(
                                     self._do_service_content.PropertyCollector)
                _this.set_attribute_type(MORTypes.PropertyCollector)
                request.set_element__this(_this)
                request.set_element_token(token)
                retval = self._proxy.ContinueRetrievePropertiesEx(
                                                  request)._returnval
                ret.extend(retval.Objects)
            return ret            

        if self.__api_version >= "4.1":
            #RetrieveProperties is deprecated (but supported) in sdk 4.1.
            #skd 4.1 adds RetrievePropertiesEx with an extra 'options' arg

            request = VI.RetrievePropertiesExRequestMsg()
            #set options
            options = request.new_options()
            request.set_element_options(options)
            call_pointer = call_retrieve_properties_ex

        else:
            request = VI.RetrievePropertiesRequestMsg()
            call_pointer = call_retrieve_properties

        return request, call_pointer

    def _set_header(self, name, value):
        """Sets a HTTP header to be sent with the SOAP requests.
        E.g. for impersonation of a particular client.
        Both name and value should be strings."""
        if not (isinstance(name, basestring) and isinstance(value, basestring)):
            return
        
        if not self.__logged:
            self.__initial_headers[name] = value
        else:
            self._proxy.binding.AddHeader(name, value)
        
    def _reset_headers(self):
        """Resets the additional HTTP headers configured to be sent along with
        the SOAP requests."""
        if not self.__logged:
            self.__initial_headers = {}
        else:
            self._proxy.binding.ResetHeaders()
            
    def _get_managed_objects(self, mo_type, from_mor=None):
        """Returns a dictionary of managed objects and their names"""
        
        content = self._retrieve_properties_traversal(property_names=['name'],
                                                      from_node=from_mor,
                                                      obj_type=mo_type)
        if not content: return {}
        try:
            return dict([(o.Obj, o.PropSet[0].Val) for o in content])
        except VI.ZSI.FaultException, e:
            raise VIApiException(e)
    
    #---- DEPRECATED METHODS ----#    
            
    def _get_clusters(self, from_cache=True):
        """DEPRECATED: use get_clusters instead."""
        import warnings
        from exceptions import DeprecationWarning
        warnings.warn("method '_get_clusters' is DEPRECATED use "\
                      "'get_clusters' instead",
                      DeprecationWarning)
        
        ret = self.get_clusters()
        return dict([(v,k) for k,v in ret.items()])
    
    def _get_datacenters(self, from_cache=True):
        """DEPRECATED: use get_datacenters instead."""
        import warnings
        from exceptions import DeprecationWarning
        warnings.warn("method '_get_datacenters' is DEPRECATED use "\
                      "'get_datacenters' instead",
                      DeprecationWarning)

        ret = self.get_datacenters()
        return dict([(v,k) for k,v in ret.items()])
    
    def _get_resource_pools(self, from_cache=True):
        """DEPRECATED: use get_resource_pools instead."""
        import warnings
        from exceptions import DeprecationWarning
        warnings.warn("method '_get_resource_pools' is DEPRECATED use "\
                      "'get_resource_pools' instead",
                      DeprecationWarning)

        ret = self.get_resource_pools()
        return dict([(v,k) for k,v in ret.items()])     