import dotenv
import json
import os
import time
from typing import Dict, List
import requests


class StravaAccess:
    ENV_PATH = ".env"
    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"
    # TODO :  when get_authorization_code will be implemented, you will not need this var anymore
    READ_AUTHORIZATION_CODE = "READ_AUTHORIZATION_CODE"
    WRITE_AUTHORIZATION_CODE = "WRITE_AUTHORIZATION_CODE"
    READ_TOKEN = "READ_TOKEN"
    WRITE_TOKEN = "WRITE_TOKEN"

    def __init__(self):
        self.check_valid_env_file(self.ENV_PATH)
        # load env variable
        dotenv.load_dotenv(self.ENV_PATH)
        self.read_token = self.authenticate("READ")

    def check_valid_env_file(self, path_to_file):
        with  open(path_to_file, 'r') as file_content:
            contents = file_content.read()
            if not contents.endswith("\n"):
                print(path_to_file + " file must end with an empty line.")
                exit(1)

    # authenticate the user and return a read or write token api
    def authenticate(self, op_type):
        token = None
        authorization_code = None
        rw_token = None
        rw_code = None
        if op_type == "READ":
            rw_token = self.READ_TOKEN
            rw_code = self.READ_AUTHORIZATION_CODE
            token = os.getenv(self.READ_TOKEN)
            authorization_code = os.getenv(self.READ_AUTHORIZATION_CODE)
        elif op_type == "WRITE":
            rw_token = self.WRITE_TOKEN
            rw_code = self.WRITE_AUTHORIZATION_CODE
            token = os.getenv(self.WRITE_TOKEN)
            authorization_code = os.getenv(self.WRITE_AUTHORIZATION_CODE)
        else:
            print(op_type + " is a non supported operation")
            exit(1)

        assert authorization_code is not None, "For " + op_type + " operation, you need to retrieve a " + op_type \
                                               + " authorization code and set " + rw_code \
                                               + " variable in the " + self.ENV_PATH + " file. See README instructions."
        client_id = os.getenv(self.CLIENT_ID)
        client_secret = os.getenv(self.CLIENT_SECRET)
        assert client_id is not None, "Env var " + self.CLIENT_ID + " is required. Copy its value from your strava account"
        assert client_secret is not None, "Env var " + self.CLIENT_SECRET + " is required. Copy its value from your strava account"

        if token is not None:
            token = json.loads(token)
        else:
            # First call, we do not yet have the read or write token, let's retrieve a authorization code and
            # then retrieve the token
            res = requests.post(
                url='https://www.strava.com/oauth/token',
                data={
                    'client_id': int(client_id),
                    'client_secret': client_secret,
                    'code': authorization_code,
                    'grant_type': 'authorization_code',
                }
            )
            if res.status_code < 200 or res.status_code > 300:
                print("Cannot retrieve " + op_type + " token ", res.content)
                exit(1)
            token = res.json()
        if token['expires_at'] < time.time():
            # Incoherent state, if the read/write token is set, that mean that we have already retrieve a read_token/write_token and an
            # read/write authorization code. So, we should have store the authorization code
            assert authorization_code is not None, "Incoherent state. " + rw_token + " env variable has been set in" + self.ENV_PATH \
                                                   + " file but not the " \
                                                   + rw_code + " env variable. See README instruction to how to retrieve " \
                                                   + op_type + " authorization code and set " + rw_code + " variable in " \
                                                   + self.ENV_PATH + " file"

            res = requests.post(
                url='https://www.strava.com/oauth/token',
                data={
                    'client_id': int(client_id),
                    'client_secret': client_secret,
                    'code': authorization_code,
                    'grant_type': 'refresh_token',
                    'refresh_token': token['refresh_token']
                }
            )

            if res.status_code < 200 or res.status_code > 300:
                print("Cannot retrieve " + op_type + " token ", res.content)
                exit(1)
            token = res.json()  # Save new tokens to file
        if op_type == "READ":
            dotenv.set_key(self.ENV_PATH, self.READ_TOKEN, json.dumps(token))
            dotenv.set_key(self.ENV_PATH, self.READ_AUTHORIZATION_CODE, authorization_code)
        elif op_type == "WRITE":
            dotenv.set_key(self.ENV_PATH, self.WRITE_TOKEN, json.dumps(token))
            dotenv.set_key(self.ENV_PATH, self.WRITE_AUTHORIZATION_CODE, authorization_code)
        return token

    # retrieve activities that are after a timestamp
    # to retrieve all activites, put a timestamp that is in the past (for example 01/01/1970)
    def get_summary_activities(self, page_number: int, after: int = None) -> List[Dict]:
        time_param = None
        if after is None:
            print(" After parameters cannot be  null")
            exit(1)
        else:
            time_param = "&after=" + str(after)
        url = "https://www.strava.com/api/v3/activities"
        access_token = self.read_token['access_token']
        # change per_page (up to 200) and page (1,2,3 etc.) to retrieve more activities
        r = requests.get(
            url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page_number) + time_param)
        if r.status_code < 200 or r.status_code > 300:
            print("Cannot get summary activities ", r.content)
            return [{"error": r.content}]
        return r.json()

    def get_details_activity(self, activity_id: str) -> ({}, str, str):
        url = "https://www.strava.com/api/v3/activities/" + activity_id
        access_token = self.read_token['access_token']
        r = requests.get(url + '?access_token=' + access_token + '&per_page=1' + '&page=1')
        X_RateLimit_Usage = None
        if r.headers.get('X-RateLimit-Usage') is not None:
            X_RateLimit_Usage = r.headers.get('X-RateLimit-Usage')
        X_RateLimit_Limit = None
        if r.headers.get('X-RateLimit-Limit') is not None:
            X_RateLimit_Limit = r.headers.get('X-RateLimit-Limit')
        if r.status_code < 200 or r.status_code > 300:
            print("Cannot get details activities ", r.content)
            return {"error": r.content}, X_RateLimit_Usage, X_RateLimit_Limit
        return json.loads(r.content), X_RateLimit_Usage, X_RateLimit_Limit
