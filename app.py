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

app = Flask(__name__)
client = MongoClient('localhost', 27017)
collection = client.strava.activities
mongo = MongoAccess(collection=collection)
strava = StravaAccess()


@app.route('/refresh')
def refresh():
    last_date_downloaded_activity = mongo.get_last_downloaded_activity_from_mongo()
    print(last_date_downloaded_activity)
    # time_after = time.mktime(
    #     datetime.strptime(last_date_downloaded_activity, "%Y-%m-%d").timetuple())
    activities = strava.get_summary_activities(page_number=1, after=last_date_downloaded_activity)
    li = Utils.build_batch_summary_activities(activities)
    # print(li)
    mongo.insert_activities_to_mongo(li)
    ids_to_get_details = mongo.get_ids_activities_to_update_from_mongo()
    # print(len(ids_to_get_details))
    for doc_with_id in ids_to_get_details:
        # TODO : stop this loop if we reach api usage limit
        detail, _, _ = strava.get_details_activity(activity_id=str(doc_with_id["id"]))
        details_activity = Utils.build_details_activity_to_update(detail)
        if details_activity is not {}:
            mongo.update_activity_into_mongo(doc_with_id, details_activity)
    return "done"


@app.route('/global_infos')
def global_infos():
    global_infos = mongo.get_global_infos()
    return "done" + json.dumps(global_infos)


@app.route('/distance_by_month/<int:year>')
def distance_by_month(year):
    ret = mongo.distance_by_month(year)
    return "done " + json.dumps(ret)


@app.route("/get_all_segments")
def get_all_segments():
    segments = mongo.get_all_segments()
    return "done " + ', '.join(segments)


@app.route("/get_recorded_time_for_a_segment")
def get_recorded_time_for_a_segment():
    times = mongo.get_recorded_time_for_a_segment("Porte d'Italie > Porte d'Ivry")
    return "domes " + ', '.join(times)


@app.route('/average_speed')
@app.route('/average_speed/<int:year>')
@app.route('/average_speed/<int:year>/<int:month>')
def average_speed(year=None, month=None):
    data = mongo.get_average_speed_from_mongo(year, month)
    return {"average_speed": data}


@app.route('/get_available_year_and_month')
def get_available_year_and_month():
    year_and_months = mongo.get_available_year_and_month()
    return json.dumps(year_and_months)


@app.route("/")
def home():
    data = mongo.get_average_speed_from_mongo()
    infos = mongo.get_global_infos()
    year_and_months = mongo.get_available_year_and_month()
    return render_template('index.html', datar=data, global_infos=infos, y_and_m=year_and_months)

# if __name__ == "__main__":
#     check_valid_env_file(ENV_PATH)
#     # load env variable
#     dotenv.load_dotenv(ENV_PATH)
#     read_token = authenticate("READ")
#     client = MongoClient('localhost', 27017)
#     collection = client.strava.activities
#     # last_date_downloaded_activity = get_last_downloaded_activity_from_mongo(collection)
#     # time_after = time.mktime(
#     #     datetime.datetime.strptime(last_date_downloaded_activity, "%Y-%m-%d").timetuple())
#     # activities = get_summary_activities(r_token=read_token, page_number=1, after=time_after)
#     # li = build_batch_summary_activities(activities)
#     # # # print(li)
#     # insert_activities_to_mongo(li, collection)
#     # ids_to_get_details = get_ids_activities_to_update_from_mongo(collection)
#     # print(len(ids_to_get_details))
#     # for doc_with_id in ids_to_get_details:
#     #     detail, _, _ = get_details_activity(r_token=read_token, activity_id=str(doc_with_id["id"]))
#     #     details_activity = build_details_activity_to_update(detail)
#     #     if details_activity is not {}:
#     #         update_activity_into_mongo(doc_with_id, details_activity, collection)
#
#     print(get_average_speed_from_mongo(collection))
