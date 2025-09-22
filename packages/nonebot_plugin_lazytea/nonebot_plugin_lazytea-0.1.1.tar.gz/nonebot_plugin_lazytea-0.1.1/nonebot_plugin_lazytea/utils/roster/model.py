from typing import Dict, Set, Tuple, Optional, FrozenSet, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer, model_serializer
from nonebot.matcher import Matcher
from nonebot.rule import (
    CommandRule, ShellCommandRule, RegexRule, KeywordsRule,
    StartswithRule, EndswithRule, FullmatchRule, IsTypeRule, ToMeRule
)
from nonebot_plugin_alconna.rule import AlconnaRule
import orjson
import xxhash


class RuleData(BaseModel):
    """规则数据模型，支持序列化和比较"""
    commands: FrozenSet[Tuple[str, ...]] = Field(default_factory=frozenset)
    shell_commands: FrozenSet[Tuple[str, ...]
                              ] = Field(default_factory=frozenset)
    regex_patterns: FrozenSet[str] = Field(default_factory=frozenset)
    keywords: FrozenSet[str] = Field(default_factory=frozenset)
    startswith: FrozenSet[str] = Field(default_factory=frozenset)
    endswith: FrozenSet[str] = Field(default_factory=frozenset)
    fullmatch: FrozenSet[str] = Field(default_factory=frozenset)
    alconna_commands: FrozenSet[str] = Field(default_factory=frozenset)
    event_types: FrozenSet[str] = Field(default_factory=frozenset)
    to_me: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer('commands', 'shell_commands')
    def serialize_commands(self, value: FrozenSet[Tuple[str, ...]], _info) -> List[List[str]]:
        return [list(cmd) for cmd in value]

    @field_serializer('regex_patterns', 'keywords', 'startswith', 'endswith', 'fullmatch', 'event_types', 'alconna_commands')
    def serialize_frozenset(self, value: FrozenSet[str], _info) -> List[str]:
        return list(value)

    def _quick_hash(self) -> int:
        """
        快速哈希方法，用于运行时内存操作。
        """
        return hash((
            self.commands,
            self.shell_commands,
            self.regex_patterns,
            self.keywords,
            self.startswith,
            self.endswith,
            self.fullmatch,
            self.alconna_commands,
            self.event_types,
            self.to_me
        ))

    def _persist_hash(self) -> int:
        """
        持久化哈希方法，用于存储或跨进程通信。
        保证哈希值在不同环境、不同时间下的一致性。
        """
        hash_obj = xxhash.xxh64()
        all_data = []
        for cmd in self.commands:
            all_data.append(f"cmd:{str(tuple(cmd))}")
        for shell_cmd in self.shell_commands:
            all_data.append(f"scmd:{str(tuple(shell_cmd))}")
        for pattern in self.regex_patterns:
            all_data.append(f"re:{pattern}")
        for keyword in self.keywords:
            all_data.append(f"kw:{keyword}")
        for prefix in self.startswith:
            all_data.append(f"sw:{prefix}")
        for suffix in self.endswith:
            all_data.append(f"ew:{suffix}")
        for full in self.fullmatch:
            all_data.append(f"fm:{full}")
        for event_type in self.event_types:
            all_data.append(f"evt:{event_type}")
        for alc_cmd in self.alconna_commands:
            all_data.append(f"alc:{alc_cmd}")
        all_data.append(f"tome:{str(self.to_me)}")

        all_data.sort()

        for item in all_data:
            hash_obj.update(item.encode('utf-8'))

        return int.from_bytes(hash_obj.digest(), byteorder='big')

    def __hash__(self) -> int:
        return self._quick_hash()

    @field_validator(
        "commands", "shell_commands", "regex_patterns", "keywords",
        "startswith", "endswith", "fullmatch", "event_types", "alconna_commands",
        mode="before"
    )
    @classmethod
    def ensure_frozenset(cls, v: Any) -> FrozenSet:
        """确保输入数据转换为不可变集合"""
        if v is None:
            return frozenset()
        if isinstance(v, (set, list, tuple)):
            return frozenset(v)
        if isinstance(v, frozenset):
            return v
        return frozenset({v})

    @classmethod
    def extract_rule(cls, matcher: Matcher) -> "RuleData":
        """从Matcher对象中提取规则数据"""
        commands = set()
        shell_commands = set()
        regex_patterns = set()
        keywords = set()
        startswith = set()
        endswith = set()
        fullmatch = set()
        event_types = set()
        alconna_commands = set()
        to_me = False

        for checker in matcher.rule.checkers:
            if not hasattr(checker, "call"):
                continue

            rule_call = checker.call

            if isinstance(rule_call, CommandRule):
                commands.update(tuple(cmd) for cmd in rule_call.cmds)
            elif isinstance(rule_call, ShellCommandRule):
                shell_commands.update(tuple(cmd) for cmd in rule_call.cmds)
            elif isinstance(rule_call, RegexRule):
                regex_patterns.add(rule_call.regex)
            elif isinstance(rule_call, KeywordsRule):
                keywords.update(rule_call.keywords)
            elif isinstance(rule_call, StartswithRule):
                startswith.update(rule_call.msg)
            elif isinstance(rule_call, EndswithRule):
                endswith.update(rule_call.msg)
            elif isinstance(rule_call, FullmatchRule):
                fullmatch.update(rule_call.msg)
            elif isinstance(rule_call, IsTypeRule):
                event_types.update(t.__name__ for t in rule_call.types)
            elif isinstance(rule_call, ToMeRule):
                to_me = True
            elif isinstance(rule_call, AlconnaRule):
                alconna_commands.add(rule_call._path.removeprefix("Alconna::"))

        return cls(
            commands=commands,  # type: ignore
            shell_commands=shell_commands,  # type: ignore
            regex_patterns=regex_patterns,  # type: ignore
            keywords=keywords,  # type: ignore
            startswith=startswith,  # type: ignore
            endswith=endswith,  # type: ignore
            fullmatch=fullmatch,  # type: ignore
            event_types=event_types,  # type: ignore
            alconna_commands=alconna_commands,  # type: ignore
            to_me=to_me
        )


