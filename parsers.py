import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple

import re

def parse_sublist3r(raw_text_output: str) -> List[str]:
    """Parses the text output of Sublist3r to extract subdomains."""
    # This regex is designed to find subdomains, which are typically alphanumeric and can contain hyphens.
    # It avoids capturing the banner and other noisy output from the tool.
    subdomain_pattern = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    found_subdomains = []
    for line in raw_text_output.splitlines():
        clean_line = line.strip()
        if subdomain_pattern.match(clean_line):
            found_subdomains.append(clean_line)
    return found_subdomains

def parse_theharvester_json(json_output: str) -> Dict[str, List[str]]:
    """
    Parses the JSON output of TheHarvester.
    Returns a dictionary with 'emails', 'hosts', and 'ips'.
    """
    try:
        data = json.loads(json_output)
        return {
            "emails": data.get("emails", []),
            "hosts": data.get("hosts", []),
            "ips": data.get("ips", []),
        }
    except json.JSONDecodeError:
        return {"emails": [], "hosts": [], "ips": []}

def parse_nmap_xml(xml_output: str) -> Tuple[List[str], List[str]]:
    """Parses the XML output of Nmap to extract ports and services."""
    ports = []
    services = []
    try:
        root = ET.fromstring(xml_output)
        for port in root.findall(".//port"):
            ports.append(port.get("portid"))
            service = port.find("service")
            if service is not None:
                services.append(service.get("name"))
    except ET.ParseError:
        pass
    return ports, services

def parse_sherlock(raw_text_output: str) -> List[str]:
    """Parses the text output of Sherlock to extract URLs."""
    urls = []
    # Sherlock prefixes found profile URLs with "[+]"
    for line in raw_text_output.splitlines():
        if line.strip().startswith("[+]"):
            # Extract the URL, which is the last part of the line
            parts = line.split(" ")
            if len(parts) > 0 and parts[-1].startswith("http"):
                urls.append(parts[-1])
    return urls
