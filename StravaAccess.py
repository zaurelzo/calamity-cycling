import os
import json
import time
import requests
import dotenv


class StravaAccess:
    ENV_PATH = ".env"

    def __init__(self):
        dotenv.load_dotenv(self.ENV_PATH)
        self.token = self.load_or_refresh_token()

    # -----------------------------
    # STEP 1: exchange code once
    # -----------------------------
    def exchange_code_for_token(self, code):
        r = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "code": code,
                "grant_type": "authorization_code",
            },
        )

        if not r.ok:
            return {"error": r.text}

        token = r.json()

        dotenv.set_key(self.ENV_PATH, "READ_TOKEN", json.dumps(token))

        self.token = token
        return token

    # -----------------------------
    # STEP 2: load or refresh
    # -----------------------------
    def load_or_refresh_token(self):
        token = os.getenv("READ_TOKEN")

        if not token:
            return None

        token = json.loads(token)

        if token["expires_at"] < time.time():
            token = self.refresh_token(token)

        dotenv.set_key(self.ENV_PATH, "READ_TOKEN", json.dumps(token))
        return token

    def refresh_token(self, token):
        r = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
            },
        )

        return r.json()

    # -----------------------------
    # API
    # -----------------------------
    def get_summary_activities(self, page=1, after=0):
        r = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            params={
                "access_token": self.token["access_token"],
                "page": page,
                "per_page": 200,
                "after": after,
            },
        )
        return r.json()

    def get_details_activity(self, activity_id):
        r = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}",
            params={"access_token": self.token["access_token"]},
        )
        return r.json(), None, None