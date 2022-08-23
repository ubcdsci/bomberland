import asyncio
from html import entities
from typing import Union
import websockets
import json

from classes import UnitState, Coordinate, Indestructible, Destructible, Radius, Ammo, Bomb, Fire, BoardState
from websockets.client import WebSocketClientProtocol

_move_set = set(("up", "down", "left", "right"))


class GameState:
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self.agent_id = None
        self.agent_a_ids = None
        self.agent_b_ids = None
        self.config = None
        self._states = []
        self._tick_callback = None

    def set_game_tick_callback(self, generate_agent_action_callback):
        self._tick_callback = generate_agent_action_callback

    async def connect(self):
        self.connection = await websockets.connect(self._connection_string)
        if self.connection.open:
            return self.connection

    async def _send(self, packet):
        await self.connection.send(json.dumps(packet))

    async def send_move(self, move: str, unit_id: str):
        if move in _move_set:
            packet = {"type": "move", "move": move, "unit_id": unit_id}
            await self._send(packet)

    async def send_bomb(self, unit_id: str):
        packet = {"type": "bomb", "unit_id": unit_id}
        await self._send(packet)

    async def send_detonate(self, x, y, unit_id: str):
        packet = {"type": "detonate", "coordinates": [
            x, y], "unit_id": unit_id}
        await self._send(packet)

    async def _handle_messages(self, connection: WebSocketClientProtocol):
        while True:
            try:
                raw_data = await connection.recv()
                data = json.loads(raw_data)
                await self._on_data(data)
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

    async def _on_data(self, data):

        data_type = data.get("type")

        if data_type == "info":
            # no operation
            pass
        elif data_type == "game_state":
            payload = data.get("payload")
            self._on_game_state(payload)
        elif data_type == "tick":
            payload = data.get("payload")
            await self._on_game_tick(payload)
        elif data_type == "endgame_state":
            payload = data.get("payload")
            winning_agent_id = payload.get("winning_agent_id")
            print(f"Game over. Winner: Agent {winning_agent_id}")
        else:
            print(f"unknown packet \"{data_type}\": {data}")

    def _on_game_state(self, game_state):
        self.agent_id = game_state["connection"]["agent_id"]
        self.config = game_state["config"]
        self.agent_a_ids = game_state["agents"]["a"]["unit_ids"]
        self.agent_b_ids = game_state["agents"]["b"]["unit_ids"]

        entities = []
        for unit in self.agent_a_ids+self.agent_b_ids:
            state = game_state["unit_state"][f"{unit}"]

            entities.append(UnitState(
            state["unit_id"], 
            state["agent_id"],
            Coordinate(state["coordinates"][0], state["coordinates"][1]),
            state["hp"],
            state["blast_diameter"],
            state["inventory"]["bombs"],
            state["invulnerability"]))
        
        for entity in game_state["entities"]:
            entity_type = entity["type"]
            if entity_type == "m":
                entities.append(Indestructible(entity["created"], Coordinate(entity["x"],entity["y"])))
            elif entity_type == "w" or entity["type"] == "o":
                entities.append(Destructible(entity["created"], Coordinate(entity["x"],entity["y"]),entity["hp"]))
            elif entity_type == "a":
                entities.append(Ammo(entity["created"], Coordinate(entity["x"],entity["y"]),entity["expires"],entity["hp"]))
            elif entity_type == "bp":
                entities.append(Radius(entity["created"], Coordinate(entity["x"],entity["y"]),entity["expires"],entity["hp"]))
            elif entity_type == "b":
                entities.append(Bomb(entity["created"], 
                Coordinate(entity["x"],entity["y"]),
                entity["owner_unit_id"],
                entity["expires"],
                entity["hp"],
                entity["blast_diameter"]))
            elif entity_type == "x":
                try:
                    entities.append(Fire(entity["created"], Coordinate(entity["x"],entity["y"]),
                    entity["owner_unit_id"],entity["expires"]))
                except KeyError:
                    entities.append(Fire(entity["created"], Coordinate(entity["x"],entity["y"])))

        self._states.append(BoardState(game_state["world"]["width"],game_state["world"]["height"],
        game_state["tick"],entities))

        print(self._states)

        return 1

    async def _on_game_tick(self, game_tick):
        events = game_tick.get("events")
        for event in events:
            event_type = event.get("type")
            if event_type == "entity_spawned":
                self._on_entity_spawned(event)
            elif event_type == "entity_expired":
                self._on_entity_expired(event)
            elif event_type == "unit_state":
                payload = event.get("data")
                self._on_unit_state(payload)
            elif event_type == "entity_state":
                x, y = event.get("coordinates")
                updated_entity = event.get("updated_entity")
                self._on_entity_state(x, y, updated_entity)
            elif event_type == "unit":
                unit_action = event.get("data")
                self._on_unit_action(unit_action)
            else:
                print(f"unknown event type {event_type}: {event}")
        if self._tick_callback is not None:
            tick_number = game_tick.get("tick")
            await self._tick_callback(tick_number, self._state)

    def _on_entity_spawned(self, spawn_event):
        spawn_payload = spawn_event.get("data")
        self._state["entities"].append(spawn_payload)

    def _on_entity_expired(self, spawn_event):
        expire_payload = spawn_event.get("data")

        def filter_entity_fn(entity):
            [x, y] = expire_payload
            entity_x = entity.get("x")
            entity_y = entity.get("y")
            should_remove = entity_x == x and entity_y == y
            return should_remove == False

        self._state["entities"] = list(filter(
            filter_entity_fn, self._state["entities"]))

    def _on_unit_state(self, unit_state):
        unit_id = unit_state.get("unit_id")
        self._state["unit_state"][unit_id] = unit_state

    def _on_entity_state(self, x, y, updated_entity):
        for entity in self._state.get("entities"):
            if entity.get("x") == x and entity.get("y") == y:
                self._state["entities"].remove(entity)
        self._state["entities"].append(updated_entity)

    def _on_unit_action(self, action_packet):
        unit_id = action_packet["unit_id"]
        unit = self._state["unit_state"][unit_id]
        coordinates = unit.get("coordinates")
        action_type = action_packet.get("type")
        if action_type == "move":
            move = action_packet.get("move")
            if move in _move_set:
                new_coordinates = self._get_new_unit_coordinates(
                    coordinates, move)
                self._state["unit_state"][unit_id]["coordinates"] = new_coordinates
        elif action_type == "bomb":
            # no - op since this is redundant info
            pass
        elif action_type == "detonate":
            # no - op since this is redundant info
            pass
        else:
            print(f"Unhandled agent action recieved: {action_type}")

    def _get_new_unit_coordinates(self, coordinates, move_action) -> Union[int, int]:
        [x, y] = coordinates
        if move_action == "up":
            return [x, y+1]
        elif move_action == "down":
            return [x, y-1]
        elif move_action == "right":
            return [x+1, y]
        elif move_action == "left":
            return [x-1, y]
