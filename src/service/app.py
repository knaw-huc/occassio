"""
The Flask application, with routes for handling the
back-end of the application.
"""
import os
from functools import wraps

import dotenv
from jwt import PyJWKClient

from elastic_index import Index
from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import CORS, cross_origin
import yaml
import jwt

app = Flask(__name__, static_folder="browser", static_url_path="")

dotenv.load_dotenv()

cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers="*")

config = {
    "url": os.getenv("ES_URI", "127.0.0.1"),
    "port": os.getenv("ES_PORT ", "9200"),
    "doc_type": "article"
}

oidc_config = {
    "issuer": os.getenv("OIDC_ISSUER"),
    "jwks_uri": os.getenv("OIDC_JWKS_URI"),
    "client_id": os.getenv("OIDC_CLIENT_ID"),
}

jwks_client = PyJWKClient(oidc_config['jwks_uri'])

index = Index(config)

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    """
    Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with"
                             " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """
    Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        unverified_header = jwt.get_unverified_header(token)
        public_key = jwks_client.get_signing_key(unverified_header['kid'])
        if public_key:
            try:
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256', 'ES256'],
                    audience=oidc_config['client_id'],
                    issuer=oidc_config['issuer']
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.InvalidAudienceError:
                raise AuthError({"code": "invalid_audience",
                                 "description":
                                     "incorrect audience,"
                                     " please check the audience"}, 401)
            except jwt.InvalidIssuerError:
                raise AuthError({"code": "invalid_issuer",
                                 "description":
                                     "incorrect issuer,"
                                     " please check the issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                     "Unable to parse authentication"
                                     " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return decorated


@app.after_request
def after_request(response):
    """
    Add CORS headers.
    :param response:
    :return:
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return response


@app.route("/", methods=["GET", "POST"])
@app.route("/search")
@app.route("/oidc/redirect")
def catch_all():
    """
    Return the front-end, pages are handled by React
    :return:
    """
    return app.send_static_file("index.html")


@app.route("/detail/<article_id>")
def detail(article_id):
    """
    Return the front-end, pages are handled by React
    :return:
    """
    print(f"Requesting page for id: {article_id}")
    return app.send_static_file("index.html")


@app.route("/api/facets", methods=["GET"])
@requires_auth
def get_facets():
    """
    Get all used facets, and their configuration.
    :return:
    """
    try:
        data = index.get_facets()
    except yaml.YAMLError as e:
        print(e)
        return jsonify({"error": "facets misconfigured"}), 500

    return jsonify(data)


@app.route("/api/facet", methods=["POST", "GET"])
@requires_auth
def get_facet():
    """
    Get facet information.
    :return:
    """
    struc = request.get_json()
    ret_struc = index.get_facet(
        struc["name"],
        struc["amount"],
        struc["filter"],
        struc["searchvalues"]
    )
    return jsonify(ret_struc)


@app.route("/api/browse", methods=["POST", "GET"])
@requires_auth
def browse():
    """
    Search for articles using elasticsearch.
    :return:
    """
    # print(auth.current_token_identity)
    # token = request.headers.get("Authorization")


    struc = request.get_json()
    ret_struc = index.browse(struc["page"], struc["page_length"], struc["searchvalues"])
    return jsonify(ret_struc)


@app.route("/api/article", methods=["GET"])
@requires_auth
def get_article():
    """
    Get details of a single article.
    :return:
    """
    article_id = request.args.get("rec")
    return jsonify(index.by_id(article_id))
