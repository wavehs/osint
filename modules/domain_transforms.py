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
        # Using create_subprocess_exec to prevent command injection
        process = await asyncio.create_subprocess_exec(
            "python", # Assuming 'python' is in the PATH and it's python3
            "sublist3r.py", # Assuming sublist3r.py is in the PATH or current directory
            "-d",
            entity.value,
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
            # Using create_subprocess_exec to prevent command injection
            process = await asyncio.create_subprocess_exec(
                "theharvester",
                "-d",
                entity.value,
                "-b",
                "all",
                "-f",
                temp_filename,
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
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def parse(self, raw_output: str) -> List[BaseEntity]:
        """
        Parses the raw output of TheHarvester and returns a list of subdomains, emails, and IPs.
        """
        from models import Subdomain, Email, IPAddress

        results: List[BaseEntity] = []
        data = parse_theharvester_json(raw_output)

        for subdomain in data.get("hosts", []):
            results.append(Subdomain(value=subdomain.split(":")[0]))
        for email in data.get("emails", []):
            results.append(Email(value=email))
        for ip in data.get("ips", []):
            results.append(IPAddress(value=ip))

        return results
