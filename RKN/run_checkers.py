import os
import subprocess
import sys

def run_script(script_name: str) -> None:
    print(f"Запуск {script_name}...")

    # путь к текущему файлу
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # абсолютный путь к скрипту
    script_path = os.path.join(base_dir, script_name)
    
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Ошибка при выполнении {script_name}")
        print(result.stderr)
        sys.exit(1)

    print(f"{script_name} успешно завершён.\n")
    print(result.stdout)


def main():
    scripts = [
        "sites_auto_checker.py",
        # "sites_auto_checker_SB.py",
        "check_spamhaus.py",
        "check_domain_reputation.py"
    ]

    for script in scripts:
        run_script(script)


if __name__ == "__main__":
    main()