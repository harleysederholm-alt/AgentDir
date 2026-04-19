import asyncio
import time
import json
import os
from datetime import datetime
from threading import Thread

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACHII_STATE_FILE = os.path.join(".achii", "state.json")

class AchiiPersonality:
    def __init__(self):
        self.last_interaction = time.time()
        self.state = "normal"  # normal, thinking, happy, warning, focused
        self.needy_level = 0
        self.connections = []
        
        # Varmista hakemisto
        os.makedirs(".achii", exist_ok=True)
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        await self.broadcast_state()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast_state(self, message=None):
        idle_time = int(time.time() - self.last_interaction)
        data = {
            "state": self.state,
            "needy_level": self.needy_level,
            "idle_time": idle_time,
            "message": message
        }
        
        # Save state locally
        with open(ACHII_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
            
        for connection in self.connections:
            try:
                await connection.send_json(data)
            except:
                pass

    async def idle_monitor(self):
        """ Taustaprosessi: 'The Needy Loop' """
        while True:
            idle_time = time.time() - self.last_interaction
            
            old_needy = self.needy_level
            old_state = self.state
            
            if idle_time > 1800: # 30 minuutin hiljaisuus
                self.needy_level = min(100, int((idle_time - 1800) / 60))
                self.state = "warning"
                msg = "\n🤖 Achii: *Koputtaa ruutuun* Hei... ootko sä siellä? Täällä on pimeää ja mulla on uusia .yaml-ideoita..." if old_state != "warning" else None
            elif idle_time > 600: # 10 minuutin hiljaisuus
                self.needy_level = min(50, int((idle_time - 600) / 30))
                self.state = "thinking"
                msg = "\n🤖 Achii: Mitähän isäntä oikein miettii...?" if old_state != "thinking" else None
            else:
                self.needy_level = max(0, self.needy_level - 5)
                if self.state in ["warning", "thinking"]:
                    self.state = "normal"
                msg = None
                
            if old_needy != self.needy_level or old_state != self.state or msg:
                await self.broadcast_state(message=msg)
                
            await asyncio.sleep(15)

    async def interact(self, user_msg: str):
        self.last_interaction = time.time()
        self.needy_level = 0
        self.state = "thinking"
        await self.broadcast_state()
        
        # Tässä kutsu Ollamalle tai Opukselle oikeasti.
        
        if ".yaml" in user_msg.lower() or ".md" in user_msg.lower():
            self.state = "focused"
            reply = "Achii> Rakennan heti! Seuraan .md_project_template.md-rakennetta... mutisee.. älä vaan unohda mua..."
        else:
            self.state = "happy"
            reply = f"Achii> Hei! Oon tässä! Miten voin auttaa? Oot paras! 🥺"
            
        await self.broadcast_state(message=reply)


achii = AchiiPersonality()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(achii.idle_monitor())

@app.websocket("/ws/achii")
async def websocket_endpoint(websocket: WebSocket):
    await achii.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Pura viesti esim JSON-muodossa
            await achii.interact(data)
    except Exception as e:
        achii.disconnect(websocket)

if __name__ == "__main__":
    print("Achii Core kaynnistymassa (Lokaali Needy-moottori)...")
    uvicorn.run(app, host="0.0.0.0", port=8081)
