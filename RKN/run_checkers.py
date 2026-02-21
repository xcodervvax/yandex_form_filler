import subprocess
import sys

def run_script(script_name: str) -> None:
    print(f"Запуск {script_name}...")
    
    result = subprocess.run(
        [sys.executable, script_name],
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
        "check_spamhause.py",
        # позже просто добавишь:
        # "script3.py"
    ]

    for script in scripts:
        run_script(script)


if __name__ == "__main__":
    main()