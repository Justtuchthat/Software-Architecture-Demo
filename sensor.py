from __future__ import annotations
import pygame
import math
from mqtt_broker import MessageBroker
import uuid

# simulates the MQTT message broker.
broker = MessageBroker()

def calc_dist(p1: pygame.Vector2, p2: pygame.Vector2) -> float:
    dif_x: float = p1.x - p2.x
    dif_y: float = p1.y - p2.y
    return math.sqrt(dif_x * dif_x + dif_y * dif_y)

class Sensor():
    _id_counter = 0

    def __init__(self, x: int, y: int, range_x: int, range_y: int):
        Sensor._id_counter += 1
        self.id = Sensor._id_counter
        self.x = x
        self.y = y
        self.range = calc_dist(pygame.Vector2(x, y), pygame.Vector2(range_x, range_y))
        self.connected_sensors: list[Sensor|Hub] = []
        self.visited = False

        # Virtual MQTT setup
        self.topic = f"mesh/sensor/{self.id}"

        #Track messages already seen to prevent infinite loops
        self.seen_messages: set[str] = set()
    
    def subscribe_to(self, other: Sensor | Hub):
        """Subscribe to another nodes topic"""
        broker.subscribe(other.topic, self.on_message)

    def on_message(self, topic: str, message: str) -> None:
        try:
            msg_id, content = message.split(":", 1)
        except ValueError:
            # If message has no ID, treat as new
            msg_id = str(uuid.uuid4())
            content = message

        # Ignore already seen messages
        if msg_id in self.seen_messages:
            return
        self.seen_messages.add(msg_id)

        # Forward to neighbors
        for neighbor in self.connected_sensors:
            if isinstance(neighbor, Sensor):
                neighbor.publish(content, msg_id)
            else:
                neighbor.publish(f"From Sensor {self.id}: {content}", msg_id)
    
    def publish(self, message: str, msg_id: str | None = None) -> None:
        if msg_id == None:
            msg_id = str(uuid.uuid4())
        self.seen_messages.add(msg_id)
        broker.publish(self.topic, f"{msg_id}:{message}")

    
    def get_location(self) -> pygame.Vector2:
        return pygame.Vector2(self.x, self.y)
    
    def get_range(self) -> float:
        return self.range


def sensor_list() -> list[Sensor]:
    return []

def add_sensor(sensor_list: list[Sensor], sensor: Sensor) -> None:
    sensor_list.append(sensor)

def gen_mesh_no_update_MQTT(sensors: list[Sensor], hub: Hub) -> None:
    for s in sensors:
        s.connected_sensors = []
    hub.connect_sensors(sensors, update_MQTT=False)
    for s in sensors:
        s_center = s.get_location()
        for a in sensors:
            if s==a:
                continue
            a_center = a.get_location()
            dist = calc_dist(s_center, a_center)
            if dist < s.get_range() and dist < a.get_range():
                s.connected_sensors.append(a)

def gen_mesh(sensors: list[Sensor], hub: Hub) -> None:
    for s in sensors:
        s.connected_sensors = []
    hub.connect_sensors(sensors)
    for s in sensors:
        s_center = s.get_location()
        for a in sensors:
            if s==a:
                continue
            a_center = a.get_location()
            dist = calc_dist(s_center, a_center)
            if dist < s.get_range() and dist < a.get_range():
                s.connected_sensors.append(a)
                s.subscribe_to(a)

def flood_fill(sensor_list: list[Sensor], hub: Hub) -> None:
    if len(sensor_list) == 0: return
    hub.visited = False
    for s in sensor_list:
        s.visited = False
    flood_queue: list[Hub|Sensor] = [hub]
    while len(flood_queue) > 0:
        next_sensor = flood_queue.pop(0)
        if next_sensor.visited:
            continue
        next_sensor.visited = True
        for a in next_sensor.connected_sensors:
            flood_queue.append(a)

def send_message_on_click(sensor_list: list[Sensor], mouse_pos: pygame.Vector2) -> None:
    closest: int = -1
    closest_dist: float = float("inf")
    for i, sensor in enumerate(sensor_list):
        dist = calc_dist(sensor.get_location(), mouse_pos)
        if dist < closest_dist:
            closest = i
            closest_dist = dist
    if closest == -1:
        print("Cannot send message from any sensors when none have been placed")
        return
    if closest_dist < 10:
        sensor_list[closest].publish(f"sensor #{sensor_list[closest].id} got clicked!")
    else:
        print("No sensor was close to click to send message")

def delete_sensor(sensor_list: list[Sensor], mouse_pos: pygame.Vector2) -> None:
    closest: int = -1
    closest_dist: float = float("inf")
    for i, sensor in enumerate(sensor_list):
        dist = calc_dist(sensor.get_location(), mouse_pos)
        if dist < closest_dist:
            closest = i
            closest_dist = dist
    if closest == -1:
        print("Cannot delete any sensors when none have been placed")
        return
    if closest_dist < 10:
        sensor_list.pop(closest)
    else:
        print("No sensor was close to click to remove")

def generate_hex_sensor_mesh(sensor_list: list[Sensor], screen: pygame.Surface, hub: Hub) -> None:
    loc = hub.get_location()
    x = int(loc.x)
    y = int(loc.y)
    dif_x = 180
    x -= dif_x
    up_x = int(180*(-1/2))
    up_y = int(180*(math.sqrt(3)/2))
    while y > 0:
        dif_x *= -1
        while x > 0 and x < screen.get_size()[0]:
            add_sensor(sensor_list, Sensor(x, y, x+200, y))
            x += dif_x
        x += up_x
        y -= up_y
        while x < 0:
            x += 180
        


class Hub:
    def __init__(self, x: int, y: int, range: float):
        self.x = x
        self.y = y
        self.range = range
        self.connected_sensors: list[Sensor] = []
        self.visited = False

        self.topic = "mesh/hub"

        self.seen_messages: set[str] = set()

    def on_message(self, topic: str, message: str) -> None:
        try:
            msg_id, content = message.split(":", 1)
        except ValueError:
            msg_id = str(uuid.uuid4())
            content = message

        if msg_id in self.seen_messages:
            return
        self.seen_messages.add(msg_id)
        print(f"[Hub] received on {topic}:{content}")
    
    def publish(self, message: str, msg_id: str | None = None) -> None:
        if msg_id is None:
            msg_id = str(uuid.uuid4())
        if msg_id in self.seen_messages:
            return
        # print(f"[Hub] publishing: {message}")
        broker.publish(self.topic, f"{msg_id}:{message}")

    def get_location(self) -> pygame.Vector2:
        return pygame.Vector2(self.x, self.y)
    
    def connect_sensors(self, sensor_list: list[Sensor], update_MQTT: bool = True) -> None:
        self.connected_sensors = []
        for s in sensor_list:
            dist = calc_dist(self.get_location(), s.get_location())
            if dist > self.range: continue
            if dist > s.range: continue
            self.connected_sensors.append(s)
            s.connected_sensors.append(self)
            if not update_MQTT:
                return
            broker.subscribe(s.topic, self.on_message)
            s.subscribe_to(self)