class MatcherInfo(BaseModel):
    """匹配器信息模型，支持序列化"""
    rule: RuleData
    permission: Dict[str, Dict[str, FrozenSet[str]]] = Field(   # key: white_list OR ban_list
        default_factory=lambda: {
            "white_list": {"user": frozenset(), "group": frozenset()},
            "ban_list": {"user": frozenset(), "group": frozenset()},
        }
    )
    is_on: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _quick_hash(self) -> int:
        """
        快速哈希方法。
        """
        perm_tuple = (
            ("white_list",
                ("user", self.permission["white_list"]["user"]),
                ("group", self.permission["white_list"]["group"])
             ),
            ("ban_list",
                ("user", self.permission["ban_list"]["user"]),
                ("group", self.permission["ban_list"]["group"])
             )
        )
        return hash((
            self.rule,
            perm_tuple,
            self.is_on
        ))

    def _persist_hash(self) -> int:
        """
        持久化哈希方法。
        """
        hash_obj = xxhash.xxh64()
        hash_obj.update(str(self.rule._persist_hash()).encode('utf-8'))

        perm_data = []
        for perm_type in sorted(self.permission.keys()):  # white_list, ban_list
            # group, user
            for id_type in sorted(self.permission[perm_type].keys()):
                for item in sorted(self.permission[perm_type][id_type]):
                    perm_data.append(f"{perm_type}:{id_type}:{item}")

        for item in perm_data:
            hash_obj.update(item.encode('utf-8'))

        hash_obj.update(str(self.is_on).encode('utf-8'))
        return int.from_bytes(hash_obj.digest(), byteorder='big')

    def __hash__(self) -> int:
        return self._quick_hash()

    @field_serializer('permission')
    def serialize_permission(self, value: Dict[str, Dict[str, FrozenSet[str]]], _info) -> Dict[str, Dict[str, List[str]]]:
        """序列化权限数据"""
        return {
            "white_list": {
                "user": list(value["white_list"]["user"]),
                "group": list(value["white_list"]["group"]),
            },
            "ban_list": {
                "user": list(value["ban_list"]["user"]),
                "group": list(value["ban_list"]["group"]),
            },
        }


@field_validator("permission", mode="before")
@classmethod
def ensure_permission_frozenset(cls, v: Any) -> Dict[str, Dict[str, FrozenSet[str]]]:
    """确保权限数据转换为不可变集合，并且结构严格符合预期"""
    if isinstance(v, str):
        try:
            v = orjson.loads(v)
        except orjson.JSONDecodeError:
            raise ValueError("permission 字段不是合法的 JSON 字符串")

    if not isinstance(v, dict):
        v = {}

    _ALLOWED_OUTER_KEYS = {"white_list", "ban_list"}
    _ALLOWED_INNER_KEYS = {"user", "group"}

    provided_outer_keys = set(v.keys())
    if not provided_outer_keys.issubset(_ALLOWED_OUTER_KEYS):
        extra_keys = provided_outer_keys - _ALLOWED_OUTER_KEYS
        raise ValueError(
            f"permission 只允许包含 {list(_ALLOWED_OUTER_KEYS)}，但收到了额外键: {list(extra_keys)}")

    white_list = v.get("white_list", {})
    ban_list = v.get("ban_list", {})

    for name, inner_dict in [("white_list", white_list), ("ban_list", ban_list)]:
        if not isinstance(inner_dict, dict):
            raise ValueError(f"{name} 必须是一个字典")
        provided_inner_keys = set(inner_dict.keys())
        if not provided_inner_keys.issubset(_ALLOWED_INNER_KEYS):
            extra_keys = provided_inner_keys - _ALLOWED_INNER_KEYS
            raise ValueError(
                f"{name} 只允许包含 {list(_ALLOWED_INNER_KEYS)}，但收到了额外键: {list(extra_keys)}")

    return {
        "white_list": {
            "user": frozenset(white_list.get("user", [])),
            "group": frozenset(white_list.get("group", [])),
        },
        "ban_list": {
            "user": frozenset(ban_list.get("user", [])),
            "group": frozenset(ban_list.get("group", [])),
        },
    }


