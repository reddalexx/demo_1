import asyncio
import cachetools.func
import json
import logging
import os
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaProducer

from .schemas import HotelsRequest, HotelData, SaveHotelDataRequest
from .search import TripAdviserHotelsSearch
from .tasks import get_hotels_urls, get_completed_tasks


logger = logging.getLogger(__name__)


app = FastAPI(
    title='Demo App FastAPI',
    version='1.0.0',
    openapi_url='/fastapi/openapi.json',
    docs_url='/fastapi/docs',
    redoc_url='/fastapi/redoc',
)


origins = [
    os.environ.get('DAPHNE_URL', 'localhost:3350')
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


kafka_url = os.environ.get('KAFKA_URL', 'localhost:9092')
topic = os.environ.get('KAFKA_TOPIC', 'demo')


@app.get('/fastapi/')
async def root():
    return {'message': 'Hello World'}


@app.post('/fastapi/search-hotels-using-asyncio/', response_model=List[HotelData])
async def search_hotels_asyncio(request: HotelsRequest):
    engine = TripAdviserHotelsSearch()
    return await engine.async_scrape(**request.dict())


@app.post('/fastapi/search-hotels-using-celery/', response_model=str)
async def search_hotels_celery(request: HotelsRequest):
    task = get_hotels_urls.s(**request.dict()).delay()
    return task.id


@cachetools.func.ttl_cache(maxsize=128, ttl=3600)
def get_kafka_producer():
    logger.info(f'Activated Kafka Producer, KAFKA_URL: {kafka_url}')
    return KafkaProducer(
        bootstrap_servers=[kafka_url],
        # security_protocol="SSL",
        # ssl_cafile="./ca.pem",
        # ssl_certfile="./service.cert",
        # ssl_keyfile="./service.key",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


@app.post('/fastapi/save-selected-hotels/')
async def save_selected_hotels(request: SaveHotelDataRequest):
    req_data = request.dict()
    for i in req_data['data']:
        i['city_id'] = req_data['city_id']
        i['uid'] = i.pop('id')

    kafka_producer = get_kafka_producer()
    kafka_producer.send(topic, value=req_data['data'])
    kafka_producer.flush()
    logger.info(f'Kafka Producer has send message: {req_data["data"]}')


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket('/fastapi/ws')
async def websocket_endpoint(websocket: WebSocket):
    tasks = None
    await manager.connect(websocket)
    try:
        while True:
            # data = await websocket.receive_text()
            await asyncio.sleep(2)
            _tasks = get_completed_tasks()
            if _tasks and _tasks != tasks:
                await manager.send_personal_message({'tasks': _tasks}, websocket)
            tasks = _tasks
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({'data': f'Client #.. left the channel'})


@app.exception_handler(404)
async def custom_404_handler(_, __):
    return RedirectResponse('/404')
