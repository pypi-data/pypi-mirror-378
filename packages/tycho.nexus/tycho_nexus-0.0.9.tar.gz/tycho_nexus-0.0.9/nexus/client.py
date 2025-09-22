"""

The main client.

"""

from typing import List, Callable, Optional, Type, TypeVar, Dict, Any, Tuple
from .cache import Cache, CacheConfig
from .requests import Requests
from functools import wraps
from .api_types.v1 import *
from .exceptions import *
from .models import *
import hashlib
import asyncio
import httpx
import json

R = TypeVar("R")


class ClientCache:
    """Client object caches and config. TTL in seconds, 0 to disable. (max_size, TTL)"""

    def __init__(
        self,
        roblox_accounts: CacheConfig = (250, 120),
        discord_accounts: CacheConfig = (250, 120),
    ):
        self.roblox_accounts = Cache[int, Account](*roblox_accounts)
        self.discord_accounts = Cache[int, Account](*discord_accounts)


def _ephemeral(func):
    @wraps(func)
    async def wrapper(self: "Nexus", *args, **kwargs):
        try:
            args_repr = json.dumps(args, sort_keys=True, default=str)
            kwargs_repr = json.dumps(kwargs, sort_keys=True, default=str)
        except (TypeError, ValueError):
            args_repr = str(args)
            kwargs_repr = str(kwargs)

        hashed_args = hashlib.sha256(f"{args_repr}|{kwargs_repr}".encode()).hexdigest()
        cache_key = f"{func.__name__}_cache_{hashed_args}"

        if hasattr(self, cache_key):
            cached_result, timestamp = getattr(self, cache_key)
            if (asyncio.get_event_loop().time() - timestamp) < self._ephemeral_ttl:
                return cached_result

        result = await func(self, *args, **kwargs)
        setattr(self, cache_key, (result, asyncio.get_event_loop().time()))
        return result

    return wrapper


class Nexus:
    """The main Nexus API client."""

    def __init__(
        self,
        nexus_key: str,
        _base_url: str = "https://api.tycho.team/nexus/v1",
        _rts_base_url: str = "wss://rts.tycho.team/nexus/v1",
        _ephemeral_ttl: int = 10,
        _cache: Optional[ClientCache] = None,
    ):
        self._nexus_key = nexus_key
        self._requests = Requests(
            base_url=_base_url, headers={"X-Nexus-Key": nexus_key}
        )
        self._rts_base_url = _rts_base_url
        self._ephemeral_ttl = _ephemeral_ttl
        self._cache = _cache or ClientCache()

    def _raise_error_code(self, response: Any):
        if not isinstance(response, Dict):
            raise NexusException("A malformed response was received.")

        error_code = response.get("code")
        if error_code is None:
            raise NexusException("No error was received.")

        exceptions: List[Callable[..., APIException]] = [
            UnknownDiscordUser,
            UnknownKey,
            UnknownDiscordAccount,
            UnknownRobloxAccount,
            InternalError,
            InvalidParameter,
            RateLimited,
        ]

        for _exception in exceptions:
            exception = _exception()
            if error_code == exception.code:
                raise exception

        raise APIException(
            error_code,
            f"An unknown API error has occured: {response.get('message') or '...'}",
        )

    def _handle(
        self, response: httpx.Response, return_type: Type[R]
    ) -> Tuple[R, httpx.Response]:
        if not response.is_success:
            self._raise_error_code(response.json())
        return response.json(), response

    @_ephemeral
    async def get_discord_account(self, id: int):
        """Get a Nexus account from a Discord user."""
        _cached = self._cache.discord_accounts.get(id)
        if _cached:
            return _cached

        try:
            return Account(
                self,
                data=self._handle(
                    await self._requests.get("/accounts/discord/" + str(id)),
                    v1_AccountResponse,
                )[0],
            )
        except UnknownDiscordAccount:
            return None

    @_ephemeral
    async def get_roblox_account(self, id: int):
        """Get a Nexus account from a Roblox user."""
        _cached = self._cache.roblox_accounts.get(id)
        if _cached:
            return _cached

        try:
            return Account(
                self,
                data=self._handle(
                    await self._requests.get("/accounts/roblox/" + str(id)),
                    v1_AccountResponse,
                )[0],
            )
        except UnknownRobloxAccount:
            return None

    @_ephemeral
    async def get_roblox_accounts(self, ids: List[int]):
        """Get Nexus accounts from Roblox users."""
        _found_in_cache = {
            a.roblox.id: a
            for a in [self._cache.roblox_accounts.get(id) for id in ids]
            if a
        }
        if len(_found_in_cache) == len(ids):
            return _found_in_cache

        r = self._handle(
            await self._requests.get(
                "/accounts/roblox?ids=" + "&ids=".join([str(id) for id in ids])
            ),
            v1_AccountsResponse,
        )[0]
        return {int(k): Account(self, data=v) if v else None for k, v in r.items()}

    async def create_session(self, id: int):
        """Create a Nexus verification session for a Discord user."""
        r = self._handle(
            await self._requests.post(
                "/sessions", json={"platform": Platform.DISCORD, "user_id": str(id)}
            ),
            v1_NewSessionResponse,
        )
        return Session(self, data=r[0], status_code=r[1].status_code)
