import boto3
from aws_config import AwsConfig
from aws_config import OrcaConfig


class AwsServiceAppAutoscaling(object):
    '''
    The class provides a simpler abstraction to the AWS boto3
    Autoscaling client interface
    '''
    def __init__(self,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None):
        """
        Create a Autoscaling service client to one ore more environments
        by name.
        """
        service = 'application-autoscaling'

        orca_config = OrcaConfig()
        self.regions = orca_config.get_regions()
        self.clients = {}

        if profile_names is not None:
            for profile_name in profile_names:
                session = boto3.Session(profile_name=profile_name)
                self.clients[profile_name] = session.client(service)
        elif access_key_id is not None and secret_access_key is not None:
            self.clients['default'] = boto3.client(
                service,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key)
        else:
            awsconfig = AwsConfig()
            profiles = awsconfig.get_profiles()

            for profile in profiles:
                session = boto3.Session(profile_name=profile)
                self.clients[profile] = {}
                for region in self.regions:
                    self.clients[profile][region] = \
                        session.client(service, region_name=region)

    def list_scaling_policies(self, service, profile_names=None, regions=None):
        """List Application scaling policies.

        :param service: AWS Service Namespace (ec2, etc.)

        """
        scaling_policies = list()
        for profile in self.clients.keys():
            if profile_names is not None and profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and region not in regions:
                    continue

                client = self.clients[profile][region]
                policies = client.describe_scaling_policies(
                    ServiceNamespace=service)

                for policy in policies['ScalingPolicies']:
                    policy['region'] = region
                    policy['profile_name'] = profile
                    scaling_policies.append(policy)

        return scaling_policies
