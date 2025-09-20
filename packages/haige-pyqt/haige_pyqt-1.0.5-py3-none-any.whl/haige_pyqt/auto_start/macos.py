import os
import plistlib


def enable_autostart_macos(app_name, app_path):
    """在macOS上启用开机自启动"""
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    plist_path = os.path.join(launch_agents_dir, f"com.{app_name}.plist")

    # 确保目录存在
    os.makedirs(launch_agents_dir, exist_ok=True)

    # 创建plist文件
    plist_content = {
        "Label": f"com.{app_name}",
        "Program": app_path,
        "RunAtLoad": True,
        "KeepAlive": False,
    }

    with open(plist_path, "wb") as f:
        plistlib.dump(plist_content, f)

    return True


def disable_autostart_macos(app_name):
    """在macOS上禁用开机自启动"""
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{app_name}.plist")
    if os.path.exists(plist_path):
        os.remove(plist_path)
        return True
    return False
