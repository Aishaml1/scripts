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

main()