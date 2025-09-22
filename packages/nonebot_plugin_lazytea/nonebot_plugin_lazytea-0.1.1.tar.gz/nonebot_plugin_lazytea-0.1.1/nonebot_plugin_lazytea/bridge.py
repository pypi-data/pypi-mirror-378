import time
from threading import Lock
import orjson
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from nonebot import get_driver, logger
from nonebot.typing import T_State
from nonebot.exception import IgnoredException
from nonebot.internal.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.message import event_preprocessor, run_preprocessor, run_postprocessor
from nonebot_plugin_alconna import UniMessage, Segment
from nonebot_plugin_alconna.uniseg.segment import (
    Text, At, AtAll, Emoji,
    Image, Audio, Voice, Video, File,
    Reply, Reference,
    Hyper, Button, Keyboard, Other, I18n
)
from nonebot_plugin_uninfo import Uninfo, get_interface
from nonebot_plugin_uninfo.adapters import alter_get_fetcher
from .utils.commute import send_event, bot_off_line
from .utils.parse import get_function_fingerprint
from .utils.roster import FuncTeller, RuleData

driver = get_driver()


_bot_avatar_cache: Dict[str, Optional[str]] = {}
_bot_avatar_cache_lock = Lock()


async def fetch_bot_avatar(bot: Bot) -> Optional[str]:
    bot_id = bot.self_id
    with _bot_avatar_cache_lock:
        if bot_id in _bot_avatar_cache:
            return _bot_avatar_cache[bot_id]

    avatar = None
    try:
        interface = get_interface(bot)
        if interface:
            bot_user = await interface.get_user(bot_id)
            avatar = bot_user.avatar if bot_user else None
    except Exception as e:
        logger.error(f"获取 {bot_id} 的头像时出现错误: {e}")

    with _bot_avatar_cache_lock:
        _bot_avatar_cache[bot_id] = avatar
    return avatar


def get_bot_avatar(bot_id: str) -> Optional[str]:
    with _bot_avatar_cache_lock:
        return _bot_avatar_cache.get(bot_id)


class UniMessageMarkdownConverter:
    """
    一个将 UniMessage 对象转换为 Markdown 字符串的转换器。

    使用方法:
    converter = UniMessageMarkdownConverter()
    markdown_list = converter.convert(uni_message_object)  # 返回 (消息类型, md字符串) 的列表
    """

    def __init__(self):
        self._handlers: Dict[Type[Segment], Callable[[Any], str]] = {
            Text: self._handle_text,
            At: self._handle_at,
            AtAll: self._handle_at_all,
            Emoji: self._handle_emoji,
            Image: self._handle_image,
            Voice: self._handle_media,
            Audio: self._handle_media,
            Video: self._handle_media,
            File: self._handle_media,
            Reply: self._handle_reply,
            Reference: self._handle_reference,
            Hyper: self._handle_hyper,
            Keyboard: self._handle_keyboard,
            Button: self._handle_button,
            I18n: self._handle_i18n,
            Other: self._handle_other,
        }

    def convert(self, message: Union[UniMessage, str]) -> List[Tuple[str, str]]:
        """
        将 UniMessage 转换为 (消息类型, Markdown字符串) 的列表

        Args:
            message: UniMessage 对象 或 纯文本

        Returns:
            包含元组的列表，每个元组格式为 (消息类型, 转换后的Markdown字符串)
        """
        if not message:
            return []

        if isinstance(message, str):
            return [("text", self._handle_text(Text(message)))]

        result = []
        for segment in message:
            seg_type = type(segment).__name__.lower()
            handler = self._handlers.get(type(segment), self._handle_default)
            md_str = handler(segment)
            result.append((seg_type, md_str))

        return result

    def _handle_default(self, seg: Segment) -> str:
        return f"[{seg.__class__.__name__}]"

    def _handle_text(self, seg: Text) -> str:
        text = seg.text.replace("\n", "  \n")
        if not seg.styles:
            return text

        style_map = {"bold": "**", "italic": "*",
                     "strikethrough": "~~", "spoiler": "||", "code": "`"}

        sorted_styles = sorted(
            seg.styles.items(), key=lambda x: (x[0][0], -x[0][1]))
        parts = list(text)
        for (start, end), styles in reversed(sorted_styles):
            prefix, suffix = "", ""
            for style_name in styles:
                if mark := style_map.get(style_name):
                    prefix += mark
                    suffix = mark + suffix
            if prefix:
                parts.insert(end, suffix)
                parts.insert(start, prefix)

        return "".join(parts)

    def _handle_at(self, seg: At) -> str:
        return f"**@{seg.display or seg.target}**"

    def _handle_at_all(self, seg: AtAll) -> str:
        return "**@全体成员**" if not seg.here else "**@在线成员**"

    def _handle_emoji(self, seg: Emoji) -> str:
        return f"[表情:{seg.name or seg.id}]"

    def _handle_image(self, seg: Image) -> str:
        alt_text = seg.name if seg.name != seg.__default_name__ else "图片"
        url = seg.url or seg.path or ""
        return f"![{alt_text}]({url})"

    def _handle_media(self, seg: Union[Voice, Audio, Video, File]) -> str:
        type_map = {Voice: "语音", Audio: "音频", Video: "视频", File: "文件"}
        seg_type = type(seg)
        type_name = type_map.get(seg_type, "媒体")

        if seg_type is File and seg.name != seg.__default_name__:
            return f"[{type_name}: {seg.name}]"

        if seg.url:
            return f"[{type_name}]({seg.url})"

        return f"[{type_name}]"

    def _handle_reply(self, seg: Reply) -> str:
        return f"↩️ [回复给: {seg.id}] "

    def _handle_reference(self, seg: Reference) -> str:
        count = len(seg.children)
        return f"📨 [合并转发 (共 {count} 条)]"

    def _handle_hyper(self, seg: Hyper) -> str:
        return f"[卡片消息: {seg.format.upper()}]"

    def _handle_button(self, seg: Button) -> str:
        label = seg.label.text if isinstance(
            seg.label, Text) else str(seg.label)
        flag_map = {
            "action": f"操作:{seg.id}", "link": f"链接:{seg.url}",
            "input": f"输入:{seg.text}", "enter": f"发送:{seg.text}",
        }
        return f"`{label}` ({flag_map.get(seg.flag, '未知')})"

    def _handle_keyboard(self, seg: Keyboard) -> str:
        if not seg.children:
            return "[按钮组]"

        buttons_md = "\n".join(
            f"- {self._handle_button(btn)}" for btn in seg.children)
        return f"\n> **按钮组**\n{buttons_md}"

    def _handle_other(self, seg: Other) -> str:
        return f"[未知类型: {seg.origin.type}]"

    def _handle_i18n(self, seg: I18n) -> str:
        try:
            return str(seg)
        except Exception as e:
            return f"[i18n: {seg.item.scope}.{seg.item.type} error: {e}]"


