# Author: LE VAN THIEN
# Email: ngocthien3920@gmail.com
# Phone: 0329615785

from pymongo import MongoClient
from bson.objectid import ObjectId

uri = "mongodb://localhost:27017/"
Client = MongoClient(uri)
DataBase = Client["ParkingManagement"]

AdminCollection = DataBase["Admin"]


AdminCollection.insert_one({"UserName":"Admin","PassWord":"Admin"})
