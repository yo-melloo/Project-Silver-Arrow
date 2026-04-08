import subprocess
import time
import sys
import os
import signal
from concurrent.futures import ThreadPoolExecutor

def run_process(command, cwd=None, name="Process", env=None):
    print(f"[LAUNCHER] Starting {name}...")
    try:
        # Usando shell=True para lidar com npm e caminhos de arquivos no Windows
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True,
            env=env
        )
        
        # Lê a saída em tempo real
        for line in iter(process.stdout.readline, ""):
            if line:
                print(f"[{name}] {line.strip()}")
        
        process.stdout.close()
        return_code = process.wait()
        print(f"[LAUNCHER] {name} finished with return code {return_code}")
    except Exception as e:
        print(f"[LAUNCHER] Error in {name}: {str(e)}")

def main():
    # Configura o terminal para UTF-8 caso suporte (Windows)
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul')

    print("="*60)
    print("   PROJECT SILVER ARROW: AUTOMATED LAUNCHER")
    print("="*60)
    
    # Injetar PYTHONIOENCODING para garantir que os processos filhos falem UTF-8
    env_utf8 = os.environ.copy()
    env_utf8["PYTHONIOENCODING"] = "utf-8"

    # Comandos
    tasks = [
        {
            "name": "BRIDGE",
            "command": "python scripts_python/argentum_bridge.py",
            "cwd": os.getcwd(),
            "env": env_utf8
        },
        {
            "name": "WEB-DASHBOARD",
            "command": "npm run dev",
            "cwd": os.path.join(os.getcwd(), "dashboard_web"),
            "env": env_utf8
        },
        {
            "name": "RGB-INTEGRATION",
            "command": "python open_RGB/ac_rgb_integration.py",
            "cwd": os.getcwd(),
            "env": env_utf8
        }
    ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for task in tasks:
            futures.append(
                executor.submit(
                    run_process, 
                    task["command"], 
                    task["cwd"], 
                    task["name"],
                    task.get("env")
                )
            )
        
        try:
            # Mantém o script rodando enquanto os processos estão ativos
            while any(f.running() for f in futures):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[LAUNCHER] Shutting down all processes...")
            sys.exit(0)

if __name__ == "__main__":
    main()
