# modules/ip_transforms.py
import asyncio
from typing import List
from modules.base_transform import BaseTransform
from models import IPAddress, Port, Service, BaseEntity
from parsers import parse_nmap_xml
from config import DEFAULT_PROCESS_TIMEOUT

class NmapTransform(BaseTransform):
    transform_name = "Nmap_Top1000"
    input_type = IPAddress # Принимает IPAddress

    async def run(self) -> str:
        # Nmap - это системная утилита, а не скрипт.
        # -oX - : Вывод XML в stdout
        # -T4: Агрессивный тайминг
        # --top-ports 1000: Сканируем 1000 самых популярных портов

        cmd = f"nmap -T4 --top-ports 1000 -oX - {self.entity.value}"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=DEFAULT_PROCESS_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise Exception(f"Nmap превысил таймаут ({DEFAULT_PROCESS_TIMEOUT}c)")

        if proc.returncode != 0:
            raise Exception(f"Nmap завершился с ошибкой: {stderr.decode()}")

        # Nmap пишет XML в stdout
        return stdout.decode()

    def parse(self, raw_output: str) -> List[BaseEntity]:
        """Парсит XML и возвращает Port и Service."""
        open_ports_services = parse_nmap_xml(raw_output)

        new_entities: List[BaseEntity] = []
        for port, service in open_ports_services:
            new_entities.append(Port(value=port))
            if service != "unknown":
                new_entities.append(Service(value=service))

        return new_entities
