import os
import random
import ConfigParser
from unittest import TestCase

from pysphere import VIServer, VIProperty, MORTypes, VIException, FaultTypes, \
                     VMPowerState

class VIServerTest(TestCase):

    @classmethod
    def setUpClass(cls):
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        cls.config = ConfigParser.ConfigParser()
        cls.config.read(config_path)
        
        host = cls.config.get("READ_ONLY_ENV", "host")
        user = cls.config.get("READ_ONLY_ENV", "user")
        pswd = cls.config.get("READ_ONLY_ENV", "password")
        
        cls.server = VIServer()
        cls.server.connect(host, user, pswd)

    @classmethod
    def tearDownClass(cls):
        cls.server.disconnect()

    def test_get_hosts_by_datacenter(self):
        all_hosts = self.server.get_hosts()
        datacenters = self.server.get_datacenters()
        hosts_by_datacenter = [self.server.get_hosts(from_mor=dc)
                            for dc in datacenters.keys()]
        all_hosts2 = {}
        [all_hosts2.update(group) for group in hosts_by_datacenter]
        
        assert all_hosts == all_hosts2

    def test_get_hosts_by_cluster(self):
        clusters = self.server.get_clusters()
        count_hosts1 = 0
        count_hosts2 = 0
        for cl in clusters.keys():
            count_hosts1 += len(self.server.get_hosts(from_mor=cl))
            prop = VIProperty(self.server, cl)
            count_hosts2 += len(prop.host)
        assert count_hosts1 == count_hosts2
        
    def test_get_datastores_by_datacenter(self):
        all_datastores = self.server.get_datastores()
        datacenters = self.server.get_datacenters()
        datastores_by_datacenter = [self.server.get_datastores(from_mor=dc)
                            for dc in datacenters.keys()]
        all_datastores2 = {}
        [all_datastores2.update(group) for group in datastores_by_datacenter]
        
        assert all_datastores == all_datastores2
        
    def test_get_resource_pools(self):
        all_rp = self.server.get_resource_pools()
        rp_by_root_rp = []
        for rp_key, rp_path in all_rp.items():
            if rp_path.count('/') == 1:
                rp_by_root_rp.extend(self.server.get_resource_pools(
                                                        from_mor=rp_key).keys())
        print len(rp_by_root_rp), len(all_rp)
        assert sorted(rp_by_root_rp) == sorted(all_rp.keys())
        
    def test_get_registered_vms(self):
        all_vms = self.server.get_registered_vms()
        datacenters = self.server.get_datacenters()
        vms_by_datacenter = []
        resource_pools = self.server.get_resource_pools()
        vms_by_root_rp = []
        for dc in datacenters.keys():
            vms_by_datacenter.extend(self.server.get_registered_vms(
                                                                 datacenter=dc))
        for rp_key, rp_path in resource_pools.items():
            if rp_path.count('/') == 1:
                vms_by_root_rp.extend(self.server.get_registered_vms(
                                                          resource_pool=rp_key))
        oc = self.server._retrieve_properties_traversal(
                                             property_names=['config.template',
                                                     'config.files.vmPathName'],
                                             obj_type=MORTypes.VirtualMachine)
        templates = []
        for o in oc:
            path = None
            template = False
            if not hasattr(o, "PropSet"):
                continue
            for p in o.PropSet:
                if p.Name=="config.template" and p.Val:
                    template = True
                if p.Name=="config.files.vmPathName":
                    path = p.Val
            if template:
                templates.append(path)
                
        vms_by_root_rp.extend(templates)
        assert sorted(all_vms) == sorted(vms_by_datacenter) == sorted(
                                                                 vms_by_root_rp)

    def test_get_registered_vms_by_datacenter(self):
        for dc_key, dc_name in self.server.get_datacenters().items():
            vms1 = self.server.get_registered_vms(datacenter=dc_key)
            vms2 = self.server.get_registered_vms(datacenter=dc_name)
            assert vms1 == vms2

    def test_get_registered_vms_by_cluster(self):
        for cl_key, cl_name in self.server.get_clusters().items():
            vms1 = self.server.get_registered_vms(cluster=cl_key)
            vms2 = self.server.get_registered_vms(cluster=cl_name)
            assert vms1 == vms2

    def test_get_registerd_vms_by_status(self):
        #powered on
        vms = self.server.get_registered_vms(status='poweredOn')
        if vms:
            vm = self.server.get_vm_by_path(random.choice(vms))
            assert vm.get_status(basic_status=True) == VMPowerState.POWERED_ON
        #powered off
        vms = self.server.get_registered_vms(status='poweredOff')
        if vms:
            vm = self.server.get_vm_by_path(random.choice(vms))
            assert vm.get_status(basic_status=True) == VMPowerState.POWERED_OFF
        #suspended
        vms = self.server.get_registered_vms(status='suspended')
        if vms:
            vm = self.server.get_vm_by_path(random.choice(vms))
            assert vm.get_status(basic_status=True) == VMPowerState.SUSPENDED

    def test_is_connected(self):
        assert self.server.is_connected()

    def test_keep_session_alive(self):
        assert self.server.keep_session_alive()
        
    def test_api_version_and_server(self):
        assert self.server.get_api_version()
        assert self.server.get_server_type()
        
    def test_existent_vm_path(self):
        vms = self.server.get_registered_vms()
        path = random.choice(vms)
        vm = self.server.get_vm_by_path(path)
        assert path == vm.properties.config.files.vmPathName
        
    def test_unexistent_vm_path(self):
        try:
            self.server.get_vm_by_path("zaraza")
        except VIException, e:
            assert e.fault == FaultTypes.OBJECT_NOT_FOUND
        else:
            assert False

    def test_existent_vm_path_by_datacenter(self):
        datacenters = self.server.get_datacenters()
        for k, v in datacenters.items():
            vms = self.server.get_registered_vms(datacenter=k)
            path = random.choice(vms)
            vm1 = self.server.get_vm_by_path(path, datacenter=k)
            vm2 = self.server.get_vm_by_path(path, datacenter=v)
            assert vm1._mor == vm2._mor
            
    def test_existent_vm_path_in_other_datacenter(self):
        datacenters = self.server.get_datacenters()
        if len(datacenters) >= 2:
            dc1 = datacenters.keys()[0]
            dc2 = datacenters.keys()[1]
            vms = self.server.get_registered_vms(datacenter=dc1)
            path = random.choice(vms)
            try:
                self.server.get_vm_by_path(path, datacenter=dc2)
            except VIException, e:
                assert e.fault == FaultTypes.OBJECT_NOT_FOUND
            else:
                raise AssertionError("VM shouldn't be found")
                
    def test_get_object_properties(self):
        hosts = self.server.get_hosts()
        props = ['name', 'summary.config.vmotionEnabled']
        for mor, name in hosts.items():
            prop = self.server._get_object_properties(mor, 
                                                          property_names=props)
            assert prop.Obj == mor
            assert len(prop.PropSet) == 2
            pname = None
            pvmotion = None
            for p in prop.PropSet:
                if p.Name == 'name':
                    pname = p.Val
                elif p.Name == "summary.config.vmotionEnabled":
                    pvmotion = p.Val
                else:
                    raise AssertionError("Got not expected property")
            assert pname == name
            assert pvmotion in (True, False)
            
    def test_get_object_properties_get_all(self):
        datastores = self.server.get_datastores()
        props = ['name', 'info.url']
        for mor, name in datastores.items():
            prop = self.server._get_object_properties(mor, 
                                                        property_names=props,
                                                        get_all=True)
            assert prop.Obj == mor
            assert len(prop.PropSet) > 2
            
            for p in prop.PropSet:
                if p.Name == 'name':
                    assert p.Val == name
                    
    def test_get_object_properties_bulk(self):
        
        hosts = self.server.get_hosts()
        datastores = self.server.get_datastores()
        oc = self.server._retrieve_properties_traversal(
                                                        property_names=['name'],
                                               obj_type=MORTypes.VirtualMachine)
        random.shuffle(oc)
        vms = dict([(o.Obj, o.PropSet[0].Val) for o in oc[:10]])
        
        all_mors = hosts.keys() + datastores.keys() + vms.keys()
        found = []
        random.shuffle(all_mors)
        
        properties = {MORTypes.VirtualMachine:['name', 'config.files.vmPathName'],
                      MORTypes.HostSystem:['name', 'summary.config.vmotionEnabled'],
                      MORTypes.Datastore:[], #get all
                      MORTypes.Folder:['name']
                      }
        
        res = self.server._get_object_properties_bulk(all_mors, properties)
        
        for o in res:
            mor = o.Obj
            found.append(mor)
            assert mor in all_mors
            if mor.get_attribute_type() == MORTypes.VirtualMachine:
                assert len(o.PropSet) == 2
                path = None
                name = None
                for p in o.PropSet:
                    if p.Name == "name": name = p.Val
                    elif p.Name == "config.files.vmPathName": path = p.Val
                    else:
                        raise AssertionError("Unexpected property for VM: %s"
                                             % p.Name)
                assert name == vms[mor]
                assert path
            elif mor.get_attribute_type() == MORTypes.Datastore:
                assert len(o.PropSet) > 5
                name = None
                for p in o.PropSet:
                    if p.Name == "name": name = p.Val
                assert name == datastores[mor]
            elif mor.get_attribute_type() == MORTypes.HostSystem:
                assert len(o.PropSet) == 2
                name = None
                vmotion = None
                for p in o.PropSet:
                    if p.Name == "name": name = p.Val
                    elif p.Name == "summary.config.vmotionEnabled": vmotion = p.Val
                    else:
                        raise AssertionError("Unexpected property for Host: %s"
                                             % p.Name)
                assert name == hosts[mor]
                assert vmotion in [True, False]
            else:
                raise AssertionError("Unexpected mor type %s" 
                                     % mor.get_attribute_type())
        assert sorted(all_mors) == sorted(found)
                
        