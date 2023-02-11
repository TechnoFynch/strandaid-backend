import os
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, render_template, Response, request
import json
from flask_cors import CORS
import cloudinary
from cloudinary.uploader import upload

# from azure.storage.blob import BlobServiceClient
# import traceback

# Setup Blob Storage
# key = "6i3k6TdEWMvYRJ5IlPUK7/8vD17OR7TF6DvuvMLassJMIZqHXRL4Iof7PnmCZt2pzhuEbImFQpkf+ASt382CjQ=="
# conn = "DefaultEndpointsProtocol=https;AccountName=strandaidobjects;AccountKey=6i3k6TdEWMvYRJ5IlPUK7/8vD17OR7TF6DvuvMLassJMIZqHXRL4Iof7PnmCZt2pzhuEbImFQpkf+ASt382CjQ==;EndpointSuffix=core.windows.net"
# account = "strandaidobjects"
# container = "iden-person"
# ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

# Setup Client
# bsc = BlobServiceClient.from_connection_string(conn)

# Setup Google Firebase
cred = credentials.Certificate('./key.json')
firebase = initialize_app(cred)

# Setup Firestore DB
db = firestore.client()
records = db.collection('records')
drones = db.collection('captures')

app = Flask(__name__)
cors = CORS(app)


@app.route('/', methods=['GET'])
def home():
    return "Hello From Team Strandaid!"


@app.route('/objects', methods=['POST'])
def objects():
    try:
        if "file" not in request.files:
            return "File Not Found!"
        # file = request.files["file"].read()
        # filename = file.filename
        # file.save(filename)
        # blob_client = bsc.get_blob_client(container=container, blob=filename)
        data = json.loads(request.form.get("data"))
        # blob_client.upload_blob(file, overwrite=True)
        # with open(filename, "rb") as filedata:
        #         try:
        #             blob_client.upload_blob(filedata, overwrite=True)
        #         except:
        #             pass

        cloudinary.config(
            cloud_name = "dfkbmhslx",
            api_key = "379349734269924",
            api_secret = "3PNcYjpZMqhvHLlpYldvKhVJOzc",
            secure = True
        )

            # Get the image file from the request
        # print(request.files)
        file = request.files["file"]
    
    # Upload the image to Cloudinary
        response = upload(file, folder="images")

        newData = {
                "imageBy": data["imageBy"],
                "imgUrl": response["secure_url"],
                "lat": data["lat"],
                "long": data["long"],
                "object": data["object"],
                "time": data["time"]
                }

        print(newData)
        drones.add(newData)
        return jsonify({"success": True}), 200
    except Exception as e:
        # traceback.print_exc()
        # return traceback.extract_tb
        return "An Error Occurred: {}".format(e)


@app.route('/drone_record', methods=['GET'])
def droneList():
    try:
        docs = drones.stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        return jsonify(data), 200
    except Exception as e:
        return "An Error Occurred"


@app.route('/all', methods=['GET'])
def all():
    try:
        docs = records.stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        return jsonify(data), 200
    except Exception as e:
        return e


@app.route('/list', methods=['GET'])
def list():
    try:
        record_id = request.args.get('id')
        docs = records.stream()
        for doc in docs:
            data = doc.to_dict()
            if data["drone_id"] == int(record_id):
                return jsonify(data), 200
        return "No Data Found!"
    except Exception as e:
        print(e)
        return "An Error Occurred"


@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        records.add(data)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return "An Error Occurred"


@app.route('/clear', methods=['GET', 'DELETE'])
def clear():
    try:
        docs = records.stream()
        for doc in docs:
            doc.reference.delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return "An Error Occurred"
