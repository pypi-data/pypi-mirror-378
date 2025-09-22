import os
import json
import logging
import threading
import time
import socket
import requests
import configparser
from datetime import datetime
import cx_Oracle
from .ip_utils import MachineIPDetector
from .app_version import get_app_version

# Configuration class for user-supplied settings
class GlobalServiceConfig:
    def __init__(self, GLOBAL_LOG_URL=None, PROJECT_TYPE=None, FAILED_LOG_FILE=None, FLUSH_INTERVAL_SEC=None, APP_CODE=None,
                 ORACLE_DB_HOST=None, ORACLE_DB_PORT=None, ORACLE_DB_SERVICE=None, ORACLE_USER=None, ORACLE_PASS=None, ORACLE_DSN=None,
                 LOCAL_ACCESS_LOG_FILE=None, LOCAL_ACTIVITY_LOG_FILE=None, GLOBAL_CONFIG_PATH=None,
                 ACTIVITY_FAILED_LOG_FILE=None):
        self.GLOBAL_LOG_URL = GLOBAL_LOG_URL or os.getenv("GLOBAL_LOG_URL")
        self.PROJECT_TYPE = PROJECT_TYPE or os.getenv("PROJECT_TYPE")
        self.FAILED_LOG_FILE = FAILED_LOG_FILE or os.getenv("FAILED_LOG_FILE")
        self.FLUSH_INTERVAL_SEC = FLUSH_INTERVAL_SEC or int(os.getenv("FLUSH_INTERVAL_SEC") or 15)
        self.APP_CODE = APP_CODE or os.getenv("APP_CODE")
        self.ORACLE_DB_HOST = ORACLE_DB_HOST or os.getenv("ORACLE_DB_HOST")
        self.ORACLE_DB_PORT = ORACLE_DB_PORT or os.getenv("ORACLE_DB_PORT")
        self.ORACLE_DB_SERVICE = ORACLE_DB_SERVICE or os.getenv("ORACLE_DB_SERVICE")
        self.ORACLE_USER = ORACLE_USER or os.getenv("ORACLE_DB_USER")
        self.ORACLE_PASS = ORACLE_PASS or os.getenv("ORACLE_DB_PASS")
        self.ORACLE_DSN = ORACLE_DSN or self._build_dsn()
        # Local JSONL files for access/activity logs
        # Base file paths (we will write date-wise JSON files based on these names)
        self.LOCAL_ACCESS_LOG_FILE = LOCAL_ACCESS_LOG_FILE or os.getenv("LOCAL_ACCESS_LOG_FILE") or os.path.abspath(os.path.join(os.getcwd(), "app_access_logs.json"))
        self.LOCAL_ACTIVITY_LOG_FILE = LOCAL_ACTIVITY_LOG_FILE or os.getenv("LOCAL_ACTIVITY_LOG_FILE") or os.path.abspath(os.path.join(os.getcwd(), "app_activity_logs.json"))
        # Optional override for global config path
        self.GLOBAL_CONFIG_PATH = GLOBAL_CONFIG_PATH or os.getenv("GLOBAL_SERVICE_CONFIG_PATH")
        # Failed activity (DB) logs buffer file (JSONL)
        self.ACTIVITY_FAILED_LOG_FILE = ACTIVITY_FAILED_LOG_FILE or os.getenv("ACTIVITY_FAILED_LOG_FILE") or os.path.abspath(os.path.join(os.getcwd(), "app_failed_activity_logs.json"))

    def _build_dsn(self):
        if self.ORACLE_DB_HOST and self.ORACLE_DB_PORT and self.ORACLE_DB_SERVICE:
            return cx_Oracle.makedsn(
                self.ORACLE_DB_HOST,
                int(self.ORACLE_DB_PORT),
                service_name=self.ORACLE_DB_SERVICE
            )
        return None

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        # Rebuild DSN if any DB param is updated and DSN not set directly
        if any(k in kwargs for k in ["ORACLE_DB_HOST", "ORACLE_DB_PORT", "ORACLE_DB_SERVICE"]):
            self.ORACLE_DSN = self._build_dsn()

