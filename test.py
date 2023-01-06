from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(f"mongodb+srv://developers:1234@cluster0.a8ug08d.mongodb.net/?retryWrites=true&w=majority")
db = cluster["discord-bot"]
userinfo = db["userinfo"]

# get current datetime
# today = datetime.now()
# print('Today Datetime:', today)
#
# # Get current ISO 8601 datetime in string format
# iso_date = today.isoformat()
# print('ISO DateTime:', iso_date)

userinfo.update_many({}, {"$set": {"todayLevelUp" : 0 }})
