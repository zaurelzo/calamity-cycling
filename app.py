import os
from datetime import datetime
from flask import Flask, redirect, request, render_template, jsonify
from pymongo import MongoClient

from MongoAccess import MongoAccess
from StravaAccess import StravaAccess
import Utils

app = Flask(__name__)

client = MongoClient("mongo", 27017)
collection = client.strava.activities
mongo = MongoAccess(collection)

strava = StravaAccess()


# -----------------------------
# HELPERS
# -----------------------------
def build_years_and_months(datar):
    result = {}
    for entry in datar:
        date = datetime.strptime(entry["date"], "%Y-%m-%d")
        year = date.year
        month = date.month
        if year not in result:
            result[year] = set()
        result[year].add(month)
    return {year: sorted(months) for year, months in result.items()}


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    datar = mongo.get_average_speed_from_mongo() or []
    global_infos = mongo.get_global_infos() or {}
    y_and_m = build_years_and_months(datar) if datar else {}

    monthy_dist = {}
    for year in y_and_m.keys():
        monthy_dist[year] = mongo.distance_by_month(year)

    segs = mongo.get_all_segments() or {}

    return render_template(
        "index.html",
        datar=datar,
        global_infos=global_infos,
        y_and_m=y_and_m,
        monthy_dist=monthy_dist,
        segs=segs
    )


# -----------------------------
# CONNECT STRAVA (BUTTON)
# -----------------------------
@app.route("/connect_strava")
def connect_strava():
    client_id = os.getenv("CLIENT_ID")

    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        "&redirect_uri=http://localhost:5000/exchange_token"
        "&approval_prompt=force"
        "&scope=read,activity:read_all,profile:read_all"
    )

    return redirect(url)


# -----------------------------
# CALLBACK (AUTO TOKEN EXCHANGE)
# -----------------------------
@app.route("/exchange_token")
def exchange_token():
    code = request.args.get("code")

    token = strava.exchange_code_for_token(code)

    if "error" in token:
        return token

    return {"status": "connected"}


# -----------------------------
# REFRESH DATA
# -----------------------------
@app.route("/refresh")
def refresh():
    last_date = mongo.get_last_downloaded_activity_from_mongo()

    activities = strava.get_summary_activities(
        page=1,
        after=int(last_date.timestamp())
    )

    if isinstance(activities, list) and activities and activities[0].get("error"):
        return activities[0]

    mongo.insert_activities_to_mongo(
        Utils.build_batch_summary_activities(activities)
    )

    ids = mongo.get_ids_activities_to_update_from_mongo()

    for activity in ids:
        activity_id = str(activity["id"])

        detail, _, _ = strava.get_details_activity(activity_id)

        if isinstance(detail, dict) and detail.get("error"):
            return detail

        mongo.update_activity_into_mongo(
            {"id": activity_id},
            Utils.build_details_activity_to_update(detail)
        )

    return {"status": "success"}


# -----------------------------
# ANALYTICS
# -----------------------------
@app.route("/average_speed")
def average_speed():
    return {"data": mongo.get_average_speed_from_mongo()}


@app.route("/distance_by_month/<int:year>")
def distance_by_month(year):
    return {"data": mongo.distance_by_month(year)}