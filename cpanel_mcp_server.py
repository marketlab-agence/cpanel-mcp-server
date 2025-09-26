# cPanel Advanced MCP Server
# Author: Gemini
# Version: 2.0.0
# Description: A comprehensive Flask-based API gateway for cPanel & WHM.
# This server provides secure, centralized access to both WHM API 1 for server
# administration and a proxied UAPI for individual cPanel account management.

import os
import requests
from flask import Flask, request, jsonify

# --- Configuration ---
# Load credentials securely from environment variables.
# For WHM API access, you need a WHM user (like 'root') and a WHM API Token.
#
# export WHM_HOST="https://your-whm-host.com:2087"
# export WHM_USER="your_whm_username"
# export WHM_API_TOKEN="your_whm_api_token"

WHM_HOST = os.environ.get('WHM_HOST')
WHM_USER = os.environ.get('WHM_USER')
WHM_API_TOKEN = os.environ.get('WHM_API_TOKEN')

# --- Flask App Initialization ---
app = Flask(__name__)

def check_config():
    """Checks if all required WHM environment variables are set."""
    return all()

def make_whm_api_request(method, url, params=None, data=None):
    """
    A helper function to execute requests against the WHM API.
    It handles authentication and error handling centrally.
    """
    headers = {
        'Authorization': f'whm {WHM_USER}:{WHM_API_TOKEN}'
    }

    try:
        print(f"--> Forwarding request to WHM: {url}")
        print(f"    - Method: {method}")
        print(f"    - Params/Data: {params or data}")

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            verify=True  # Set to False only if you have SSL issues and trust the source
        )
        
        response.raise_for_status()
        return response.json(), response.status_code

    except requests.exceptions.HTTPError as http_err:
        print(f"!!! HTTP error occurred: {http_err}")
        try:
            # Try to parse cPanel's JSON error response if possible
            cpanel_error = http_err.response.json()
        except ValueError:
            cpanel_error = http_err.response.text
        
        return {
            "status": "error",
            "message": "HTTP Error from WHM server.",
            "details": str(http_err),
            "cpanel_response": cpanel_error
        }, http_err.response.status_code
    except requests.exceptions.RequestException as req_err:
        print(f"!!! Request error occurred: {req_err}")
        return {
            "status": "error",
            "message": "Failed to connect to WHM server.",
            "details": str(req_err)
        }, 503  # Service Unavailable
    except Exception as e:
        print(f"!!! An unexpected error occurred: {e}")
        return {
            "status": "error",
            "message": "An internal server error occurred.",
            "details": str(e)
        }, 500

@app.route('/')
def index():
    """Root endpoint to check server status and configuration."""
    if not check_config():
        return jsonify({
            "status": "error",
            "message": "Server configuration is incomplete. Please set WHM_HOST, WHM_USER, and WHM_API_TOKEN environment variables."
        }), 500
        
    return jsonify({
        "status": "running",
        "message": "cPanel Advanced MCP Server is active. Ready for WHM and UAPI calls.",
        "whm_host": WHM_HOST,
        "whm_user": WHM_USER,
    })

# --- Phase 1: WHM API 1 Endpoints ---
@app.route('/whmapi/<function>', methods=['GET', 'POST'])
def whmapi_proxy(function):
    """
    Handles direct calls to WHM API 1 functions.
    This is used for server-level administrative tasks.
    
    Example: GET /whmapi/listaccts
    Example: POST /whmapi/createacct with form data
    """
    if not check_config():
        return jsonify({"status": "error", "message": "Server configuration is incomplete."}), 500

    # Construct the full WHM API 1 URL
    api_url = f"{WHM_HOST}/json-api/{function}?api.version=1"

    params = {}
    data = {}
    if request.method == 'GET':
        params = request.args.to_dict()
    elif request.method == 'POST':
        data = request.form.to_dict() if request.form else request.get_json()

    result, status_code = make_whm_api_request(request.method, api_url, params=params, data=data)
    return jsonify(result), status_code

# --- Phase 2: UAPI Endpoints (Proxied through WHM) ---
@app.route('/uapi/<cpanel_user>/<module>/<function>', methods=['GET', 'POST'])
def uapi_proxy(cpanel_user, module, function):
    """
    Handles proxied UAPI calls for a specific cPanel user.
    This is the secure way for an admin to perform actions on behalf of a user.
    
    Example: GET /uapi/mycpaneluser/Email/list_pops
    Example: POST /uapi/mycpaneluser/Mysql/create_database
    """
    if not check_config():
        return jsonify({"status": "error", "message": "Server configuration is incomplete."}), 500

    # The WHM function to call UAPI is 'cpanel'
    api_url = f"{WHM_HOST}/json-api/cpanel?api.version=1"

    # Prepare the base parameters for the UAPI proxy call
    proxy_params = {
        'cpanel_jsonapi_user': cpanel_user,
        'cpanel_jsonapi_module': module,
        'cpanel_jsonapi_func': function,
        'cpanel_jsonapi_apiversion': 3  # '3' specifies UAPI
    }

    # Merge with parameters from the incoming client request
    if request.method == 'GET':
        client_params = request.args.to_dict()
        proxy_params.update(client_params)
        result, status_code = make_whm_api_request('GET', api_url, params=proxy_params)
    
    elif request.method == 'POST':
        client_data = request.form.to_dict() if request.form else request.get_json()
        proxy_params.update(client_data)
        result, status_code = make_whm_api_request('POST', api_url, data=proxy_params)

    return jsonify(result), status_code

# --- Main Execution ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
