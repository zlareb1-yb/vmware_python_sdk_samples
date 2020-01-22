# -*- coding: utf-8 -*-
"""Interface for vmware sdk"""

import atexit
import ssl

import vmware_utils
from ..constants import VMWARE
from ..logger import CustomLogger
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


LOG = CustomLogger(__name__)


# ESX data model related constants.

ESX_VM_NIC_ADAPTER_MAP = {
    VMWARE.NETADAPTERS.E1000: vim.vm.device.VirtualE1000,
    VMWARE.NETADAPTERS.E1000E: vim.vm.device.VirtualE1000e,
    VMWARE.NETADAPTERS.PCNET: vim.vm.device.VirtualPCNet32,
    VMWARE.NETADAPTERS.VMXNET: vim.vm.device.VirtualVmxnet,
    VMWARE.NETADAPTERS.VMXNET2: vim.vm.device.VirtualVmxnet2,
    VMWARE.NETADAPTERS.VMXNET3: vim.vm.device.VirtualVmxnet3,
}


DISK_ADAPTERS = [
    VMWARE.DISKADAPTER.SCSI,
    VMWARE.DISKADAPTER.IDE,
    VMWARE.DISKADAPTER.SATA,
]


class VMwareError(Exception):
    """Custom class for VMware exceptions"""

    pass


