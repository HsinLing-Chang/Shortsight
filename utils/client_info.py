from fastapi import Request
from user_agents import parse
from urllib.parse import urlparse, parse_qs
# from device_detector import DeviceDetector

GA_SOURCE_CATEGORIES = {
    "com.linkedin.android": ("linkedin", "referral", "Organic Social"),
    "linkedin":    ("linkedin", "referral", "Organic Social"),
    "com.facebook.katana": ("facebook", "referral", "Organic Social"),
    "facebook":    ("facebook", "referral", "Organic Social"),
    "t.co":        ("Twitter", "referral", "Organic Social"),
    "google":      ("google", "organic", "Organic Search"),
    "bing":        ("bing", "organic", "Organic Search"),
    "baidu":       ("baidu", "organic", "Organic Search"),
    "yahoo":       ("yahoo", "organic", "Organic Search"),
    "instagram":   ("instagram", "referral", "Organic Social"),
    "youtube":     ("youtube", "referral", "Organic Video"),
    "vimeo":       ("vimeo", "referral", "Organic Video"),
    "s.ppluchuli.com":   ("shortsight", "referral", "Referral"),
}


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        print(x_forwarded_for)
        return x_forwarded_for.split(",")[0].strip()

    return request.client.host


def get_client_referer(request: Request, utm_source, utm_medium, utm_campaign):
    referer = request.headers.get("referer")
    domain = None

    if referer:
        parsed = urlparse(referer)
        domain = parsed.netloc.lower()

    parsed_source = utm_source or None
    parsed_medium = utm_medium or None
    parsed_campaign = utm_campaign or None

    if utm_source or utm_medium:
        return {
            "domain": domain,
            "source": parsed_source or "(direct)",
            "medium": parsed_medium or "(none)",
            "channel": "Referral",
            "campaign": parsed_campaign
        }, referer

    if not referer:  # 沒有referrer就歸類在direct
        return {
            "domain": None,
            "source": "(direct)",
            "medium": "(none)",
            "channel": "Direct",
            "campaign": None
        }, None

    for known_domain, (source, medium, channel) in GA_SOURCE_CATEGORIES.items():
        if known_domain in domain:
            return {
                "domain": domain,
                "source": source,
                "medium": medium,
                "channel": channel,
                "campaign": None
            }, referer
    # 有referrer但找不到
    return {
        "domain": domain,
        "source": domain,
        "medium": "referral",
        "channel": "Referral",
        "campaign": None
    }, referer


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
    elif "linkedin" in ua:
        app_source = "Linkedin"
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
                           "axios", "go-http-client", "postmanruntime", "java", "facebookexternalhit", "twitterbot", "applebot", "linkedinbot"]
    return any(keyword in ua for keyword in custom_bot_keywords)
