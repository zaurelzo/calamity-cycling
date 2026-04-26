import os
import logging
from datetime import datetime
from flask import Flask, redirect, request, render_template, jsonify
from pymongo import MongoClient

from MongoAccess import MongoAccess
from StravaAccess import StravaAccess
import Utils

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

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
# CONNECT STRAVA
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
# CALLBACK
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
    if not strava.token:
        log.warning("Refresh called but Strava is not connected")
        return {"error": "not_connected", "message": "Please connect your Strava account first."}, 401

    log.info("=== Refresh started ===")

    last_date = mongo.get_last_downloaded_activity_from_mongo()
    log.info(f"Last activity in DB: {last_date}")

    activities = strava.get_summary_activities(
        page=1,
        after=int(last_date.timestamp())
    )

    if isinstance(activities, list) and activities and activities[0].get("error"):
        log.error(f"Strava error fetching activities: {activities[0]}")
        return activities[0]

    log.info(f"Fetched {len(activities)} new activities from Strava")

    mongo.insert_activities_to_mongo(
        Utils.build_batch_summary_activities(activities)
    )
    log.info(f"Inserted/updated {len(activities)} summary activities in MongoDB")

    ids = mongo.get_ids_activities_to_update_from_mongo()
    log.info(f"Found {len(ids)} activities missing details, fetching...")

    for i, activity in enumerate(ids):
        activity_id = str(activity["id"])
        log.info(f"  [{i+1}/{len(ids)}] Fetching details for activity {activity_id}")

        detail, _, _ = strava.get_details_activity(activity_id)

        if isinstance(detail, dict) and detail.get("error"):
            log.error(f"  Error fetching details for {activity_id}: {detail}")
            return detail

        name = detail.get("name", "unknown")
        distance = round(detail.get("distance", 0) / 1000, 2)
        date = detail.get("start_date_local", "unknown date")
        log.info(f"  -> '{name}' | {distance} km | {date}")

        mongo.update_activity_into_mongo(
            {"id": activity_id},
            Utils.build_details_activity_to_update(detail)
        )

    log.info("=== Refresh complete ===")
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


@app.route("/get_recorded_time_for_a_segment/<int:segment_id>")
def get_recorded_time_for_a_segment(segment_id):
    data = mongo.get_recorded_time_for_a_segment(segment_id)
    return {"data": data}