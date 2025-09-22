import random

WINDOWS = {
    "platform": "Windows NT 10.0; Win64; x64",
    "versions": ["126.0.0.0", "125.0.0.0", "124.0.0.0"],
    "platformVersion": '"15.0.0"',
}
MAC = {
    "platform": "Macintosh; Intel Mac OS X 10_15_7",
    "versions": ["126.0.0.0", "125.0.0.0", "124.0.0.0"],
    "platformVersion": '"15.7.9"',
}


def random_user_agent():
    os = random.choice([WINDOWS, MAC])
    version = random.choice(os["versions"])
    major = version.split(".")[0]
    user_agent = f"Mozilla/5.0 ({os['platform']}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    brands = [
        '"Not/A)Brand";v="8"',
        f'"Chromium";v="{major}"',
        f'"Google Chrome";v="{major}"',
    ]
    return {
        "userAgent": user_agent,
        "secChUa": ", ".join(brands),
        "secChUaFullVersionList": ", ".join([b.replace('"', '"').replace(";v=\"", ";v=\"") for b in brands]),
        "secChUaPlatform": '"Windows"' if os is WINDOWS else '"macOS"',
        "secChUaPlatformVersion": os["platformVersion"],
    }
