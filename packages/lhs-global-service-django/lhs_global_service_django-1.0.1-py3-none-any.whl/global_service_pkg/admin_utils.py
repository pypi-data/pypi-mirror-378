import cx_Oracle
import logging
from . import config

def is_user_blocked(user_code):
    try:
        connection = cx_Oracle.connect(
            user=config.ORACLE_USER,
            password=config.ORACLE_PASS,
            dsn=config.ORACLE_DSN
        )
        cursor = connection.cursor()
        query = """
            SELECT COUNT(*) FROM lhswma_py_blocked_users
            WHERE user_code = :user_code AND app_code = :app_code
        """
        cursor.execute(query, {"user_code": user_code, "app_code": config.APP_CODE})
        result = cursor.fetchone()[0]
        return result > 0
    except Exception as e:
        logging.error(f"Error checking blocked user: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def is_admin_and_get_menus(user_code):
    """
    Check if user is admin and return allowed APP_MENU list for the user.
    Returns a list of menu codes (split by #), or empty list if not admin.
    """
    try:
        connection = cx_Oracle.connect(
            user=config.ORACLE_USER,
            password=config.ORACLE_PASS,
            dsn=config.ORACLE_DSN
        )
        cursor = connection.cursor()
        query = """
            SELECT APP_MENU FROM LHSWMA_PY_APP_ADMIN_CONTROL
            WHERE USER_CODE = :user_code AND APP_CODE = :app_code
        """
        cursor.execute(query, {"user_code": user_code, "app_code": config.APP_CODE})
        row = cursor.fetchone()
        if row and row[0]:
            # Split by # and remove empty strings/spaces
            return [menu.strip() for menu in row[0].split('#') if menu.strip()]
        return []
    except Exception as e:
        logging.error(f"Error checking admin menus for user {user_code}: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def is_super_admin_and_get_menus(user_code):
    """
    Check if user is super admin and return allowed APP_MENU list for the user.
    Returns a list of menu codes (split by #), or empty list if not super admin.
    """
    try:
        connection = cx_Oracle.connect(
            user=config.ORACLE_USER,
            password=config.ORACLE_PASS,
            dsn=config.ORACLE_DSN
        )
        cursor = connection.cursor()
        query = """
            SELECT APP_MENU FROM LHSWMA_PY_SUPER_APP_ADMIN_CONTROL
            WHERE USER_CODE = :user_code AND APP_CODE = :app_code
        """
        cursor.execute(query, {"user_code": user_code, "app_code": config.APP_CODE})
        row = cursor.fetchone()
        if row and row[0]:
            # Split by # and remove empty strings/spaces
            return [menu.strip() for menu in row[0].split('#') if menu.strip()]
        return []
    except Exception as e:
        logging.error(f"Error checking admin menus for user {user_code}: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