# Singleton config instance
config = GlobalServiceConfig()

################################ Read global service remote and local storage settings from global_config.properties ####################
def _find_global_config_path():
    """Resolve path to global_config.properties with reasonable fallbacks.
    Priority:
      1) Explicit config.GLOBAL_CONFIG_PATH if provided
      2) ENV GLOBAL_SERVICE_CONFIG_PATH
      3) CWD/global_config.properties (project root typical)
      4) Package directory/global_config.properties (legacy)
    """
    # 1 & 2 handled by config.GLOBAL_CONFIG_PATH (set from env in __init__)
    candidates = []
    if config.GLOBAL_CONFIG_PATH:
        candidates.append(config.GLOBAL_CONFIG_PATH)
    candidates.append(os.path.abspath(os.path.join(os.getcwd(), 'global_config.properties')))
    candidates.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'global_config.properties')))
    for p in candidates:
        try:
            if p and os.path.exists(p):
                return p
        except Exception:
            continue
    return candidates[-1]

def _read_global_flag(section_key: str, default: str = 'false') -> bool:
    parser = configparser.ConfigParser()
    config_path = _find_global_config_path()
    try:
        parser.read(config_path)
        value = parser.get('GLOBAL SERVICE', section_key, fallback=default)
        return str(value).strip().lower() == 'true'
    except Exception:
        return str(default).strip().lower() == 'true'

def get_global_service_remote_access_enabled():
    return _read_global_flag('GLOBAL_SERVICE_REMOTE_ACCESS', default='false')

def get_global_service_local_storage_enabled():
    return _read_global_flag('GLOBAL_SERVICE_LOCAL_STORAGE', default='false')

GLOBAL_SERVICE_REMOTE_ACCESS_ENABLED = get_global_service_remote_access_enabled()
GLOBAL_SERVICE_LOCAL_STORAGE_ENABLED = get_global_service_local_storage_enabled()

#####################################################################################

def flush_failed_logs():
    """
    Periodically send logs stored in the JSON file to the GLOBAL_LOG_URL.
    Only delete logs from the file after receiving a 200 OK response.
    """
    while True:
        try:
            if config.FAILED_LOG_FILE and os.path.exists(config.FAILED_LOG_FILE):
                with open(config.FAILED_LOG_FILE, "r+", encoding="utf-8") as f:
                    logs = f.readlines()
                    if logs:
                        remaining_logs = []
                        for log in logs:
                            try:
                                payload = json.loads(log.strip())
                                # Re-evaluate remote flag dynamically
                                if get_global_service_remote_access_enabled() and config.GLOBAL_LOG_URL:
                                    resp = requests.post(config.GLOBAL_LOG_URL, json=payload, timeout=2.0)
                                    if resp.status_code == 200:
                                        logging.info(f"Log sent successfully: {payload}")
                                    else:
                                        logging.warning(f"Failed to send log (status {resp.status_code}): {payload}")
                                        remaining_logs.append(log)  # Keep the log if not successful
                                else:
                                    # Remote access disabled; keep the logs in failed file
                                    remaining_logs.append(log)
                            except Exception as e:
                                logging.warning(f"Failed to resend log: {e}")
                                remaining_logs.append(log)  # Keep the log if an exception occurs
                        # Rewrite the file with remaining logs
                        f.seek(0)
                        f.truncate()
                        f.writelines(remaining_logs)
        except Exception as e:
            logging.error(f"Error in periodic log flushing: {e}")
        time.sleep(config.FLUSH_INTERVAL_SEC)  # Wait for the specified interval before retrying

# Start the background thread
threading.Thread(target=flush_failed_logs, daemon=True).start()

