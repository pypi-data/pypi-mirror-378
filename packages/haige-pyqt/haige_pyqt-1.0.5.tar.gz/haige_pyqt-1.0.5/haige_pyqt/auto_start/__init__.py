# 根据操作系统导入相应的自启动函数
import sys

if sys.platform == "win32":
    from haige_pyqt.auto_start.win import enable_autostart, disable_autostart, is_autostart_enabled
elif sys.platform == "darwin":
    from haige_pyqt.auto_start.macos import enable_autostart, disable_autostart, is_autostart_enabled
else:
    from haige_pyqt.auto_start.linux import enable_autostart, disable_autostart, is_autostart_enabled


class AutoStarter:
    def __init__(self, app_name, app_path):
        self._app_name = app_name
        self._app_path = app_path

    def enable(self):
        return enable_autostart(self._app_name, self._app_path)

    def disable(self):
        return disable_autostart(self._app_name)

    def is_enabled(self):
        return is_autostart_enabled(self._app_name)
