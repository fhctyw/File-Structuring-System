import subprocess
import threading
import signal
import sys
import argparse
import os
import shutil

processes = []

# ANSI кольори
COLORS = {
    "Backend": "\033[94m",   # синій
    "Frontend": "\033[92m",  # зелений
    "SYSTEM": "\033[93m",    # жовтий
    "ERROR": "\033[91m",     # червоний
    "RESET": "\033[0m"
}

def run_command(command, cwd, env=None):
    result = subprocess.run(command, shell=True, cwd=cwd, env=env)
    if result.returncode != 0:
        print(f"{COLORS['ERROR']}❌ Команда не виконана: {command}{COLORS['RESET']}")
        sys.exit(1)

def check_tool(tool_name):
    result = shutil.which(tool_name)
    if result is None:
        print(f"{COLORS['ERROR']}❌ {tool_name} не знайдено. Будь ласка, встановіть його та переконайтеся, що він є в PATH.{COLORS['RESET']}")
        sys.exit(1)
    return result

def setup_backend(backend_dir, production=False):
    venv_path = os.path.join(backend_dir, 'venv')
    if not os.path.exists(venv_path):
        print(f"{COLORS['SYSTEM']}🔹 Створення віртуального середовища...{COLORS['RESET']}")
        run_command("python -m venv venv", backend_dir)
    else:
        print(f"{COLORS['SYSTEM']}✅ Віртуальне середовище вже існує{COLORS['RESET']}")

    if os.name == 'nt':
        python_path = os.path.abspath(os.path.join(venv_path, 'Scripts', 'python.exe'))
    else:
        python_path = os.path.join(venv_path, 'bin', 'python')

    print(f"{COLORS['SYSTEM']}🔹 Встановлення залежностей для бекенду...{COLORS['RESET']}")
    run_command(f'"{python_path}" -m pip install --upgrade pip', backend_dir)
    run_command(f'"{python_path}" -m pip install -r requirements.txt', backend_dir)

    # Команда для продакшену або розробки
    if production:
        # Для Windows не використовуємо workers у продакшен-режимі
        if os.name == 'nt':
            # Для Windows без воркерів
            uvicorn_cmd = f'"{python_path}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
        else:
            # Для Linux/Mac з воркерами
            uvicorn_cmd = f'"{python_path}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4'
    else:
        # Розробка з гарячим перезавантаженням
        uvicorn_cmd = f'"{python_path}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
    
    return uvicorn_cmd

def setup_frontend(frontend_dir, production=False):
    check_tool("node")
    check_tool("npm")

    package_json = os.path.join(frontend_dir, 'package.json')
    if not os.path.isfile(package_json):
        print(f"{COLORS['ERROR']}❌ package.json не знайдено в {frontend_dir}{COLORS['RESET']}")
        sys.exit(1)

    node_modules = os.path.join(frontend_dir, 'node_modules')
    if not os.path.exists(node_modules) or len(os.listdir(node_modules)) == 0:
        print(f"{COLORS['SYSTEM']}🔹 Встановлення пакетів для фронтенду (npm install)...{COLORS['RESET']}")
        run_command("npm install", frontend_dir)
    else:
        print(f"{COLORS['SYSTEM']}✅ Пакети для фронтенду вже встановлені{COLORS['RESET']}")
    
    # Якщо режим продакшену, будуємо фронтенд
    if production:
        # Встановлюємо serve, якщо потрібно
        print(f"{COLORS['SYSTEM']}🔹 Перевірка наявності serve для обслуговування SPA...{COLORS['RESET']}")
        if not os.path.exists(os.path.join(frontend_dir, 'node_modules', '.bin', 'serve')):
            print(f"{COLORS['SYSTEM']}🔹 Встановлення serve для обслуговування SPA...{COLORS['RESET']}")
            run_command("npm install serve --save-dev", frontend_dir)
        
        print(f"{COLORS['SYSTEM']}🔹 Побудова фронтенду для продакшену...{COLORS['RESET']}")
        run_command("npm run build", frontend_dir)

def run_process(command, name, cwd, env=None):
    print(f"{COLORS['SYSTEM']}🔹 Запуск {name}: {command}{COLORS['RESET']}")
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )
    processes.append(process)

    try:
        for line in process.stdout:
            colored_line = f"{COLORS[name]}[{name}] {line.rstrip()}{COLORS['RESET']}"
            print(colored_line)
    except Exception as e:
        print(f"{COLORS['ERROR']}❌ Помилка читання виводу {name}: {e}{COLORS['RESET']}")

    process.wait()
    print(f"{COLORS['ERROR']}❌ {name} зупинено{COLORS['RESET']}")

def serve_frontend(frontend_dir):
    # Обслуговування побудованого фронтенду за допомогою простого HTTP сервера
    dist_dir = os.path.join(frontend_dir, 'dist')
    if not os.path.exists(dist_dir):
        print(f"{COLORS['ERROR']}❌ Директорію збірки фронтенду не знайдено: {dist_dir}{COLORS['RESET']}")
        sys.exit(1)
    
    # Використовуємо http.server з стандартної бібліотеки Python для обслуговування статичних файлів
    return f"python -m http.server 3000 --directory {dist_dir}"

def stop_all():
    print(f"\n{COLORS['SYSTEM']}🛑 Зупинка всіх процесів...{COLORS['RESET']}")
    for proc in processes:
        proc.terminate()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Запуск бекенду (FastAPI) та фронтенду (Vite) разом з конфігурацією")
    parser.add_argument("-c", "--config", help="Шлях до конфігураційного файлу для структурування", default=None)
    parser.add_argument("-p", "--production", action="store_true", help="Запуск в режимі продакшену")

    args = parser.parse_args()

    backend_dir = "./backend"
    frontend_dir = "./frontend"
    
    # Відображення режиму
    mode = "ПРОДАКШЕН" if args.production else "РОЗРОБКА"
    print(f"{COLORS['SYSTEM']}🚀 Запуск у режимі {mode}{COLORS['RESET']}")

    # Перевірка конфігураційного файлу (якщо він був вказаний)
    if args.config and not os.path.isfile(args.config):
        print(f"{COLORS['ERROR']}❌ Конфігураційний файл не знайдено: {args.config}{COLORS['RESET']}")
        sys.exit(1)

    # Налаштування середовища бекенду
    uvicorn_cmd = setup_backend(backend_dir, args.production)

    # Налаштування середовища фронтенду
    setup_frontend(frontend_dir, args.production)

    # Передача шляху до конфігурації як змінної середовища (якщо файл вказано)
    backend_env = os.environ.copy()
    if args.config:
        backend_env["STRUCTURE_CONFIG_PATH"] = os.path.abspath(args.config)
    
    # Додавання прапорця продакшену до середовища
    if args.production:
        backend_env["ENVIRONMENT"] = "production"
    else:
        backend_env["ENVIRONMENT"] = "development"

    # Обробка Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: stop_all())

    # Запуск бекенду (FastAPI)
    backend_thread = threading.Thread(
        target=run_process,
        args=(uvicorn_cmd, "Backend", backend_dir, backend_env)
    )
    backend_thread.start()

    # Запуск фронтенду - або сервера розробки, або обслуговування статичних файлів
    if args.production:
        frontend_cmd = serve_frontend(frontend_dir)
    else:
        frontend_cmd = "npm run dev"
        
    frontend_thread = threading.Thread(
        target=run_process,
        args=(frontend_cmd, "Frontend", frontend_dir)
    )
    frontend_thread.start()

    # Очікування завершення обох
    backend_thread.join()
    frontend_thread.join()

if __name__ == "__main__":
    main()