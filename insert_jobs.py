from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from io import BytesIO 

# Create a new client and connect to the server
client = MongoClient("mongodb://localhost:27017")


db = client['Peedeed']
collection = db['jobs']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def add_jobs(company, position, location, skills, job_type, description):
    job={
        company: company,
        position : position,
        location : location,
        skills : skills,
        job_type : job_type,
        description : description


    }
    collection.insert_one(job)