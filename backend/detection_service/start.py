# start.py
import subprocess
import sys
import os
import time
import signal

# Configurações
PYTHON = sys.executable  # Usa o Python atual
STOP_FLAG = "stop.flag"
APP_FILE = "app.py"
DETECTOR_FILE = "detector.py"

def limpar_flag():
    """Remove o arquivo de parada se existir"""
    if os.path.exists(STOP_FLAG):
        os.remove(STOP_FLAG)
        print("\033[93m[INFO]\033[0m stop.flag removido (início limpo).")

def iniciar_detector():
    """Inicia o detector YOLO e monitora para reiniciar se cair"""
    while True:
        print("\033[92m[START]\033[0m Iniciando detector.py...")
        process = subprocess.Popen([PYTHON, DETECTOR_FILE])
        ret = process.wait()

        if os.path.exists(STOP_FLAG):
            print("\033[93m[STOP]\033[0m Detecção parada pelo usuário.")
            break
        else:
            print("\033[91m[ERROR]\033[0m Detector caiu! Reiniciando em 3s...")
            time.sleep(3)
    return

def iniciar_app():
    """Inicia o Streamlit"""
    print("\033[92m[START]\033[0m Iniciando Streamlit (app.py)...")
    return subprocess.Popen(["streamlit", "run", APP_FILE])

def main():
    limpar_flag()

    # Inicia Streamlit em background
    app_proc = iniciar_app()

    # Inicia detector e aguarda
    try:
        iniciar_detector()
    except KeyboardInterrupt:
        print("\n\033[93m[INFO]\033[0m Encerrando manualmente...")
    finally:
        # Mata o app Streamlit
        print("\033[93m[INFO]\033[0m Encerrando Streamlit...")
        if os.name == "nt":  # Windows
            app_proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:  # Linux/Mac
            app_proc.terminate()
        app_proc.wait()
        print("\033[92m[OK]\033[0m Tudo encerrado.")

if __name__ == "__main__":
    main()
