from pymongo.errors import BulkWriteError
from datetime import timedelta
from typing import Dict, List
from datetime import datetime


class MongoAccess:
    def __init__(self, collection):
        self.collection = collection

    def insert_activities_to_mongo(self, activities: List[Dict]) -> List:
        try:
            for act in activities:
                self.collection.update_one({"id": act["id"]}, {"$set": act}, True)
        except BulkWriteError as bwe:
            return [{"error": bwe.details}]

    # TODO : better handling of errors.
    def update_activity_into_mongo(self, doc_to_update: {}, new_values: {}):
        return self.collection.update_one(doc_to_update, {"$set": new_values}, True).acknowledged

    def get_ids_activities_to_update_from_mongo(self):
        match = self.collection.find({"segment_efforts": {"$exists": False}}, {"_id": 0, "id": 1})
        return [m for m in match]

    def get_last_downloaded_activity_from_mongo(self):
        match = self.collection.find({}, {"start_date_local": 1, "_id": 0}).sort("start_date_local", -1).limit(1)
        date_array = [m for m in match]
        if len(date_array) == 0:
            return datetime.strptime("1980-01-01", "%Y-%m-%d")
        else:
            return date_array[0]["start_date_local"]

    def get_average_speed_from_mongo(self, year=None, month=None):
        date_condition = {'$lte': datetime.today()}
        if (year is not None) and (month is None):
            date_condition['$gte'] = datetime(year, 1, 1, 0, 0, 0)
            date_condition['$lte'] = datetime(year, 12, 31, 23, 59, 00)
        elif (year is not None) and (month is not None):
            y = year
            m = month + 1
            if month == 12:
                y = y + 1
                m = 1
            date_condition['$gte'] = datetime(year, month, 1, 0, 0, 0)
            date_condition['$lte'] = datetime(y, m, 1, 23, 59, 0) - timedelta(days=1)

        # start = datetime(2020, 9, 24, 7, 51, 4)
        match = self.collection.find({"average_speed": {"$exists": True}, "start_date_local": date_condition},
                                     {"_id": 0, "average_speed": 1, "start_date_local": 1}).sort("start_date_local", 1)
        res = []
        for m in match:
            # print(m)
            doc = {}
            doc["speed"] = m["average_speed"] * 3.6
            doc["date"] = str((m["start_date_local"]).year) + "-" + str((m["start_date_local"]).month) + "-" + str(
                (m["start_date_local"]).day)
            res.append(doc)
        return res

    def get_global_infos(self) -> {}:
        global_infos = {}
        # exclude virtual Ride because its type is virtualRide
        top_activity_speed = self.collection.find({"type": "Ride"},
                                                  {"average_speed": 1, "_id": 0, "start_date_local": 1,
                                                   'distance': 1}).sort(
            "average_speed", -1).limit(1)
        array = [m for m in top_activity_speed]

        global_infos["top_activity_speed"] = {'average_speed (km/h)': round(array[0]['average_speed'] * 3.6, 2),
                                              'distance (km)': round(array[0]['distance'] / 1000, 2),
                                              "date": str((array[0]["start_date_local"]).year) + "-" + str(
                                                  (array[0]["start_date_local"]).month) + "-" + str(
                                                  (array[0]["start_date_local"]).day)}
        top_distance = self.collection.find({"type": "Ride"},
                                            {"average_speed": 1, "_id": 0, "start_date_local": 1,
                                             'distance': 1}).sort(
            "distance", -1).limit(1)
        array = [m for m in top_distance]
        global_infos["top_distance"] = {'average_speed (km/h)': round(array[0]['average_speed'] * 3.6, 2),
                                        'distance (km)': round(array[0]['distance'] / 1000, 2),
                                        "date": str((array[0]["start_date_local"]).year) + "-" + str(
                                            (array[0]["start_date_local"]).month) + "-" + str(
                                            (array[0]["start_date_local"]).day)}

        total_distance = self.collection.aggregate([{"$group": {"_id": "null", "sum": {"$sum": "$distance"}}}])
        array = [m for m in total_distance]
        global_infos["total_distance"] = {"total distance (km) ": round(array[0]["sum"] / 1000, 2)}
        return global_infos

    # for the given year, count the total distance by month
    def distance_by_month(self, year) -> {}:
        total_distance_by_month_for_a_given_year = self.collection.aggregate([
            {"$project": {
                "month": {"$month": "$start_date_local"},
                "year": {"$year": "$start_date_local"},
                "distance": 1
            }},
            {"$group": {
                "_id": {"month": "$month", "year": "$year"},
                "total": {"$sum": "$distance"}
            }}])
        array = []
        for m in total_distance_by_month_for_a_given_year:
            if m["_id"]["year"] == year:
                m["total"] = m["total"] / 1000
                array.append(m)
        if len(array) != 0:
            array = sorted(array, key=lambda elt: elt["_id"]["month"])
        return array

    def get_available_year_and_month(self):
        avaible_year_and_months = self.collection.aggregate([
            {"$project": {
                "month": {"$month": "$start_date_local"},
                "year": {"$year": "$start_date_local"}
            }},
            {"$group": {
                "_id": {"month": "$month", "year": "$year"}
            }}])
        res = {}
        for y__and_m in avaible_year_and_months:
            if res.get(y__and_m["_id"]["year"]) is None:
                res[y__and_m["_id"]["year"]] = [y__and_m["_id"]["month"]]
            else:
                res[y__and_m["_id"]["year"]].append(y__and_m["_id"]["month"])
        for year in res:
            res[year] = sorted(res[year])
        # if len(array) != 0:
        #     array = sorted(array, key=lambda elt: elt["_id"]["month"])
        print("array ", res)
        return res

    # TODO : use unique segment id  instead of segment name
    def get_all_segments(self) -> List:
        unique_segments = self.collection.find().distinct("segment_efforts.name")
        array = sorted([m for m in unique_segments])
        return array

    # TODO : use unique segment id  instead of segment name
    def get_recorded_time_for_a_segment(self, segment):
        match = self.collection.find({"segment_efforts.name": segment}, {"segment_efforts.$": 1, "_id": 0}).sort(
            "segment_efforts.start_date_local", 1)
        array = []
        for m in match:
            for o in m["segment_efforts"]:
                o["date"] = str((o["start_date_local"]).year) + "-" + str((o["start_date_local"]).month) + "-" + str(
                    (o["start_date_local"]).day)
                del (o["start_date_local"])
                del (o['segment'])
                array.append(o)
                print(array)
        return array
