import ctypes
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import List


SCRIPT_DIR = Path(__file__).resolve().parent
INSTALL_DIR = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "3proxy"
LOG_DIR = INSTALL_DIR / "logs"
LOCAL_EXTRACT_DIRS = [
    SCRIPT_DIR / "3proxy",
    SCRIPT_DIR.parent / "client" / "3proxy",
]
ZIP_NAMES = [
    "3proxy-0.9.6.1-x64.zip",
    "3proxy-0.9.5-x64.zip",
]
DOWNLOAD_URLS = [
    "https://github.com/z3APA3A/3proxy/releases/download/0.9.6/3proxy-0.9.6.1-x64.zip",
    "https://github.com/3proxy/3proxy/releases/download/0.9.6/3proxy-0.9.6.1-x64.zip",
    "https://github.com/z3APA3A/3proxy/releases/download/0.9.5/3proxy-0.9.5-x64.zip",
    "https://github.com/3proxy/3proxy/releases/download/0.9.5/3proxy-0.9.5-x64.zip",
]
OFFICIAL_DOWNLOAD_PAGES = [
    "https://github.com/3proxy/3proxy/releases",
    "https://3proxy.org/download/?l=EN",
]


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def elevate() -> None:
    params = " ".join('"{0}"'.format(arg) for arg in sys.argv)
    rc = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, str(SCRIPT_DIR), 1
    )
    if rc <= 32:
        raise RuntimeError("Unable to obtain administrator rights.")
    sys.exit(0)


def run(cmd: List[str], check: bool = True, cwd: str = None) -> subprocess.CompletedProcess:
    print(">>> {0}".format(" ".join(cmd)))
    return subprocess.run(cmd, universal_newlines=True, check=check, cwd=cwd)


def run_powershell(script: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        check=check,
    )


def run_capture(cmd: List[str]) -> str:
    print(">>> {0}".format(" ".join(cmd)))
    result = subprocess.run(
        cmd,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def prompt_text(label: str, default: str = "") -> str:
    prompt = label
    if default:
        prompt = "{0} [{1}]".format(label, default)
    prompt += ": "
    try:
        value = input(prompt).strip()
    except EOFError:
        value = ""
    return value or default


def get_service_status(service_name: str) -> str:
    try:
        return run_capture(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "(Get-Service -Name '{0}' -ErrorAction Stop).Status".format(service_name),
            ]
        )
    except Exception:
        return ""


def ensure_firewall_rule(name: str, port: str) -> None:
    if get_service_status("MpsSvc").lower() != "running":
        print("Windows Firewall is not running. Skipping inbound rule: {0}".format(name))
        return

    run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            "name={0}".format(name),
        ],
        check=False,
    )
    run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            "name={0}".format(name),
            "dir=in",
            "action=allow",
            "protocol=TCP",
            "localport={0}".format(port),
        ],
        check=False,
    )


def configure_service_recovery(service_name: str) -> None:
    run(
        [
            "sc.exe",
            "failure",
            service_name,
            "reset=",
            "0",
            "actions=",
            "restart/5000/restart/5000/restart/5000",
        ],
        check=False,
    )


def find_existing_zip() -> Path:
    for name in ZIP_NAMES:
        candidate = SCRIPT_DIR / name
        if candidate.exists():
            return candidate
    return Path()


def find_existing_extract_dir() -> Path:
    for base in LOCAL_EXTRACT_DIRS:
        if not base.exists():
            continue
        if (base / "bin64" / "3proxy.exe").exists():
            return base
        if (base / "3proxy.exe").exists():
            return base
    return Path()


def download_zip() -> Path:
    zip_path = SCRIPT_DIR / ZIP_NAMES[0]
    for url in DOWNLOAD_URLS:
        result = run_powershell(
            "try { Invoke-WebRequest -Uri '{0}' -OutFile '{1}' -UseBasicParsing; exit 0 } catch {{ exit 1 }}".format(
                url, zip_path
            ),
            check=False,
        )
        if result.returncode == 0 and zip_path.exists():
            return zip_path
    raise RuntimeError("Could not download 3proxy automatically. Download the x64 zip from the official releases page.")


