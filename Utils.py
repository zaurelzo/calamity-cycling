from datetime import datetime


def build_batch_summary_activities(activities):
    result = []

    for a in activities:
        if not a:
            continue

        doc = {
            "id": a.get("id"),
            "name": a.get("name"),
            "distance": a.get("distance"),
            "moving_time": a.get("moving_time"),
            "elapsed_time": a.get("elapsed_time"),
            "average_speed": a.get("average_speed"),
            "type": a.get("type"),
        }

        if a.get("start_date"):
            doc["start_date_local"] = datetime.strptime(
                a["start_date"], "%Y-%m-%dT%H:%M:%SZ"
            )

        result.append(doc)

    return result


def build_details_activity_to_update(activity):
    return {
        "calories": activity.get("calories"),
        "description": activity.get("description"),
        "gear": activity.get("gear"),
        "segment_efforts": activity.get("segment_efforts"),
    }