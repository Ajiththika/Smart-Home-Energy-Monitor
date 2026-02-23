from dataclasses import dataclass

@dataclass
class Device:
    device_id: str
    name: str
    wattage: float                
    avg_hours_per_day: float       
    room_location: str