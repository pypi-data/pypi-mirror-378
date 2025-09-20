import aiohttp
import time
from datetime import datetime


class InvalidAPIKey(Exception):
    """Uncorrect API key"""


class Status:
    def __init__(self, session_data: dict, recent_games_data: list):
        self._session = session_data or {}
        self._recent_games = recent_games_data or []

    def session(self) -> bool:
        return self._session.get("online", False)

    def mode(self) -> str | None:
        return self._session.get("gameType")

    def sub_mode(self) -> str | None:
        return self._session.get("mode")

    def recent_games(self) -> list[dict]:
        return self._recent_games

class Login:
    def __init__(self, first_login: int | None, last_login: int | None):
        self._first = first_login
        self._last = last_login

    def first(self) -> datetime | None:
        if self._first:
            return datetime.fromtimestamp(self._first / 1000)
        return None

    def last(self) -> datetime | None:
        if self._last:
            return datetime.fromtimestamp(self._last / 1000)
        return None

class Ranks:
    def __init__(self, data: dict):
        self._data = data or {}

    def monthly_rank(self) -> str | None:
        rank = self._data.get("monthlyPackageRank")
        if rank in ("NONE", None):
            return None
        return rank

    def global_rank(self) -> str | None:
        special = self._data.get("rank")
        if special and special != "NORMAL":
            return special

        monthly = self.monthly_rank()
        if monthly:
            return monthly

        rank = self._data.get("newPackageRank") or self._data.get("packageRank")
        if rank in ("NONE", None):
            return "DEFAULT"
        return rank

    def raw(self) -> dict:
        return {
            "rank": self._data.get("rank"),
            "packageRank": self._data.get("packageRank"),
            "newPackageRank": self._data.get("newPackageRank"),
            "monthlyPackageRank": self._data.get("monthlyPackageRank"),
        }

class StatsMode:
    def __init__(self, data: dict):
        self._data = data or {}

    def __call__(self, key: str, default: int | None = 0):
        return self._data.get(key, default)


class Socials:
    def __init__(self, links: dict):
        self._links = links

    def twitter(self) -> str | None:
        return self._links.get("TWITTER")

    def youtube(self) -> str | None:
        return self._links.get("YOUTUBE")

    def instagram(self) -> str | None:
        return self._links.get("INSTAGRAM")

    def tiktok(self) -> str | None:
        return self._links.get("TIKTOK")

    def twitch(self) -> str | None:
        return self._links.get("TWITCH")

    def discord(self) -> str | None:
        return self._links.get("DISCORD")

    def forums(self) -> str | None:
        return self._links.get("HYPIXEL")


class Stats:
    def __init__(self, stats_data: dict):
        self._stats_data = stats_data or {}


class User:
    def __init__(self, data: dict, session_data: dict, recent_games_data: list):
        self._data = data
        self._stats = data.get("stats", {})

        self.socials = Socials(data.get("socialMedia", {}).get("links", {}))
        self.ranks = Ranks(data)
        self.stats = Stats(self._stats)

        self.stats.skywars = StatsMode(self._stats.get("SkyWars", {}))
        self.stats.bedwars = StatsMode(self._stats.get("Bedwars", {}))
        self.stats.duels = StatsMode(self._stats.get("Duels", {}))
        self.stats.uhc = StatsMode(self._stats.get("UHC", {}))
        self.stats.arcade = StatsMode(self._stats.get("Arcade", {}))
        self.stats.murder_mystery = StatsMode(self._stats.get("MurderMystery", {}))
        self.stats.build_battle = StatsMode(self._stats.get("BuildBattle", {}))
        self.stats.megawalls = StatsMode(self._stats.get("Walls3", {}))
        self.stats.classic = StatsMode(self._stats.get("Arena", {}))
        self.stats.blitz = StatsMode(self._stats.get("HungerGames", {}))
        self.stats.tnt_games = StatsMode(self._stats.get("TNTGames", {}))
        self.stats.smash_heroes = StatsMode(self._stats.get("SuperSmash", {}))
        self.stats.speed_uhc = StatsMode(self._stats.get("SpeedUHC", {}))
        self.stats.pit = StatsMode(self._stats.get("Pit", {}))
        self.stats.walls = StatsMode(self._stats.get("Walls", {}))
        self.stats.quake = StatsMode(self._stats.get("Quake", {}))
        self.stats.paintball = StatsMode(self._stats.get("Paintball", {}))
        self.stats.turbo_kart = StatsMode(self._stats.get("GingerBread", {}))
        self.stats.vampirez = StatsMode(self._stats.get("VampireZ", {}))

        self.status = Status(
            session_data,
            recent_games_data 
        )
        self.login = Login(data.get("firstLogin"), data.get("lastLogin"))

class Guild:
    def __init__(self, data: dict):
        self._data = data or {}

    def id(self) -> str | None:
        return self._data.get("_id")

    def name(self) -> str | None:
        return self._data.get("name")

    def description(self) -> str | None:
        return self._data.get("description")

    def created(self) -> datetime | None:
        ts = self._data.get("created")
        return datetime.fromtimestamp(ts / 1000) if ts else None

    def members(self) -> list[dict]:
        return self._data.get("members", [])

    def tag(self) -> str | None:
        return self._data.get("tag")

    def tag_color(self) -> str | None:
        return self._data.get("tagColor")

    def coins(self) -> int:
        return self._data.get("coins", 0)

    def exp(self) -> int:
        return self._data.get("exp", 0)

