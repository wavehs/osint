import asyncio
from modules.base_transform import BaseTransform
from models import Username, URL
from parsers import parse_sherlock
from typing import List

class SherlockTransform(BaseTransform):
    @property
    def name(self) -> str:
        return "Sherlock"

    async def run(self, entity: Username) -> str:
        """
        Runs Sherlock on the given username.
        """
        process = await asyncio.create_subprocess_shell(
            f"sherlock {entity.value}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Sherlock failed: {stderr.decode()}")
        return stdout.decode()

    def parse(self, raw_output: str) -> List[URL]:
        """
        Parses the raw output of Sherlock and returns a list of URLs.
        """
        urls = parse_sherlock(raw_output)
        return [URL(value=url) for url in urls]
