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
    """Generate a summary of usage for a given month with run time statistics."""
    path = _usage_log_path(base_dir, month_key)
    summary = {
        "total_runs": 0, 
        "modules": {},
        "total_run_time_seconds": 0,
        "average_run_time_seconds": 0,
        "run_details": []
    }
    if not os.path.exists(path):
        return summary
    
    run_times = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            summary["total_runs"] += 1
            module_name = rec.get("module") or "(unknown)"
            run_time = rec.get("run_time_seconds")
            
            # Update module count
            if module_name not in summary["modules"]:
                summary["modules"][module_name] = {"count": 0, "total_time": 0}
            summary["modules"][module_name]["count"] += 1
            
            # Track run times
            if run_time is not None:
                run_times.append(run_time)
                summary["total_run_time_seconds"] += run_time
                summary["modules"][module_name]["total_time"] += run_time
            
            # Store run details for report
            summary["run_details"].append({
                "date": rec.get("date", ""),
                "time": rec.get("time", ""),
                "module": module_name,
                "run_time": f"{run_time:.2f}s" if run_time else "N/A"
            })
    
    # Calculate average run time
    if run_times:
        summary["average_run_time_seconds"] = sum(run_times) / len(run_times)
    
    return summary


def _write_csv_summary(base_dir: str, month_key: str, summary: dict) -> str:
    csv_path = os.path.join(_logs_dir(base_dir), f"summary-{month_key}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header information
        writer.writerow(["TRUETAG Monthly Usage Report"])
        writer.writerow(["Month", month_key])
        writer.writerow(["Total Runs", summary.get("total_runs", 0)])
        writer.writerow(["Total Run Time", f"{summary.get('total_run_time_seconds', 0):.2f} seconds"])
        writer.writerow(["Average Run Time", f"{summary.get('average_run_time_seconds', 0):.2f} seconds"])
        writer.writerow([])
        
        # Module breakdown
        writer.writerow(["Module Usage Breakdown"])
        writer.writerow(["Module", "Runs", "Total Time (seconds)", "Average Time (seconds)"])
        for module_name, data in sorted(summary.get("modules", {}).items()):
            count = data.get("count", 0)
            total_time = data.get("total_time", 0)
            avg_time = total_time / count if count > 0 else 0
            writer.writerow([module_name, count, f"{total_time:.2f}", f"{avg_time:.2f}"])
        
        writer.writerow([])
        
        # Detailed run log
        writer.writerow(["Detailed Run Log"])
        writer.writerow(["Date", "Time", "Module", "Run Time (seconds)"])
        for run in summary.get("run_details", []):
            writer.writerow([run.get("date", ""), run.get("time", ""), run.get("module", ""), run.get("run_time", "N/A")])
    
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


def record_run(module_name: str, run_time_seconds: float = None):
    """Record a script run in the usage log with optional run time."""
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
        "run_time_seconds": run_time_seconds,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    }
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def test_email():
    """Send a test email to verify SMTP configuration with sample monthly report format."""
    cfg = _state.get("cfg")
    if not cfg:
        return False, "No configuration loaded"
    
    if not cfg.get("smtp_host") or not cfg.get("email_to") or not cfg.get("email_from"):
        return False, "SMTP not configured. Please set smtp_host, email_from, and email_to in config.json"
    
    # Create sample data for test report
    current_month = datetime.now().strftime("%Y-%m")
    sample_summary = {
        "total_runs": 5,
        "total_run_time_seconds": 15.67,
        "average_run_time_seconds": 3.13,
        "modules": {
            "Instrument-v2": {"count": 3, "total_time": 9.45},
            "TML": {"count": 2, "total_time": 6.22}
        },
        "run_details": [
            {"date": "2025-10-01", "time": "09:15:30", "module": "Instrument-v2", "run_time": "3.12s"},
            {"date": "2025-10-01", "time": "10:22:15", "module": "TML", "run_time": "3.45s"},
            {"date": "2025-10-02", "time": "14:30:20", "module": "Instrument-v2", "run_time": "3.20s"},
            {"date": "2025-10-02", "time": "16:45:10", "module": "TML", "run_time": "2.77s"},
            {"date": "2025-10-03", "time": "11:10:05", "module": "Instrument-v2", "run_time": "3.13s"}
        ]
    }
    
    # Create test CSV file
    base_dir = _state.get("base_dir", ".")
    test_csv_path = os.path.join(_logs_dir(base_dir), f"test-summary-{current_month}.csv")
    os.makedirs(_logs_dir(base_dir), exist_ok=True)
    
    with open(test_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header information
        writer.writerow(["TRUETAG Monthly Usage Report (TEST)"])
        writer.writerow(["Month", current_month])
        writer.writerow(["Total Runs", sample_summary.get("total_runs", 0)])
        writer.writerow(["Total Run Time", f"{sample_summary.get('total_run_time_seconds', 0):.2f} seconds"])
        writer.writerow(["Average Run Time", f"{sample_summary.get('average_run_time_seconds', 0):.2f} seconds"])
        writer.writerow([])
        
        # Module breakdown
        writer.writerow(["Module Usage Breakdown"])
        writer.writerow(["Module", "Runs", "Total Time (seconds)", "Average Time (seconds)"])
        for module_name, data in sorted(sample_summary.get("modules", {}).items()):
            count = data.get("count", 0)
            total_time = data.get("total_time", 0)
            avg_time = total_time / count if count > 0 else 0
            writer.writerow([module_name, count, f"{total_time:.2f}", f"{avg_time:.2f}"])
        
        writer.writerow([])
        
        # Detailed run log
        writer.writerow(["Detailed Run Log"])
        writer.writerow(["Date", "Time", "Module", "Run Time (seconds)"])
        for run in sample_summary.get("run_details", []):
            writer.writerow([run.get("date", ""), run.get("time", ""), run.get("module", ""), run.get("run_time", "N/A")])
    
    subject = f"TRUETAG Test Email - Monthly Report Format"
    body = (
        f"TRUETAG Test Email - Monthly Report Format\n"
        f"==========================================\n\n"
        f"This is a test email to verify your SMTP configuration and show the monthly report format.\n\n"
        f"Sample Monthly Report for {current_month}:\n"
        f"Total Runs: {sample_summary.get('total_runs', 0)}\n"
        f"Total Run Time: {sample_summary.get('total_run_time_seconds', 0):.2f} seconds\n"
        f"Average Run Time: {sample_summary.get('average_run_time_seconds', 0):.2f} seconds\n\n"
        f"Module Usage Summary:\n"
    )
    
    # Add module breakdown to email body
    for module_name, data in sorted(sample_summary.get("modules", {}).items()):
        count = data.get("count", 0)
        total_time = data.get("total_time", 0)
        avg_time = total_time / count if count > 0 else 0
        body += f"  • {module_name}: {count} runs, {total_time:.2f}s total, {avg_time:.2f}s average\n"
    
    body += f"\nDetailed breakdown is attached as CSV file.\n"
    body += f"Test email sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    body += f"SMTP Configuration:\n"
    body += f"  Host: {cfg.get('smtp_host')}\n"
    body += f"  Port: {cfg.get('smtp_port', 587)}\n"
    body += f"  From: {cfg.get('email_from')}\n"
    body += f"  To: {cfg.get('email_to')}\n"
    
    try:
        _send_email(cfg, subject, body, [test_csv_path])
        return True, "Test email with monthly report format sent successfully!"
    except Exception as e:
        return False, f"Failed to send test email: {str(e)}"


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

    subject = f"TRUETAG Monthly Usage Report - {report_month}"
    body = (
        f"TRUETAG Monthly Usage Report\n"
        f"============================\n\n"
        f"Month: {report_month}\n"
        f"Total Runs: {summary.get('total_runs', 0)}\n"
        f"Total Run Time: {summary.get('total_run_time_seconds', 0):.2f} seconds\n"
        f"Average Run Time: {summary.get('average_run_time_seconds', 0):.2f} seconds\n\n"
        f"Module Usage Summary:\n"
    )
    
    # Add module breakdown to email body
    for module_name, data in sorted(summary.get("modules", {}).items()):
        count = data.get("count", 0)
        total_time = data.get("total_time", 0)
        avg_time = total_time / count if count > 0 else 0
        body += f"  • {module_name}: {count} runs, {total_time:.2f}s total, {avg_time:.2f}s average\n"
    
    body += f"\nDetailed breakdown and raw logs are attached as CSV and JSONL files.\n"
    body += f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    try:
        _send_email(cfg, subject, body, [csv_path, jsonl_path])
        cfg["last_report_month"] = current_month
    except Exception:
        # Do not crash the app due to email issues
        pass


