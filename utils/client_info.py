from fastapi import Request
from user_agents import parse
from urllib.parse import urlparse, parse_qs
# from device_detector import DeviceDetector

GA_SOURCE_CATEGORIES = {
    "google.com":      ("google", "organic", "Search Engine"),
    "bing.com":        ("bing", "organic", "Search Engine"),
    "yahoo.com":       ("yahoo", "organic", "Search Engine"),
    "facebook.com":    ("facebook", "referral", "Social Site"),
    "instagram.com":   ("instagram", "referral", "Social Site"),
    "linkedin.com":    ("linkedin", "referral", "Social Site"),
    "youtube.com":     ("youtube", "referral", "Video Site"),
    "vimeo.com":       ("vimeo", "referral", "Video Site"),
    "ppluchuli.com":   ("shortsight", "referral", "Referral"),
}


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        print(x_forwarded_for)
        return x_forwarded_for.split(",")[0].strip()

    return request.client.host


def get_client_referer(request: Request):
    referer = request.headers.get("referer")
    if not referer:
        return {
            "domain": None,
            "source": "(direct)",
            "medium": "none",
            "channel": "Direct"
        }, referer
    parsed = urlparse(referer)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    for known_domain, (source, medium, channel) in GA_SOURCE_CATEGORIES.items():
        if known_domain in domain:
            return {
                "domain": domain,
                "source": source,
                "medium": medium,
                "channel": channel
            }, referer

    return {
        "domain": domain,
        "source": domain,
        "medium": "referral",
        "channel": "Referral"
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
