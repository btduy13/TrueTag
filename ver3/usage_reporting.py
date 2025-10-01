import os
import json
import csv
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


_state = {
    "cfg": None,
    "base_dir": None,
}


def _logs_dir(base_dir: str) -> str:
    path = os.path.join(base_dir, "logs")
    os.makedirs(path, exist_ok=True)
    return path


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _usage_log_path(base_dir: str, month_key: str) -> str:
    return os.path.join(_logs_dir(base_dir), f"usage-{month_key}.jsonl")


def _summarize_month(base_dir: str, month_key: str):
    path = _usage_log_path(base_dir, month_key)
    summary = {"total_runs": 0, "modules": {}}
    if not os.path.exists(path):
        return summary
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            summary["total_runs"] += 1
            module_name = rec.get("module") or "(unknown)"
            summary["modules"][module_name] = summary["modules"].get(module_name, 0) + 1
    return summary


def _write_csv_summary(base_dir: str, month_key: str, summary: dict) -> str:
    csv_path = os.path.join(_logs_dir(base_dir), f"summary-{month_key}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Month", month_key])
        writer.writerow(["Total Runs", summary.get("total_runs", 0)])
        writer.writerow([])
        writer.writerow(["Module", "Runs"])
        for module_name, count in sorted(summary.get("modules", {}).items()):
            writer.writerow([module_name, count])
    return csv_path


def _send_email(cfg: dict, subject: str, body: str, attachments: list):
    host = cfg.get("smtp_host")
    port = int(cfg.get("smtp_port", 587) or 587)
    user = cfg.get("smtp_user")
    password = cfg.get("smtp_password")
    use_tls = bool(cfg.get("smtp_use_tls", True))
    email_from = cfg.get("email_from")
    email_to = cfg.get("email_to")

    if not host or not email_from or not email_to:
        return  # Not configured

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    prefix = cfg.get("email_subject_prefix", "TRUETAG")
    msg['Subject'] = f"{prefix} - {subject}" if prefix else subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    for path in attachments or []:
        if not path or not os.path.exists(path):
            continue
        part = MIMEBase('application', 'octet-stream')
        with open(path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(path)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

    with smtplib.SMTP(host, port) as server:
        if use_tls:
            server.starttls()
        if user and password:
            server.login(user, password)
        server.send_message(msg)


def init(cfg: dict, base_dir: str):
    _state["cfg"] = dict(cfg or {})
    _state["base_dir"] = base_dir
    # Ensure logs dir exists
    _logs_dir(base_dir)


def record_run(module_name: str):
    cfg = _state.get("cfg")
    base_dir = _state.get("base_dir")
    if not cfg or not base_dir:
        return
    now = datetime.now()
    month_key = _month_key(now)
    log_path = _usage_log_path(base_dir, month_key)
    rec = {
        "ts": now.isoformat(),
        "module": module_name,
    }
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def shutdown():
    cfg = _state.get("cfg")
    base_dir = _state.get("base_dir")
    if not cfg or not base_dir:
        return
    now = datetime.now()
    current_month = _month_key(now)
    last_month_sent = cfg.get("last_report_month") or ""

    # Send report only if SMTP configured and month changed since last send
    if not cfg.get("smtp_host") or not cfg.get("email_to") or not cfg.get("email_from"):
        return
    if last_month_sent == current_month:
        return

    # Report the PREVIOUS month when month flips; else, send for current month on first run
    report_month = last_month_sent if last_month_sent else current_month
    if last_month_sent and last_month_sent != current_month:
        report_month = last_month_sent
    else:
        report_month = current_month

    summary = _summarize_month(base_dir, report_month)
    csv_path = _write_csv_summary(base_dir, report_month, summary)
    jsonl_path = _usage_log_path(base_dir, report_month)

    subject = f"Monthly usage report {report_month}"
    body = (
        f"Month: {report_month}\n"
        f"Total runs: {summary.get('total_runs', 0)}\n\n"
        f"Per-module breakdown is attached as CSV. Raw logs are attached as JSONL.\n"
    )

    try:
        _send_email(cfg, subject, body, [csv_path, jsonl_path])
        cfg["last_report_month"] = current_month
    except Exception:
        # Do not crash the app due to email issues
        pass


