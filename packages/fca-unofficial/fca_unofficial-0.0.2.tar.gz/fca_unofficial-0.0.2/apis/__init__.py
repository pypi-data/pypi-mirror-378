from typing import Any

from .messaging import attach_messaging
from .login import attach_login
from .extra import attach_extra
from .notes import attach_notes
from .stickers import attach_stickers
from .posting import attach_posting
from .mqtt import attach_mqtt


def attach_all(api: Any):
    """Attach all API groups to the Api instance.

    For large areas not yet implemented (posting, mqtt, extra, login variants),
    we attach stubs that raise NotImplementedError to signal planned coverage.
    """
    attach_messaging(api)
    attach_login(api)
    attach_extra(api)
    attach_notes(api)
    attach_stickers(api)
    attach_posting(api)
    attach_mqtt(api)

    # Stubs for other namespaces to ensure API coverage
    def _stub(*_args, **_kwargs):  # pragma: no cover
        raise NotImplementedError("This API is planned; pending implementation in Python port.")

    # Attach stubs only if not already provided by concrete attach_* modules
    # mqtt group (listen, sendMessageMqtt, setMessageReactionMqtt, typing are attached)
    if not hasattr(api, "listenSpeed"):
        api.listenSpeed = _stub
    if not hasattr(api, "realtime"):
        api.realtime = _stub

    # posting
    # postComment and postFollow are attached by attach_posting
    if not hasattr(api, "postShare"):
        api.postShare = _stub
    if not hasattr(api, "postStory"):
        api.postStory = _stub

    # threads - some exist on api already (getThreadList, getThreadInfo, getThreadHistory)
    # users - getUserInfo exists

    # extra already attached by attach_extra
