import os
import json
from datetime import datetime

# This small launcher loads config.json and triggers monthly email sending

def _load_config(base_dir: str) -> dict:
    cfg_path = os.path.join(base_dir, 'config.json')
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    from usage_reporting import init as usage_init, send_if_month_end

    cfg = _load_config(base_dir)
    usage_init(cfg, base_dir)
    # Safe to call daily; will only send on last day and if not already sent
    send_if_month_end()


if __name__ == '__main__':
    main()


