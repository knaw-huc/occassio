from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from elastic_index import Index
import yaml

app = Flask(__name__, static_folder="browser", static_url_path="")

CORS(app)

config = {
    "url": os.getenv("ES_URI", "127.0.0.1"),
    "port": os.getenv("ES_PORT ", "9200"),
    "doc_type": "article"
}

index = Index(config)


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return response


@app.route("/", methods=["GET", "POST"])
@app.route("/search")
def catch_all():
    return app.send_static_file("index.html")


@app.route("/api/detail/<id>")
def detail(id):
    return app.send_static_file("index.html")


@app.route("/api/facets", methods=["GET"])
def get_facets():
    try:
        data = index.get_facets()
    except yaml.YAMLError as e:
        print(e)
        return jsonify({"error": "facets misconfigured"}), 500

    return jsonify(data)


@app.route("/api/facet", methods=["POST", "GET"])
def get_facet():
    struc = request.get_json()
    ret_struc = index.get_facet(struc["name"], struc["amount"], struc["filter"], struc["searchvalues"])
    return jsonify(ret_struc)


@app.route("/api/browse", methods=["POST", "GET"])
def browse():
    struc = request.get_json()
    ret_struc = index.browse(struc["page"], struc["page_length"], struc["searchvalues"])
    return jsonify(ret_struc)


@app.route("/api/article", methods=["GET"])
def get_article():
    id = request.args.get("rec")
    return jsonify(index.by_id(id))