
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import os
import time
from dotenv import load_dotenv

load_dotenv()

def diagnose():
    try:
        host = os.getenv("OPEN_RGB_HOST", "localhost")
        port = int(os.getenv("OPEN_RGB_PORT", 6742))
        client = OpenRGBClient(host, port)
        
        print(f"Conectado a {host}:{port}")
        print(f"Total de dispositivos: {len(client.devices)}")
        print("-" * 50)
        
        for i, device in enumerate(client.devices):
            print(f"ID {i}: {device.name}")
            print(f"  - LEDs: {len(device.leds)}")
            modes = [m.name for m in device.modes]
            print(f"  - Modos disponíveis: {modes}")
            print(f"  - Modo ativo: {device.active_mode}")
            
            # Tentar encontrar modo Direct ou Static
            direct_mode = next((m for m in modes if 'direct' in m.lower()), None)
            if not direct_mode:
                direct_mode = next((m for m in modes if 'static' in m.lower()), None)
                
            if direct_mode:
                print(f"  - [INFO] Sugerido modo: {direct_mode}")
            else:
                print(f"  - [AVISO] Nenhum modo de controle direto óbvio.")
            
            # Se for o Device 0 (RAM), testar uma cor
            if i == 0:
                print(f"  - [TESTE] Tentando colocar Vermelho no Device 0...")
                try:
                    # Tentar trocar para Direct se possível
                    if direct_mode and device.active_mode != direct_mode:
                        device.set_mode(direct_mode)
                        time.sleep(0.5)
                    
                    device.set_color(RGBColor(255, 0, 0))
                    print(f"  - [TESTE] Comando enviado. A RAM ficou vermelha?")
                except Exception as test_e:
                    print(f"  - [ERRO NO TESTE] {test_e}")
            
            print("-" * 50)
            
    except Exception as e:
        print(f"Erro no diagnóstico: {e}")

if __name__ == "__main__":
    diagnose()
