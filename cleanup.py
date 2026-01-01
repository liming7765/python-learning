import os
import sys
import subprocess
if __name__ == "__main__":
    tg_bot_token = os.environ.get("TG_BOT_TOKEN")
    tg_user_id = os.environ.get("TG_USER_ID")
    log_file = "log.txt"
    caption = "Detailed Log (Action)"
    if not tg_bot_token or not tg_user_id or not os.path.exists(log_file):
        sys.exit(0)

    try:
        command = [
            "curl", "-s",
            "-F", f"chat_id={tg_user_id}",
            "-F", f"document=@{log_file}",
            "-F", f"caption={caption}",
            f"https://api.telegram.org/bot{tg_bot_token}/sendDocument"
        ]
        subprocess.run(command, check=False, capture_output=True) 
        
    except Exception:
        pass 
    finally:
        if os.path.exists(log_file):
            try:
                os.remove(log_file)
            except Exception:
                pass