def extract_zip(zip_path: Path) -> Path:
    extract_dir = SCRIPT_DIR / "3proxy_extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(zip_path), "r") as archive:
        archive.extractall(str(extract_dir))
    return extract_dir


def find_3proxy_binary(base_dir: Path) -> Path:
    for pattern in ("3proxy.exe", "bin\\3proxy.exe"):
        candidate = base_dir / pattern
        if candidate.exists():
            return candidate
    matches = list(base_dir.rglob("3proxy.exe"))
    if matches:
        return matches[0]
    raise FileNotFoundError("3proxy.exe was not found after extraction.")


def install_files(binary_path: Path) -> Path:
    source_dir = binary_path.parent
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
    shutil.copytree(str(source_dir), str(INSTALL_DIR))
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return INSTALL_DIR / "3proxy.exe"


def write_config(config_path: Path, port: str, username: str, password: str, dns1: str, dns2: str) -> None:
    config = "\n".join(
        [
            'nserver {0}'.format(dns1),
            'nserver {0}'.format(dns2),
            'nscache 65536',
            'timeouts 1 5 30 60 180 1800 15 60 15 5',
            'log "{0}" D'.format((LOG_DIR / "3proxy.log").as_posix()),
            'rotate 14',
            'auth strong',
            'users {0}:CL:{1}'.format(username, password),
            'allow {0}'.format(username),
            'socks -p{0}'.format(port),
            'flush',
            'deny *',
            '',
        ]
    )
    config_path.write_text(config, encoding="utf-8")


def install_service(binary_path: Path, config_path: Path) -> None:
    run(["net.exe", "stop", "3proxy"], check=False)
    run([str(binary_path), "--remove"], check=False, cwd=str(binary_path.parent))
    run([str(binary_path), "--install", str(config_path)], check=False, cwd=str(binary_path.parent))
    status = get_service_status("3proxy")
    if not status:
        raise RuntimeError("3proxy service was not installed successfully.")
    run(["sc.exe", "config", "3proxy", "start=", "auto"], check=False)
    configure_service_recovery("3proxy")
    run(["sc.exe", "start", "3proxy"], check=False)


def main() -> None:
    print("3proxy SOCKS5 server setup")
    print("Folder: {0}".format(SCRIPT_DIR))
    print("")
    print("This installs a lightweight SOCKS5 service on Windows.")
    print("Official downloads:")
    for url in OFFICIAL_DOWNLOAD_PAGES:
        print("- {0}".format(url))
    print("Recommended file: 3proxy-0.9.5-x64.zip")
    print("")

    if not is_admin():
        print("Requesting elevation...")
        elevate()

    port = prompt_text("SOCKS5 port", "10808")
    username = prompt_text("SOCKS5 username", "proxyuser")
    password = prompt_text("SOCKS5 password", "ProxyUser2026X")
    dns1 = prompt_text("Primary DNS", "114.114.114.114")
    dns2 = prompt_text("Secondary DNS", "8.8.8.8")

    extracted = find_existing_extract_dir()
    if not extracted:
        zip_path = find_existing_zip()
        if not zip_path:
            print("3proxy zip not found locally. Trying official download...")
            zip_path = download_zip()
        extracted = extract_zip(zip_path)

    binary_path = find_3proxy_binary(extracted)
    installed_binary = install_files(binary_path)
    config_path = INSTALL_DIR / "3proxy.cfg"
    write_config(config_path, port, username, password, dns1, dns2)
    install_service(installed_binary, config_path)
    ensure_firewall_rule("3proxy SOCKS5 {0}".format(port), port)

    print("")
    print("Done.")
    print("Service: 3proxy")
    print("Address: 0.0.0.0:{0}".format(port))
    print("Username: {0}".format(username))
    print("Password: {0}".format(password))
    print("Config: {0}".format(config_path))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nSetup failed: {0}".format(exc))
        sys.exit(1)
