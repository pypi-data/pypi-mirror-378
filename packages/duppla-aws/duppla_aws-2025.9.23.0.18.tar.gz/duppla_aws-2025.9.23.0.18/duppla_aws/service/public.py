import boto3
from types_boto3_amplify import AmplifyClient
from types_boto3_cloudwatch import CloudWatchClient
from types_boto3_cloudformation import CloudFormationServiceResource
from duppla_aws.service._cloudwatchlog import AWSLogClient
from duppla_aws.service._dynamodb import DynamoDBResource
from duppla_aws.service._s3 import S3Resource
from duppla_aws.service._ses import SESResource
from duppla_aws.service._sns import SNSResource


class AmazonWebServices:
    def __init__(
        self, aws_access_key_id: str, aws_secret: str, aws_region: str = "us-east-1"
    ) -> None:
        _session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
        )

        self.s3 = S3Resource(resource=_session.resource("s3"))
        """The connection to the S3 bucket service"""
        self.dynamo = DynamoDBResource(resource=_session.resource("dynamodb"))
        """The connection to the DynamoDB service"""
        DynamoDBResource._upload_and_insert.f_put_object = self.s3.put_object  # pyright: ignore[reportPrivateUsage, reportFunctionMemberAccess]
        self.cloudformation: CloudFormationServiceResource = _session.resource("cloudformation")
        """The connection to the CloudFormation service"""
        self.cloudwatch: CloudWatchClient = _session.client("cloudwatch")
        """The connection to the CloudWatch service"""
        self.awslogs: AWSLogClient = AWSLogClient(client=_session.client("logs"))
        """The connection to the CloudWatch Logs service"""
        self.amplify: AmplifyClient = _session.client("amplify")
        """The connection to the Amplify service"""
        self.sns = SNSResource(client=_session.client("sns"))
        """The connection to the SNS service"""
        self.ses = SESResource(client=_session.client("ses"))
        """The connection to the SES service"""

        self._session = _session
        """The boto3 session object, for custom use"""
