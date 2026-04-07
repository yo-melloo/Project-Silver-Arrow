from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from argentum_core import AssettoCorsaProvider, TelemetryProvider

# Load .env from root or current directory
load_dotenv(Path(__file__).parent.parent / '.env')
load_dotenv()

app = FastAPI()

# Configuração de CORS para permitir conexões externas (Celular/Tablet)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem na rede local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o provedor de dados
ac = AssettoCorsaProvider()
mock = TelemetryProvider()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client: str = "web"):
    await websocket.accept()
    client_host = websocket.client.host
    print(f"📡 Conexão recebida de {client_host} | Tipo: {client}")
    
    # Determina qual provedor usar
    provider = ac if ac.connect() else mock
    print(f"🔄 WebBridge: Usando {provider.__class__.__name__}")
    
    try:
        while True:
            data = provider.fetch()
            if data:
                # Envio condicional baseado no tipo de cliente
                if client == "esp":
                    # JSON reduzido para ESP32 (evita fragmentação)
                    reduced_data = {
                        "rpm": data["rpm"],
                        "max_rpm": data["max_rpm"],
                        "speed": data["speed"],
                        "gear": data["gear"],
                        "car": data["car"][:10]  # Limita nome do carro a 10 caracteres
                    }
                    await websocket.send_text(json.dumps(reduced_data))
                    # 60 FPS para ESP32 (16ms) - Sincronizado com OpenRGB
                    await asyncio.sleep(0.016)
                else:
                    # Objeto completo para Dashboard Web
                    await websocket.send_text(json.dumps(data))
                    # 60 FPS para a Web (16ms)
                    await asyncio.sleep(0.016)
    except Exception as e:
        print(f"Conexão encerrada: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    host = os.getenv("BRIDGE_HOST", "0.0.0.0")
    port = int(os.getenv("BRIDGE_PORT", 8001))
    print(f"🚀 Argentum WebBridge disparando em http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
