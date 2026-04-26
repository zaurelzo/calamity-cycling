from datetime import datetime, timedelta
import calendar


class MongoAccess:
    def __init__(self, collection):
        self.collection = collection

    # -----------------------------
    # INSERT / UPDATE
    # -----------------------------
    def insert_activities_to_mongo(self, activities):
        for a in activities:
            self.collection.update_one(
                {"id": a["id"]},
                {"$set": a},
                upsert=True
            )

    def update_activity_into_mongo(self, query, update):
        self.collection.update_one(query, {"$set": update}, upsert=True)

    # -----------------------------
    # LAST ACTIVITY DATE
    # -----------------------------
    def get_last_downloaded_activity_from_mongo(self):
        last = self.collection.find_one(
            {},
            sort=[("start_date_local", -1)]
        )

        if not last:
            return datetime(1980, 1, 1)

        return last["start_date_local"]

    # -----------------------------
    # IDS TO UPDATE
    # -----------------------------
    def get_ids_activities_to_update_from_mongo(self):
        return list(
            self.collection.find(
                {"segment_efforts": {"$exists": False}},
                {"_id": 0, "id": 1}
            )
        )

    # -----------------------------
    # AVERAGE SPEED
    # -----------------------------
    def get_average_speed_from_mongo(self, year=None, month=None):
        date_filter = {"$lte": datetime.today()}

        if year and not month:
            date_filter["$gte"] = datetime(year, 1, 1)
            date_filter["$lte"] = datetime(year, 12, 31, 23, 59, 59)

        elif year and month:
            next_month = month + 1
            next_year = year

            if month == 12:
                next_month = 1
                next_year += 1

            date_filter["$gte"] = datetime(year, month, 1)
            date_filter["$lte"] = datetime(next_year, next_month, 1) - timedelta(days=1)

        cursor = self.collection.find(
            {
                "average_speed": {"$exists": True},
                "start_date_local": date_filter
            },
            {"_id": 0, "average_speed": 1, "start_date_local": 1}
        ).sort("start_date_local", 1)

        result = []

        for doc in cursor:
            date_obj = doc.get("start_date_local")
            if not date_obj:
                continue
            result.append({
                "speed": round(doc["average_speed"] * 3.6, 2),
                "date": date_obj.strftime("%Y-%m-%d")
            })

        return result

    # -----------------------------
    # GLOBAL STATS
    # -----------------------------
    def get_global_infos(self):
        stats = {}

        fastest = list(self.collection.find(
            {"type": "Ride"},
            {"average_speed": 1, "distance": 1, "start_date_local": 1, "_id": 0}
        ).sort("average_speed", -1).limit(1))

        if fastest:
            f = fastest[0]
            stats["top_activity_speed"] = {
                "average_speed_kmh": round(f["average_speed"] * 3.6, 2),
                "distance_km": round(f["distance"] / 1000, 2),
                "date": f["start_date_local"].strftime("%Y-%m-%d")
            }

        longest = list(self.collection.find(
            {"type": "Ride"},
            {"average_speed": 1, "distance": 1, "start_date_local": 1, "_id": 0}
        ).sort("distance", -1).limit(1))

        if longest:
            l = longest[0]
            stats["top_distance"] = {
                "average_speed_kmh": round(l["average_speed"] * 3.6, 2),
                "distance_km": round(l["distance"] / 1000, 2),
                "date": l["start_date_local"].strftime("%Y-%m-%d")
            }

        total = list(self.collection.aggregate([
            {"$group": {"_id": None, "sum": {"$sum": "$distance"}}}
        ]))

        if total:
            stats["total_distance_km"] = round(total[0]["sum"] / 1000, 2)

        return stats

    # -----------------------------
    # MONTHLY DISTANCE
    # -----------------------------
    def distance_by_month(self, year):
        cursor = self.collection.aggregate([
            {
                "$project": {
                    "month": {"$month": "$start_date_local"},
                    "year":  {"$year":  "$start_date_local"},
                    "distance": 1
                }
            },
            {
                "$group": {
                    "_id": {"month": "$month", "year": "$year"},
                    "total": {"$sum": "$distance"}
                }
            }
        ])

        result = []

        for doc in cursor:
            if doc["_id"]["year"] == year:
                result.append({
                    "month": calendar.month_name[doc["_id"]["month"]],
                    "distance": int(doc["total"] / 1000),
                    "month_id": doc["_id"]["month"]
                })

        return sorted(result, key=lambda x: x["month_id"])

    # -----------------------------
    # SEGMENTS
    # -----------------------------
    def get_all_segments(self):
        cursor = self.collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "name":      "$segment_efforts.name",
                        "id":        "$segment_efforts.segment.id",
                        "distance":  "$segment_efforts.segment.distance",
                        "avg_grade": "$segment_efforts.segment.average_grade",
                        "city":      "$segment_efforts.segment.city",
                        "state":     "$segment_efforts.segment.state"
                    }
                }
            }
        ])

        segments = {}

        for doc in cursor:
            if not doc["_id"].get("name"):
                continue

            for entry in zip(
                doc["_id"]["name"],
                doc["_id"]["id"],
                doc["_id"]["distance"],
                doc["_id"]["avg_grade"],
                doc["_id"]["city"],
                doc["_id"]["state"],
            ):
                name = entry[0].strip()
                if name not in segments:
                    segments[name] = {
                        "id":        entry[1],
                        "distance":  entry[2],
                        "avg_grade": entry[3],
                        "city":      entry[4],
                        "state":     entry[5]
                    }

        return segments

    # -----------------------------
    # SEGMENT SPEED HISTORY
    # -----------------------------
    def get_recorded_time_for_a_segment(self, segment_id):
        segment_id = int(segment_id)

        cursor = self.collection.find(
            {"segment_efforts": {"$exists": True}},
            {"_id": 0, "start_date_local": 1, "segment_efforts": 1}
        )

        result = []

        for activity in cursor:
            date = activity.get("start_date_local")
            if not date:
                continue

            for effort in activity.get("segment_efforts", []):
                seg = effort.get("segment", {})
                if seg.get("id") == segment_id:
                    speed = effort.get("average_speed")
                    if speed:
                        result.append({
                            "date":  date.strftime("%Y-%m-%d"),
                            "speed": round(speed * 3.6, 2)
                        })

        return sorted(result, key=lambda x: x["date"])
