import os, json, yaml

def merge(d1, d2):
    r = d1.copy()
    for k, v in d2.items():
        if k in r and isinstance(r[k], dict) and isinstance(v, dict):
            r[k] = merge(r[k], v)
        else:
            r[k] = v
    return r

if __name__ == "__main__":
    files = []
    
    try:
        p_str = os.environ.get("PUSH_CONFIG")
        if p_str:
            try:
                p_data = json.loads(p_str)
                if p_data.get("enable"):
                    srv = p_data.get("push_server", "telegram")
                    lines = ["[setting]", "enable=true", f"push_server={srv}"]
                    
                    for k in ["push_token", "push_block_keys", "error_push_only", "topic"]:
                        if k in p_data: lines.append(f"{k}={str(p_data[k]).lower()}")

                    lines.append(f"\n[{srv}]")
                    if srv in p_data:
                        for k, v in p_data[srv].items(): lines.append(f"{k}={v}")
                    
                    with open("config/push.ini", "w", encoding="utf-8") as f:
                        f.write("\n".join(lines))
            except: 
                pass

        u_str = os.environ.get("PROFILES")
        if u_str:
            profiles = json.loads(u_str)
            with open("config/config.yaml.example", "r", encoding="utf-8") as f:
                base = yaml.safe_load(f)
            
            for i, p in enumerate(profiles):
                cfg = base.copy()
                cfg.setdefault("account", {}).update({
                    "cookie": p.get("cookie", ""),
                    "stoken": p.get("stoken", "")
                })
                if "config" in p: cfg = merge(cfg, p["config"])
                
                fn = f"config/account_{i}.yaml"
                with open(fn, "w", encoding="utf-8") as f:
                    yaml.dump(cfg, f, allow_unicode=True)
                files.append(fn)

            os.environ.pop("GITHUB_ACTIONS", None)
            os.system("python main_multi.py autorun")

    except Exception:
        pass
        
    finally:
        for f in files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists("config/push.ini"): os.remove("config/push.ini")