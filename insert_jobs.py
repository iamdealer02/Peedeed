from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from io import BytesIO 
import json

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
        'company': company,
        'position' : position,
        'location' : location,
        'skills' : skills,
        'job_type' : job_type,
        'description' : description


    }
    collection.insert_one(job)

def get_jobs():
    jobs = collection.find()
    return jobs

def get_job(job_id):
    query={'_id': ObjectId(job_id)}
    job = list(collection.find(query))
    for j in job:
        j['_id'] = str(j['_id'])
    return job

# print(get_job('652bc596b01092e9698b4a3a'))
# add_jobs('Google', 'Software Engineer', ['New York'], ['Python', 'Java', 'C++'], ['Full-Time'], '''The Software Engineer will be responsible for designing, developing, and maintaining software applications and systems. The ideal candidate will have a strong background in computer science, software engineering, and programming languages such as Python, Java, and C++. The Software Engineer will work closely with cross-functional teams to develop and implement software solutions that meet business requirements. They will be responsible for writing clean, efficient, and maintainable code, as well as debugging and troubleshooting issues as they arise. The Software Engineer will also be responsible for staying up-to-date with the latest software development trends and technologies, and for continuously improving their skills and knowledge. They will be expected to work independently and as part of a team, and to communicate effectively with stakeholders at all levels of the organization. In addition to technical skills, the ideal candidate will possess strong problem-solving, analytical, and communication skills. They will be able to work in a fast-paced, dynamic environment, and to adapt to changing priorities and requirements. Overall, the Software Engineer role at Google offers an exciting opportunity to work on cutting-edge software development projects, to collaborate with talented and passionate professionals, and to make a meaningful impact on the world''')
 