
import os, json, yaml, sys, urllib.request, traceback

def merge(d1, d2):
    r = d1.copy()
    for k, v in d2.items():
        if k in r and isinstance(r[k], dict) and isinstance(v, dict):
            r[k] = merge(r[k], v)
        else: r[k] = v
    return r

def notify(m):
    try:
        p_str = os.environ.get("PUSH_CONFIG", "{}")
        p = json.loads(p_str)
        if p.get("push_server") == "telegram":
            tg = p.get("telegram", {})
            token = tg.get("bot_token")
            chat_id = tg.get("chat_id")
            api_url = tg.get("api_url", "api.telegram.org")
            if token and chat_id:
                url = f"https://{api_url}/bot{token}/sendMessage"
                data = json.dumps({"chat_id": chat_id, "text": f"Execution Error:\n{m}"}).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as response: pass
    except: pass

if __name__ == "__main__":
    files = []
    try:
        p_str = os.environ.get("PUSH_CONFIG")
        if p_str:
            p_data = json.loads(p_str)
            if p_data.get("enable"):
                srv = p_data.get("push_server", "telegram")
                lines = ["[setting]", "enable=true", f"push_server={srv}"]
                for k in ["push_token", "push_block_keys", "error_push_only", "topic"]:
                    if k in p_data: lines.append(f"{k}={str(p_data[k]).lower()}")
                lines.append(f"\n[{srv}]")
                if srv in p_data:
                    for k, v in p_data[srv].items(): lines.append(f"{k}={v}")
                os.makedirs("config", exist_ok=True)
                with open("config/push.ini", "w") as f: f.write("\n".join(lines))

        u_str = os.environ.get("PROFILES")
        if not u_str or u_str.strip() == "": raise Exception("PROFILES_IS_EMPTY_OR_NOT_SET")
        
        profiles = json.loads(u_str)
        with open("config/config.yaml.example", "r") as f: base = yaml.safe_load(f)
        
        for i, p in enumerate(profiles):
            cfg = merge(base, {})
            cfg.setdefault("account", {}).update({"cookie": p.get("cookie", ""), "stoken": p.get("stoken", "")})
            if "config" in p: cfg = merge(cfg, p["config"])
            fn = f"config/account_{i}.yaml"
            with open(fn, "w") as f: yaml.dump(cfg, f)
            files.append(fn)

        os.environ.pop("GITHUB_ACTIONS", None)
        if os.system("python main_multi.py autorun") != 0:
            raise Exception("MAIN_EXE_ERROR")

    except Exception:
        notify(traceback.format_exc())
        sys.exit(1)
    finally:
        for f in files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists("config/push.ini"): os.remove("config/push.ini")
