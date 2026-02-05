from pymongo import MongoClient
import os
from django.conf import settings

client = MongoClient(settings.MONGO_URI)
db = client.telegram_drive
users_collection = db.users