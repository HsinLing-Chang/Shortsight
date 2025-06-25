import boto3
import json
import os
from dotenv import load_dotenv
load_dotenv()


class SqsHandler():
    def __init__(self):
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = "ap-northeast-1"
        self.q_uerl = os.getenv("QUEUE_URL")
        self.sqs = boto3.client(
            "sqs",
            region_name=region,
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret
        )

    def sqs_send_message(self, event_data):
        response = self.sqs.send_message(
            QueueUrl=self.q_uerl,
            MessageBody=json.dumps(event_data)
        )
        print(response)


sqs = SqsHandler()
