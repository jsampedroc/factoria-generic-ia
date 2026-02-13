import asyncio
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from ai.main import run_factory_pipeline # Suponiendo que encapsulamos el main

app = FastAPI(title="AI Software Factory Dashboard")

# Permitir que el Frontend se conecte sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "Factory is online"}

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Aquí el dashboard enviará la orden de inicio
            data = await websocket.receive_json()
            idea = data.get("idea")
            
            # Enviaremos actualizaciones al front sobre el Token Usage Tracker
            await websocket.send_json({
                "event": "started",
                "message": f"Iniciando factoría para: {idea}"
            })
            
            # Aquí llamaríamos a la lógica de tu main.py
            # pasándole el websocket para que vaya informando [TOKEN SAVED/SPENT]
            
    except Exception as e:
        print(f"WebSocket closed: {e}")