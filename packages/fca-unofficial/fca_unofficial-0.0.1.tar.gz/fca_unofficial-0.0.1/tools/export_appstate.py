import json
from python_facebookapi import login

if __name__ == "__main__":
    import os
    email = os.getenv("FB_EMAIL") or input("Email: ")
    password = os.getenv("FB_PASSWORD") or input("Password: ")
    twofa_env = os.getenv("FB_2FA")
    def prompt_2fa():
        code = twofa_env or input("2FA code (if requested): ")
        return code.strip().replace(" ", "")
    try:
        api = login({
            "email": email,
            "password": password,
            # Optional: provide a static code via env or a callback for interactive prompt
            "twoFactorCode": twofa_env,
            "getTwoFactorCode": prompt_2fa,
        })
        print("Logged in as:", api.get_current_user_id())
        path = api.save_app_state("appstate.json")
        print("Saved app state:", path)
    except Exception as e:
        print("Login failed:", e)
        print("Tip: set FB_2FA env var or enter the code when prompted if 2FA is required.")