def flush_failed_activity_logs():
    """Periodically push failed activity (DB) logs from JSONL buffer into Oracle DB."""
    while True:
        try:
            path = config.ACTIVITY_FAILED_LOG_FILE
            if path and os.path.exists(path):
                with open(path, 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    if not lines:
                        time.sleep(config.FLUSH_INTERVAL_SEC)
                        continue
                    remaining = []
                    # Try to connect once per batch
                    try:
                        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
                        cursor = connection.cursor()
                        insert_sql = """
                        INSERT INTO LHSWMA_PY_WEB_ACTIVITY_LOGS (
                        ENTRY_ROWID_SEQ,  APP_CODE,LOGIN_RRN, ENDPOINT, LOG_TIMESTAMP, LOG_EVENT, LOG_EVENT_SLNO, LOG_REMARK, USER_CODE, LASTUPDATE, FLAG
                        )
                        VALUES (
                          LHSWMA_PY_WEB_ACTIVITY_LOGS_SEQ.NEXTVAL, :app_code, :login_rrn, :endpoint, SYSDATE, :log_event, :log_event_slno, :log_remark, :user_code, SYSDATE, :flag
                        )
                        """
                        for raw in lines:
                            try:
                                row = json.loads(raw.strip())
                                # Minimal validation
                                if not row.get('LOGIN_RRN'):
                                    remaining.append(raw)
                                    continue
                                cursor.execute(insert_sql, {
                                    'app_code': row.get('APP_CODE', config.APP_CODE),
                                    'login_rrn': row.get('LOGIN_RRN', ''),
                                    'endpoint': row.get('ENDPOINT', ''),
                                    'log_event': row.get('LOG_EVENT', 'INFO'),
                                    'log_event_slno': row.get('LOG_EVENT_SLNO', 0),
                                    'log_remark': row.get('LOG_REMARK', ''),
                                    'user_code': row.get('USER_CODE', ''),
                                    'flag': row.get('FLAG', 'T'),
                                })
                            except Exception as row_e:
                                logging.warning(f"Failed to flush activity row: {row_e}")
                                remaining.append(raw)
                        try:
                            connection.commit()
                        except Exception as commit_e:
                            logging.warning(f"Commit failed for activity flush: {commit_e}")
                            # If commit fails, keep all rows
                            remaining = lines
                    except Exception as conn_e:
                        logging.warning(f"Could not connect to Oracle for activity flush: {conn_e}")
                        remaining = lines
                    finally:
                        try:
                            if 'cursor' in locals():
                                cursor.close()
                        except Exception:
                            pass
                        try:
                            if 'connection' in locals():
                                connection.close()
                        except Exception:
                            pass
                    # Rewrite remaining
                    f.seek(0)
                    f.truncate()
                    f.writelines(remaining)
        except Exception as e:
            logging.error(f"Error in periodic activity log flushing: {e}")
        time.sleep(config.FLUSH_INTERVAL_SEC)

threading.Thread(target=flush_failed_activity_logs, daemon=True).start()

MACHINE_IP, MACHINE_HOSTNAME = MachineIPDetector().get_info()

# ── Step-wise Logger ─
class StepLogger:
    def __init__(self):
        self.steps = []

    def log(self, step_name):
        self.steps.append(step_name)  # Save step name directly without timestamp or numbering

    def get_log_remark(self):
        return "\n".join(self.steps)

def _is_flask_request(request) -> bool:
    # Heuristic: Flask request has headers attr and no META dict
    return hasattr(request, 'headers') and not hasattr(request, 'META')

def _get_flask_session():
    try:
        from flask import session as flask_session
        return flask_session
    except Exception:
        return {}

def get_real_client_ip(request):
    """Works for both Django and Flask request objects."""
    try:
        if _is_flask_request(request):
            xff = request.headers.get('X-Forwarded-For') or request.headers.get('X_FORWARDED_FOR')
            if xff:
                return xff.split(',')[0].strip()
            return request.headers.get('X-Real-IP') or getattr(request, 'remote_addr', '') or ''
        else:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0].strip()
            return request.META.get("REMOTE_ADDR", "")
    except Exception:
        return ""

