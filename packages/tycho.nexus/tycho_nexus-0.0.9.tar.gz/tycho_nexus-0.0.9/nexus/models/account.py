from typing import TYPE_CHECKING
from enum import IntEnum

if TYPE_CHECKING:
    from ..client import Nexus
    from nexus.api_types.v1 import v1_AccountResponse, v1_PlatformAccount


class Platform(IntEnum):
    DISCORD = 0
    ROBLOX = 1


class PlatformAccount:
    """Represents a Nexus platform account."""

    def __init__(self, data: "v1_PlatformAccount"):
        self.id = int(data.get("id"))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class Account:
    """Represents a Nexus account."""

    def __init__(self, client: "Nexus", data: "v1_AccountResponse"):
        self.discord = PlatformAccount(data.get("discord"))
        self.roblox = PlatformAccount(data.get("roblox"))

        if self.discord.id not in client._cache.discord_accounts:
            client._cache.discord_accounts.set(self.discord.id, self)
        if self.roblox.id not in client._cache.roblox_accounts:
            client._cache.roblox_accounts.set(self.roblox.id, self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} discord.id={self.discord.id}, roblox.id={self.roblox.id}>"
