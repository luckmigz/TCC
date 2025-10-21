# CÓDIGO: teste_monitor_light.py
# Executa o monitor leve de restaurante (sem stream contínuo e sem vídeo).

import time
from restaurante_monitor_light import RestauranteMonitorLight

if __name__ == "__main__":
    print("🚀 Iniciando monitoramento leve do restaurante...")

    monitor = RestauranteMonitorLight(
        cnpj="00.000.000/0001-01",
        nome="Restaurante Light",
        intervalo=5  # segundos
    )

    try:
        monitor.iniciar()

        while True:
            # Pode ser expandido para salvar logs ou enviar dados a um dashboard
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Encerrando monitoramento leve...")
        monitor.parar()
    except Exception as e:
        print(f"\n⚠️ Erro inesperado: {e}")
