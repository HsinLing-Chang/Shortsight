from fastapi import Request
from user_agents import parse
from urllib.parse import urlparse, parse_qs
# from device_detector import DeviceDetector

GA_SOURCE_CATEGORIES = {
    "google.com":      ("google", "organic", "Organic Search"),
    "bing.com":        ("bing", "organic", "Organic Search"),
    "baidu.com":       ("baidu", "organic", "Organic Search"),
    "yahoo.com":       ("yahoo", "organic", "Organic Search"),
    "facebook.com":    ("facebook", "referral", "Organic Social"),
    "instagram.com":   ("instagram", "referral", "Organic Social"),
    "linkedin.com":    ("linkedin", "referral", "Organic Social"),
    "youtube.com":     ("youtube", "referral", "Organic Video"),
    "vimeo.com":       ("vimeo", "referral", "Organic Video"),
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
        if domain.startswith("www."):
            domain = domain[4:]

    parsed_source = utm_source or None
    parsed_medium = utm_medium or None
    parsed_campaign = utm_campaign or None

    if utm_source or utm_medium:
        return {
            "domain": domain,
            "source": parsed_source or "(direct)",
            "medium": parsed_medium or "(none)",
            "channel": "Paid" if parsed_medium in ["cpc", "banner"] else "Referral",
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
