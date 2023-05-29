from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("CONNECTION"))
client = MongoClient(os.getenv("CONNECTION"))
db = client["survey-database"]
survey_questions_and_answers = db["survey-questions-and-answers"]

try:
    # db = client["survey-database"]
    # user = db["user"]
    # user_list = user.find_one({"username": "amongus"})
    # print(user_list)

    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# uri = "mongodb+srv://transcendes:hHEKCXtrt9BHZLUo@storagecluster.amgihr0.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)