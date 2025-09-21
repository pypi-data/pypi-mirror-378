import importlib as _i
import typing as _t

if _t.TYPE_CHECKING:
    from ._base import BaseBotCheckin, BotCheckin, AnswerBotCheckin, MessageType
    from ._templ_a import TemplateACheckin
    from ._templ_b import TemplateBCheckin, TemplateBCheckinConfig

MENU = {
    "._base": ["BaseBotCheckin", "BotCheckin", "AnswerBotCheckin", "MessageType"],
    "._templ_a": ["TemplateACheckin"],
    "._templ_b": ["TemplateBCheckin", "TemplateBCheckinConfig"],
}


def __getattr__(spec: str):
    for module, specs in MENU.items():
        if isinstance(specs, dict):
            for s, t in specs.items():
                if s == spec:
                    m = _i.import_module(module, package=__name__)
                    return getattr(m, t or s)
        else:
            if spec in specs:
                m = _i.import_module(module, package=__name__)
                return getattr(m, spec)
    else:
        try:
            m = _i.import_module(f".{spec}", package=__name__)
            return m
        except ImportError:
            raise AttributeError(f"module '{__name__}' has no attribute '{spec}'") from None
