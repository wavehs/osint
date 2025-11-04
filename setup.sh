#!/bin/bash
set -e

echo "[+] 1. Обновление системных пакетов и установка зависимостей (Nmap, Python3-pip)..."
# Используем sudo, если не root
if [ "$EUID" -ne 0 ]; then
  SUDO=sudo
else
  SUDO=""
fi

# Проверка дистрибутива
if [ -f /etc/debian_version ]; then
    echo "[i] Обнаружена Debian/Ubuntu..."
    $SUDO apt-get update -y
    $SUDO apt-get install -y nmap python3-pip git
elif [ -f /etc/redhat-release ]; then
    echo "[i] Обнаружена RHEL/CentOS/Fedora..."
    $SUDO dnf install -y nmap python3-pip git
elif [ "$(uname)" == "Darwin" ]; then
    # macOS с Homebrew
    echo "[i] Обнаружен macOS. Используем Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "[!] Homebrew не найден. Пожалуйста, установите его."
        exit 1
    fi
    brew install nmap python3 git
else
    echo "[!] Не удалось определить дистрибутив. Установите nmap, python3-pip, git вручную."
    exit 1
fi

echo "[+] 2. Создание директорий (tools, output)..."
mkdir -p tools
mkdir -p output

# Путь к директории инструментов
TOOLS_DIR=$(pwd)/tools

echo "[+] 3. Установка фреймворка и зависимостей..."
python3 -m pip install -e .

echo "[+] 4. Клонирование и установка Sublist3r..."
if [ ! -d "$TOOLS_DIR/sublist3r" ]; then
    git clone https://github.com/aboul3la/Sublist3r.git $TOOLS_DIR/sublist3r
    echo "[i] Установка зависимостей Sublist3r..."
    python3 -m pip install -r $TOOLS_DIR/sublist3r/requirements.txt
else
    echo "[i] Директория Sublist3r уже существует, пропускаем."
fi

echo "[+] 5. Клонирование и установка Sherlock..."
if [ ! -d "$TOOLS_DIR/sherlock" ]; then
    git clone https://github.com/sherlock-project/sherlock.git $TOOLS_DIR/sherlock
    echo "[i] Установка зависимостей Sherlock..."
    python3 -m pip install -r $TOOLS_DIR/sherlock/requirements.txt
else
    echo "[i] Диретория Sherlock уже существует, пропускаем."
fi

echo ""
echo "[*] -----------------------------------------------"
echo "[*] Установка завершена!"
echo "[*] Активируйте ваше виртуальное окружение, если вы его используете (source venv/bin/activate)."
echo "[*] Запустите программу командой: robust"
echo "[*] -----------------------------------------------"
