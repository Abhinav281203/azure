import json
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
import config

tenant_id = config.AZURE_TENANT_ID
client_id = config.AZURE_CLIENT_ID
client_secret = config.AZURE_CLIENT_SECRET_VALUE
subscription_id = config.AZURE_SUBSCRIPTION_ID

credential = ClientSecretCredential(tenant_id, client_id, client_secret)
compute_client = ComputeManagementClient(credential, subscription_id)
resource_client = ResourceManagementClient(credential, subscription_id)

vm_sizes_memory = {}

resource_groups = resource_client.resource_groups.list()

for resource in resource_groups:
    vm_sizes = compute_client.virtual_machine_sizes.list(location=resource.location)

    for size in vm_sizes:
        size_name = size.name
        vcpus = size.number_of_cores
        memory_mb = size.memory_in_mb

        if size_name in vm_sizes_memory:
            existing_vcpus = vm_sizes_memory[size_name]["vCPUs"]
            existing_memory = vm_sizes_memory[size_name]["memoryMB"]

            if existing_vcpus == vcpus and existing_memory == memory_mb:
                print(f"Continuing for {size_name}: same vCPUs and memory found.")
                continue
            else:
                print(f"Breaking for {size_name}: different vCPUs or memory found.")
                break

        vm_sizes_memory[size_name] = {
            "vCPUs": vcpus,
            "memoryMB": memory_mb
        }

with open('instance_details.json', 'w') as json_file:
    json.dump(vm_sizes_memory, json_file, indent=4)

print("Saved to 'azure_vm_sizes_memory.json'")
