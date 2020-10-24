import datetime
from datetime import datetime
from typing import Dict, List
from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from MongoAccess import MongoAccess
from StravaAccess import StravaAccess


def build_batch_summary_activities(strava_activities: List[Dict]) -> List[Dict]:
    if len(strava_activities) == 0:
        return []
    batch_docs_to_insert: List = []
    for activity in strava_activities:
        current_doc = {}
        # level 1
        level1_keys = ['id', 'name', 'distance', 'moving_time', 'elapsed_time', 'total_elevation_gain',
                       'start_date_local', 'start_latlng', 'start_latlng', 'end_latlng', 'average_speed',
                       'max_speed',
                       'average_watts', 'type']
        for k in level1_keys:
            if activity.get(k) is not None:
                if k == 'start_date_local':
                    current_doc[k] = datetime.strptime(activity[k], "%Y-%m-%dT%H:%M:%SZ")
                else:
                    current_doc[k] = activity[k]
            # add logging if key not found

        if current_doc is not {}:
            batch_docs_to_insert.append(current_doc)
    return batch_docs_to_insert


def build_details_activity_to_update(activity: {}) -> {}:
    current_doc = {}
    for k in ['description']:
        if activity.get(k) is not None:
            current_doc[k] = activity[k]
        # add logging if key not found
    # print("current", current_doc)
    level2_keys = [('gear', 'id'), ('gear', 'name')]
    for k1, k2 in level2_keys:
        if activity.get(k1) is not None:
            if activity.get(k1).get(k2) is not None:
                if current_doc.get(k1) is None:
                    current_doc[k1] = {}
                current_doc[k1][k2] = activity[k1][k2]
        # add logging if key not found

    # keep interesting key in segments efforts.
    if activity.get('segment_efforts'):
        list_of_segments = activity['segment_efforts']
        if list_of_segments is not None:
            current_doc['segment_efforts'] = []
            for i in range(len(list_of_segments)):
                current_doc['segment_efforts'].append({})
            segments_keys = ['name', 'moving_time', 'elapsed_time', 'start_date_local', 'distance', 'average_watts']
            for i, seg in enumerate(list_of_segments):
                for k in segments_keys:
                    if seg.get(k) is not None:
                        if k == 'start_date_local':
                            current_doc['segment_efforts'][i][k] = datetime.strptime(seg[k],
                                                                                     "%Y-%m-%dT%H:%M:%SZ")
                        else:
                            current_doc['segment_efforts'][i][k] = seg[k]

                # get segment_efforts.segment.id'
                if seg.get('segment') is not None:
                    if seg.get('segment').get('id') is not None:
                        current_doc['segment_efforts'][i]['segment'] = {'id': seg.get('segment').get('id')}
                # add logging if key not found

    return current_doc


######################################  web app endpoints ####################################
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
    li = build_batch_summary_activities(activities)
    # print(li)
    mongo.insert_activities_to_mongo(li)
    ids_to_get_details = mongo.get_ids_activities_to_update_from_mongo()
    # print(len(ids_to_get_details))
    for doc_with_id in ids_to_get_details:
        # TODO : stop this loop if we reach api usage limit
        detail, _, _ = strava.get_details_activity(activity_id=str(doc_with_id["id"]))
        details_activity = build_details_activity_to_update(detail)
        if details_activity is not {}:
            mongo.update_activity_into_mongo(doc_with_id, details_activity)
    return "done"


@app.route('/global_infos')
def global_infos():
    global_infos = mongo.get_global_infos()
    return "done" + json.dumps(global_infos)


@app.route('/average_speed')
@app.route('/average_speed/<int:year>')
@app.route('/average_speed/<int:year>/<int:month>')
def average_speed(year=None, month=None):
    # check_valid_env_file(ENV_PATH)
    # # load env variable
    # dotenv.load_dotenv(ENV_PATH)
    # read_token = authenticate("READ")
    # last_activity_info = get_last_activity(read_token, "4098064182")
    # print(last_activity_info)
    # mov = collection.find(projection={'_id': 0})
    data = mongo.get_average_speed_from_mongo(year, month)
    return render_template('index.html', datar=data)
    # return mov[0]

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
