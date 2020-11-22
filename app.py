import datetime
from datetime import datetime
from typing import Dict, List
from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from MongoAccess import MongoAccess
from StravaAccess import StravaAccess
import Utils
import time

app = Flask(__name__)
client = MongoClient('localhost', 27017)
collection = client.strava.activities
mongo = MongoAccess(collection=collection)
strava = StravaAccess()


@app.route('/refresh')
def refresh():
    last_date_downloaded_activity = mongo.get_last_downloaded_activity_from_mongo()
    print("Last downloaded activity ", last_date_downloaded_activity)
    # time_after = time.mktime(
    #     datetime.strptime(last_date_downloaded_activity, "%Y-%m-%d").timetuple())
    activities = strava.get_summary_activities(page_number=1, after=last_date_downloaded_activity)
    # print(activities)
    li = Utils.build_batch_summary_activities(activities)
    # print(li)
    mongo.insert_activities_to_mongo(li)
    ids_to_get_details = mongo.get_ids_activities_to_update_from_mongo()
    # print(len(ids_to_get_details))
    print("retrieving " + str(len(ids_to_get_details)) + " activities")
    for doc_with_id in ids_to_get_details:
        print("Get detailled activity for " + str(doc_with_id))
        # TODO : stop this loop if we reach api usage limit
        detail, _, _ = strava.get_details_activity(activity_id=str(doc_with_id["id"]))
        details_activity = Utils.build_details_activiget_all_segmentsty_to_update(detail)
        print(details_activity)
        if details_activity is not {}:
            mongo.update_activity_into_mongo(doc_with_id, details_activity)
            print("update activity " + str(doc_with_id))
        print("done for activity " + str(doc_with_id))
    return "done"


@app.route('/distance_by_month/<int:year>')
def distance_by_month(year):
    ret = mongo.distance_by_month(year)
    return {"monthly_dist": ret}


@app.route("/get_all_segments")
def get_all_segments():
    segments = mongo.get_all_segments()
    return {"segments": segments}


@app.route("/get_recorded_time_for_a_segment/<int:segment_id>")
def get_recorded_time_for_a_segment(segment_id):
    times = mongo.get_recorded_time_for_a_segment(segment_id)
    return {"segments": times}


@app.route('/average_speed')
@app.route('/average_speed/<int:year>')
@app.route('/average_speed/<int:year>/<int:month>')
def average_speed(year=None, month=None):
    data = mongo.get_average_speed_from_mongo(year, month)
    return {"average_speed": data}


@app.route("/")
def home():
    data = mongo.get_average_speed_from_mongo()
    infos = mongo.get_global_infos()
    year_and_months = mongo.get_available_year_and_month()
    current_year = datetime.now().year
    dist_by_month = mongo.distance_by_month(current_year)
    segments = mongo.get_all_segments()
    return render_template('index.html', datar=data, global_infos=infos, y_and_m=year_and_months,
                           monthy_dist=dist_by_month, segs=segments)
