from .sensing import Sensing
import json, os

class Variable(Sensing):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
        if not os.path.exists("Data/data.json"):
            if not os.path.exists("Data/"):
                os.makedirs("Data", exist_ok=True)
            with open("Data/data.json", "x", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            
        with open("Data/data.json", "r") as file:
            data  = json.load(file)
        
        if type(data) != list:
            with open("Data/data.json", "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

    def set_JSON(self, name, vaule):
        with open("Data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        data = [item for item in data if item["name"] != name]
        
        vaule = {
            "name": str(name),
            "data": str(vaule)
        }
        data.append(vaule)
        
        with open("Data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    
    def read_JSON(self, name):
        with open("Data/data.json", "r") as file:
            data = json.load(file)
            for i in range(len(data)):
                if data[i]["name"] == name:
                    return data[i]["data"]