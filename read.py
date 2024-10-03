from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import utils
import config
import format

tenant_id = config.AZURE_TENANT_ID
client_id = config.AZURE_CLIENT_ID
client_secret = config.AZURE_CLIENT_SECRET_VALUE

credential = ClientSecretCredential(tenant_id, client_id, client_secret)

subscription_id = "55dc1720-1158-426f-9981-0029b674ae0a"

resource_client = ResourceManagementClient(credential, subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
monitor_client = MonitorManagementClient(credential, subscription_id)


vm_details_list = []


try:
    resource_groups = resource_client.resource_groups.list()

    for resource_group in resource_groups:
        vms = compute_client.virtual_machines.list(resource_group.name)

        for vm in vms:
            os_disk = vm.storage_profile.os_disk
            os_disk_name = os_disk.name
            
            os_disk_size = "N/A"
            os_disk_sku = "N/A"

            if os_disk.managed_disk:
                os_disk_size = utils.get_disk_size(compute_client, resource_group.name, os_disk_name)
                os_disk_sku = utils.get_disk_sku(compute_client, resource_group.name, os_disk_name)
            
            os_type = os_disk.os_type

            data_disks_info = [(disk.name, utils.get_disk_size(compute_client, resource_group.name, disk.name)) for disk in vm.storage_profile.data_disks]
            data_disk_names = ", ".join([info[0] for info in data_disks_info]) if data_disks_info else "N/A"
            data_disk_sizes = ", ".join([str(info[1]) for info in data_disks_info]) if data_disks_info else "N/A"

            public_ip_address = utils.get_public_ip_address(network_client=network_client, 
                                                            resource_group_name=resource_group.name, 
                                                            vm_name=vm.name, 
                                                            vm=vm)

            metrics = utils.get_vm_metrics(monitor_client=monitor_client,
                                            subscription_id=subscription_id, 
                                            resource_group_name=resource_group.name, 
                                            vm_name=vm.name,
                                            vm_size=vm.hardware_profile.vm_size)
            
            vm_details = {
                "VM_Name": vm.name,
                "Resource_Group": resource_group.name,
                "Region": vm.location,
                "VM_Size": vm.hardware_profile.vm_size,
                "OS_Type": os_type,
                "OS_Disk_Name": os_disk_name,
                "OS_Disk_Size": os_disk_size,
                "OS_Disk_SKU": os_disk_sku,
                "Data_Disk_Names": data_disk_names,
                "Data_Disk_Sizes": data_disk_sizes,
                "Public_IP_Address": public_ip_address,
                "CPU": metrics["CPU"],
                "CPU_Min": metrics["CPU_min"],
                "CPU_Max": metrics["CPU_max"],
                "CPU_Avg": metrics["CPU_avg"],
                "Memory_Min": metrics["Mem_min"],
                "Memory_Max": metrics["Mem_max"],
                "Memory_Avg": metrics["Mem_avg"],
                "Total_Memory_GB": metrics["Mem"],
            }

            vm_details_list.append(vm_details)

    format.format(vm_details_list, "output.xlsx")

except Exception as ex:
    print(ex)
