from collections.abc import Awaitable, Callable

from .models import Tokens

type TokenListener = Callable[[Tokens], Awaitable[None] | None]
