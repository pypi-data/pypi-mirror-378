# SPDX-License-Identifier: Apache-2.0
import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

# Global variable to store heartbeat data
HEARTBEAT_DATA = {}


@app.route("/lmcache_heartbeat", methods=["GET"])
def record_heartbeat():
    api_address = request.args.get("api_address")
    pid = request.args.get("pid", type=int)
    version = request.args.get("version", "1.0.0")
    other_info = request.args.get("other_info", "{}")

    if api_address:
        HEARTBEAT_DATA[api_address] = {
            "pid": pid,
            "version": version,
            "otherInfo": other_info,
            "lastReportTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    return jsonify({"status": "success"})


@app.route("/lmcache_infos", methods=["GET"])
def get_lmcache_infos():
    hour = request.args.get("hour", type=int)
    minute = request.args.get("minute", type=int)

    if hour is not None:
        threshold = datetime.datetime.now() - datetime.timedelta(hours=hour)
    elif minute is not None:
        threshold = datetime.datetime.now() - datetime.timedelta(minutes=minute)
    else:
        # Format HEARTBEAT_DATA to match MOCK_DATA structure
        process_infos = {}
        for api_address, data in HEARTBEAT_DATA.items():
            process_infos[api_address] = {
                "count": 1,
                "lmCacheInfoEntities": [
                    {
                        "ipAddress": None,
                        "pid": data.get("pid"),
                        "apiAddress": api_address,
                        "version": data.get("version", "1.0.0"),
                        "startTime": data.get(
                            "startTime",
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        "lastReportTime": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "otherInfo": data.get("otherInfo", "{}"),
                    }
                ],
            }
        return jsonify(
            {
                "processCount": len(HEARTBEAT_DATA),
                "versionCount": len(HEARTBEAT_DATA),
                "processInfos": process_infos,
                "versions": None,
            }
        )

    # Filter data based on threshold
    filtered_data = {
        "processCount": 0,
        "versionCount": 0,
        "processInfos": {},
        "versions": None,
    }

    for api_address, data in HEARTBEAT_DATA.items():
        last_report_time = datetime.datetime.strptime(
            data.get(
                "lastReportTime", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            "%Y-%m-%d %H:%M:%S",
        )
        if last_report_time >= threshold:
            filtered_data["processInfos"][api_address] = {
                "count": 1,
                "lmCacheInfoEntities": [
                    {
                        "ipAddress": None,
                        "pid": data.get("pid"),
                        "apiAddress": api_address,
                        "version": data.get("version", "1.0.0"),
                        "startTime": data.get(
                            "startTime",
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        "lastReportTime": last_report_time.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "otherInfo": data.get("otherInfo", "{}"),
                    }
                ],
            }
            filtered_data["processCount"] += 1

    return jsonify(filtered_data)


if __name__ == "__main__":
    app.run(debug=True)
