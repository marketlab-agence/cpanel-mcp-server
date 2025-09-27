# cPanel API Handler
# Author: Aboubakrine
# Version: 2.0.0 (MCP Integrated)
# Description: An object-oriented class to encapsulate all communication
# with the cPanel & WHM APIs, now with structured logging.

import requests
import os
import logging

class CpanelApiHandler:
    def __init__(self):
        logging.info('[Setup] Initializing CpanelApiHandler...')
        self.host = os.environ.get('CPANEL_HOST')
        self.user = os.environ.get('CPANEL_USER')
        self.token = os.environ.get('CPANEL_API_TOKEN')

        if not all([self.host, self.user, self.token]):
            logging.error('[Setup] CRITICAL: Server configuration incomplete. Check .env file.')
            raise ConnectionError("Server configuration incomplete. Ensure CPANEL_HOST, CPANEL_USER, and CPANEL_API_TOKEN are set.")
        
        self.headers = {'Authorization': f'whm {self.user}:{self.token}'}
        logging.info('[Setup] CpanelApiHandler configured successfully.')

    def whm_call(self, function, method='POST', params=None):
        url = f"{self.host}/json-api/{function}"
        logging.info(f'[API] Executing WHM call to endpoint: {url}')
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            verify=True,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def uapi_call(self, cpanel_user, module, function, params=None):
        logging.info(f'[API] Preparing UAPI call for user {cpanel_user} -> {module}::{function}')
        client_params = params or {}
        proxy_payload = {
            "cpanel_jsonapi_user": cpanel_user,
            "cpanel_jsonapi_module": module,
            "cpanel_jsonapi_func": function,
            "cpanel_jsonapi_apiversion": 2,
            **client_params
        }
        
        return self.whm_call('cpanel', method='POST', params=proxy_payload)