class VMware:
    """VMware Helpers to Update VM's"""

    def __init__(self, hostname, username, password, port=443):
        """Initialize vmware handle
        Args:
            hostname (str) : vshpere server name
            username (str) : username for the vsphere account
            password (str) : password for the vsphere account
            port (int) : port to send api requests
        Raises: VMwareError
        """
        try:
            sslcontext = ssl._create_unverified_context()
            self.si = connect.SmartConnect(
                host=hostname,
                user=username,
                pwd=password,
                port=port,
                sslContext=sslcontext,
            )
            if not self.si:
                raise VMwareError(
                    "Could not connect to the specified"
                    "host using specified username and password"
                )
            atexit.register(connect.Disconnect, self.si)
        except Exception as ex:
            LOG.error("Unable to connect to vmware server: %s" % ex)
            raise VMwareError(
                "Unable to connect to vmware server: '{0}'".format(hostname)
            )

    def add_vdisk(self, datacenter_name, vm_id, disk_size=1, disk_type="disk"):
        """
        Adds VDisk to vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            disk_size (int): size of Disk
            disk_type (str): type of disk
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            esx_vm = self.get_vm_in_dc(datacenter_name, vm_id)
            return self._add_vdisk(esx_vm, self.si, disk_size, disk_type)
        except Exception as ex:
            LOG.error("Adding VDisk failed: %s" % ex)
            raise

    def add_virtual_network(self, datacenter_name, vm_id, network_name, nic_type):
        """
        Adds Virtual Network to vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            network_name (str): network name
            nic_type (str): type of nic
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            esx_vm = self.get_vm_in_dc(datacenter_name, vm_id)
            return self._add_virtual_network(self.si, esx_vm, network_name, nic_type)
        except Exception as ex:
            LOG.error("Adding  VNIC failed: %s" % ex)
            raise

    def update_vm_networks_in_nic(self, datacenter_name, vm_id, network):
        """
        Updates VM Network of NIC of vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            network (str): vm network name
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            vm = self.get_vm_in_dc(datacenter_name, vm_id)
            device_change = []
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    nicspec = vim.vm.device.VirtualDeviceSpec()
                    nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                    nicspec.device = device
                    nicspec.device.wakeOnLanEnabled = True

                    nicspec.device.backing = (
                        vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    )
                    nicspec.device.backing.network = vmware_utils.get_obj(
                        self.si.content, [vim.Network], network
                    )
                    nicspec.device.backing.deviceName = network

                    nicspec.device.connectable = (
                        vim.vm.device.VirtualDevice.ConnectInfo()
                    )
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    device_change.append(nicspec)
                    break

            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)

            return self.update_vm(vm, config_spec)
        except Exception as ex:
            LOG.error("Updating VM Network of NIC of VM failed: %s" % ex)
            raise

    def update_vcpu(self, datacenter_name, vm_id, num_vcpu):
        """
        Update vcpu of vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            num_vcpu (int): number of vcpu
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.update_vcpu_core_memory(
                datacenter_name, vm_id, num_vcpu=num_vcpu
            )
        except Exception as ex:
            LOG.error("Updating vCPUs failed: %s" % ex)
            raise

    def update_core(self, datacenter_name, vm_id, num_cores):
        """
        Update cores of vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            num_cores (int): number of cores
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.update_vcpu_core_memory(
                datacenter_name, vm_id, num_cores=num_cores
            )
        except Exception as ex:
            LOG.error("Updating cores failed: %s" % ex)
            raise

    def update_memory(self, datacenter_name, vm_id, memory):
        """
        Update memory of vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            memory (int): memory of vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.update_vcpu_core_memory(datacenter_name, vm_id, memory=memory)
        except Exception as ex:
            LOG.error("Updating memory failed: %s" % ex)
            raise

    def update_vcpu_core_memory(
        self, datacenter_name, vm_id, num_vcpu=None, num_cores=None, memory=None
    ):
        """
        Update vcpu, core and memory of vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            num_vcpu (int): number of vcpu
            num_cores (int): number of cores
            memory (int): memory of vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            esx_vm = self.get_vm_in_dc(datacenter_name, vm_id)
            config_spec = vim.vm.ConfigSpec()
            if num_vcpu:
                config_spec.numCPUs = num_vcpu
            if num_cores:
                config_spec.numCoresPerSocket = num_cores
            if memory:
                config_spec.memoryMB = memory
            return self.update_vm(esx_vm, config_spec)
        except Exception as ex:
            LOG.error("Update of VM failed: %s" % ex)
            raise

    def update_disk(
        self,
        datacenter_name,
        vm_id,
        controller_key,
        disk_slot,
        disk_size=None,
        disk_mode=None,
    ):
        """
        Update disk of vm
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            controller_key (int): Key of Controller
            disk_slot (int): Slot for Disk
            disk_size (int): Size of Disk
            disk_mode (str): Mode of Disk
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            vm = self.get_vm_in_dc(datacenter_name, vm_id)
            disk = None
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    if (
                        device.controllerKey == controller_key
                        and device.unitNumber == disk_slot
                    ):
                        disk = device
                        break
            if disk is None:
                raise Exception("Failed to find disk for VM")

            if disk_size:
                disk.capacityInKB = int(1048576 * disk_size)
            if disk_mode:
                disk.backing.diskMode = disk_mode

            spec = vim.vm.ConfigSpec()
            devSpec = vim.vm.device.VirtualDeviceSpec(device=disk, operation="edit")
            spec.deviceChange.append(devSpec)

            return self.update_vm(vm, spec)
        except Exception as ex:
            LOG.error("Updating Disk failed: %s" % ex)
            raise

    # TODO: Update VM based on Values Given in kwargs
    '''
    def update(self, datacenter_name, vm_id, **kwargs):
        """
        Update fields of VM specified in kwargs
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
            controller_key (int): Key of Controller
            disk_slot (int): Slot for Disk
            disk_size (int): Size of Disk
            disk_mode (str): Mode of Disk
        Returns (bool): status of operation
        Raises: VMwareError
        """

        try:
            esx_vm = self.get_vm_in_dc(datacenter_name, vm_id)
            config_spec = vim.vm.ConfigSpec()
            if kwargs.get("num_vcpu", None):
                config_spec.numCPUs = kwargs.get("num_vcpu")
            if kwargs.get("num_cores", None):
                config_spec.numCoresPerSocket = kwargs.get("num_cores")
            if kwargs.get("memory", None):
                config_spec.memoryMB = kwargs.get("memory")

            return self.update_vm(esx_vm, config_spec)
        except Exception as ex:
            LOG.error("Updating vCPUs failed: %s" % ex)
            raise
    '''

    def poweron_vm(self, datacenter_name, vm_id):
        """
        Do power on operation on VM
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.change_vm_power_state(datacenter_name, vm_id, "poweron")
        except Exception as ex:
            LOG.error("VM power on failed: %s" % ex)
            raise

    def poweroff_vm(self, datacenter_name, vm_id):
        """
        Do power off operation on VM
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): name of vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.change_vm_power_state(
                datacenter_name, vm_id, VMWARE.OPERATIONS.POWER_OFF
            )
        except Exception as ex:
            LOG.error("VM power off failed: %s" % ex)
            raise

    def reboot_vm(self, datacenter_name, vmname):
        """
        Do reboot operation on VM
        Args:
            datacenter_name (str): name of the datacenter
            vmname (str): name of vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.change_vm_power_state(datacenter_name, vmname, "reboot")
        except Exception as ex:
            LOG.error("VM reboot failed: %s" % ex)
            raise

    def suspend_vm(self, datacenter_name, vmname):
        """
        Do suspend operation on VM
        Args:
            datacenter_name (str): name of the datacenter
            vmname (str): name of vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            return self.change_vm_power_state(datacenter_name, vmname, "suspend")
        except Exception as ex:
            LOG.error("VM suspend failed: %s" % ex)
            raise

    # operation, one of:
    # [poweron | poweroff | reset | suspend | reboot | shutdown | standby]
    def change_vm_power_state(self, datacenter_name, vm_id, operation):
        """
        Do power operation on VM
        Args:
            datacenter_name (str): name of the datacenter
            vm_id (str): unique identifier of the vm
            operation (str): operation to be performed
        Returns (bool): status of operation
        Raises: VMwareError
        """
        vm = self.get_vm_in_dc(datacenter_name, vm_id)

        operation_task_map = {
            VMWARE.OPERATIONS.POWER_OFF: vm.PowerOffVM_Task,
            VMWARE.OPERATIONS.POWER_ON: vm.PowerOnVM_Task,
            VMWARE.OPERATIONS.RESET: vm.ResetVM_Task,
            VMWARE.OPERATIONS.SUSPEND: vm.SuspendVM_Task,
            VMWARE.OPERATIONS.REBOOT: vm.RebootGuest,
            VMWARE.OPERATIONS.SHUTDOWN: vm.ShutdownGuest,
            VMWARE.OPERATIONS.STANDBY: vm.StandbyGuest,
        }

        try:
            if operation in [
                VMWARE.OPERATIONS.POWER_OFF,
                VMWARE.OPERATIONS.POWER_ON,
                VMWARE.OPERATIONS.RESET,
                VMWARE.OPERATIONS.SUSPEND,
            ]:
                task = operation_task_map[operation]()
                vmware_utils.wait_for_tasks(self.si, [task])
            elif operation in [
                VMWARE.OPERATIONS.REBOOT,
                VMWARE.OPERATIONS.SHUTDOWN,
                VMWARE.OPERATIONS.STANDBY,
            ]:
                operation_task_map[operation]()
            else:
                raise VMwareError(
                    "Invalid Operation name '%s', Valid "
                    "operations are poweron, poweroff, "
                    "reset, standby, reboot, "
                    "shutdown and suspend" % operation
                )

        except (vim.fault.InvalidPowerState, vim.fault.InvalidState) as e:
            pass

        except Exception as ex:
            LOG.error("VMware power_op failed: %s" % ex)
            raise
        return True

    def delete_vm(self, datacenter_name, vm_id):
        """
        Delete vm in the given datacenter
        Args:
            datacenter_name (str): datacenter name
            vm_id (str): instance id of vm to be deleted
        Returns (bool): status of operation
        Raises: VMwareError
        """
        try:
            vm = self.get_vm_in_dc(datacenter_name, vm_id)
            if not vm:
                raise VMwareError("VM with id: {0} not found".format(vm_id))
            if format(vm.runtime.powerState) == VMWARE.STATE.RUNNING:
                task = vm.PowerOffVM_Task()
                vmware_utils.wait_for_tasks(self.si, [task])

            task = vm.Destroy_Task()
            vmware_utils.wait_for_tasks(self.si, [task])
            return True
        except vmodl.fault.ManagedObjectNotFound:
            raise VMwareError(
                "Datacenter: '{0}' does not have VM:"
                "'{1}'".format(datacenter_name, vm_id)
            )
        except Exception as ex:
            LOG.error("VMware delete_vm failed: %s" % ex)
            raise

    def get_datacenter(self, dc_name):
        """
        Returns datacenter object given the datacenter name
        Args:
            dc_name (str) : datacenter name
        Returns:
            (vim.Datacenter) datacenter object
        Raises: VMwareError
        """
        try:
            datacenter = None
            if dc_name:
                datacenter = vmware_utils.get_objects_by_prop(
                    self.si, prop="name", obj_type=vim.Datacenter, obj_value=dc_name
                )
            return datacenter
        except Exception as ex:
            LOG.error("VMware get datacenter failed: %s" % ex)
            raise

    def get_vm_in_dc(self, datacenter_name, vm_id):
        """
        Get vm in a given datacenter
        Args:
            datacenter_name (str) : datacenter name
            vm_id (str) : unique id of the esx vm
        Returns:
            (vim.VirtualMachine)
        Raises: VMwareError
        """
        datacenter = self.get_datacenter(datacenter_name)
        if not datacenter:
            raise VMwareError(
                "Datacenter with name: '{0}' not found".format(datacenter_name)
            )
        vm = self.si.content.searchIndex.FindByUuid(datacenter, vm_id, True, True)
        if not vm:
            raise VMwareError("VM with id: {0} not found".format(vm_id))
        return vm

    def update_vm(self, esx_vm, esx_config_spec):
        """
        Update vm properties
        Args:
            esx_vm (vim.VirtualMachine) : esx vm to update
            esx_config_spec (vim.VirtualMachineConfigSpec)) : config spec for the vm
        Returns (bool): status of operation
        Raises: VMwareError
        """
        if esx_vm:
            task = esx_vm.ReconfigVM_Task(esx_config_spec)
            vmware_utils.wait_for_tasks(self.si, [task])
            return True

    def _add_virtual_network(self, si, vm, network_name, nic_type):
        """
        Update vm properties
        Args:
            si: Service Instance
            vm: Virtual Machine Object
            network_name: Name of the Virtual Network
            nic_type: Type of the Virtual Network
        Returns: status of operation
        Raises: VMwareError
        """
        spec = vim.vm.ConfigSpec()
        nic_changes = []

        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

        nic_spec.device = ESX_VM_NIC_ADAPTER_MAP[nic_type]()

        nic_spec.device.deviceInfo = vim.Description()
        nic_spec.device.deviceInfo.summary = "vCenter API to add vnic"

        content = si.RetrieveContent()
        network = vmware_utils.get_obj(content, [vim.Network], network_name)
        if isinstance(network, vim.OpaqueNetwork):
            nic_spec.device.backing = (
                vim.vm.device.VirtualEthernetCard.OpaqueNetworkBackingInfo()
            )
            nic_spec.device.backing.opaqueNetworkType = (
                network.summary.opaqueNetworkType
            )
            nic_spec.device.backing.opaqueNetworkId = network.summary.opaqueNetworkId
        else:
            nic_spec.device.backing = (
                vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            )
            nic_spec.device.backing.useAutoDetect = False
            nic_spec.device.backing.network = network
            # nic_spec.device.backing.deviceName = network
            nic_spec.device.backing.deviceName = network_name

        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.allowGuestControl = True
        nic_spec.device.connectable.connected = False
        nic_spec.device.connectable.status = "untried"
        nic_spec.device.wakeOnLanEnabled = True
        nic_spec.device.addressType = "assigned"

        nic_changes.append(nic_spec)
        spec.deviceChange = nic_changes

        return self.update_vm(vm, spec)

    def _add_vdisk(self, vm, disk_size, disk_type):
        """
        Update vm properties
        Args:
            vm: Virtual Machine Object
            disk_size: Size of Disk
            disk_type: Type of Disk
        Returns: status of operation
        Raises: VMwareError
        """
        spec = vim.vm.ConfigSpec()
        # get all disks on a VM, set unit_number to the next available
        unit_number = 0
        for dev in vm.config.hardware.device:
            if hasattr(dev.backing, "fileName"):
                unit_number = int(dev.unitNumber) + 1
                # unit_number 7 reserved for scsi controller
                if unit_number == 7:
                    unit_number += 1
                if unit_number >= 16:
                    LOG.error("we don't support this many disks")
                    return
            if isinstance(dev, vim.vm.device.VirtualSCSIController):
                controller = dev

        # add disk here
        dev_changes = []
        new_disk_kb = int(disk_size) * 1024 * 1024
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()

        if disk_type == "thin":
            disk_spec.device.backing.thinProvisioned = True

        disk_spec.device.backing.diskMode = "persistent"
        disk_spec.device.unitNumber = unit_number
        disk_spec.device.capacityInKB = new_disk_kb
        disk_spec.device.controllerKey = controller.key
        dev_changes.append(disk_spec)
        spec.deviceChange = dev_changes

        return self.update_vm(vm, spec)

if __name__=='main':
    print(LOG.error('aaa'))