class PluginMatchers(BaseModel):
    """插件匹配器集合模型"""
    matchers: Set[MatcherInfo] = Field(default_factory=set)
    rule_mapping: Dict[int, MatcherInfo] = Field(
        default_factory=dict, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """序列化模型数据"""
        return {"matchers": list(self.matchers)}

    def perm(
        self,
        user_id: str,
        group_id: Optional[str],
        rule: RuleData
    ) -> bool:
        """检查用户权限"""
        matcher_info = self.rule_mapping.get(hash(rule))
        if matcher_info is None:
            return True
        if not matcher_info.is_on:
            white_list = matcher_info.permission["white_list"]
            if (user_id in white_list["user"] or
                    (group_id and group_id in white_list["group"])):
                return True
            return False
        else:
            ban_list = matcher_info.permission["ban_list"]
            if (user_id in ban_list["user"] or
                    (group_id and group_id in ban_list["group"])):
                return False
        return True

    def rebuild_rule_mapping(self) -> None:
        """重建规则映射关系"""
        self.rule_mapping = {hash(info.rule): info for info in self.matchers}

    def add_matcher(self, matcher_info: MatcherInfo):
        """安全地添加一个 matcher 并更新映射"""
        self.matchers.add(matcher_info)
        self.rebuild_rule_mapping()

    def remove_matcher(self, matcher_info: MatcherInfo):
        """安全地移除一个 matcher 并更新映射"""
        if matcher_info in self.matchers:
            self.matchers.remove(matcher_info)
            self.rebuild_rule_mapping()


class BotPlugins(BaseModel):
    """机器人插件集合模型"""
    plugins: Dict[str, PluginMatchers] = Field(default_factory=dict)

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """序列化模型数据"""
        return {"plugins": self.plugins}

    def perm(
        self,
        plugin_name: str,
        user_id: str,
        group_id: Optional[str],
        rule: RuleData
    ) -> bool:
        """检查插件权限"""
        if plugin_name not in self.plugins:
            return True
        return self.plugins[plugin_name].perm(user_id, group_id, rule)


class MatcherRuleModel(BaseModel):
    """完整的匹配器规则模型，支持序列化"""
    bots: Dict[str, BotPlugins] = Field(default_factory=dict)

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """序列化模型数据"""
        return {"bots": self.bots}

    def perm(
        self,
        bot_id: str,
        plugin_name: str,
        user_id: str,
        group_id: Optional[str],
        rule: RuleData
    ) -> bool:
        """检查机器人权限"""
        if bot_id not in self.bots:
            return True
        return self.bots[bot_id].perm(plugin_name, user_id, group_id, rule)

    def __str__(self) -> str:
        """返回格式化字符串表示"""
        return "MatcherRuleModel\n" + self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_data: str) -> "MatcherRuleModel":
        """从JSON数据创建模型实例"""
        data = orjson.loads(json_data)
        instance = cls.model_validate(data)

        for bot_plugins in instance.bots.values():
            for plugin_matchers in bot_plugins.plugins.values():
                plugin_matchers.rebuild_rule_mapping()

        return instance

    @classmethod
    def from_matchers(cls, matchers: Dict[str, Dict[str, Set[Matcher]]]) -> "MatcherRuleModel":
        """从Matcher集合创建模型实例"""
        model = cls()

        for bot_id, plugins in matchers.items():
            bot_plugins = BotPlugins()

            for plugin_name, matcher_set in plugins.items():
                plugin_matchers = PluginMatchers()

                for matcher in matcher_set:
                    rule_data = RuleData.extract_rule(matcher)
                    matcher_info_kwargs = {
                        "rule": rule_data,
                        "is_on": getattr(matcher, "lazytea_is_on", True)
                    }

                    if hasattr(matcher, "lazytea_permission"):
                        matcher_info_kwargs["permission"] = getattr(
                            matcher, "lazytea_permission")

                    matcher_info = MatcherInfo(**matcher_info_kwargs)
                    plugin_matchers.add_matcher(matcher_info)

                bot_plugins.plugins[plugin_name] = plugin_matchers

            model.bots[bot_id] = bot_plugins

        return model
