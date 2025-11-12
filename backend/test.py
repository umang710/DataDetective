# from pymongo import MongoClient
# import certifi
# uri = 'mongodb+srv://karthik10:Newpassword123@cluster0.1yvkxkp.mongodb.net/?appName=Cluster0'
# client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
# try:
#     print(client.server_info())
#     print("✅ MongoDB connection successful")
# except Exception as e:
#     print("❌", e)


from pymongo import MongoClient
import certifi
uri = "mongodb+srv://karthik10:Newpassword123@cluster0.1yvkxkp.mongodb.net/?appName=Cluster0"
client = MongoClient(uri,  tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
try:
    print(client.server_info())
    print("OK")
except Exception as e:
    print("ERR", e)

