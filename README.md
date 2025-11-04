# Project ROBUST - Automated OSINT Investigation Framework

ROBUST is an intelligent, modular, and extensible OSINT (Open Source Intelligence) framework built on Python 3 and `asyncio`. It is designed to automate the process of reconnaissance by taking a single starting "entity" (like a domain name) and recursively discovering related entities (subdomains, IPs, emails, etc.) through a series of "transforms." The framework builds a correlation graph of the findings, allowing for deep and automated pivoting.

***

> ## ⚠️ Ethical Use Notice
>
> This tool is intended for professional security analysis, penetration testing, and authorized research purposes only. Unauthorized use of this framework against systems or individuals is strictly prohibited and illegal. The developers assume no liability and are not responsible for any misuse or damage caused by this program. **By using this tool, you agree to do so responsibly and in accordance with all applicable laws.**

## ✨ Features

-   **Asynchronous Core:** Built on `asyncio` for high-performance, concurrent execution of dozens of OSINT tools.
-   **Modular & Extensible:** Easily add new tools by creating simple "Transform" modules. The engine handles the rest.
-   **Automated Pivoting Engine:** The framework automatically takes discovered entities and feeds them back into the engine for deeper recursive analysis.
-   **Persistent State:** Uses an SQLAlchemy backend with a SQLite database to store investigation progress, ensuring that you can resume or review findings later.
-   **Validated Data Models:** Leverages Pydantic to ensure that all data flowing through the system is structured and validated.
-   **Interactive CLI:** A user-friendly command-line interface powered by `rich` and `questionary` makes starting and managing investigations simple.

## ⚙️ Installation

ROBUST is a Python-based framework but orchestrates many popular third-party OSINT tools. Installation is a two-step process: installing the framework's dependencies and installing the external tools.

### Step 1: Install Python Dependencies

It is highly recommended to use a Python virtual environment.

```bash
# Clone the repository
git clone <repository_url>
cd robust-framework

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

### Step 2: Install External OSINT Tools

The framework currently integrates with the following tools. They **must be installed and available in your system's PATH** for the corresponding transforms to work.

-   **Nmap:** Essential for port scanning.
    ```bash
    # For Debian/Ubuntu
    sudo apt-get update && sudo apt-get install nmap
    # For Fedora/CentOS
    sudo dnf install nmap
    # For macOS (using Homebrew)
    brew install nmap
    ```

-   **Masscan:** A very fast port scanner.
    ```bash
    # For Debian/Ubuntu
    sudo apt-get install masscan
    # For macOS (using Homebrew)
    brew install masscan
    ```

-   **Sublist3r:** For subdomain enumeration.
    ```bash
    git clone https://github.com/aboul3la/Sublist3r.git
    # Make sure sublist3r.py is executable and in your PATH
    ```

-   **theHarvester:** For gathering emails, subdomains, and more.
    ```bash
    git clone https://github.com/laramies/theHarvester.git
    cd theHarvester
    pip install -r requirements/base.txt
    # Make sure theHarvester.py is executable and in your PATH
    ```

-   **Sherlock:** To hunt for social media accounts by username.
    ```bash
    git clone https://github.com/sherlock-project/sherlock.git
    cd sherlock
    python3 -m pip install -r requirements.txt
    # Make sure sherlock is executable and in your PATH
    ```

## 🚀 Usage

Once all dependencies and external tools are installed, you can run the framework from the main project directory.

```bash
python main.py
```

You will be greeted by the main menu:

1.  **Start New Investigation:** This will prompt you for the necessary information to begin a new investigation.
    -   **Investigation Name:** A friendly name for your investigation (e.g., `my-company-audit`).
    -   **Seed Entity Type:** The type of the initial data point you want to investigate (e.g., `Domain`).
    -   **Enter Domain:** The actual value of the entity (e.g., `example.com`).

2.  **View Results (by ID):** (Placeholder) This feature will be implemented in a future release to allow you to review the findings of completed investigations.

3.  **Exit:** Close the application.

The engine will then take the seed entity and begin running all relevant transforms. As new entities are discovered, they will be added to the queue for processing, and the cycle will continue until no more new information can be found. All findings are stored in the `investigations.db` SQLite database file.

## 🛠️ Extending the Framework

ROBUST is designed to be easily extensible. Adding a new tool integration is straightforward:

1.  **Create a Pydantic Model:** If your new tool produces a new type of entity (e.g., a `MACAddress`), add a new model to `models.py`.
2.  **Write a Parser:** Add a parsing function to `parsers.py`. This function will take the raw text/json/xml output from your tool and turn it into a list of Pydantic entity models.
3.  **Create a Transform Class:**
    -   Create a new file in the `modules/` directory (e.g., `modules/mac_address_transforms.py`).
    -   Inside this file, create a new class that inherits from `BaseTransform` (from `modules/base_transform.py`).
    -   Implement the `name` property, the `run` async method (which executes your tool using `asyncio.create_subprocess_shell`), and the `parse` method (which calls your parser function).
4.  **Register the Transform:** In `engine.py`, import your new transform class and add it to the `transform_map` dictionary, mapping it to the input entity type it operates on.

That's it! The engine will automatically discover and use your new transform.
