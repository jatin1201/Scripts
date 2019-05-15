#!/usr/bin/env python
import boto3
import argparse


def lookup_by_id(sgid):
    sg = ec2.get_all_security_groups(group_ids=sgid)
    return sg[0].name


# get a full list of the available regions
client = boto3.client('ec2')
regions_dict = client.describe_regions()
region_list = [region['RegionName'] for region in regions_dict['Regions']]

# parse arguments
parser = argparse.ArgumentParser(description="Show unused security groups")
parser.add_argument("-r", "--region", type=str, default="us-east-1",
                    help="The default region is us-east-1. The list of available regions are as follows: %s" % sorted(
                        region_list))
parser.add_argument("-d", "--delete", help="delete security groups from AWS", action="store_true")
args = parser.parse_args()

ec2 = boto3.resource('ec2')
all_groups = []
security_groups_in_use = []
# Get ALL security groups names
security_groups_dict = client.describe_security_groups()
security_groups = security_groups_dict['SecurityGroups']
for groupobj in security_groups:
    if groupobj['GroupName'] == 'default':
        security_groups_in_use.append(groupobj['GroupId'])
    all_groups.append(groupobj['GroupId'])

# Get all security groups used by instances
instances_dict = client.describe_instances()
reservations = instances_dict['Reservations']
network_interface_count = 0

for i in reservations:
    for j in i['Instances']:
        for k in j['SecurityGroups']:
            if k['GroupId'] not in security_groups_in_use:
                security_groups_in_use.append(k['GroupId'])

# Security groups used by RDS
rds_client = boto3.client('rds')
rds_dict = rds_client.describe_db_security_groups()

for i in rds_dict['DBSecurityGroups']:
    for j in i['EC2SecurityGroups']:
        if j not in security_groups_in_use:
            security_groups_in_use.append(j)

# Security groups used by VPCs
vpc_dict = client.describe_vpcs()
for i in vpc_dict['Vpcs']:
    vpc_id = i['VpcId']
    vpc = ec2.Vpc(vpc_id)
    for s in vpc.security_groups.all():
        if s.group_id not in security_groups_in_use:
            security_groups_in_use.append(s.group_id)