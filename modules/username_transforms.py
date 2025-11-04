# modules/username_transforms.py
import asyncio
from typing import List
from modules.base_transform import BaseTransform
from models import Username, URL, BaseEntity
from parsers import parse_sherlock
from config import TOOLS_DIR, DEFAULT_PROCESS_TIMEOUT

class SherlockTransform(BaseTransform):
    transform_name = "Sherlock"
    input_type = Username # Принимает Username

    async def run(self) -> str:
        sherlock_dir = TOOLS_DIR / "sherlock"
        sherlock_script = sherlock_dir / "sherlock" / "sherlock.py"

        if not sherlock_script.exists():
            raise FileNotFoundError(f"Sherlock не найден в {sherlock_script}. Запустите setup.sh")

        # Sherlock требует запуска из своей директории
        # --no-color - чтобы парсить чистый текст
        # --timeout 10 - таймаут на 1 запрос
        cmd = [
            "python3",
            str(sherlock_script),
            self.entity.value,
            "--no-color",
            "--timeout",
            "10"
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(sherlock_dir), # ВАЖНО: меняем рабочую директорию, нужен str()
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=DEFAULT_PROCESS_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise Exception(f"Sherlock превысил таймаут ({DEFAULT_PROCESS_TIMEOUT}c)")

        # Sherlock может падать (returncode != 0), но все равно выводить результат
        # Поэтому мы просто возвращаем stdout в любом случае
        return stdout.decode()

    def parse(self, raw_output: str) -> List[BaseEntity]:
        urls = parse_sherlock(raw_output)
        return [URL(value=u) for u in urls]
