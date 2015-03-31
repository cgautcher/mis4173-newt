#!/bin/bash
# Purpose: generate config_details data
#
# Author: Chris G.
# Date: 03/30/2015
#
## Start ##

random_choice() {
    field_separator=" "
    the_choice=$(echo $@ | awk -v field=$(($RANDOM % $(echo $@ | awk -F"$field_separator" '{print NF}') + 1)) -F"$field_separator" '{print $field}')
    echo $the_choice
}


os_type_version=("'Windows Server','2012 R2'")
os_type_version+=("'Windows Server','2012'")
os_type_version+=("'Windows Server','2008 R2 SP1'")
os_type_version+=("'Windows Server','2008'")
os_type_version+=("'Windows Server','2003 R2 SP2'")
os_type_version+=("'Linux - Redhat', '5.4'")
os_type_version+=("'Linux - Redhat', '5.5'")
os_type_version+=("'Linux - Redhat', '5.6'")
os_type_version+=("'Linux - Redhat', '6.4'")
os_type_version+=("'Linux - Redhat', '6.5'")
os_type_version+=("'Linux - SuSE', '11 SP3'")
os_type_version+=("'Linux - SuSE', '12 SP1'")
os_type_version+=("'Linux - SuSE', '11 SP4'")
os_type_version+=("'Linux - Oracle', '5.9'")
os_type_version+=("'Linux - Oracle', '6.5'")
os_type_version+=("'Linux - Oracle', '6.4'")
os_type_version+=("'Oracle VM', '3.1'")
os_type_version+=("'Oracle VM', '3.2.8'")
os_type_version+=("'Oracle VM', '3.3.2'")
os_type_version+=("'VMware vSphere', '5.0u3'")
os_type_version+=("'VMware vSphere', '5.5'")
os_type_version+=("'VMware vSphere', '5.5u2'")
os_type_version+=("'VMware vSphere', '5.5u1'")
os_type_version+=("'VMware vSphere', '5.1u2'")
os_type_version+=("'VMware vSphere', '5.1u1'")
os_type_version+=("'VMware vSphere', '5.5u1'")
os_type_version+=("'VMware vSphere', '5.0u1'")
os_type_version+=("'Solaris', '10 - update 10'")
os_type_version+=("'Solaris', '11u1'")
os_type_version+=("'Solaris', '11.1'")
os_type_version+=("'AIX', '5.3 TL12 SP8'")
os_type_version+=("'AIX', '6.1 TL8 SP11'")
os_type_version+=("'HP-UX', '11.31'")

adapter_info=("'Cisco', 'v1240', '2.2(2e)', '2.2(2e)'")
adapter_info+=("'Cisco', '1280', '2.3(2)', '2.3(2)'")
adapter_info+=("'Cisco', '1340', '2.4.2', '2.4.2'")
adapter_info+=("'Brocade', '425', '3.3.2.1', '3.3.2.1'")
adapter_info+=("'Brocade', '804', '3.2.2.0', '3.2.2.0'")
adapter_info+=("'Brocade', '825', '3.1.1.2', 'w/driver'")
adapter_info+=("'Brocade', '815', '3.3.2.0 (inbox)', '3.3.2.0 (w/driver)'")
adapter_info+=("'Emulex', '554FLB', '10.4.222.101', '4.8.122f'")
adapter_info+=("'Emulex', 'LPe-12002', '8.4.482.4', '4.552.22ea'")
adapter_info+=("'Emulex', 'LPe-1105-HP', '8.71.322.4', '4.88.122.4b'")
adapter_info+=("'QLogic', 'QLA2432', 'qla2xxx 8.05.07.88k', '5.0.53'")
adapter_info+=("'QLogic', 'QLE2562', 'qla2xxx 8.07.18.52-2k', '7.0.3'")
adapter_info+=("'QLogic', 'QMH4062', '4.4.46.82', '5.0.45'")
adapter_info+=("'QLogic', 'QMH2562', 'qla2xxx 8.07.18.52-2k', '7.0.3'")
adapter_info+=("'QLogic', 'QMI2592', '934.0.35-vmw', '7.00.3'")
adapter_info+=("'QLogic', 'QLE8242', '1.1.29.0', '7.0.2'")
adapter_info+=("'Broadcom', '57800', '2.4.2e', '7.10.18'")
adapter_info+=("'Broadcom', '57710', '2.22.4f', '5.6.14'")
adapter_info+=("'Broadcom', '57840', '4.56.32f', 'w/driver'")
adapter_info+=("'Intel', 'T540', '9.11.1.4', '4.3.2.1'")

ontap_version=("'8.1.4p2'")
ontap_version+=("'8.1.4p4'")
ontap_version+=("'8.2.1p3'")
ontap_version+=("'8.2.1p1'")
ontap_version+=("'8.2.2p2'")
ontap_version+=("'8.2.3p1'")
ontap_version+=("'8.3'")
ontap_version+=("'8.3p1'")
ontap_version+=("'8.3p2'")


for x in $(seq 200); do
    echo "INSERT INTO objects_configdetails (os_type,os_version,storage_adapter_vendor,storage_adapter_model,storage_adapter_driver,storage_adapter_firmware,data_ontap_version) VALUES (${os_type_version[$(random_choice $(seq 0 $((${#os_type_version[@]}-1))))]}, ${adapter_info[$(random_choice $(seq 0 $((${#adapter_info[@]}-1))))]}, ${ontap_version[$(random_choice $(seq 0 $((${#ontap_version[@]}-1))))]});"
done

## End ##
