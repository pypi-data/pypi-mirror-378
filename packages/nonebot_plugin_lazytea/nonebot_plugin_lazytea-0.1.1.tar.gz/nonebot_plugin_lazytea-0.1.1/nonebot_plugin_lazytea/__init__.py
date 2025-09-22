import subprocess
import time
from nonebot import get_driver, logger, require
require("nonebot_plugin_uninfo")  # noqa
require("nonebot_plugin_localstore")  # noqa
require("nonebot_plugin_alconna")  # noqa


from .bridge import for_import as _  # noqa
from .ipc import server, Server  # noqa
from .utils.commute import server_send_queue  # noqa
from .utils.config import Config  # noqa
from .utils.config import _config as config  # noqa
from nonebot.plugin import PluginMetadata, inherit_supported_adapters  # noqa
from nonebot.drivers import ASGIMixin, WebSocket, WebSocketServerSetup, URL  # noqa
import asyncio  # noqa
import os  # noqa
from pathlib import Path  # noqa
import sys  # noqa
from importlib.resources import files, as_file  # noqa


import nonebot_plugin_localstore    # noqa

__version__ = "0.1.1"
__author__ = "hlfzsi"

try:
    resource_ref = files(__package__).joinpath("ui", "resources", "app.ico")
    with as_file(resource_ref) as icon_file:
        _icon_path = str(icon_file) if icon_file.is_file() else ""
except Exception:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)  # type: ignore
        _icon_path = str(base_path / "ui" / "resources" / "app.ico")
        if not Path(_icon_path).is_file():
            _icon_path = ""
    else:
        base_path = Path(__file__).parent
        _icon_path = str(base_path / "ui" / "resources" / "app.ico")
        if not Path(_icon_path).is_file():
            _icon_path = ""
    del base_path


__plugin_meta__ = PluginMetadata(
    name="LazyTea",
    description="图形化管理您的NoneBot--今天也来杯红茶吗?",
    usage="开箱即用!",
    type="application",
    homepage="https://github.com/hlfzsi/nonebot_plugin_lazytea",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_uninfo", "nonebot_plugin_localstore", "nonebot_plugin_alconna"),

    extra={
        "version": __version__,  # 用于在插件界面中显示版本与版本更新检查
        "author": __author__,   # 用于在插件界面中显示作者
        "icon_abspath": _icon_path  # 用于在插件界面中自定义插件图标 ，仅支持绝对路径
    }
)


driver = get_driver()
ui_process = None
send_task = None


@driver.on_startup
async def pre():
    async def websocket_endpoint(ws: WebSocket):
        await server.start(ws, config.get_token())
    if isinstance(driver, ASGIMixin):
        driver.setup_websocket_server(
            WebSocketServerSetup(
                path=URL("/plugin_GUI"),
                name="ui_ws",
                handle_func=websocket_endpoint,
            )
        )
    global ui_process, send_task
    script_dir = Path(__file__).parent.resolve()
    ui_env = os.environ.copy()
    ui_env["PORT"] = str(config.port)
    ui_env["TOKEN"] = str(config.get_token())
    ui_env["UIVERSION"] = __version__
    ui_env["UIAUTHOR"] = __author__
    ui_env["LOGLEVEL"] = str(config.log_level)
    ui_env["UIDATADIR"] = str(
        nonebot_plugin_localstore.get_plugin_data_dir())

    ui_env["LAUNCHASCHILD"] = "true"

    creation_flags = {}
    if sys.platform == "win32":
        creation_flags['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        creation_flags['start_new_session'] = True

    if not config.headless:
        ui_process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "ui.main_window",
            cwd=script_dir,
            env=ui_env,
            stdin=asyncio.subprocess.PIPE,
            **creation_flags
        )

    async def send_data(server: Server, queue: asyncio.Queue):
        try:
            while True:
                type, data = await queue.get()
                await server.broadcast(type, data)
        except asyncio.CancelledError:
            pass

    send_task = asyncio.create_task(send_data(server, server_send_queue))
    server.start_time = time.time()
    asyncio.create_task(server.clear_transient_buffer_after_delay())


@driver.on_shutdown
async def cl():
    global send_task, ui_process
    if send_task:
        send_task.cancel()

    if ui_process:

        if ui_process.stdin and ui_process.returncode is None:
            try:
                ui_process.stdin.write(b"shutdown\n")
                await ui_process.stdin.drain()
                ui_process.stdin.close()
            except (BrokenPipeError, ConnectionResetError):
                pass

        try:
            await asyncio.wait_for(ui_process.wait(), timeout=5.0)
        except asyncio.TimeoutError:

            logger.warning("UI 进程未能及时退出，将强制终止。")
            ui_process.kill()
            await ui_process.wait()

    ui_process = None
    send_task = None
