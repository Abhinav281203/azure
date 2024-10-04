from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from datetime import datetime, timedelta
import json

# Load instance details from JSON file
instance_sizes = json.load(open('instance_details.json'))

def get_memo(monitor_client: MonitorManagementClient,
             subscription_id: str,
             resource_group_name: str,
             vm_name: str,
             total_memory_gb: int,):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)

    available_memo = monitor_client.metrics.list(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
        timespan=f"{start_time}/{end_time}",
        interval='PT1H',
        metricnames='Available Memory Bytes',
        aggregation='Average'
    )   
    
    available_memo_max = max(data.average for data in available_memo.value[0].timeseries[0].data if data.average is not None)
    available_memo_min = min(data.average for data in available_memo.value[0].timeseries[0].data if data.average is not None)
    available_memo_max_in_gb = int(available_memo_max) / (1024 ** 3)
    available_memo_min_in_gb = int(available_memo_min) / (1024 ** 3)
    memo_min = total_memory_gb - available_memo_max_in_gb
    memo_max = total_memory_gb - available_memo_min_in_gb


    # print(f"{memo_max} is {(memo_max / total_memory_gb) * 100}% in {total_memory_gb} GB")
    # print(f"{memo_min} is {(memo_min / total_memory_gb) * 100}% in {total_memory_gb} GB")
    return memo_min, memo_max, (memo_max / total_memory_gb) * 100, (memo_min / total_memory_gb) * 100

def get_cpu(monitor_client: MonitorManagementClient,
            subscription_id: str,
            resource_group_name: str,
            vm_name: str,
            total_vcpus: int,):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)

    precentage_cpu = monitor_client.metrics.list(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
        timespan=f"{start_time}/{end_time}",
        interval="PT1H",
        metricnames="Percentage CPU",
        aggregation="Average",
    )
    precentage_cpu_max = max(data.average for data in precentage_cpu.value[0].timeseries[0].data if data.average is not None)
    precentage_cpu_min = min(data.average for data in precentage_cpu.value[0].timeseries[0].data if data.average is not None)
    cpu_min = (precentage_cpu_min / 100) * total_vcpus
    cpu_max = (precentage_cpu_max / 100) * total_vcpus

    return cpu_min, cpu_max, precentage_cpu_min, precentage_cpu_max


def get_vm_metrics(monitor_client: MonitorManagementClient, 
                   subscription_id: str, 
                   resource_group_name: str, 
                   vm_name: str, 
                   vm_size: str):
    instance_details = instance_sizes.get(vm_size, {})
    total_vcpus = instance_details.get("vCPUs")
    total_memory_gb = instance_details.get("memoryMB") / 1024

    memo_min, memo_max, available_memo_max, available_memo_min = get_memo(monitor_client, subscription_id, resource_group_name, vm_name, total_memory_gb)
    available_memo_avg = (available_memo_max + available_memo_min) / 2
    cpu_min, cpu_max, precentage_cpu_min, precentage_cpu_max = get_cpu(monitor_client, subscription_id, resource_group_name, vm_name, total_vcpus)
    precentage_cpu_avg = (precentage_cpu_min + precentage_cpu_max) / 2

    metrics_result = {
        "CPU": f"{total_vcpus} cores",
        "CPU_min": f"{precentage_cpu_min:.2f}% ({cpu_min:.2f} cores)",
        "CPU_max": f"{precentage_cpu_max:.2f}% ({cpu_max:.2f} cores)",
        "CPU_avg": f"{precentage_cpu_avg:.2f}% ({(cpu_max + cpu_min) / 2:.2f} cores)",

        "Mem": f"{total_memory_gb} GB",
        "Mem_min": f"{available_memo_min:.2f}% ({memo_min:.2f} GB)",
        "Mem_max": f"{available_memo_max:.2f}% ({memo_max:.2f} GB)",
        "Mem_avg": f"{available_memo_avg:.2f}% ({(memo_max + memo_min) / 2:.2f} GB)",
    }

    return metrics_result




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