markdown_converter = UniMessageMarkdownConverter()


@event_preprocessor
async def record_event(bot: Bot, event: Event, session: Uninfo):
    if bot.self_id in bot_off_line[session.scope]:
        raise IgnoredException(f"{bot.self_id}已经下线")

    type = event.get_type()
    if type == "message":

        group_id = session.scene.id
        user_id = session.user.id
        avatar = session.user.avatar
        message = event.get_message()
        unimsg = UniMessage.of(message, bot, bot.adapter.get_name())
        content_md = markdown_converter.convert(unimsg)

        # session
        group_record = "群聊: " + group_id if group_id is not None else "私信"
        user_record = f"用户: {session.user.nick or ''} | {user_id}"

        data = {
            "bot": bot.self_id,
            "content": content_md,
            "userid": user_id,
            "session": group_record + " | " + user_record,
            "avatar": avatar,
            "groupid": group_id,
            "time": int(time.time())
        }

        await send_event(type, data)


@run_preprocessor
async def run_pre(bot: Bot, matcher: Matcher, state: T_State, session: Uninfo):
    group_id = session.scene.id
    user_id = session.user.id
    plugin_name = matcher.plugin_name or "Unknown"

    current_rule = RuleData.extract_rule(matcher)
    standard_model = await FuncTeller.get_model()
    permission = standard_model.perm(bot.self_id, plugin_name,
                                     user_id, group_id, current_rule)

    if not permission:
        logger.debug("消息被LazyTea拦截")
        raise IgnoredException("LazyTea命令开关判断跳过")

    state[f"UI{plugin_name}{hash(matcher)}"] = time.time()


