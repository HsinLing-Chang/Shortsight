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
    referer = request.headers.get("referer")
    print(f"referer: {referer}")
    if referer is None:
        return "Direct"
    elif "google.com" in referer:
        return "Google"
    elif "linkedin.com" in referer:
        return "Linkedin"
    elif "instagram.com" in referer:
        return "Instagram"
    elif "facebook.com" in referer:
        return "Facebook"
    elif "t.co" in referer:
        return "X"
    elif "ppluchuli.com" in referer:
        return "Shortsight"
    else:
        return "Other"


def get_client_device(request: Request):
    ua = request.headers.get("user-agent")
    print(ua)
    user_agent = parse(ua)
    print(user_agent)
    ua = ua.lower()
    isBot = is_custom_bot(ua)
    device_type = (
        "Bot" if user_agent.is_bot or isBot else
        "Desktop" if user_agent.is_pc else
        "Mobile" if user_agent.is_mobile else
        "Tablet" if user_agent.is_tablet else
        "Other"
    )
    device_browser = user_agent.browser.family
    device_os = user_agent.os.family

    if isBot:
        app_source = "Bot"
    elif "fbav" in ua or "fban" in ua or "facebook" in ua:
        app_source = "Facebook"
    elif "instagram" in ua:
        app_source = "Instagram"
    elif "line" in ua:
        app_source = "LINE"
    elif "micromessenger" in ua:
        app_source = "WeChat"
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


def is_custom_bot(ua: str):
    custom_bot_keywords = ["python-requests", "curl", "wget",
                           "axios", "go-http-client", "postmanruntime", "java", "facebookexternalhit", "Twitterbot", "Applebot", "LinkedInBot"]
    return any(keyword in ua for keyword in custom_bot_keywords)
