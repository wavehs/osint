import asyncio
from modules.base_transform import BaseTransform
from models import IPAddress, Port, Service
from parsers import parse_nmap_xml
from typing import List, Tuple

class NmapTransform(BaseTransform):
    @property
    def name(self) -> str:
        return "Nmap"

    async def run(self, entity: IPAddress) -> str:
        """
        Runs Nmap on the given IP address.
        """
        # Using create_subprocess_exec to prevent command injection
        process = await asyncio.create_subprocess_exec(
            "nmap",
            "-sV",
            "-oX",
            "-",
            entity.value,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Nmap failed: {stderr.decode()}")
        return stdout.decode()

    def parse(self, raw_output: str) -> List[Port | Service]:
        """
        Parses the raw output of Nmap and returns a list of ports and services.
        """
        ports, services = parse_nmap_xml(raw_output)
        results = []
        for port in ports:
            results.append(Port(value=port))
        for service in services:
            results.append(Service(value=service))
        return results

class MasscanTransform(BaseTransform):
    @property
    def name(self) -> str:
        return "Masscan"

    async def run(self, entity: IPAddress) -> str:
        """
        Runs Masscan on the given IP address.
        """
        # Using create_subprocess_exec to prevent command injection
        process = await asyncio.create_subprocess_exec(
            "masscan",
            entity.value,
            "-p0-65535",
            "--rate=1000",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            # masscan often prints to stderr, so we check for specific error indicators
            if "ERROR" in stderr.decode():
             raise Exception(f"Masscan failed: {stderr.decode()}")
        return stdout.decode()

    def parse(self, raw_output: str) -> List[Port]:
        """
        Parses the raw output of Masscan and returns a list of open ports.
        """
        ports = []
        for line in raw_output.splitlines():
            if "open port" in line:
                parts = line.split(" ")
                port = parts[3].split("/")[0]
                ports.append(Port(value=port))
        return ports
