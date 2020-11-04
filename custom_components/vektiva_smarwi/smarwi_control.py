import aiohttp

class SmarwiControl:
    """Control class."""

    def __init__(self, hosts):
        """Initialize."""
        self.hosts = [x.strip() for x in hosts.split(',')]
        self.title = ', '.join([x.split('.')[0] for x in self.hosts])

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            for host in self.hosts:
                ctl = SmarwiControlItem(host)
                await ctl.get_status()
            result = True
        except:
            result = False
        return result

    def list(self) -> list:
        """List what we have"""

        return [SmarwiControlItem(host) for host in self.hosts]


class SmarwiControlItem:
    """Control class for single host."""

    def __init__(self, host):
        self.host = host
        self.name = host.split('.')[0]

    async def __request(self, path):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self.host}/{path}") as resp:
                if resp.status != 200:
                    raise ValueError(f"Request failed with {resp.status}/{resp.reason}")
                return await resp.text()

    async def open(self):
        await self.__request("cmd/open/100")

    async def set_position(self, pos:int):
        await self.__request("cmd/open/{}".format(pos))

    async def close(self):
        await self.__request("cmd/close")

    async def get_status(self):
        response = await self.__request("statusn")
        result = {}
        for item in response.split('\n'):
            item_list = item.split(':', maxsplit=1)
            result[item_list[0]] = item_list[1]
        return result