# config.py
import pathlib

# Путь к корневой директории проекта
BASE_DIR = pathlib.Path(__file__).parent.resolve()

# Директории
TOOLS_DIR = BASE_DIR / "tools"
OUTPUT_DIR = BASE_DIR / "output"

# Таймаут для внешних процессов (в секундах)
DEFAULT_PROCESS_TIMEOUT = 300