class LeaderboardMode:
    def __init__(self, data: list[dict]):
        self._data = data or []

    async def __call__(self, stat: str) -> list[str]:
        stat = stat.lower()
        result = []
        for entry in self._data:
            path = entry.get("path", "").lower()
            if stat in path:
                result.extend(entry.get("leaders", []))
        return result
    
class FetchLeaderboard:
    def __init__(self, client, data: dict):
        self._client = client
        self._data = data or {}

    def _get_mode(self, mode: str) -> "LeaderboardMode":
        return LeaderboardMode(self._data.get(mode.upper(), []))

    async def bedwars(self) -> "LeaderboardMode":
        return self._get_mode("BEDWARS")

    async def skywars(self) -> "LeaderboardMode":
        return self._get_mode("SKYWARS")

    async def duels(self) -> "LeaderboardMode":
        return self._get_mode("DUELS")

    async def uhc(self) -> "LeaderboardMode":
        return self._get_mode("UHC")

    async def arcade(self) -> "LeaderboardMode":
        return self._get_mode("ARCADE")

    async def murder_mystery(self) -> "LeaderboardMode":
        return self._get_mode("MURDER_MYSTERY")

    async def build_battle(self) -> "LeaderboardMode":
        return self._get_mode("BUILD_BATTLE")

    async def megawalls(self) -> "LeaderboardMode":  
        return self._get_mode("WALLS3")

    async def battlegrounds(self) -> "LeaderboardMode":
        return self._get_mode("BATTLEGROUNDS")

    async def quakecraft(self) -> "LeaderboardMode":
        return self._get_mode("QUAKECRAFT")

    async def speeduhc(self) -> "LeaderboardMode":
        return self._get_mode("SPEED_UHC")

    async def tntgames(self) -> "LeaderboardMode":
        return self._get_mode("TNTGAMES")

    async def vampire_z(self) -> "LeaderboardMode":
        return self._get_mode("VAMPIREZ")

    async def housing(self) -> "LeaderboardMode":
        return self._get_mode("HOUSING")

    async def duels2(self) -> "LeaderboardMode":
        return self._get_mode("DUELS2") 

    async def smash_heroes(self) -> "LeaderboardMode":
        return self._get_mode("SMASH_HEROES")

class HypixelStatus:
    def __init__(self, data: dict):
        self._data = data or {}

    def players(self) -> int:
        return self._data.get("playerCount", 0)
    
    def games(self) -> str:
        return self._data.get("games")

class HyAPIClient:
    BASE_URL = "https://api.hypixel.net"
    BASE_URL_V2 = "https://api.hypixel.net/v2"
    MOJANG_URL = "https://api.mojang.com/users/profiles/minecraft"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.fetch_leaderboard = None

    async def _request(self, endpoint: str, **params):
        headers = {"API-Key": self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/{endpoint}", headers=headers, params=params) as resp:
                if resp.status == 403:
                    raise InvalidAPIKey("Uncorrect API key")
                data = await resp.json()
                if not data.get("success", False):
                    raise Exception(f"Hypixel API error: {data}")
                return data

    async def _v2_request(self, endpoint: str, **params):
        headers = {"API-Key": self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL_V2}/{endpoint}", headers=headers, params=params) as resp:
                if resp.status == 403:
                    raise InvalidAPIKey("Uncorrect API key")
                data = await resp.json()
                if not data.get("success", False):
                    raise Exception(f"Hypixel API V2 error: {data}")
                return await resp.json()

    async def _get_uuid(self, name: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.MOJANG_URL}/{name}") as resp:
                if resp.status == 204:
                    return None
                data = await resp.json()
                return data.get("id")

    async def get_user(self, identifier: str) -> User:
        if "-" not in identifier and len(identifier) <= 16:
            uuid = await self._get_uuid(identifier)
        else:
            uuid = identifier.replace("-", "")

        data = await self._request("player", uuid=uuid)
        status_data = await self._request("status", uuid=uuid)
        recent_games_data = await self._v2_request("recentgames", uuid=uuid)

        return User(
            data.get("player", {}),
            status_data.get("session", {}),
            recent_games_data.get("games", []),
        )
    
    async def get_guild(self, *, guild_id: str = None, player: str = None, name: str = None) -> Guild | None:
        if not (guild_id or player or name):
            raise ValueError("Missing params")

        params = {}

        if guild_id:
            params["id"] = guild_id
        elif player:
            if "-" not in player and len(player) <= 16:
                uuid = await self._get_uuid(player)
            else:
                uuid = player.replace("-", "")
            params["player"] = uuid
        elif name:
            params["name"] = name

        data = await self._request("guild", **params)
        return Guild(data.get("guild", {}))


    async def get_leaderboards(self) -> FetchLeaderboard:
        data = await self._request("leaderboards")
        self.fetch_leaderboard = FetchLeaderboard(self, data.get("leaderboards", {}))
        return self.fetch_leaderboard
    
    async def hypixel(self) -> HypixelStatus:
        data = await self._v2_request("counts")
        return HypixelStatus(data)
    
    async def latency(self) -> float:
        start = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/status", headers={"API-Key": self.api_key}) as resp:
                await resp.text() 
        end = time.perf_counter()
        return (end - start) * 1000  

def connect(api_key: str) -> HyAPIClient:
    return HyAPIClient(api_key)
