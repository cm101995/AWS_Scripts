import boto3
import gzip
from itertools import islice
import json
from flowlogs_reader import FlowRecord, FlowLogsReader


s3 = boto3.client('s3')
sqs = boto3.client('sqs')


# reading from s3 event notification & decoding the log gz file
def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = gzip.decompress(obj['Body'].read())
        lines = body.decode('UTF-8').splitlines()

        # removing the first line in the logfile and converting the log to json format
        for line in islice(lines, 1, None):
            flow_record = FlowRecord.from_cwl_event({'message': line[:]})
            actual = FlowRecord.to_dict(flow_record)
            json_object = json.dumps(actual, indent=4, sort_keys=True, default=str)

            # sending the output to SQS
            response = sqs.send_message(QueueUrl="REPLACE_WITH_SQS_URL",
                                        MessageBody=json_object)