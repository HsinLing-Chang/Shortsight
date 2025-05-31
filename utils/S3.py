import boto3
import os
from dotenv import load_dotenv
load_dotenv()


class S3_handler():
    def __init__(self):
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = "ap-northeast-1"
        self.client = boto3.client(
            "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret, region_name=region)
        self.bucket = os.getenv("BUCKET_NAME")
        self.cloudfront_domain = "dcymcz24d7wyx.cloudfront.net"

    def __CDN_URL(self, url):
        cdn_url = f"https://{self.cloudfront_domain}/{url}"
        return cdn_url

    async def upload_qrcode(self, key, image_data, content_type: str = "image/png"):
        try:
            file_path = f"qrcodes/{key}.PNG"
            self.client.put_object(
                Bucket=self.bucket,
                Key=file_path,
                Body=image_data,
                ContentType=content_type,
            )
            print("上傳成功")
            return self.__CDN_URL(file_path)
        except Exception as e:
            print(f"上傳失敗{e}")
            raise e

    async def delete_qrcode(self, key):
        file_path = f"qrcodes/{key}.PNG"
        self.client.delete_object(
            Bucket=self.bucket,
            Key=file_path,
        )


aws_s3 = S3_handler()
