import os
import random
import time
import ConfigParser
from unittest import TestCase

from pysphere import VIServer, VMPowerState, ToolsStatus

class VIVirtualMachineTest(TestCase):

    @classmethod
    def setUpClass(cls):
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        cls.config = ConfigParser.ConfigParser()
        cls.config.read(config_path)
        
        host = cls.config.get("READ_ONLY_ENV", "host")
        user = cls.config.get("READ_ONLY_ENV", "user")
        pswd = cls.config.get("READ_ONLY_ENV", "password")
        
        host2 = cls.config.get("SANDBOX_ENV", "host")
        user2 = cls.config.get("SANDBOX_ENV", "user")
        pswd2 = cls.config.get("SANDBOX_ENV", "password")
        
        cls.server = VIServer()
        cls.server.connect(host, user, pswd)
        
        cls.server2 = VIServer()
        cls.server2.connect(host2, user2, pswd2)
        
        cls.vm_tools_path = cls.config.get("SANDBOX_ENV", "windows_vm_with_tools")
        cls.vm_tools_snap = cls.config.get("SANDBOX_ENV", "windwos_vm_snapshot")
        cls.vm_tools_user = cls.config.get("SANDBOX_ENV", "windows_vm_username")
        cls.vm_tools_pass = cls.config.get("SANDBOX_ENV", "windows_vm_password")
        cls.vm_tools = cls.server2.get_vm_by_path(cls.vm_tools_path)
        
        cls.vm_toy_path = cls.config.get("SANDBOX_ENV", "writable_vm")
        cls.vm_toy = cls.server2.get_vm_by_path(cls.vm_toy_path)
        
    @classmethod
    def tearDownClass(cls):
        cls.server.disconnect()
        if cls.vm_tools.get_status(basic_status=True) != VMPowerState.POWERED_OFF:
            cls.vm_tools.power_off()
        if cls.vm_toy.get_status(basic_status=True) != VMPowerState.POWERED_OFF:
            cls.vm_toy.power_off()
        cls.server2.disconnect()

    def test_get_resource_pool_name(self):
        for mor in self.server.get_resource_pools().iterkeys():
            vms = self.server.get_registered_vms(resource_pool=mor)
            if not vms:
                continue
            path = random.choice(vms)
            print "picked:", path
            vm = self.server.get_vm_by_path(path)
            assert vm.get_resource_pool_name()
        
    def test_vm_status(self):
        vm = self.get_random_vm()
        expected = {
            VMPowerState.BLOCKED_ON_MSG: ["is_blocked_on_msg", False],
            VMPowerState.POWERED_OFF: ["is_powered_off", False],
            VMPowerState.POWERED_ON: ["is_powered_on", False],
            VMPowerState.POWERING_OFF: ["is_powering_off", False],
            VMPowerState.POWERING_ON: ["is_powering_on", False],
            VMPowerState.RESETTING: ["is_resetting", False],
            VMPowerState.REVERTING_TO_SNAPSHOT: ["is_reverting", False],
            VMPowerState.SUSPENDED: ["is_suspended", False],
            VMPowerState.SUSPENDING: ["is_suspending", False],
        }        
        sta = vm.get_status()
        assert sta in expected
        expected[sta][1] = True
        for method, result in expected.itervalues():
            assert getattr(vm, method)() is result

    def test_power_ops(self):
        vm = self.vm_toy
        if not vm.is_powered_off():
            vm.power_off()
        assert vm.is_powered_off()
        
        vm.power_on()
        assert vm.is_powered_on()
        assert not vm.is_powered_off()
        
        vm.suspend()
        assert vm.is_suspended()
        assert not vm.is_powered_on()
        
        vm.power_on()
        assert vm.is_powered_on()
        
        vm.reset()
        assert vm.is_powered_on()
        
        vm.power_off()
        assert vm.is_powered_off()
        assert not(vm.is_powered_on() or vm.is_suspended())

    def test_extra_config(self):
        #just check no exception are raised
        vm = self.vm_toy
        vm.set_extra_config({'isolation.tools.diskWiper.disable':'TRUE',
                             'isolation.tools.diskShrink.disable':'TRUE'})

    def test_guest_power_ops(self):
        vm = self.start_vm_with_tools()
        time.sleep(20)
        assert self.retry_guest_operation(vm.reboot_guest, 240)
        time.sleep(20)
        assert self.wait_for_status(vm, [VMPowerState.POWERED_ON], 60)
        
        vm = self.start_vm_with_tools()
        time.sleep(20)
        assert self.retry_guest_operation(vm.standby_guest, 240)
        assert self.wait_for_status(vm, [VMPowerState.SUSPENDED], 60)
        
        vm = self.start_vm_with_tools()
        time.sleep(20)
        assert self.retry_guest_operation(vm.shutdown_guest, 240)
        assert self.wait_for_status(vm, [VMPowerState.POWERED_OFF], 60)
        
    def test_get_properties(self):
        vm = self.get_random_vm()
        props = vm.get_properties(from_cache=False)
        
        for p in ["name", "guest_id", "guest_full_name", "path", "memory_mb",
                  "num_cpu", "devices", "hostname", "ip_address", "net",
                  "files", "disks"]:
            if p in props:
                assert vm.get_property(p) == props[p]
        
        props2 = vm.get_properties(from_cache=True)
        assert props == props2

    def test_tools_status(self):
        vm = self.get_random_vm()
        assert vm.get_tools_status() in [ToolsStatus.NOT_INSTALLED,
                                         ToolsStatus.NOT_RUNNING,
                                         ToolsStatus.RUNNING,
                                         ToolsStatus.RUNNING_OLD,
                                         ToolsStatus.UNKNOWN]
    def test_vm_property(self):
        vm = self.get_random_vm()
        assert (vm.properties.name 
                and vm.properties.name == vm.get_property("name"))

    def test_guest_file_ops(self):
        vm = self.start_vm_with_tools()
        
        vm.login_in_guest(self.vm_tools_user, self.vm_tools_pass)
        
        short_dir_name = str(random.randint(10000, 99999))
        short_dir_name2 = str(random.randint(10000, 99999))
        random_dir_name = "C:\\" + short_dir_name
        random_dir_name2 = "C:\\" + short_dir_name2
        random_file_name = str(random.randint(10000, 99999))
        random_file_name2 = str(random.randint(10000, 99999))
        random_content = str(random.randint(10000, 99999))
        local_path = os.path.join(os.path.dirname(__file__), "test_file.txt")
        fd = open(local_path, "w")
        fd.write(random_content)
        fd.close()
        
        local_path2 = os.path.join(os.path.dirname(__file__), "downloaded.txt")
        remote_path = random_dir_name2 + "\\" + random_file_name
        remote_path2 = random_dir_name2 + "\\" + random_file_name2
        
        vm.make_directory(random_dir_name)
        vm.move_directory(random_dir_name, random_dir_name2)       
        vm.send_file(local_path, remote_path)
        vm.move_file(remote_path, remote_path2)
        vm.get_file(remote_path2, local_path2, overwrite=True)
        
        fd = open(local_path2, "r")
        downloaded_content = fd.read()
        fd.close()
        
        #this assert tests: make_directory, move_directory,
        #                   send_file, move_file, get_file
        assert random_content == downloaded_content
        
        #check list files without regex
        files = vm.list_files(random_dir_name2)
        assert len(files) == 3 # '.', '..', and our file
        assert {'path': '.', 'type': 'directory', 'size': 0} in files
        assert {'path': '..', 'type': 'directory', 'size': 0} in files
        assert {'path': random_file_name2, 'type': 'file', 'size': 5} in files
        
        #check list files with regex
        files = vm.list_files(random_dir_name2, match_pattern=random_file_name2)
        assert len(files) == 1 # just our file
        assert {'path': random_file_name2, 'type': 'file', 'size': 5} in files
        
        #check delete file
        vm.delete_file(remote_path2)
        files = vm.list_files(random_dir_name2)
        assert len(files) == 2 # '.', '..'
        assert {'path': '.', 'type': 'directory', 'size': 0} in files
        assert {'path': '..', 'type': 'directory', 'size': 0} in files
        
        #check delete directory
        files = vm.list_files("C:\\")
        found = False
        for f in files:
            if f.get('path') == short_dir_name2:
                found = True
                break
        assert found
        vm.delete_directory(random_dir_name2, recursive=True)
        files = vm.list_files("C:\\")
        found = False
        for f in files:
            if f.get('path') == short_dir_name2:
                found = True
                break
        assert not found

    def test_guest_process_ops(self):
        vm = self.start_vm_with_tools()
        vm.login_in_guest(self.vm_tools_user, self.vm_tools_pass)
        
        #check start process
        proc_command = "calc.exe"
        pid = vm.start_process(proc_command)
        assert pid
        
        #check list processes
        processes = vm.list_processes()
        our_process = None
        for proc in processes:
            if proc['pid'] == pid:
                our_process = proc
                break
        assert our_process      
        assert proc_command in our_process['cmd_line']
        assert proc_command in our_process['name']
        assert our_process['exit_code'] is None
        assert our_process['end_time'] is None
        assert isinstance(our_process['start_time'], tuple)
        assert our_process['owner'].lower() == self.vm_tools_user.lower()
        
        #check terminate process
        vm.terminate_process(pid)
        time.sleep(10)
        #check list processes
        processes = vm.list_processes()
        our_process = None
        for proc in processes:
            if proc['pid'] == pid:
                our_process = proc
                break
        assert our_process
        assert proc_command in our_process['cmd_line']
        assert proc_command in our_process['name']
        assert 'exit_code' in our_process
        assert isinstance(our_process['end_time'], tuple)
        assert isinstance(our_process['start_time'], tuple)
        assert our_process['owner'].lower() == self.vm_tools_user.lower()
        
        #check get environment variables
        assert vm.get_environment_variables()

    def wait_for_status(self, vm, statuses, timeout):
        if not isinstance(statuses, list):
            statuses = [statuses]
        
        start = time.time()
        reached = False
        while True:
            sta = vm.get_status()
            if sta in statuses:
                reached = True
                break
            if time.time() - start > timeout:
                break
            time.sleep(2)
        return reached

    def retry_guest_operation(self, method, timeout):
        result = False
        start = time.time()
        while True:
            try:
                method()
            except:
                if time.time() - start > timeout:
                    break
                time.sleep(30)
            else:
                result = True
                break
        return result
        
    def get_random_vm(self):
        vms = self.server.get_registered_vms()
        path = random.choice(vms)
        print "picked:", path
        return self.server.get_vm_by_path(path)
    
    def start_vm_with_tools(self):
        vm = self.vm_tools
        vm.revert_to_named_snapshot(self.vm_tools_snap)
        vm.wait_for_tools(timeout=60)
        time.sleep(5)
        assert vm.get_tools_status() in [ToolsStatus.RUNNING,
                                         ToolsStatus.RUNNING_OLD]
        vm.properties._flush_cache()
        return vm