def build_global_log_payload(request, user_menu=None, logout_time=None, logout_method=None, app_version=None, request_body=None, response_body=None):
    # Session abstraction for Flask/Django
    if _is_flask_request(request):
        sess = _get_flask_session()
        headers = getattr(request, 'headers', {})
        ua = headers.get('User-Agent', '')
        path = getattr(request, 'path', '')
    else:
        sess = getattr(request, 'session', {})
        headers = getattr(request, 'META', {})
        ua = headers.get('HTTP_USER_AGENT', '')
        path = getattr(request, 'path', '')

    client_ip = get_real_client_ip(request)
    # Prefer client_browser set in session, else header value
    browser_user_agent = sess.get("client_browser", "") if isinstance(sess, dict) else getattr(sess, 'get', lambda *_: '')("client_browser", "")
    if not browser_user_agent or str(browser_user_agent).lower().startswith("unknown"):
        browser_user_agent = ua

    get_sess = sess.get if isinstance(sess, dict) else (lambda k, d=None: getattr(sess, 'get')(k, d))

    payload = {
        "APP_CODE": config.APP_CODE,
        "LOGIN_RRN": get_sess("session_id", ""),
        "LOGIN_TIME": get_sess("last_login", ""),
        "LOGOUT_TIME": logout_time or "",
        "LOGOUT_METHOD": logout_method or "",
        "APP_VERSION": app_version if app_version is not None else get_app_version(),
        "GROUP_CODE": get_sess("group_code") or "LHS",
        "CLIENT_IP": get_sess("client_address") or client_ip,
        "CLIENT_HOSTNAME": get_sess("client_hostname") or MachineIPDetector().resolve_hostname(client_ip) if client_ip else "unknown",
        "CALLING_APP_NAME": get_sess("calling_app_name", ""),
        "SERVER_HOSTNAME": get_sess("server_hostname") or MACHINE_HOSTNAME,
        "BROWSER_USER_AGENT": get_sess("client_browser") or browser_user_agent,
        "USER_USED_MENU": user_menu or path,
        "USER_CODE": get_sess("user_code", ""),
        "LASTUPDATE": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "APPKEY": get_sess("appkey", ""),
        "CALLING_APP_NAME": get_sess("calling_app_name", ""),
    }
    return payload

def _ensure_dir_for(path: str):
    dir_name = os.path.dirname(os.path.abspath(path))
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

def _datewise_path(base_file_path: str) -> str:
    """Return a file path with _YYYY-MM-DD before extension for date-wise logs."""
    base_file_path = os.path.abspath(base_file_path)
    root, ext = os.path.splitext(base_file_path)
    if not ext:
        ext = '.json'
    date_str = datetime.now().strftime('%Y-%m-%d')
    return f"{root}_{date_str}{ext}"

