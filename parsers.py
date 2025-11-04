# parsers.py
import re
from typing import List, Set, Tuple
import xml.etree.ElementTree as ET # Для парсинга Nmap

def parse_sublist3r(raw_output: str) -> Set[str]:
    """Парсит стандартный вывод Sublist3r."""
    # Sublist3r выводит много мусора, но домены - с BRUTEFORCE
    # или просто на новой строке.
    # Это простое регулярное выражение ищет FQDN.

    # Регулярка для FQDN (Fully Qualified Domain Name)
    fqdn_regex = r"([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})"

    matches = re.findall(fqdn_regex, raw_output)

    # Очищаем от мусора, который может поймать регулярка
    cleaned_subdomains = set()
    for match in matches:
        match_lower = match.lower()
        if "sublist3r" in match_lower or "total" in match_lower or "scanning" in match_lower or "saving" in match_lower or "github.com" in match_lower:
            continue
        cleaned_subdomains.add(match.strip())

    return cleaned_subdomains

def parse_nmap_xml(xml_output: str) -> List[Tuple[int, str]]:
    """Парсит XML-вывод Nmap (-oX)."""
    results: List[Tuple[int, str]] = []

    if not xml_output.strip():
        return []

    try:
        root = ET.fromstring(xml_output)

        for port in root.findall(".//port"):
            port_num = int(port.get("portid"))
            service_elem = port.find("service")

            if service_elem is not None:
                service_name = service_elem.get("name", "unknown")
            else:
                service_name = "unknown"

            state_elem = port.find("state")
            if state_elem is not None and state_elem.get("state") == "open":
                results.append((port_num, service_name))

        return results

    except ET.ParseError as e:
        print(f"Ошибка парсинга Nmap XML: {e}")
        return []

def parse_sherlock(raw_output: str) -> Set[str]:
    """Парсит стандартный вывод Sherlock."""
    # Sherlock выводит URL'ы в формате:
    # [*] Username found at: [https://www.example.com/username](https://www.example.com/username)

    url_regex = r"Username found at: (https?://[^\s]+)"
    matches = re.findall(url_regex, raw_output)
    return set(matches)
