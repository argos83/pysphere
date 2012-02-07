import os
from threading import Thread
import random
import time
import ConfigParser
from unittest import TestCase

from pysphere import VIServer

class ThreadingTest(TestCase):

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

                    
    def test_same_server(self):        
        self.passes = True
        def check_result(expected, method, times, *args, **kwargs):
            for _ in xrange(times):
                try:
                    obtained = method(*args, **kwargs)                    
                    if not expected == obtained:
                        self.passes = False                    
                    time.sleep(random.random())
                except:
                    self.passes = False
                    
        hosts = self.server.get_hosts()
        rp = self.server.get_resource_pools()
        vms = self.server.get_registered_vms()
        vm = self.server.get_vm_by_path(vms[random.randint(0, len(vms)-1)])
        vm_props = vm.get_properties(from_cache=False)
        threads = []
        
        threads.append(
            Thread(target=check_result, 
                   args=(hosts, self.server.get_hosts, random.randint(8,15)))
        )
        threads.append(
            Thread(target=check_result, 
               args=(rp, self.server.get_resource_pools, random.randint(8,15)))
        )
        threads.append(
            Thread(target=check_result, 
               args=(vms, self.server.get_registered_vms, random.randint(8,15)))
        )
        threads.append(
            Thread(target=check_result, 
               args=(vm_props, vm.get_properties, random.randint(8,15)),
               kwargs={'from_cache':False})
        )
        for t in threads:
            t.daemon = True
            t.start()
        [t.join() for t in threads]
        
        assert self.passes
        
        
        
                
        