from typing import Any, Callable, Dict, List, Optional, Tuple
from http.cookiejar import CookieJar
import requests
import re

from ...utils.logging import log, error as log_error
from ...utils.net import get_session, get, post
from .build_api import build_api


FB_BASE = "https://www.facebook.com"


async def login_helper(credentials: Dict[str, Any], global_options: Dict[str, Any], callback: Callable, set_options_func, build_api_func, initial_api: Optional[Any] = None) -> Any:
    try:
        sess = get_session()
        jar: requests.cookies.RequestsCookieJar = sess.cookies  # type: ignore
        log("Logging in... starting session and preparing cookies/credentials")

        app_state = credentials.get("appState")
        if app_state:
            cookie_strings: List[str] = []
            if isinstance(app_state, list):
                for c in app_state:
                    key = c.get("name") or c.get("key")
                    val = c.get("value")
                    if key and val:
                        cookie_strings.append(f"{key}={val}")
            elif isinstance(app_state, str):
                cookie_strings = [s.strip() for s in app_state.split(";") if s.strip()]
            else:
                raise ValueError("Invalid appState format. Provide array of cookie objects or a cookie string.")

            for cstr in cookie_strings:
                # set for both fb and messenger
                if "=" not in cstr:
                    continue
                name, val = cstr.split("=", 1)
                sess.cookies.set(name.strip(), val.strip(), domain=".facebook.com", path="/")
                sess.cookies.set(name.strip(), val.strip(), domain=".messenger.com", path="/")
        elif credentials.get("email") and credentials.get("password"):
            # Best-effort email/password login by emulating the web form
            email = credentials.get("email")
            password = credentials.get("password")
            # 1) Load login page to get hidden tokens
            login_url = FB_BASE + "/login/device-based/regular/login/?login_attempt=1&lwv=110"
            log("GET login page:", login_url)
            status_login, res_login = get(login_url, jar, None, global_options, None, {"noRef": True})
            log("Login page status:", status_login, "final url:", res_login.get("url"))
            if status_login < 200 or status_login >= 600:
                raise RuntimeError(f"Failed to GET login page. Status {status_login}")
            html = res_login.get("body", "")

            def _find(name: str):
                m = re.search(fr'name="{name}" value="([^"]+)"', html)
                return m.group(1) if m else None

            lsd = _find("lsd")
            jazoest = _find("jazoest")
            li = _find("li")
            m_ts = _find("m_ts")

            form = {
                "email": email,
                "pass": password,
                "lsd": lsd or "",
                "jazoest": jazoest or "",
                "li": li or "",
                "m_ts": m_ts or "",
                "try_number": "0",
                "unrecognized_tries": "0",
                "login": "Log In",
            }
            # 2) Submit credentials
            log("POST credentials to:", login_url)
            status_post, res_post = post(login_url, jar, form, global_options, None, {"Referer": FB_BASE + "/login/"})
            log("POST status:", status_post, "final url:", res_post.get("url"))
            if status_post < 200 or status_post >= 400:
                raise RuntimeError(f"Login POST failed with status {status_post}")
            # 3) Check cookies for c_user/xs (basic success indicator)
            has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
            has_xs = any(c.name == "xs" for c in jar)  # type: ignore
            if not (has_c_user and has_xs):
                # Look for checkpoint or 2FA hint and try to complete 2FA flow
                body_post = res_post.get("body", "")
                final_url = res_post.get("url", "")
                # Direct 2FA page flow (two_step_verification)
                if "two_step_verification" in final_url or "two_step_verification" in body_post:
                    log("Detected two_step_verification flow. Fetching 2FA page...")
                    # Load the 2FA form
                    status_tfa, res_tfa = get(final_url, jar, None, global_options, None, {"noRef": True})
                    log("2FA page status:", status_tfa, "url:", res_tfa.get("url"))
                    html_tfa = res_tfa.get("body", "")

                    # Gather hidden inputs
                    hidden: Dict[str, str] = {}
                    for m in re.finditer(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"', html_tfa):
                        hidden[m.group(1)] = m.group(2)
                    # Find submit buttons
                    submit_names: List[str] = []
                    try:
                        submit_names = [m.group(1) for m in re.finditer(r'name="submit\[([^\]]+)\]"', html_tfa)]
                    except Exception:
                        submit_names = []
                    # Find the code field name
                    code_name = None
                    for m in re.finditer(r'<input[^>]+name="([^"]+)"[^>]+', html_tfa):
                        nm = m.group(1)
                        if re.search(r"approvals?_code|twofactor|2fa|otp|auth|code", nm, re.I):
                            code_name = nm
                            break
                    if not code_name:
                        # Try legacy
                        code_name = "approvals_code"

                    # Try push-approval before asking for 2FA code (if enabled)
                    push_success = False
                    if global_options.get("pushApprove"):
                        import time as _time
                        log("Push-approve mode: trying to trigger device approval...")
                        push_form: Dict[str, Any] = {**hidden}
                        # Best-effort: try to pick an action that sends/approves notification
                        pref_push = [
                            "Send Notification",
                            "Approve login",
                            "Approve",
                            "This was me",
                            "Continue",
                            "Next",
                            "OK",
                        ]
                        chosen_push = next((s for s in pref_push if s in submit_names), (submit_names[0] if submit_names else None)) if submit_names else None
                        if chosen_push:
                            push_form[f"submit[{chosen_push}]"] = chosen_push
                        push_form.setdefault("save_device", "true")
                        push_form.setdefault("remember_device", "on")
                        status_push, res_push = post(final_url, jar, push_form, global_options, None, {"Referer": final_url})
                        log("Push-approve submit status:", status_push, "url:", res_push.get("url"))
                        # Poll a few endpoints to consolidate cookies while user approves on their device
                        wait_secs = int(global_options.get("pushApproveWaitSeconds", 90))
                        polls = max(1, wait_secs // 3)
                        for i in range(polls):
                            try:
                                s1, _ = get(FB_BASE, jar, None, global_options, None, {"noRef": True})
                                s2, _ = get("https://www.messenger.com/", jar, None, global_options, None, {"noRef": True})
                                s3, _ = get("https://m.facebook.com/", jar, None, global_options, None, {"noRef": True})
                                log(f"Waiting for device approval... ({i+1}/{polls}) statuses:", s1, s2, s3)
                            except Exception:
                                pass
                            has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
                            has_xs = any(c.name == "xs" for c in jar)  # type: ignore
                            if has_c_user and has_xs:
                                push_success = True
                                break
                            _time.sleep(3)

                        # If push didn't result in cookies, try to switch method to code automatically
                        if not push_success and not (any(c.name == "c_user" for c in jar) and any(c.name == "xs" for c in jar)):
                            log("Push approval not received in time. Trying alternate verification method (code)...")
                            # Try anchors like "Try another way", "Use a code generator", etc.
                            links = []
                            for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html_tfa, re.S | re.I):
                                href = m.group(1)
                                text = re.sub(r"<[^>]+>", "", m.group(2) or "").strip().lower()
                                links.append((href, text))
                            prefer_texts = [
                                "try another way",
                                "enter code",
                                "use code",
                                "code generator",
                                "text me a code",
                                "use a text message",
                                "didn't get a code",
                            ]
                            chosen_href = None
                            for href, text in links:
                                if any(p in text for p in prefer_texts):
                                    chosen_href = href
                                    break
                            if chosen_href:
                                if chosen_href.startswith("/"):
                                    chosen_href = FB_BASE + chosen_href
                                try:
                                    s_alt, r_alt = get(chosen_href, jar, None, global_options, None, {"noRef": True})
                                    log("Alternate method GET status:", s_alt, "url:", r_alt.get("url"))
                                    html_tfa = r_alt.get("body", html_tfa)
                                    # Rebuild hidden fields and submit names and code field
                                    hidden = {}
                                    for m in re.finditer(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"', html_tfa):
                                        hidden[m.group(1)] = m.group(2)
                                    submit_names = [m.group(1) for m in re.finditer(r'name="submit\[([^\]]+)\]"', html_tfa)]
                                    code_name = None
                                    for m in re.finditer(r'<input[^>]+name="([^"]+)"[^>]+', html_tfa):
                                        nm = m.group(1)
                                        if re.search(r"approvals?_code|twofactor|2fa|otp|auth|code", nm, re.I):
                                            code_name = nm
                                            break
                                    if not code_name:
                                        code_name = "approvals_code"
                                except Exception as _alt_ex:
                                    log("Alternate method navigation failed:", _alt_ex)
                            else:
                                # Some flows present a radio/selector for verification method; try to choose code/generator
                                try:
                                    method_inputs = [m.group(1) for m in re.finditer(r'name="(verification_method|approvals_method)"', html_tfa)]
                                    if method_inputs:
                                        method_name = method_inputs[0]
                                        form_alt = {**hidden}
                                        pref_vals = ["code", "generator", "auth_app", "sms"]
                                        # Try to find values from the html for these names
                                        value_match = None
                                        for val in pref_vals:
                                            if re.search(fr'value="{val}"', html_tfa, re.I):
                                                value_match = val
                                                break
                                        if value_match:
                                            form_alt[method_name] = value_match
                                            ch = next((s for s in ["Continue", "Next", "OK"] if s in submit_names), (submit_names[0] if submit_names else None))
                                            if ch:
                                                form_alt[f"submit[{ch}]"] = ch
                                            s_altp, r_altp = post(final_url, jar, form_alt, global_options, None, {"Referer": final_url})
                                            log("Alternate method POST status:", s_altp, "url:", r_altp.get("url"))
                                            html_tfa = r_altp.get("body", html_tfa)
                                            # Refresh hidden and code field
                                            hidden = {}
                                            for m in re.finditer(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"', html_tfa):
                                                hidden[m.group(1)] = m.group(2)
                                            submit_names = [m.group(1) for m in re.finditer(r'name="submit\[([^\]]+)\]"', html_tfa)]
                                            code_name = None
                                            for m in re.finditer(r'<input[^>]+name="([^"]+)"[^>]+', html_tfa):
                                                nm = m.group(1)
                                                if re.search(r"approvals?_code|twofactor|2fa|otp|auth|code", nm, re.I):
                                                    code_name = nm
                                                    break
                                            if not code_name:
                                                code_name = "approvals_code"
                                except Exception:
                                    pass

                    # Up to 3 attempts for 2FA in case of invalid code or extra steps
                    for attempt in range(3):
                        # If push approval already yielded session cookies, skip code prompt
                        if push_success or (any(c.name == "c_user" for c in jar) and any(c.name == "xs" for c in jar)):
                            break
                        # Ask for code
                        code = None
                        if credentials.get("twoFactorCode") and attempt == 0:
                            code = str(credentials.get("twoFactorCode")).strip().replace(" ", "")
                        elif callable(credentials.get("getTwoFactorCode")):
                            try:
                                code = str(credentials.get("getTwoFactorCode")()).strip().replace(" ", "")
                            except Exception:
                                code = None
                        else:
                            try:
                                code = input("Enter Facebook 2FA code: ").strip().replace(" ", "")
                            except Exception:
                                code = None
                        if not code:
                            raise RuntimeError("2FA required but no code provided. Pass twoFactorCode or getTwoFactorCode in credentials.")

                        form_tfa: Dict[str, Any] = {**hidden}
                        form_tfa[code_name] = code
                        # Best-effort trust device flags
                        form_tfa.setdefault("save_device", "true")
                        form_tfa.setdefault("remember_device", "on")

                        # Submit to same URL (most flows accept POST to same path)
                        log("Submitting 2FA code on two_step_verification page...")
                        preferred = ["Continue", "Save Device", "Trust", "Approve", "Next", "OK", "Confirm"]
                        chosen = next((s for s in preferred if s in submit_names), (submit_names[0] if submit_names else None)) if submit_names else None
                        if chosen:
                            form_tfa[f"submit[{chosen}]"] = chosen
                        status_tfa_post, res_tfa_post = post(final_url, jar, form_tfa, global_options, None, {"Referer": final_url})
                        log("2FA submit status:", status_tfa_post, "url:", res_tfa_post.get("url"))

                        # After submitting code, try typical follow-ups via checkpoint/async
                        html_after = res_tfa_post.get("body", "")
                        # If page still asks for code or shows invalid message, retry loop
                        if re.search(r"incorrect|invalid|try again|didn't match", html_after, re.I):
                            log("2FA code appears invalid or not accepted; retrying...")
                            continue

                        # Extract tokens and try to press Save Device/Continue if present
                        def _extract_tokens2(html_any: str):
                            def _f(name: str):
                                m = re.search(fr'name="{name}" value="([^"]+)"', html_any)
                                return m.group(1) if m else None
                            fb = _f("fb_dtsg") or _f("fb_dtsg_ag")
                            jz = _f("jazoest")
                            nh = _f("nh")
                            submits2 = [m.group(1) for m in re.finditer(r'name="submit\[([^\]]+)\]"', html_any)]
                            return fb, jz, nh, submits2

                        fb2, jz2, nh2, submits2 = _extract_tokens2(html_after)
                        if fb2 or jz2 or nh2 or submits2:
                            follow_form = {k: v for k, v in {"fb_dtsg": fb2, "jazoest": jz2, "nh": nh2}.items() if v}
                            pref2 = ["Save Device", "Continue", "Yes", "This was me", "Approve", "Next", "OK"]
                            chosen2 = next((s for s in pref2 if s in submits2), (submits2[0] if submits2 else None))
                            if chosen2:
                                follow_form[f"submit[{chosen2}]"] = chosen2
                                log(f"Submitting follow-up checkpoint action: {chosen2}")
                                status_follow, res_follow = post("https://www.facebook.com/checkpoint/async/", jar, follow_form, global_options, None, {"Referer": res_tfa_post.get("url", final_url) or final_url})
                                log("Follow-up submit status:", status_follow, "url:", res_follow.get("url"))

                        # Force-load home to trigger cookie consolidation and re-check cookies
                        status_home, res_home = get(FB_BASE, jar, None, global_options, None, {"noRef": True})
                        log("Post-2FA home status:", status_home, "url:", res_home.get("url"))
                        # Try messenger.com and m.facebook.com as well
                        try:
                            s_msg, r_msg = get("https://www.messenger.com/", jar, None, global_options, None, {"noRef": True})
                            log("Post-2FA messenger status:", s_msg, "url:", r_msg.get("url"))
                        except Exception:
                            pass
                        try:
                            s_mob, r_mob = get("https://m.facebook.com/", jar, None, global_options, None, {"noRef": True})
                            log("Post-2FA m.facebook status:", s_mob, "url:", r_mob.get("url"))
                        except Exception:
                            pass
                        has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
                        has_xs = any(c.name == "xs" for c in jar)  # type: ignore
                        if has_c_user and has_xs:
                            break
                    # end 2FA attempts loop
                    has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
                    has_xs = any(c.name == "xs" for c in jar)  # type: ignore
                    if not (has_c_user and has_xs):
                        # Some flows redirect to checkpoint after TFA; fall through to checkpoint handling
                        body_post = res_tfa_post.get("body", body_post)
                        final_url = res_tfa_post.get("url", final_url)

                if "checkpoint" in body_post or "/checkpoint/" in body_post or "/checkpoint/" in final_url:
                    # Attempt to drive the checkpoint flow until cookies appear
                    import time as _time
                    cp_url = final_url if "/checkpoint/" in final_url else (FB_BASE + "/checkpoint/")
                    code_attempted = False

                    def _extract_tokens(html_cp: str):
                        def _f(name: str):
                            m = re.search(fr'name="{name}" value="([^"]+)"', html_cp)
                            return m.group(1) if m else None
                        fb = _f("fb_dtsg") or _f("fb_dtsg_ag")
                        jz = _f("jazoest")
                        nh = _f("nh")
                        # Gather submit buttons like submit[Continue], submit[This was me], etc.
                        submits = re.findall(r'name="submit\[([^\]]+)\]"', html_cp)
                        return fb, jz, nh, submits

                    # Poll/advance up to ~90s
                    for step in range(30):
                        log(f"Checkpoint step {step+1}/30 fetching:", cp_url)
                        status_cp, res_cp = get(cp_url, jar, None, global_options, None, {"noRef": True})
                        log("Checkpoint GET status:", status_cp, "url:", res_cp.get("url"))
                        if status_cp < 200 or status_cp >= 600:
                            break
                        html_cp = res_cp.get("body", "")
                        fb_dtsg, jazoest2, nh, submit_names = _extract_tokens(html_cp)

                        # If approvals_code field exists, submit 2FA code
                        if re.search(r'name="approvals_code"', html_cp) and not code_attempted:
                            code = None
                            if credentials.get("twoFactorCode"):
                                code = str(credentials.get("twoFactorCode")).strip().replace(" ", "")
                            elif callable(credentials.get("getTwoFactorCode")):
                                try:
                                    code = str(credentials.get("getTwoFactorCode")()).strip().replace(" ", "")
                                except Exception:
                                    code = None
                            else:
                                try:
                                    code = input("Enter Facebook 2FA code: ").strip().replace(" ", "")
                                except Exception:
                                    code = None
                            if not code:
                                raise RuntimeError("2FA required but no code provided. Pass twoFactorCode or getTwoFactorCode in credentials.")
                            code_form = {
                                "fb_dtsg": fb_dtsg or "",
                                "jazoest": jazoest2 or "",
                                "nh": nh or "",
                                "approvals_code": code,
                                "save_device": "true",
                            }
                            # try to include a submit button
                            preferred = ["Continue", "Yes", "This was me", "Approve", "Next", "OK"]
                            chosen = next((s for s in preferred if s in submit_names), (submit_names[0] if submit_names else None))
                            if chosen:
                                code_form[f"submit[{chosen}]"] = chosen
                            log("Submitting 2FA code to checkpoint/async...")
                            status_code_post, res_code_post = post("https://www.facebook.com/checkpoint/async/", jar, code_form, global_options, None, {"Referer": cp_url})
                            log("2FA submit status:", status_code_post, "url:", res_code_post.get("url"))
                            code_attempted = True
                            if status_code_post < 200 or status_code_post >= 400:
                                raise RuntimeError(f"2FA code submit failed with status {status_code_post}")
                            cp_url = res_code_post.get("url", cp_url)
                        else:
                            # Try to press any available submit button to advance
                            preferred = ["Continue", "Yes", "This was me", "Approve", "Next", "OK", "Save Device"]
                            chosen = next((s for s in preferred if s in submit_names), (submit_names[0] if submit_names else None))
                            if chosen:
                                cont_form = {k: v for k, v in {"fb_dtsg": fb_dtsg, "jazoest": jazoest2, "nh": nh}.items() if v}
                                cont_form[f"submit[{chosen}]"] = chosen
                                log(f"Submitting checkpoint button: {chosen}")
                                status_cont, res_cont = post("https://www.facebook.com/checkpoint/async/", jar, cont_form, global_options, None, {"Referer": cp_url})
                                log("Checkpoint button status:", status_cont, "url:", res_cont.get("url"))
                                cp_url = res_cont.get("url", cp_url)
                            else:
                                # Nothing to click; break if page isn't a checkpoint anymore
                                loc = res_cp.get("url", "")
                                if "/checkpoint/" not in loc:
                                    log("Left checkpoint flow without action; stopping loop.")
                                    break
                                # Otherwise wait a bit before retry
                                pass

                        # Success check after each step
                        has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
                        has_xs = any(c.name == "xs" for c in jar)  # type: ignore
                        if has_c_user and has_xs:
                            break
                        _time.sleep(3)
                        log("Cookies now:", [(c.name, c.domain) for c in jar])

                    # After checkpoint loop, try home once more before giving up
                    if not (any(c.name == "c_user" for c in jar) and any(c.name == "xs" for c in jar)):
                        status_home2, res_home2 = get(FB_BASE, jar, None, global_options, None, {"noRef": True})
                        log("Final home status after checkpoint:", status_home2, "url:", res_home2.get("url"))
                        try:
                            s_msg2, r_msg2 = get("https://www.messenger.com/", jar, None, global_options, None, {"noRef": True})
                            log("Final messenger status:", s_msg2, "url:", r_msg2.get("url"))
                        except Exception:
                            pass
                        try:
                            s_mob2, r_mob2 = get("https://m.facebook.com/", jar, None, global_options, None, {"noRef": True})
                            log("Final m.facebook status:", s_mob2, "url:", r_mob2.get("url"))
                        except Exception:
                            pass

                    has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
                    has_xs = any(c.name == "xs" for c in jar)  # type: ignore
                    if not (has_c_user and has_xs):
                        # As a last headless attempt, try mobile login flow (m.facebook.com)
                        try:
                            log("Attempting mobile login fallback (m.facebook.com)...")

                            def _find_hidden(html_text: str, name: str):
                                m2 = re.search(fr'name="{name}" value="([^"]+)"', html_text)
                                return m2.group(1) if m2 else None

                            # 1) GET mobile login page
                            m_login_url = "https://m.facebook.com/login.php"
                            s_ml, r_ml = get(m_login_url, jar, None, global_options, None, {"noRef": True})
                            log("Mobile login page status:", s_ml, "url:", r_ml.get("url"))
                            h_ml = r_ml.get("body", "")
                            lsd_m = _find_hidden(h_ml, "lsd")
                            jz_m = _find_hidden(h_ml, "jazoest")
                            li_m = _find_hidden(h_ml, "li")
                            m_ts_m = _find_hidden(h_ml, "m_ts")

                            # 2) POST credentials to mobile login
                            form_m = {
                                "email": email,
                                "pass": password,
                                "lsd": lsd_m or "",
                                "jazoest": jz_m or "",
                                "li": li_m or "",
                                "m_ts": m_ts_m or "",
                                "login": "Log In",
                            }
                            s_mp, r_mp = post(m_login_url, jar, form_m, global_options, None, {"Referer": m_login_url})
                            log("Mobile login POST status:", s_mp, "url:", r_mp.get("url"))
                            body_m = r_mp.get("body", "")
                            url_m = r_mp.get("url", "")

                            # 3) If mobile checkpoint/2FA required, attempt approvals flow on m.facebook
                            if "checkpoint" in body_m or "/checkpoint/" in url_m or "two_step" in url_m:
                                log("Mobile flow: checkpoint/2FA detected. Advancing...")
                                # Load checkpoint page (mobile)
                                cp_m_url = url_m if "/checkpoint/" in url_m else ("https://m.facebook.com/checkpoint/")
                                for _ in range(20):
                                    s_cpm, r_cpm = get(cp_m_url, jar, None, global_options, None, {"noRef": True})
                                    hm = r_cpm.get("body", "")
                                    fbm = _find_hidden(hm, "fb_dtsg") or _find_hidden(hm, "fb_dtsg_ag")
                                    jzm = _find_hidden(hm, "jazoest")
                                    nhm = _find_hidden(hm, "nh")
                                    # approvals_code on mobile
                                    if re.search(r'name="approvals_code"', hm):
                                        code = None
                                        if credentials.get("twoFactorCode"):
                                            code = str(credentials.get("twoFactorCode")).strip().replace(" ", "")
                                        elif callable(credentials.get("getTwoFactorCode")):
                                            try:
                                                code = str(credentials.get("getTwoFactorCode")()).strip().replace(" ", "")
                                            except Exception:
                                                code = None
                                        else:
                                            try:
                                                code = input("Enter Facebook 2FA code: ").strip().replace(" ", "")
                                            except Exception:
                                                code = None
                                        if not code:
                                            break
                                        form_cpm = {k: v for k, v in {"fb_dtsg": fbm, "jazoest": jzm, "nh": nhm}.items() if v}
                                        form_cpm["approvals_code"] = code
                                        form_cpm["save_device"] = "true"
                                        s_post_cpm, r_post_cpm = post("https://m.facebook.com/checkpoint/async/", jar, form_cpm, global_options, None, {"Referer": cp_m_url})
                                        log("Mobile 2FA submit status:", s_post_cpm, "url:", r_post_cpm.get("url"))
                                        cp_m_url = r_post_cpm.get("url", cp_m_url)
                                    else:
                                        # Try to press Continue/Save Device on mobile
                                        submits_m = [m.group(1) for m in re.finditer(r'name="submit\[([^\]]+)\]"', hm)]
                                        if submits_m:
                                            prefm = ["Continue", "Save Device", "Yes", "This was me", "Approve", "Next", "OK"]
                                            chm = next((s for s in prefm if s in submits_m), submits_m[0])
                                            form_follow_m = {k: v for k, v in {"fb_dtsg": fbm, "jazoest": jzm, "nh": nhm}.items() if v}
                                            form_follow_m[f"submit[{chm}]"] = chm
                                            s_follow_m, r_follow_m = post("https://m.facebook.com/checkpoint/async/", jar, form_follow_m, global_options, None, {"Referer": cp_m_url})
                                            log("Mobile follow-up status:", s_follow_m, "url:", r_follow_m.get("url"))
                                            cp_m_url = r_follow_m.get("url", cp_m_url)
                                    # Check cookies after each step
                                    if any(c.name == "c_user" for c in jar) and any(c.name == "xs" for c in jar):
                                        break
                                # end mobile checkpoint loop

                            # Try to consolidate cookies by hitting mobile and home
                            try:
                                s_home_m, r_home_m = get("https://m.facebook.com/", jar, None, global_options, None, {"noRef": True})
                                log("Mobile home status:", s_home_m, "url:", r_home_m.get("url"))
                            except Exception:
                                pass
                            s_home_www, r_home_www = get(FB_BASE, jar, None, global_options, None, {"noRef": True})
                            log("WWW home after mobile status:", s_home_www, "url:", r_home_www.get("url"))

                            has_c_user = any(c.name == "c_user" for c in jar)  # type: ignore
                            has_xs = any(c.name == "xs" for c in jar)  # type: ignore
                        except Exception as _mob_ex:
                            log("Mobile login fallback error:", _mob_ex)

                        if not (has_c_user and has_xs):
                            raise RuntimeError("2FA flow completed but missing session cookies. Please verify code, approve login in the app, or use appState cookies.")
                else:
                    raise RuntimeError("Login failed. Check credentials or provide appState cookies.")
        else:
            raise ValueError("No cookie or credentials found. Provide cookies (appState).")

        if not initial_api:
            api: Dict[str, Any] = {}
        else:
            api = initial_api  # type: ignore

        # Load FB home and parse embedded JSON blobs by simple scrape of scripts type=json
        log("Fetching Facebook home to build API context")
        status, res = get(FB_BASE, jar, None, global_options, None, {"noRef": True})
        log("Home GET status:", status, "url:", res.get("url"))
        if status < 200 or status >= 600:
            raise RuntimeError(f"Failed to GET Facebook. Status {status}")
        body = res.get("body", "")

        # naive extraction of JSON scripts
        json_blobs: List[Dict[str, Any]] = []
        for m in re.finditer(r'<script type="application/json"[^>]*>(.*?)</script>', body, re.S):
            try:
                import json
                json_blobs.append(json.loads(m.group(1)))
            except Exception:
                pass

        ctx, default_funcs = await build_api_func(body, jar, json_blobs, global_options)

        # api methods minimal
        class Api:
            def __init__(self):
                self.ctx = ctx
                self.defaultFuncs = default_funcs
                self.globalOptions = global_options

            def setOptions(self, opts: Dict[str, Any]):
                return set_options_func(self.globalOptions, opts)

            def getAppState(self) -> List[Dict[str, str]]:
                out = []
                for c in jar:  # type: ignore
                    if c.domain.endswith("facebook.com") or c.domain.endswith("messenger.com"):
                        out.append({"key": c.name, "value": c.value})
                # dedupe by key
                seen = set()
                uniq = []
                for c in out:
                    if c["key"] in seen:
                        continue
                    seen.add(c["key"])
                    uniq.append(c)
                return uniq

            def saveAppState(self, file_path: str = "appstate.json") -> str:
                import json, os
                data = self.getAppState()
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return os.path.abspath(file_path)

            def getCurrentUserID(self) -> str:
                return str(self.ctx.get("userID"))

            def getOptions(self, key: Optional[str] = None):
                if key:
                    return self.globalOptions.get(key)
                return self.globalOptions

            # snake_case aliases
            def set_options(self, opts: Dict[str, Any]):
                return self.setOptions(opts)

            def get_app_state(self) -> List[Dict[str, str]]:
                return self.getAppState()

            def save_app_state(self, file_path: str = "appstate.json") -> str:
                return self.saveAppState(file_path)

            def get_current_user_id(self) -> str:
                return self.getCurrentUserID()

            def get_options(self, key: Optional[str] = None):
                return self.getOptions(key)

            # HTTP wrappers mirroring deltas/apis/http/*
            def httpGet(self, url: str, qs: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
                return self.defaultFuncs.get(url, self.ctx.get("jar"), qs or {}, self.ctx, headers)

            def httpPost(self, url: str, form: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
                return self.defaultFuncs.post(url, self.ctx.get("jar"), form or {}, self.ctx, headers)

            def httpPostFormData(self, url: str, form: Dict[str, Any], qs: Optional[Dict[str, Any]] = None):
                return self.defaultFuncs.postFormData(url, self.ctx.get("jar"), form or {}, qs or {}, self.ctx)

            # Basic Threads API: getThreadList (unformatted raw nodes for now)
            def getThreadList(self, limit: int, timestamp: Optional[int] = None, tags: Optional[List[str]] = None):
                if not isinstance(limit, int) or limit <= 0:
                    raise ValueError("getThreadList: limit must be a positive integer")
                tags = tags or ["INBOX"]
                if isinstance(tags, str):
                    tags = [tags]
                form = {
                    "av": self.ctx.get("userID"),
                    "queries": __import__("json").dumps({
                        "o0": {
                            "doc_id": "3426149104143726",
                            "query_params": {
                                "limit": limit + (1 if timestamp else 0),
                                "before": timestamp,
                                "tags": tags,
                                "includeDeliveryReceipts": True,
                                "includeSeqID": False,
                            },
                        }
                    }),
                    "batch_name": "MessengerGraphQLThreadlistFetcher",
                }
                status, res = self.defaultFuncs.post("https://www.facebook.com/api/graphqlbatch/", self.ctx.get("jar"), form, self.ctx)
                if status < 200 or status >= 300:
                    raise RuntimeError(f"GraphQL batch failed with status {status}")
                text = res.get("body", "")
                text = text.replace("for (;;);", "").strip()
                try:
                    import json
                    parsed = json.loads(text)
                except Exception:
                    # Some responses are line-delimited JSON; try to parse the first JSON object
                    lines = [l for l in text.splitlines() if l.strip()]
                    import json
                    parsed = json.loads(lines[0]) if lines else {}
                if isinstance(parsed, list) and parsed:
                    first = parsed[0]
                    data = first.get("o0", {}).get("data", {})
                    nodes = data.get("viewer", {}).get("message_threads", {}).get("nodes", [])
                    if timestamp and nodes:
                        nodes = nodes[1:]
                    return nodes
                return parsed

            # Internal helpers
            def _parse_batch(self, text: str):
                text = (text or "").replace("for (;;);", "").strip()
                import json
                if not text:
                    return []
                try:
                    return json.loads(text)
                except Exception:
                    out = []
                    for line in text.splitlines():
                        l = line.strip()
                        if not l:
                            continue
                        try:
                            out.append(json.loads(l))
                        except Exception:
                            continue
                    return out

            # Threads API: getThreadInfo
            def getThreadInfo(self, threadID):
                ids = threadID if isinstance(threadID, list) else [threadID]
                queries = {}
                for i, t in enumerate(ids):
                    queries[f"o{i}"] = {
                        "doc_id": "3449967031715030",
                        "query_params": {
                            "id": str(t),
                            "message_limit": 0,
                            "load_messages": False,
                            "load_read_receipts": False,
                            "before": None,
                        },
                    }
                form = {
                    "queries": __import__("json").dumps(queries),
                    "batch_name": "MessengerGraphQLThreadFetcher",
                }
                status, res = self.defaultFuncs.post("https://www.facebook.com/api/graphqlbatch/", self.ctx.get("jar"), form, self.ctx)
                if status < 200 or status >= 300:
                    raise RuntimeError(f"getThreadInfo failed with status {status}")
                arr = self._parse_batch(res.get("body", ""))
                info_map: Dict[str, Any] = {}
                for obj in arr:
                    if not isinstance(obj, dict):
                        continue
                    for key, val in obj.items():
                        data = val.get("data") if isinstance(val, dict) else None
                        if not data:
                            continue
                        mt = data.get("message_thread")
                        if not mt:
                            continue
                        # Minimal normalize
                        thread_key = mt.get("thread_key", {})
                        tid = thread_key.get("thread_fbid") or thread_key.get("other_user_id")
                        info_map[str(tid)] = mt
                return info_map if isinstance(threadID, list) else (info_map.get(str(ids[0])) if ids else None)

            # Threads API: getThreadHistory (simplified, latest messages)
            def getThreadHistory(self, threadID, amount: int = 10, timestamp: Optional[int] = None):
                if not threadID:
                    raise ValueError("getThreadHistory: threadID is required")
                try:
                    amount = int(amount)
                except Exception:
                    amount = 10
                if amount <= 0:
                    amount = 1
                form = {
                    "queries": __import__("json").dumps({
                        "o0": {
                            "doc_id": "1498317363570230",
                            "query_params": {
                                "id": str(threadID),
                                "message_limit": amount,
                                "load_messages": True,
                                "load_read_receipts": False,
                                "before": int(timestamp) if timestamp else None,
                            },
                        }
                    }),
                    "batch_name": "MessengerGraphQLThreadFetcher",
                }
                status, res = self.defaultFuncs.post("https://www.facebook.com/api/graphqlbatch/", self.ctx.get("jar"), form, self.ctx)
                if status < 200 or status >= 300:
                    raise RuntimeError(f"getThreadHistory failed with status {status}")
                arr = self._parse_batch(res.get("body", ""))
                if not arr:
                    return []
                first = arr[0] if isinstance(arr[0], dict) else {}
                data = ((first.get("o0") or {}).get("data") or {}) if isinstance(first, dict) else {}
                mt = data.get("message_thread") or {}
                nodes = (((mt.get("messages") or {}).get("nodes")) or [])
                is_group = (mt.get("thread_type") == "GROUP")
                out = []
                for d in nodes:
                    if not isinstance(d, dict):
                        continue
                    typ = d.get("__typename")
                    if typ == "UserMessage":
                        sender = (d.get("message_sender") or {}).get("id")
                        msg = (d.get("message") or {})
                        text = msg.get("text") or ""
                        out.append({
                            "type": "message",
                            "messageID": d.get("message_id"),
                            "threadID": str(threadID),
                            "senderID": sender,
                            "body": text,
                            "timestamp": d.get("timestamp_precise"),
                            "isGroup": is_group,
                        })
                    else:
                        # Map admin/generic events as non-message entries if needed
                        out.append({
                            "type": "event",
                            "messageID": d.get("message_id"),
                            "threadID": str(threadID),
                            "senderID": (d.get("message_sender") or {}).get("id"),
                            "body": d.get("snippet") or "",
                            "timestamp": d.get("timestamp_precise"),
                            "isGroup": is_group,
                        })
                return out

            # Threads API: getThreadHistory (returns simplified message list)
            def getThreadHistory(self, threadID: str, amount: int, timestamp: Optional[int] = None):
                if not threadID or not isinstance(amount, int) or amount <= 0:
                    raise ValueError("getThreadHistory: threadID and positive amount are required")
                form = {
                    "queries": __import__("json").dumps({
                        "o0": {
                            "doc_id": "1498317363570230",
                            "query_params": {
                                "id": str(threadID),
                                "message_limit": amount,
                                "load_messages": True,
                                "load_read_receipts": False,
                                "before": timestamp or None,
                            },
                        }
                    }),
                    "batch_name": "MessagingActorMessagesQuery",
                }
                status, res = self.defaultFuncs.post("https://www.facebook.com/api/graphqlbatch/", self.ctx.get("jar"), form, self.ctx)
                if status < 200 or status >= 300:
                    raise RuntimeError(f"getThreadHistory failed with status {status}")
                arr = self._parse_batch(res.get("body", ""))
                if not arr:
                    return []
                data = (arr[0].get("o0", {}) if isinstance(arr[0], dict) else {}).get("data", {})
                mt = data.get("message_thread")
                if not mt:
                    return []
                is_group = (mt.get("thread_type") == "GROUP")
                key = mt.get("thread_key", {})
                tid = key.get("thread_fbid") or key.get("other_user_id")
                nodes = (mt.get("messages", {}) or {}).get("nodes", [])
                out = []
                for d in nodes:
                    typ = d.get("__typename")
                    if typ == "UserMessage":
                        body = (d.get("message") or {}).get("text") or ""
                        sender = (d.get("message_sender") or {}).get("id")
                        mid = d.get("message_id")
                        ts = d.get("timestamp_precise")
                        out.append({
                            "type": "message",
                            "body": body,
                            "senderID": sender,
                            "messageID": mid,
                            "threadID": tid,
                            "timestamp": ts,
                            "isGroup": is_group,
                        })
                    else:
                        out.append({"type": "event", "raw": d})
                return out

            # Users API: getUserInfo via payload endpoint
            def getUserInfo(self, ids, usePayload: bool = True):
                orig_is_array = isinstance(ids, list)
                id_list = ids if orig_is_array else [ids]
                if usePayload:
                    form: Dict[str, Any] = {}
                    for i, v in enumerate(id_list):
                        form[f"ids[{i}]"] = str(v)
                    status, res = self.defaultFuncs.post("https://www.facebook.com/chat/user_info/", self.ctx.get("jar"), form, self.ctx)
                    if status < 200 or status >= 300:
                        raise RuntimeError(f"getUserInfo failed with status {status}")
                    import json
                    try:
                        data = json.loads((res.get("body") or "").replace("for (;;);", ""))
                    except Exception:
                        data = {}
                    profiles = ((data or {}).get("payload") or {}).get("profiles") or {}
                    ret = {}
                    for k, inner in profiles.items():
                        name = inner.get("name")
                        parts = (name or "").split(" ") if name else []
                        gender_map = {1: "male", 2: "female"}
                        ret[k] = {
                            "id": k,
                            "name": name,
                            "firstName": inner.get("firstName") or (parts[0] if parts else None),
                            "lastName": (parts[-1] if len(parts) > 1 else None),
                            "vanity": inner.get("vanity"),
                            "profilePicUrl": f"https://graph.facebook.com/{k}/picture?width=720&height=720&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662",
                            "profileUrl": inner.get("uri"),
                            "gender": gender_map.get(inner.get("gender"), "no specific gender"),
                            "type": inner.get("type"),
                            "isFriend": inner.get("is_friend"),
                            "isBirthday": bool(inner.get("is_birthday")),
                        }
                    if not ret:
                        # fallback to defaults
                        for v in id_list:
                            k = str(v)
                            ret[k] = {
                                "id": k,
                                "name": "Facebook User",
                                "firstName": "Facebook",
                                "lastName": None,
                                "vanity": k,
                                "profilePicUrl": f"https://graph.facebook.com/{k}/picture?width=720&height=720&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662",
                                "profileUrl": f"https://www.facebook.com/profile.php?id={k}",
                                "gender": "no specific gender",
                                "type": "user",
                                "isFriend": False,
                                "isBirthday": False,
                            }
                    return list(ret.values()) if orig_is_array else ret.get(str(id_list[0]))
                else:
                    # TODO: implement scraping fallback similar to JS (deferred)
                    raise NotImplementedError("getUserInfo(usePayload=False) is not yet implemented in Python port.")

            # Login API: logout
            def logout(self):
                # Step 1: get settings menu to fetch logout hidden fields
                settings_url = "https://www.facebook.com/bluebar/modern_settings_menu/?help_type=364455653583099&show_contextual_help=1"
                status, res = self.defaultFuncs.post(settings_url, self.ctx.get("jar"), {"pmid": "0"}, self.ctx)
                if status < 200 or status >= 300:
                    raise RuntimeError(f"logout prefetch failed with status {status}")
                html = res.get("body", "")
                # Best-effort to extract fb_dtsg, h, ref
                def _get(name: str):
                    m = re.search(fr'\"{name}\" value=\"([^\"]+)\"', html)
                    return m.group(1) if m else None
                fb_dtsg = _get("fb_dtsg")
                h = _get("h")
                ref = _get("ref")
                form = {k: v for k, v in {"fb_dtsg": fb_dtsg, "h": h, "ref": ref}.items() if v}
                status2, res2 = self.defaultFuncs.post("https://www.facebook.com/logout.php", self.ctx.get("jar"), form, self.ctx)
                if status2 < 200 or status2 >= 400:
                    raise RuntimeError(f"logout post failed with status {status2}")
                self.ctx["loggedIn"] = False
                return True

        api_obj = Api()
        # Attach API namespaces (messaging, stubs for others) to the object
        try:
            from ...apis import attach_all
            attach_all(api_obj)
        except Exception:
            pass

        # TODO: load API modules: for Python port we expose a subset; mapping/stubs can be expanded
        # Messaging (MQTT) will need an async client; provided later as follow-up

        return callback(None, api_obj)
    except Exception as e:
        log_error("login_helper", e)
        return callback(e, None)
