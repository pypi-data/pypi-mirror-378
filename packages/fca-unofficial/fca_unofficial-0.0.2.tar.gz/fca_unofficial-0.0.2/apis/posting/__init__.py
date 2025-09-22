from typing import Any
from .follow import attach_follow
from .comment import attach_comment
from .friend import attach_friend
from .share import attach_share
from .story import attach_story


def attach_posting(api: Any) -> None:
    attach_follow(api)
    attach_comment(api)
    attach_friend(api)
    attach_share(api)
    attach_story(api)
