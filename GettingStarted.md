# Quick guide to start using PySphere #

## Installation ##

PySphere is platform independent and works with python 2.5, 2.6, and 2.7.

The simplest way to install it is using  [setuptools](http://pypi.python.org/pypi/setuptools)' easy\_install:

`easy_install -U pysphere`

Or using [pip](http://pypi.python.org/pypi/pip):

`pip install -U pysphere`

You can also find the source package and windows installer in the [downloads section](http://code.google.com/p/pysphere/downloads/list).

To install it from the windows executable just run the file and follow the wizard's instructions.

To install it from the source package:

  1. unzip pysphere-0.1.5.zip
  1. python setup.py install

## Connecting to a server ##

PySphere can interact with ESX, ESXi, Virtual Center, Virtual Server, and it should work with any other VMWare product exposing the vSphere Web Services SDK.

First you need to create a server instance from the `VIServer` class:
```
>>> from pysphere import VIServer
>>> server = VIServer()
```

Next, you must call the connect method and provide the server hostname or IP and the user credentials. E.g. For an ESX server on 192.168.100.100 with a registered user 'jdoe' with password 'secret':
```
>>> server.connect("192.168.100.100", "jdoe", "secret")
```

By default, pysphere will look for the web service at VMWare's default URL which is `https://[SERVER]/sdk`.
If your server is configured to use http instead of https or if it's serving on a different port, then you need to provide the connect method with the full URL instead of just the hostname or IP. For example:
```
>>> server.connect("http://192.168.100.100:8080/sdk", "jdoe", "secret")
```

For debugging you can also provide the keyword argument `trace_file` with a path to a file where the SOAP requests and responses generated during you session will be stored:
```
>>> server.connect("192.168.100.100", "jdoe", "secret", trace_file="debug.txt")
```
## Server properties and methods ##

If you want to start working with VMs right away you may skip this section.

Once you created your VIServer instance and got connected you are able to retrieve info from the server.

### Getting the server type and vSphere API version ###

To get Server Type
```
>>> print server.get_server_type() 
VMware vCenter Server
```
To get API Version
```
>>> print server.get_api_version() 
4.1
```


### Getting the server's registered VMs ###

This method will return a list of strings with all the VM's .vmx file paths that are registered in the server. You can use them later to connect to those vms.

```
>>> vmlist = server.get_registered_vms()
```

You may also use one or more filters through keyword arguments:

  * datacenter: Name of the datacenter to get vms from.
  * cluster: Name of the cluster to get vms from.
  * resource\_pool: Name of the resource pool to get vms from.
  * status: one of 'poweredOn', 'poweredOff', 'suspended'. To get only VM with that power state.

Note: if  cluster is set then datacenter is ignored and if resource pool is set both, datacenter and cluster, are ignored.

For example, to get all powered on VMs from the 'Windows XP' resource pool:

```
>>> vmlist = server.get_registered_vms(resource_pool='Windows XP', status='poweredOn')
```

### Disconnecting from the server ###

Once you've finalized your program or script it's recommended to logout from the server, that will release all the objects at the server side that were created during your session. If not, the server will eventually drop your session after a period of inactivity.

To disconnect from the server, just execute:

```
>>> server.disconnect()
```


## Working with virtual machines ##

Once you have created your VIServer instance and invoked the connect method (see [Connecting to a server](GettingStarted#Connecting_to_a_server.md)) you are ready to retrieve VM instances and operate with them.

The are two main methods you can use to get a VM instance:
  1. **get\_vm\_by\_path**: retrieve a virtual machine by its virtual machine configuration file path. To get this value via the VMWare VI Client:
    1. Right click on the vm icon from the resources tree and select "Edit settings..."
    1. Go to the "Options" tab.
    1. The value is on the "Virtual Machine Configuration File" field
  1. **get\_vm\_by\_name**: retrieve a virtual machine by its assigned name.

It's recommended that you use the first method. It is faster and you won't have two VMs with the same path whereas you might have more than one VM with the same name assigned in which case get\_vm\_by\_name will return the first one to be found.

Example:

```
>>> from pysphere import VIServer
>>> server = VIServer()
>>> server.connect("192.168.100.100", "jdoe", "secret")

>>> vm1 = server.get_vm_by_path("[DataStore1] Ubuntu/Ubuntu-10.vmx")
>>> vm2 = server.get_vm_by_name("Windows XP Professional")
```

both methods can receive an additional "datacenter" keyword argument that will limit the search within the specified datacenter:

```
>>> vm1 = server.get_vm_by_path("[DataStore1] Ubuntu/Ubuntu-10.vmx", "DEVELOPMENT")
>>> vm2 = server.get_vm_by_name("Windows XP Professional", "IT")
```

### Getting VM properties ###

#### **Virtual Machine Status:** ####

The following code
```
>>> print vm1.get_status()
```

will print one of these values (strings):
  * 'POWERED ON'
  * 'POWERED OFF'
  * 'SUSPENDED'
  * 'POWERING ON'
  * 'POWERING OFF'
  * 'SUSPENDING'
  * 'RESETTING'
  * 'BLOCKED ON MSG'
  * 'REVERTING TO SNAPSHOT'

The first three states are the basic ones. i.e. a virtual machine will always be in one of those three statuses, however by inspecting the list of queued tasks the other statuses can be implied. E.g. if a VM is powered off but a user has started a power on action, then the implied status will be 'POWERING ON'. The status 'BLOCKED ON MSG' means that VM can't be used until the user decides an action to be taken on that VM (one of the most common message triggered is "This virtual machine may have been moved or copied")

Some products as "VMware Server/ESX/ESXi" do not support querying the tasks history so you'll always get one of the first three statuses.
Besides, you can force pysphere to return one of the three basic statuses by providing the extra keyword argument "basic\_status" with 'True':

```
>>> print vm1.get_status(basic_status=True)
```

You might also ask if the VM is in a particular status (which will return True or False) by invoking these methods:
```
>>> print vm1.is_powering_off()
>>> print vm1.is_powered_off()
>>> print vm1.is_powering_on()
>>> print vm1.is_powered_on()
>>> print vm1.is_suspending()
>>> print vm1.is_suspended()
>>> print vm1.is_resetting()
>>> print vm1.is_blocked_on_msg()
>>> print vm1.is_reverting()
```

#### **Getting basic properties:** ####

Pysphere provides two methods to get some basic properties from a VM in a simple way. If you are looking to retrieve any other property that is not being listed here see the [Advanced Usage](AdvancedUsage.md) section.

  * **get\_properties**: retrieves a python dictionary with all the properties available at the time (Not all the vms will have all the properties, as some properties depend on the specific configuration, vmware tools, or the machine power status).
  * **get\_property(property\_name)**: retrieves the value of the requested property, or None if that property does not exist. E.g:

```
>>> vm1.get_properties()
{'guest_id': 'ubuntuGuest',
 'path': '[DataStore1] Ubuntu/Ubuntu-10.vmx',
 'guest_full_name': 'Ubuntu Linux (32-bit)',
 'name': 'Ubuntu 10.10 Desktop 2200',
 'mac_address': '00:50:56:aa:01:a7'
}
```

```
>>> print vm1.get_property('mac_address') 
'00:50:56:aa:01:a7'
```

Due to performance reasons, when pysphere creates the VM instance, all the properties are queried in a single request and cached. But some of them are volatile, their values might change, new properties can appear or an existing property might disappear. For example, to get the `ip_address` property the VM needs to have the VMWare tools installed and to be powered on. To be sure the value you request is updated you might add the 'from\_cache' keyword argument to `get_property` or `get_properties` with the value `False`. This will refresh the cache of all the properties, not only the requested.

```
>>> print vm1.get_property('ip_address', from_cache=False)
>>> print vm1.get_properties(from_cache=False)
```

This is the list of all the properties you can request:
  * name
  * path
  * guest\_id
  * guest\_full\_name
  * hostname
  * ip\_address
  * mac\_address
  * net

#### **Getting the resource pool name:** ####
To get the name of the immediate resource pool the VM belongs to, execute:

```
>>> print vm1.get_resource_pool_name() 
Linux VMs
```

### **Power ON/OFF, Suspend, Reset** ###

To power on, power off, suspend, or reset a virtual machine you should call one of these methods:

```
>>> vm1.power_on()
>>> vm1.reset()
>>> vm1.suspend() #since pysphere 0.1.5
>>> vm1.power_off()
```

By default all of them are executed synchronously, i.e, the method won't return until the requested operation has completed.

If you want to execute those operations asynchronously, you must provide the keyword argument `sync_run=False`. In that case, the method will return a task object which you can use to query the task progress and result. The methods and attributes of this task object will be explained later (see [Running Tasks Asynchronously](GettingStarted#Running_Tasks_Asynchronously.md)).

```
>>> task1 = vm1.power_on(sync_run=False)
>>> task2 = vm2.reset(sync_run=False)
>>> task3 = vm2.suspend(sync_run=False) #since pysphere 0.1.5
>>> task4 = vm3.power_off(sync_run=False)
```

Additionally, the power\_on method supports an additional 'host' keyword argument you can supply to indicate in which host the VM should be powered on (e.g. If you are working with a Virtual Center with several ESX severs registered). If this argument is either invalid or not provided the current host association is used.

```
>>> vm1.power_on(host="esx3.example.com")
```

### **Snapshots: Revert to, Create, and Delete** ###

#### **Revert to snapshot** ####

There are three methods you can use to revert a virtual machine to a snapshot:
  * **revert\_to\_snapshot**: reverts to the current snapshot.
  * **revert\_to\_named\_snapshot**: reverts to the first snapshot matching the given name.
  * **revert\_to\_path**: reverts to the snapshot matching the snapshots path and index (to disambiguate among snapshots with the same name).

For example:

```
>>> vm1.revert_to_snapshot() #reverts to the current snapshot
>>> vm1.revert_to_named_snapshot("base") #reverts to the "base" snapshot
>>> vm1.revert_to_path("/base/updated") #reverts to the "updated" snapshot which is a child of snapshot "base"
```

The "revert\_to\_path" method also accepts an "index" keyword argument which defaults to 0. If you have two or more snapshots with the exact same path you can use this argument to disambiguate among them. E.g.:

```
>>> vm1.revert_to_path("/base/updated", index=1) #reverts to the 2nd "updated" snapshot withing the "base" snapshot node
```

As with the "power\_on", "power\_off", "reset" methods (see [Powering ON/OFF, Reset](GettingStarted#Powering_ON/OFF,_Reset:.md)) the revert operations are executed synchronously, i.e, the method won't return until the requested operation has completed.

If you want to execute those operations asynchronously, you must provide the keyword argument `sync_run=False`. In that case, the method will return a task object which you can use to query the task progress and result. The methods and attributes of this task object will be explained later (see [Running Tasks Asynchronously](GettingStarted#Running_Tasks_Asynchronously.md)).

```
>>> task1 = vm1.revert_to_snapshot(sync_run=False)
>>> task2 = vm2.revert_to_named_snapshot("base", sync_run=False)
>>> task3 = vm3.revert_to_path("/base/updated", sync_run=False)
```

Besides, as with the "power\_on" method, there's an additional 'host' keyword argument you can supply to indicate in which host the VM should be reverted (e.g. If you are working with a Virtual Center with several ESX severs registered). If this argument is either invalid or not provided the current host association is used.

```
>>> vm1.revert_to_snapshot(host="esx1.example.com")
>>> vm1.revert_to_named_snapshot(host="esx2.example.com")
>>> vm1.revert_to_path(host="esx3.example.com")
```

#### **Delete snapshots** ####

As with `revert_to_*` methods, there are also three analogical methods to remove a snapshot: the current snapshot, by name, and by path:

  * **delete\_current\_snapshot**
  * **delete\_named\_snapshot(name)**
  * **delete\_snapshot\_by\_path(path, index=0)**

E.g.:

```
>>> vm1.delete_current_snapshot()
>>> vm1.delete_named_snapshot("base")
>>> vm1.delete_snapshot_by_path("/base2/foo")
```

In the case of `delete_snapshot_by_path` you can provide the "index" keyword argument to disambiguate among snapshots with the same path (defaults to 0).

The three methods have a "remove\_children" keyword argument that defaults to False, setting it to True will delete not only the specified snapshot but also all of its descendants.

E.g.:

```
>>> vm1.delete_current_snapshot(remove_children=True)
>>> vm1.delete_named_snapshot("base", remove_children=True)
>>> vm1.delete_snapshot_by_path("/base2/foo", remove_children=True)
```

The delete operation is also executed synchronously, just add the `run_sync=False` keyword argument to execute it asynchronously and get the task object (see [Running Tasks Asynchronously](GettingStarted#Running_Tasks_Asynchronously.md)). E.g.:

```
>>> task1 = vm1.delete_current_snapshot(sync_run=False)
>>> task2 = vm1.delete_named_snapshot("base", sync_run=False)
>>> task3 = vm1.delete_snapshot_by_path("/base2/foo", sync_run=False)
```

#### **Create snapshot** ####

To take a snapshot with the current state of the VM, run:

```
>>> vm1.create_snapshot("mysnapshot")
```

You can also provide a snapshot description via the "description" keyword argument:

```
>>> vm1.create_snapshot("mysnapshot", description="With SP2 installed")
```

The create operation is also executed synchronously, so you won't get the control back until the snapshot has been created, to execute it asynchronously and get the task object just add the `run_sync=False` keyword argument (see [Running Tasks Asynchronously](GettingStarted#Running_Tasks_Asynchronously.md)). E.g.:

```
>>> task1 = vm1.create_snapshot("mysnapshot", sync_run=False)
```

_since pysphere 0.1.6_

In pysphere-0.1.6 optional keyword arguments were added to this method:

  * **memory**: If True (default), a dump of the internal state of the virtual machine (basically a memory dump) is included in the snapshot. Memory snapshots consume time and resources, and thus take longer to create. When set to False, the power state of the snapshot is set to powered off.
  * **quiesce**: If True (default) and the virtual machine is powered on when the snapshot is taken, VMware Tools is used to quiesce the file system in the virtual machine. This assures that a disk snapshot represents a consistent state of the guest file systems. If the virtual machine is powered off or VMware Tools are not available, the quiesce flag is ignored.

E.g:

```
>>> vm1.create_snapshot("fastsnapshot", memory=False, quiesce=False)
```

#### **List snapshots** ####

By calling the following method:

```
>>> snapshot_list = vm2.get_snapshots()
```

You'll get a list of `VISnapthot` objects, each of which support the following methods:

  * **get\_name**: Returns the snapshot's name
  * **get\_description**: Returns the snapshot's description text, if any.
  * **get\_create\_time**: Returns a time tuple with the snapshot creation time.
  * **get\_parent**: Returns a VISnapshot object representing this snapshot's parent. Or None if this is a root snapshot.
  * **get\_children**: Returns a list of VISnapshot objects representing direct child snapshots.
  * **get\_path**: Returns the full path of ancestors names (separated by '/') E.g.: `"/base/base1/base2"`
  * **get\_state**: Returns the status in which the VM was when the snapshot was taken: 'poweredOff', 'poweredOn', or 'suspended'

For example, having a 'base\_old' snapshot with a 'base' child snapshot:

```
>>> print snapshot_list
[<pysphere.vi_snapshot.VISnapshot instance at 0x05244738>, 
 <pysphere.vi_snapshot.VISnapshot instance at 0x052448A0>]
```

```
>>> for snapshot in snapshot_list:
...    print "Name:", snapshot.get_name()
...    print "Description", snapshot.get_description()
...    print "Created:", snapshot.get_create_time()
...    print "State:", snapshot.get_state()
...    print "Path:", snapshot.get_path()
...    print "Parent:", snapshot.get_parent()
...    print "Children:", snapshot.get_children()
...
```

Might print out:
```
"""
Name: base_old
Description:
Created: (2008, 7, 30, 18, 0, 17, 54, 0, 0)
State: poweredOn
Path: /base_old
Parent: None
Children: [<pysphere.vi_snapshot.VISnapshot instance at 0x052448A0>]
Name: base
Description: With Service Pack 2
Created: (2011, 9, 28, 11, 9, 36, 165, 0, 0)
State: poweredOn
Path: /base_old/base
Parent: <pysphere.vi_snapshot.VISnapshot instance at 0x05244738>
Children: []
"""
```

### **Guest power operations: Shutdown, Reboot, and Stand By** ###

Each of these three methods issues a command to the guest operating system asking it to prepare for a shutdown, reboot or suspend operation, and returns immediately not waiting for the guest operating system to complete the operation (Requires the VM to be powered on and have the VMWare tools running)

```
>>> vm1.shutdown_guest()
>>> vm1.reboot_guest()
>>> vm1.standby_guest()
```

Notice that these methods in contrast to their equivalents `power_off`, `reset`, and `suspend` introduced before (see [Power ON/OFF, Suspend, Reset](GettingStarted#Power_ON/OFF,_Suspend,_Reset.md)) don't work on a "hard" level but on a guest OS level, i.e. shutdown\_guest will attempt to perform a clean exit on the system while power\_off is practically equivalent to unplug the power cord on a physical machine.


### **Other guest operations: Files and processes** ###
_**since pysphere 0.1.5**_

The following methods work on servers implementing vSphere 5.0 or later.
They allow you to perform operations with the guest OS. So you'll need the vmware tools to be running on the system.

Before executing any these guest operations you'll need to login in the guest OS:

```
>>> vm1.login_in_guest("os_username", "os_password")
```

If you don't get any exception then the login was successful.

#### **Files and Directories** ####

Once you have successfully executed `login_in_guest` you are ready to perform files and directories operations on the guest system:

  * **make\_directory(path, create\_parents=True)**: Creates a directory in the guest OS specified by `path`, if `create_parents` is `True` (default) all the directory components in the path are created if they don't exist.
  * **move\_directory(src\_path, dst\_path)**: Moves or renames a directory in the guest system from `src_path` to `dst_path`.
  * **delete\_directory(path, recursive)**: Deletes the directory specified by `path` in the guest OS. If `recursive` is `True` all subdirectories and files are also deleted, else the operation will fail if the directory is not empty.
  * **list\_files(path, match\_pattern=None)**: Returns information about files or directories from the guest system. `path` is the complete path to the directory or file to query. `match_pattern` is a filter for the return values specified as a perl-compatible regular expression (if not provided then '.**' is used). The method returns a list of dictionaries with these keys:
    * path: The complete path to the file
    * size: The file size in bytes
    * type: either 'directory', 'file', or 'symlink'
  ***get\_file(guest\_path, local\_path, overwrite=False)**: Downloads a file from the guest to the system running pysphere.
  ***send\_file(local\_path, guest\_path, overwrite=False)**: Uploads a file from the system running pysphere to the guest system.
  ***move\_file(src\_path, dst\_path, overwrite=False)**: Renames a file in the guest system from `src_path` to `dst_path`. If `overwrite` is `False` (default) and `dst_path` already exists the method fails, while if `overwrite` is set to `True` clobbers any existing file.
  ***delete\_file(path)**: Deletes the file specified by `path` from the guest system.**

A few examples:

```
>>> vm2.login_in_guest("admin", "secret")
>>>
>>> vm2.send_file("/home/seba/netcat.exe", r"c:\netcat.exe")
>>>
>>> vm2.make_directory(r"c:\my\binary\tools")
>>>
>>> vm2.move_file(r"c:\netcat.exe", r"c:\my\binary\tools\nc.exe")
>>>
>>> for f in vm2.list_files(r"c:\my\binary\tools"):
...   print "'%s' is a %s of %s bytes." % (f['path'], f['type'], f['size'])

'.' is a direcotory of None bytes.
'..' is a directory of None bytes.
'nc.exe' is a file of 1258291 bytes.
>>>
>>> vm2.delete_directory(r"c:\my", True)
```


#### **Processes and environment variables** ####

Once you have successfully executed `login_in_guest` you are ready to perform processes operations on the guest system:

  * **start\_process(program\_path, args=None, env=None, cwd=None)**: Starts a program in the guest operating system and returns the process identifier (PID). You need to specify `program_path` which is the absolute path to the program to be executed. Optionally you might set:
    * `args`: a list of strings with the arguments to the program.
    * `env`: a dictionary with string keys an values defining the environment variables to be set for the program.
    * `cwd`:The absolute path of the working directory for the program to be run. VMware recommends explicitly setting the working directory. If this value is unset or is an empty string, the behavior depends on the guest operating system (for Linux guest operating systems the working directory will be the home directory of the user associated with the guest authentication, for other guest operating the behavior is unspecified).
  * **terminate\_process(pid)**: Terminates a process identified by `pid` in the guest OS.
  * **list\_processes()**: List the processes running in the guest operating system, plus those started by `start_process` that have recently completed. The list contains dicctionary objects with these keys:
    * `start_time`: a datetime tuple with the process creation time.
    * `end_time`: if the process was started using `start_process` then the process completion time will be available if queried within 5 minutes after it completes (a datetime tuple), returns `None` otherwise.
    * `pid`: the process id.
    * `name`: the process name.
    * `cmd_line`: the full command line.
    * `owner`: the process owner
    * `exit_code`: if the process was started using `start_process` then the process exit code will be available if queried within 5 minutes after it completes, otherwise it will be `None`.
  * **get\_environment\_variables()**: Reads the environment variables from the guest OS (system user). Returns a dictionary with var names as keys and var values as their corresponding dictionary values.

A few examples:

```
>>> vm2.login_in_guest("admin", "secret")
>>>
>>> vm2.list_processes()
[{'cmd_line': 'C:\\WINDOWS\\system32\\services.exe',
  'end_time': None,
  'exit_code': None,
  'name': 'services.exe',
  'owner': 'NT AUTHORITY\\SYSTEM',
  'pid': 612,
  'start_time': (2011, 12, 6, 15, 26, 22, 0, 0, 0)},
 {'cmd_line': '"C:\\Program Files\\VMware\\VMware Tools\\vmacthlp.exe"',
  'end_time': None,
  'exit_code': None,
  'name': 'vmacthlp.exe',
  'owner': 'NT AUTHORITY\\SYSTEM',
  'pid': 800,
  'start_time': (2011, 12, 6, 15, 26, 24, 0, 0, 0)},
 {'cmd_line': 'C:\\WINDOWS\\system32\\svchost -k DcomLaunch',
  'end_time': None,
  'exit_code': None,
  'name': 'svchost',
  'owner': 'NT AUTHORITY\\SYSTEM',
  'pid': 812,
  'start_time': (2011, 12, 6, 15, 26, 25, 0, 0, 0)}
  ...
  ...
]
>>> pid = vm2.start_process("notepad.exe", args=["test.txt"], cwd="c:\\")
>>> print pid
1680
>>>
>>> vm2.terminate_process(1680)
>>> 
>>> vm2.get_environment_variables()
{'ALLUSERSPROFILE': 'C:\Documents and Settings\All Users',
 'COMPUTERNAME': '24377799E194466',
 'CommonProgramFiles': 'C:\Program Files\Common Files',
 'NUMBER_OF_PROCESSORS': '1',
 'OS': 'Windows_NT',
 'PATHEXT': '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH',
 'PROCESSOR_ARCHITECTURE': 'x86',
 'Path': 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem',
 'ProgramFiles': 'C:\Program Files',
 'SystemDrive': 'C:',
 'SystemRoot': 'C:\WINDOWS',
 'TEMP': 'C:\DOCUME~1\admin\LOCALS~1\Temp',
 'TMP': 'C:\DOCUME~1\admin\LOCALS~1\Temp',
 'USERDOMAIN': '24378797F195962',
 'USERNAME': 'admin',
 'USERPROFILE': 'C:\Documents and Settings\admin',
 'windir': 'C:\WINDOWS'}
>>>
```

### **Cloning a Virtual Machine** ###
_**since pysphere 0.1.6**_

To clone a virtual machine (only available for Virtual Center servers):

```
>>> new_vm = vm1.clone("Clone Name")
```

The method returns a new instance of virtual machine. The only mandatory parameter is the new VM name. There are some other keyword arguments you might pass:

  * `sync_run`: if True (default) waits for the task to finish, and returns a VIVirtualMachine instance with the new VM (raises an exception if the task didn't succeed). If sync\_run is set to False the task is started asynchronously and a VITask instance is returned (see [Running Tasks Asynchronously](GettingStarted#Running_Tasks_Asynchronously.md)).
  * `folder`: name of the folder that will contain the new VM, if not set the vm will be added to the folder the original VM belongs to.
  * `resourcepool`: MOR (Managed Object Reference)of the resource pool to be used for the new vm. If not set, it uses the same resource pool than the original vm (see [AdvancedUsage#Managed\_Object\_References](AdvancedUsage#Managed_Object_References.md)).
  * `power_on`: If the new VM will be powered on after being created (defaults to True)
  * `template`: Specifies whether or not the new virtual machine should be marked as a template (default False).

Note: `resourcepool` is ignored for a clone operation to a template. For a clone operation from a template to a virtual machine, this argument is required.

### **Migrating a Virtual Machine** ###
_**since pysphere 0.1.6**_

To cold or hot migrate a VM to a new host or resource pool:

```
>>> vm1.migrate()
```

Other optional keyword argumentes:

  * `sync_run`: if True (default) waits for the task to finish. If sync\_run is set to False the task is started asynchronously and a VITask instance is returned (see [Running Tasks Asynchronously](GettingStarted#Running_Tasks_Asynchronously.md)).
  * `priority`: Either 'default', 'high', or 'low'. Priority of the task that moves the vm. Note this priority can affect both the source and target hosts.
  * `resource_pool`: MOR (Managed Object Reference) of the target resource pool for the virtual machine. If the parameter is left unset, the virtual machine's current pool is used as the target pool (see [AdvancedUsage#Managed\_Object\_References](AdvancedUsage#Managed_Object_References.md)).
  * `host`: MOR (Managed Object Reference) of the target host to which the virtual machine is intended to migrate. The host parameter may be left unset if the compute resource associated with the target pool represents a stand-alone host or a DRS-enabled cluster. In the former case the stand-alone host is used as the target host. In the latter case, the DRS system selects an appropriate target host from the cluster (see [AdvancedUsage#Managed\_Object\_References](AdvancedUsage#Managed_Object_References.md)).
  * `state`: Either 'POWERED ON', 'POWERED OFF', or 'SUSPENDED'. If specified, the virtual machine migrates only if its state matches the specified state.


### **Running Tasks Asynchronously** ###

As mentioned before, there are many methods of a virtual machine that execute synchronously by default (i.e. you don't get the flow control back until the operation has completed) but support asynchronous execution by providing the keyword argument `sync_run=False`.

This is a list of the virtual machine methods which support this argument:
  * power\_on
  * reset
  * suspend
  * power\_off
  * revert\_to\_snapshot
  * revert\_to\_named\_snapshot
  * revert\_to\_path
  * delete\_current\_snapshot
  * delete\_named\_snapshot
  * delete\_snapshot\_by\_path
  * create\_snapshot
  * clone

When invoking the method with `sync_run=False`, a `VITask` object will be returned. For example:

```
>>> task = vm1.power_on(sync_run=False)
```

this `VITask` object has the following methods:
  * **get\_state**: Return the current status of the task. Possible values are:
    * `"error"`: The task finished but not successfully.
    * `"queued"`: The task is still queued and waiting to be executed.
    * `"running"`: The task is being run.
    * `"success"`: The task finished and was successfully executed.
  * **get\_error\_message**: If the task status is 'error', returns the error description message.
  * **wait\_for\_state**: receives a list of statuses and waits the indicated time at the most (or indefinitely if a timeout is not provided) until one of the given statuses is reached. Returns the reached status or raises a VIException if it times out.
Example:
```
>>> task = vm1.power_on(sync_run=False)
>>> try:
...     status = task.wait_for_state(['running', 'error'], timeout=10)
...     if status == 'error':
...         print "Error powering on:", task.get_error_message()
...     else:
...         print "Succesfully powered on"
... except:
...     print "10 seconds time out reached waiting for power on to finish"
```