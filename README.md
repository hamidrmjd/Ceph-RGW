# Ceph-RGW
We have a Ceph Cluster whose goal is to use it for Object Storage via RGW (Rados Gateway). The cluster consists of 20 Gen10 DL380 HP servers and each server contains 8x 20TB SAS 10K and 4x 4TB PM 1643 SAMSUNG. The total HDD pool capacity is 3.2 PB and 80 TB of SSDs. Each server contains a 1x25G Mullanux FLR card and a 1x25G Mellanux PCIe4 card. Core Switches are embedded 2x Cisco 9k Switches and vPC is completely considered. 
Cluster state:

![ceph df](https://github.com/hamidrmjd/Ceph-RGW/assets/109296831/668ab9fb-57d6-4ae9-b7f0-021b6a5288f0)


S3.Hot pool are used for Hot data (last 4 days writes) and S3.Cold used for cold storage.
For the benchmarking cluster, we used Gosbench tool (thanks to https://github.com/mulbc/gosbench.git). HDD and SSD pools were created by default configurations for the first try and the results was like the below:
