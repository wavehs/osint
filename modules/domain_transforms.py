import asyncio
from modules.base_transform import BaseTransform
from models import Domain, Subdomain
from parsers import parse_sublist3r
from typing import List

class Sublist3rTransform(BaseTransform):
    @property
    def name(self) -> str:
        return "Sublist3r"

    async def run(self, entity: Domain) -> str:
        """
        Runs Sublist3r on the given domain.
        """
        # Ensure sublist3r is installed and configured
        process = await asyncio.create_subprocess_shell(
            f"python sublist3r.py -d {entity.value}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Sublist3r failed: {stderr.decode()}")
        return stdout.decode()

    def parse(self, raw_output: str) -> List[Subdomain]:
        """
        Parses the raw output of Sublist3r and returns a list of subdomains.
        """
        subdomains = parse_sublist3r(raw_output)
        return [Subdomain(value=subdomain) for subdomain in subdomains]

import tempfile
import aiofiles

class TheHarvesterTransform(BaseTransform):
    @property
    def name(self) -> str:
        return "TheHarvester"

    async def run(self, entity: Domain) -> str:
        """
        Runs TheHarvester on the given domain.
        """
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as tmp_file:
            temp_filename = tmp_file.name

        try:
            # Ensure theharvester is installed and configured
            process = await asyncio.create_subprocess_shell(
                f"theharvester -d {entity.value} -b all -f {temp_filename}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"TheHarvester failed: {stderr.decode()}")

            async with aiofiles.open(temp_filename, "r") as f:
                return await f.read()
        finally:
            import os
            os.remove(temp_filename)

    def parse(self, raw_output: str) -> List[Subdomain]:
        """
        Parses the raw output of TheHarvester and returns a list of subdomains.
        """
        # Note: a more robust implementation would parse emails, IPs, etc.
        data = parse_theharvester_json(raw_output)
        subdomains = data.get("hosts", [])
        return [Subdomain(value=subdomain.split(":")[0]) for subdomain in subdomains]