def _append_json_daily(file_base_path: str, obj: dict):
    """Append an object to a date-wise JSON array file.
    Creates the file with a JSON array if it doesn't exist.
    """
    try:
        daily_path = _datewise_path(file_base_path)
        _ensure_dir_for(daily_path)
        # Read existing array if present
        data = []
        if os.path.exists(daily_path):
            try:
                with open(daily_path, 'r', encoding='utf-8') as rf:
                    content = rf.read().strip()
                    if content:
                        data = json.loads(content)
                        if not isinstance(data, list):
                            # If file somehow isn't a list, wrap it
                            data = [data]
            except Exception:
                # If read/parse fails, start fresh but log the issue
                logging.warning(f"Corrupt JSON in {daily_path}; recreating file")
                data = []
        data.append(obj)
        with open(daily_path, 'w', encoding='utf-8') as wf:
            json.dump(data, wf, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to append to daily JSON file based on {file_base_path}: {e}")

def save_access_log_locally(payload: dict):
    """Persist the high-level access log payload as JSONL when local storage is enabled."""
    if not payload:
        return
    try:
        _append_json_daily(config.LOCAL_ACCESS_LOG_FILE, payload)
    except Exception:
        logging.exception("save_access_log_locally: failed")

def send_log_to_global_service(payload: dict):
    # Always save locally if local storage is enabled (independent of remote flag)
    if get_global_service_local_storage_enabled():
        save_access_log_locally(payload)
    # Optionally send remote based on flag
    if not get_global_service_remote_access_enabled():
        logging.debug("Remote access disabled by config; skipping remote send")
        return
    try:
        # Only process logs where LOGIN_RRN is not null or empty
        if payload.get("LOGIN_RRN") and config.GLOBAL_LOG_URL:
            resp = requests.post(config.GLOBAL_LOG_URL, json=payload, timeout=2.0)
            resp.raise_for_status()
    except Exception as e:
        logging.warning(f"Failed to send log to {config.GLOBAL_LOG_URL}, saving locally. Reason: {e}")
        try:
            # Save log locally only if LOGIN_RRN is not null or empty
            if payload.get("LOGIN_RRN") and config.FAILED_LOG_FILE:
                # Keep failed logs as JSONL for lightweight retry
                try:
                    # Ensure directory exists if a directory is provided
                    _ensure_dir_for(config.FAILED_LOG_FILE)
                    with open(config.FAILED_LOG_FILE, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
                except Exception as inner:
                    logging.error(f"Could not save failed log to file: {inner}")
        except Exception as e2:
            logging.error(f"Could not save failed log to file: {e2}")

# ── Oracle DB Logging ─
def save_step_logs_to_oracle(payload: dict, step_logger: 'StepLogger', request_body: str, response_body: str, log_type="INFO"):
    """
    Save each step in StepLogger as a separate row in LHSWMA_PY_WEB_ACTIVITY_LOGS.
    Prevent duplicate logs for the same session, endpoint, and step_name.
    """
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        insert_sql = """
        INSERT INTO LHSWMA_PY_WEB_ACTIVITY_LOGS (
        ENTRY_ROWID_SEQ,  APP_CODE,LOGIN_RRN, ENDPOINT, LOG_TIMESTAMP, LOG_EVENT, LOG_EVENT_SLNO, LOG_REMARK, USER_CODE, LASTUPDATE, FLAG
        )
        VALUES (
          LHSWMA_PY_WEB_ACTIVITY_LOGS_SEQ.NEXTVAL, :app_code, :login_rrn, :endpoint, SYSDATE, :log_event, :log_event_slno, :log_remark, :user_code, SYSDATE, :flag
        )
        """
        check_sql = """
        SELECT COUNT(*) FROM LHSWMA_PY_WEB_ACTIVITY_LOGS
        WHERE LOGIN_RRN = :login_rrn
          AND ENDPOINT = :endpoint
          AND LOG_EVENT_SLNO = :log_event_slno
          AND LOG_REMARK = :log_remark
        """
        for idx, entry in enumerate(step_logger.steps, start=1):
            step_name = entry
            cursor.execute(check_sql, {
                "login_rrn": payload.get("LOGIN_RRN", ""),
                "endpoint": payload.get("ENDPOINT", ""),
                "log_event_slno": idx,
                "log_remark": step_name,
            })
            exists = cursor.fetchone()[0]
            if not exists:
                cursor.execute(insert_sql, {
                    "app_code": payload.get("APP_CODE", config.APP_CODE),
                    "login_rrn": payload.get("LOGIN_RRN", ""),
                    "endpoint": payload.get("ENDPOINT", ""),
                    "log_event": log_type,
                    "log_event_slno": idx,
                    "log_remark": step_name,
                    "user_code": payload.get("USER_CODE", ""),
                    "flag": payload.get("FLAG", "T"),
                })
        connection.commit()
    except Exception as e:
        logging.error(f"Failed to save step logs to Oracle DB: {e}")
        # Persist failed activity rows locally for later flush
        try:
            # Prepare per-step rows mirroring the DB insert schema
            base = {
                "APP_CODE": payload.get("APP_CODE", config.APP_CODE),
                "LOGIN_RRN": payload.get("LOGIN_RRN", ""),
                "ENDPOINT": payload.get("ENDPOINT", ""),
                "LOG_EVENT": log_type,
                "USER_CODE": payload.get("USER_CODE", ""),
                "FLAG": payload.get("FLAG", "T"),
            }
            if base["LOGIN_RRN"] and config.ACTIVITY_FAILED_LOG_FILE:
                for idx, entry in enumerate(step_logger.steps, start=1):
                    row = dict(base)
                    row.update({
                        "LOG_EVENT_SLNO": idx,
                        "LOG_REMARK": entry,
                        "REQUEST_BODY": request_body or "",
                        "RESPONSE_BODY": response_body or "",
                        "LASTUPDATE": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    })
                    try:
                        _ensure_dir_for(config.ACTIVITY_FAILED_LOG_FILE)
                        with open(config.ACTIVITY_FAILED_LOG_FILE, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    except Exception as e2:
                        logging.error(f"Could not append failed activity row: {e2}")
        except Exception:
            logging.exception("Error while storing failed activity logs locally")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    # Clear logged steps to avoid duplicate inserts in subsequent calls
    step_logger.steps.clear()

def save_step_logs_to_local(payload: dict, step_logger: 'StepLogger', request_body: str, response_body: str, log_type="INFO"):
    """Save step-wise activity logs in JSONL locally when enabled."""
    try:
        if not get_global_service_local_storage_enabled():
            return
        base = {
            "APP_CODE": payload.get("APP_CODE", config.APP_CODE),
            "LOGIN_RRN": payload.get("LOGIN_RRN", ""),
            "ENDPOINT": payload.get("ENDPOINT", ""),
            "USER_CODE": payload.get("USER_CODE", ""),
            "FLAG": payload.get("FLAG", "T"),
            "LOG_EVENT": log_type,
            "LASTUPDATE": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        }
        for idx, entry in enumerate(step_logger.steps, start=1):
            row = dict(base)
            row.update({
                "LOG_EVENT_SLNO": idx,
                "LOG_REMARK": entry,
                "REQUEST_BODY": request_body or "",
                "RESPONSE_BODY": response_body or "",
            })
            _append_json_daily(config.LOCAL_ACTIVITY_LOG_FILE, row)
    except Exception:
        logging.exception("save_step_logs_to_local: failed")
    finally:
        # Do not clear here; let Oracle saver or composite clear after all writes
        pass

def save_step_logs(payload: dict, step_logger: 'StepLogger', request_body: str, response_body: str, log_type="INFO"):
    """Composite saver that writes activity logs locally (if enabled) and to Oracle DB regardless of local flag.
    Local write is controlled by GLOBAL_SERVICE_LOCAL_STORAGE flag. DB write is always attempted.
    """
    # Local first for durability (if enabled)
    try:
        save_step_logs_to_local(payload, step_logger, request_body, response_body, log_type)
    except Exception:
        logging.exception("save_step_logs: local save failed")
    # Oracle next (always attempt)
    try:
        save_step_logs_to_oracle(payload, step_logger, request_body, response_body, log_type)
    except Exception:
        logging.exception("save_step_logs: save_step_logs_to_oracle failed")
    finally:
        # Ensure steps are cleared to avoid duplicates in subsequent calls
        step_logger.steps.clear()

#### Admin Menu Utility ####
def is_user_blocked(user_code):
    from .admin_utils import is_user_blocked as _is_user_blocked
    return _is_user_blocked(user_code)

def is_admin_and_get_menus(user_code):
    from .admin_utils import is_admin_and_get_menus as _is_admin_and_get_menus
    return _is_admin_and_get_menus(user_code)

def is_super_admin_and_get_menus(user_code):
    from .admin_utils import is_super_admin_and_get_menus as _is_super_admin_and_get_menus
    return _is_super_admin_and_get_menus(user_code)

