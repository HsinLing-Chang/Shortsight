from fastapi import Request
from user_agents import parse
# from device_detector import DeviceDetector


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        print(x_forwarded_for)
        return x_forwarded_for.split(",")[0].strip()

    return request.client.host


def get_client_referer(request: Request):
    referer = request.headers.get("referer") or "Direct"
    return referer


def get_client_device(request: Request):
    ua = request.headers.get("user-agent")
    print(ua)
    user_agent = parse(ua)
    print(user_agent)
    device_type = (
        "Bot" if user_agent.is_bot else
        "Desktop" if user_agent.is_pc else
        "Mobile" if user_agent.is_mobile else
        "Tablet" if user_agent.is_tablet else
        "Other"
    )
    device_browser = user_agent.browser.family
    device_os = user_agent.os.family
    if "line" in ua:
        app_source = "LINE"
    elif "instagram" in ua:
        app_source = "Instagram"
    elif "fbav" in ua or "fban" in ua or "facebook" in ua:
        app_source = "Facebook"
    elif "micromessenger" in ua:
        app_source = "WeChat"
    elif "tiktok" in ua:
        app_source = "TikTok"
    else:
        app_source = "Browser"

    result = {
        "device_browser": device_browser,
        "device_os": device_os,
        "device_type": device_type,
        "app_source": app_source,
    }
    print(result)
    return result
