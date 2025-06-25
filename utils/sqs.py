import boto3
import json
import os
from dotenv import load_dotenv
load_dotenv()


# message_body = {
#     "mapping_id": 1,
#     "visitor_id": "test-visitor-abc",
#     "event_type": "click",
#     "referer": "https://test.com",
#     "ip_address": "1.2.3.4",
#     "device_type": "Mobile",
#     "device_browser": "Chrome",
#     "device_os": "Android",
#     "app_source": "Browser",
#     "domain": "test.com",
#     "source": "discord",
#     "medium": "social",
#     "campaign": "test-campaign",
#     "channel": "Organic Social"
# }


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

        # response = self.sqs.send_message(
        #     QueueUrl=self.q_uerl,
        #     MessageBody=json.dumps(message_body)
        # )
        # print(response)

    def sqs_send_message(self, event_data):
        response = self.sqs.send_message(
            QueueUrl=self.q_uerl,
            MessageBody=json.dumps(event_data)
        )
        print(response)


sqs = SqsHandler()
