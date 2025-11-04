# modules/domain_transforms.py
import asyncio
from typing import List
from modules.base_transform import BaseTransform
from models import Domain, Subdomain, BaseEntity
from parsers import parse_sublist3r
from config import TOOLS_DIR, DEFAULT_PROCESS_TIMEOUT

class Sublist3rTransform(BaseTransform):
    transform_name = "Sublist3r"
    input_type = Domain # Принимает Domain

    async def run(self) -> str:
        # Путь к инструменту
        sublist3r_path = TOOLS_DIR / "sublist3r" / "sublist3r.py"
        if not sublist3r_path.exists():
            raise FileNotFoundError(f"Sublist3r не найден в {sublist3r_path}. Запустите setup.sh")

        cmd = f"python3 {sublist3r_path} -d {self.entity.value}"

        # Асинхронный запуск процесса
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=DEFAULT_PROCESS_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise Exception(f"Sublist3r превысил таймаут ({DEFAULT_PROCESS_TIMEOUT}c)")

        if proc.returncode != 0:
            # Sublist3r часто пишет ошибки в stderr, но все равно работает
            # Будем считать ошибкой, только если stdout пустой
            if not stdout:
                raise Exception(f"Sublist3r завершился с ошибкой: {stderr.decode()}")

        return stdout.decode()

    def parse(self, raw_output: str) -> List[BaseEntity]:
        """Парсит вывод и возвращает Pydantic-модели."""
        subdomains = parse_sublist3r(raw_output)
        return [Subdomain(value=s) for s in subdomains]