@run_postprocessor
async def run_post(bot: Bot, matcher: Matcher, exception: Optional[Exception], state: T_State, session: Uninfo):
    try:
        current_time = time.time()
        plugin_name = matcher.plugin_name or "Unknown"
        time_costed = current_time-state[f"UI{plugin_name}{hash(matcher)}"]
        group_id = session.scene.id
        user_id = session.user.id

        special = [i.call for i in matcher.handlers]
        special = [get_function_fingerprint(plugin_name, i) for i in special]

        data = {
            "bot": bot.self_id,
            "platform": session.scope,
            "adapter": session.adapter,
            "time_costed": time_costed,
            "time": int(current_time),
            "groupid": group_id,
            "userid": user_id,
            "plugin": plugin_name,
            "matcher_hash": special,
            "exception": {"name": type(exception).__name__ if exception else None,
                          "detail": str(exception) if exception else None}
        }
        await send_event("plugin_call", data)
    except Exception as e:
        logger.warning(f"记录插件调用数据失败 {e}")


@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: Dict[str, Any]):
    # PR welcome
    # 欢迎贡献你使用的适配器的实现
    # 实验性支持，目前已尝试支持ob11/QQApi/telegram
    avatar = get_bot_avatar(bot.self_id)

    if api == "send_msg":
        # ob11
        if msg := data.get("message"):
            message_to_send = UniMessage.of(msg)
        else:
            logger.warning(f"调用{api}时没有获得message")
            return

        content_md = markdown_converter.convert(message_to_send)

        data_to_send = {
            "api": api,
            "content": content_md,
            "bot": bot.self_id,
            "session": f'{data.get("group_id", "Unknown")}-{data.get("user_id", "Unknown")}',
            "groupid": data.get("group_id", "Unknown"),
            "time": int(time.time()),
            "avatar": avatar
        }
        await send_event("call_api", data_to_send)

    elif api in {"post_c2c_messages", "post_group_messages"}:
        # QQapi 私聊/群聊
        if msg := data.get("content"):
            if isinstance(msg, str):
                content_md = markdown_converter.convert(msg)
            else:
                content_md = markdown_converter.convert(UniMessage.of(msg))
        else:
            logger.warning(f"调用{api}没有获得content")
            return

        user_id = data.get("openid", "Unknown")
        group_id = data.get("group_openid", "私聊")

        data_to_send = {
            "api": api,
            "content": content_md,
            "bot": bot.self_id,
            "session": f'{user_id}-{group_id}',
            "groupid": group_id,
            "time": int(time.time()),
            "avatar": avatar
        }
        await send_event("call_api", data_to_send)

    elif api == "send_message":
        # telegram
        if msg := data.get("text"):
            if isinstance(msg, str):
                content_md = markdown_converter.convert(msg)
            else:
                content_md = markdown_converter.convert(UniMessage.of(msg))
        else:
            logger.warning(f"调用{api}没有获得text")
            return

        union_id = data.get("chat_id", "Unknown")

        data_to_send = {
            "api": api,
            "content": content_md,
            "bot": bot.self_id,
            "session": union_id,
            "groupid": union_id,
            "time": int(time.time()),
            "avatar": avatar
        }
        await send_event("call_api", data_to_send)

    else:
        truncated_data = {}
        for key, value in data.items():
            value_str = str(value)
            if len(value_str) > 60:
                truncated_data[key] = value_str[:57] + "..."
            else:
                truncated_data[key] = value_str

        formatted_data = orjson.dumps(
            truncated_data, option=orjson.OPT_INDENT_2).decode("utf-8")

        logger.debug(f"未捕获的api调用: {api}\n{formatted_data}")

        # else:
        #    data_to_send = {
        #        "api": api,
        #        "bot": bot.self_id,
        #        "time": int(time.time())
        #    }
        # await send_event("call_api", data_to_send)


@driver.on_bot_connect
async def track_connect(bot: Bot):
    basefetcher = alter_get_fetcher(bot.adapter.get_name())
    await fetch_bot_avatar(bot)
    if not basefetcher:
        logger.warning(f"不受支持的适配器{bot.adapter.get_name()}")
        return
    baseinfo = basefetcher.supply_self(bot)

    data = {
        "bot": baseinfo["self_id"],
        "adapter": baseinfo["adapter"],
        "platform": baseinfo["scope"],
        "time": int(time.time())
    }
    await send_event("bot_connect", data)


@driver.on_bot_disconnect
async def track_disconnect(bot: Bot):
    basefetcher = alter_get_fetcher(bot.adapter.get_name())
    if not basefetcher:
        logger.warning(f"不受支持的适配器{bot.adapter.get_name()}")
        return
    baseinfo = basefetcher.supply_self(bot)

    data = {
        "bot": baseinfo["self_id"],
        "adapter": baseinfo["adapter"],
        "platform": baseinfo["scope"],
        "time": int(time.time())
    }
    await send_event("bot_disconnect", data)

for_import = None
