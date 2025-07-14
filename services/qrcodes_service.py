import qrcode
import io
from fastapi import status, HTTPException


def create_qrcode_image(uuid):
    try:
        url = f"https://s.ppluchuli.com/qr/{uuid}"
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
