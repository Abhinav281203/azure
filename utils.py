from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from datetime import datetime, timedelta


def get_vm_metrics(monitor_client : MonitorManagementClient, subscription_id : str, resource_group_name : str, vm_name : str):
    print("get_vm_metrics function")
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)

    cpu_metric = monitor_client.metrics.list(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
        timespan=f"{start_time}/{end_time}",
        interval='PT1H',
        metricnames='Percentage CPU',
        aggregation='Average'
    )

    memory_metric = monitor_client.metrics.list(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
        timespan=f"{start_time}/{end_time}",
        interval='PT1H',
        metricnames='Available Memory Bytes',
        aggregation='Average'
    )

    cpu_data = [m.average for m in cpu_metric.value[0].timeseries[0].data if m.average is not None]
    memory_data = [m.average for m in memory_metric.value[0].timeseries[0].data if m.average is not None]

    cpu_min = min(cpu_data) if cpu_data else "N/A"
    cpu_max = max(cpu_data) if cpu_data else "N/A"
    cpu_avg = sum(cpu_data) / len(cpu_data) if cpu_data else "N/A"

    memory_min = min(memory_data) if memory_data else "N/A"
    memory_max = max(memory_data) if memory_data else "N/A"
    memory_avg = sum(memory_data) / len(memory_data) if memory_data else "N/A"

    return {
        "CPU_Min": cpu_min,
        "CPU_Max": cpu_max,
        "CPU_Avg": cpu_avg,
        "Memory_Min": memory_min,
        "Memory_Max": memory_max,
        "Memory_Avg": memory_avg,
    }


def get_disk_size(compute_client : ComputeManagementClient, resource_group_name : str, disk_name : str):
    print("get_disk_sku function")
    managed_disk = compute_client.disks.get(resource_group_name, disk_name)
    disk_size = managed_disk.disk_size_gb if managed_disk.disk_size_gb else "N/A"
    return disk_size

def get_disk_sku(compute_client : ComputeManagementClient, resource_group_name : str, disk_name : str):
    print("get_disk_sku function")
    managed_disk = compute_client.disks.get(resource_group_name, disk_name)
    disk_sku = managed_disk.sku.name if managed_disk.sku else "N/A"
    return disk_sku


def get_public_ip_address(network_client : NetworkManagementClient, 
                          resource_group_name : str, 
                          vm_name : str,
                          vm):
    print("get_public_ip_address function")
    public_ip_address = "N/A"
    if vm.network_profile:
        for nic in vm.network_profile.network_interfaces:
            network_interface = network_client.network_interfaces.get(resource_group_name, nic.id.split("/")[-1])
            for ip_config in network_interface.ip_configurations:
                if ip_config.public_ip_address:
                    public_ip = network_client.public_ip_addresses.get(resource_group_name, ip_config.public_ip_address.id.split("/")[-1])
                    public_ip_address = public_ip.ip_address

    return public_ip_address
