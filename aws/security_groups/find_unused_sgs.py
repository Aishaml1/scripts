import boto3
import botocore
import json
import argparse

REGION = ["us-east-1" ,"us-west-1", "us-west-2" "us-east-2"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--dryrun', dest='debug', action='store_true')
    parser.add_argument('-f', '--filename', dest='filename', required=True)
    args = parser.parse_args()

    with open(args.filename) as data_file:
        data = json.load(data_file)

        find_eni_with_sg(data)
        find_rds_with_sg(data)
        find_lb_with_sg(data)

def find_eni_with_sg(data):
    print(f"\nFinding associated ENI's......\n")
    for region in data:
        sg_list = data[region]
        ec2 = boto3.client('ec2', region_name=region)
        for sg_id in sg_list:
            eni_response = ec2.describe_network_interfaces(
                Filters=[{
                    'Name': 'group-id',
                    'Values': [sg_id]}]
                )
            enis = eni_response['NetworkInterfaces']
        if len(enis) > 0:
            print(f"Security Group {sg_id} has associated ENIs:")
            for eni in enis:
                print(f" - ENI ID: {eni['NetworkInterfaceId']}")
            print("------------------------------")
        else:
            print(f"Security Group {sg_id} has no associated ENIs.")
            print("------------------------------")

def find_rds_with_sg(data):
    print(f"\nFinding associated RDS Instances....\n")
    print('                                     ')
    for region in data:
        sg_list = data[region]
        rds = boto3.client('rds', region_name=region)
        for sg_id in sg_list:
            rds_response = rds.describe_db_instances()
            rds_instances = rds_response['DBInstances']
            associated = False
            for rds_instance in rds_instances:
                vpc_security_groups = rds_instance.get('VpcSecurityGroups', [])
                for sg in vpc_security_groups:
                    if sg['VpcSecurityGroupId'] == sg_id:
                        print(f"Security Group {sg_id} is associated with RDS instance {rds_instance['DBInstanceIdentifier']}")
                        print("-------------------------------------------")
                        associated = True
                        break
            if not associated:
                print(f"Security Group {sg_id} is not associated with any RDS instances.")
                print("------------------------------")

def find_lb_with_sg(data):
    print(f"\nFinding associated Load Balancers....\n")
    print('                                     ')
    for region in data:
        sg_list = data[region]
        elbv2 = boto3.client('elbv2', region_name=region)
        for sg_id in sg_list:
            response = elbv2.describe_load_balancers()
            lbs = response['LoadBalancers']
            associated = False
            for lb in lbs:
                lb_security_groups = lb.get('SecurityGroups', [])
                if sg_id in lb_security_groups:
                    print(f'Security Group {sg_id} is associated with Load Balancer {lb["LoadBalancerName"]}')
                    print("------------------------------")
                    associated = True
            if not associated:
                print(f'Security Group {sg_id} is not associated with any Load Balancers')
                print("------------------------------")
main()