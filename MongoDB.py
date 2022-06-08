from pymongo import MongoClient
from bson.objectid import ObjectId

uri = "mongodb://localhost:27017/"
Client = MongoClient(uri)
DataBase = Client["ParkingManagement"]

AdminCollection = DataBase["Admin"]


AdminCollection.insert_one({"UserName":"Admin","PassWord":"Admin"})