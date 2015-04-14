## PySphere  ##

**Python API for interaction with the vSphere Web Services SDK.**

Among other operations, it provides easy interfaces to:
  * Connect to VMWare's ESX, ESXi, Virtual Center, Virtual Server hosts
  * Query hosts, datacenters, resource pools, virtual machines
  * VM: Power on, power off, reset, revert to snapshot, get properties, update vmware tools, clone, migrate.
  * vSphere 5.0 Guest Operations: create/delete/move files and directories. Upload/download files from the guest system. List/start/stop processes in the guest system.
  * Create and delete snapshots
  * Hosts statistics and performance monitoring

An of course, you can use it to access all the vSphere API through python.

It's built upon a slightly modified version of ZSI (that comes bundled-in) which makes it really fast in contrast to other python SOAP libraries that don't provide code generation.

### Installation ###

The simplest way is using either easy\_install or pip:

`easy_install -U pysphere`

or

`pip install -U pysphere`

Or you can find the source package and windows installer in the downloads section.
To install it from the source package:
  1. Unzip the package
  1. run: `python setup.py install`

### Quick Example ###

Here's how you power on a virtual machine. See the project's wiki with the full documentation.

```
from pysphere import VIServer

server = VIServer()
server.connect("my.esx.host.com", "myusername", "secret")

vm = server.get_vm_by_path("[datastore] path/to/file.vmx")
vm.power_on()
```

### Discussion Group ###

You can find a lot more examples and use cases in the [discussion group](http://groups.google.com/group/pysphere).