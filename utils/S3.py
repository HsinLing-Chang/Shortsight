import io
from PIL import Image
import boto3
import os
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
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

    def buffer_close(self, buffer):
        try:
            buffer.close()
        except:
            pass

    async def download_qrcode(self, uuid, format):

        format = format.lower()
        key = f"qrcodes/{uuid}.PNG"
        try:
            s3_obj = self.client.get_object(Bucket=self.bucket, Key=key)
            image_bytes = s3_obj["Body"].read()
        except Exception as e:
            raise Exception(f"無法從 S3 取得圖片: {e}")
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        output = io.BytesIO()
        if format == "jpg":
            format = "jpeg"
        image.save(output, format=format.upper())
        output.seek(0)

        return StreamingResponse(
            output,
            media_type=f"image/{format}",
            headers={
                "Content-Disposition": f'attachment; filename="{uuid}.{format}"'
            },
            background=BackgroundTask(self.buffer_close, output)
        )

        # url = self.client.generate_presigned_url(
        #     ClientMethod='get_object',
        #     Params={
        #         'Bucket':  self.bucket,
        #         'Key': key,
        #         'ResponseContentDisposition': f'attachment; filename="{uuid}.PNG"'
        #     },
        #     ExpiresIn=300  # 有效時間（秒）：5 分鐘
        # )
        # print(url)
        # return url


aws_s3 = S3_handler()
