import pandas as pd

def format(vm_details_list, file_name):
    vm_details_list = sorted(vm_details_list, key=lambda x: x["VM_Name"])
    processed_data = []

    for details in vm_details_list:
        processed_data.append({
            "VM_name": details["VM_Name"],
            "Resource_Group": details["Resource_Group"],
            "Dependencies": "Virtual Machine",
            "Dependency_Count": 1,
            "Region": details["Region"],
            "VM_Size": details["VM_Size"],
            "OS_Type": details["OS_Type"],
            # "CPU_Min": details["CPU_Min"],
            # "CPU_Max": details["CPU_Max"],
            # "CPU_Avg": details["CPU_Avg"],
            # "Memory_Min": details["Memory_Min"],
            # "Memory_Max": details["Memory_Max"],
            # "Memory_Avg": details["Memory_Avg"],
            "OS_Disk_Name": None,
            "OS_Disk_Size": None,
            "OS_Disk_SKU": None,
            "Data_disk_name": None,
            "Data_disk_size": None,
            "Public_IP_address": None,
        })

        processed_data.append({
            "VM_name": details["VM_Name"],
            "Resource_Group": details["Resource_Group"],
            "Dependencies": "Disks",
            "Dependency_Count": 1,
            "Region": None,
            "VM_Size": None,
            "OS_Type": None,
            # "CPU_Min": None,
            # "CPU_Max": None,
            # "CPU_Avg": None,
            # "Memory_Min": None,
            # "Memory_Max": None,
            # "Memory_Avg": None,
            "OS_Disk_Name": details["OS_Disk_Name"],
            "OS_Disk_Size": details["OS_Disk_Size"],
            "OS_Disk_SKU": details["OS_Disk_SKU"],
            "Data_disk_name": details["Data_Disk_Names"],
            "Data_disk_size": details["Data_Disk_Sizes"],
            "Public_IP_address": None,
        })

        processed_data.append({
            "VM_name": details["VM_Name"],
            "Resource_Group": details["Resource_Group"],
            "Dependencies": "Network",
            "Dependency_Count": 1,
            "Region": None,
            "VM_Size": None,
            "OS_Type": None,
            # "CPU_Min": None,
            # "CPU_Max": None,
            # "CPU_Avg": None,
            # "Memory_Min": None,
            # "Memory_Max": None,
            # "Memory_Avg": None,
            "OS_Disk_Name": None,
            "OS_Disk_Size": None,
            "OS_Disk_SKU": None,
            "Data_disk_name": None,
            "Data_disk_size": None,
            "Public_IP_address": details["Public_IP_Address"],
        })

    df = pd.DataFrame(processed_data)
    df.to_excel(file_name, index=False, engine='openpyxl')

    print(f"Data exported to {file_name} successfully.")