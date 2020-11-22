import datetime
from datetime import datetime
from typing import Dict, List


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
    if activity.get('segment_efforts') is not None:
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
                        current_doc['segment_efforts'][i]['segment'] = {'id': seg.get('segment').get('id'),
                                                                        "average_grade": seg.get('segment').get(
                                                                            'average_grade'),
                                                                        "distance": seg.get('segment').get(
                                                                            'distance')}
    # add logging if key not found

    return current_doc
