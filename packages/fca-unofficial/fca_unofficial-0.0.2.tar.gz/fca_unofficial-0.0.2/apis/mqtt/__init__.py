from typing import Any
from .listen import attach_listen
from .send_message import attach_send_message
from .set_reaction import attach_set_reaction
from .typing_indicator import attach_typing_indicator
from .nickname import attach_nickname
from .gcname import attach_gcname
from .gcmember import attach_gcmember
from .gcrule import attach_gcrule
from .pin_message import attach_pin_message
from .edit_message import attach_edit_message


def attach_mqtt(api: Any) -> None:
    attach_listen(api)
    attach_send_message(api)
    attach_set_reaction(api)
    attach_typing_indicator(api)
    attach_nickname(api)
    attach_gcname(api)
    attach_gcmember(api)
    attach_gcrule(api)
    attach_pin_message(api)
    attach_edit_message(api)
