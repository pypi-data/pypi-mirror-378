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

    # login (implemented)

    # mqtt group (listen, sendMessageMqtt, setMessageReactionMqtt, typing are attached)
    api.listenSpeed = _stub
    api.pinMessage = _stub
    api.realtime = _stub

    # posting
    # postComment and postFollow are attached by attach_posting
    api.postShare = _stub
    api.postStory = _stub

    # threads - some exist on api already (getThreadList, getThreadInfo, getThreadHistory)
    # users - getUserInfo exists

    # extra already attached by attach_extra
