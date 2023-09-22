# import json
from dotenv import load_dotenv
from os import getenv
import requests
from sys import exit
from time import sleep
from urllib3.exceptions import InsecureRequestWarning

# load .env settings
load_dotenv()
apikey = getenv("apikey")
custom_object_name = getenv("custom_object_name")
tenant = getenv("tenant")
workspace_id = int(getenv("workspace_id"))

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Setup requests session
basic = requests.auth.HTTPBasicAuth(apikey, "x")
s = requests.Session()
s.auth = basic
# s.headers.update(headers)
s.verify = False
urlbase = f"https://{tenant}.freshservice.com/api/v2"


def get_freshservice_api(datatype, patharg="", id=0, records=False):
    if datatype == "objects" and id > 0 and records == True:
        url = f"{urlbase}/{datatype}/{id}/records"
    elif id > 0:
        url = f"{urlbase}/{datatype}/{id}"
    elif patharg is None or patharg == "":
        url = f"{urlbase}/{datatype}"
    else:
        url = f"{urlbase}/{datatype}?{patharg}"
    # print(url)
    response = s.get(url)
    results = []
    resp_json = response.json()
    # print(resp_json)
    # exit(0)
    if datatype == "objects":
        if records == True:
            mapped_datatype = "records"
        elif id > 0:
            mapped_datatype = "custom_object"
        else:
            mapped_datatype = "custom_objects"
    else:
        mapped_datatype = datatype
    results = resp_json[mapped_datatype]
    while response.links.get("next", None) is not None:
        url = response.links["next"]["url"]
        response = s.get(url)
        while response.headers.get("Retry-After") is not None:
            sleep(int(retry_after))
            response = s.get(url)
        try:
            resp_json = response.json()
        except Exception as inst:
            print(type(inst))  # the exception type
            print(inst.args)  # arguments stored in .args
            print(inst)
            print(f"response status code: {response.status_code}")
            print(f"response encoding is: {response.encoding}")
            print(f"response text is: {response.text}")
            print(f"request head is: {response.request.headers}")
            print(f"response head is: {response.headers}")
            retry_after = response.headers.get("Retry-After")
            break
        [results.append(item) for item in resp_json[mapped_datatype]]
    return results


def post_freshservice_api(datatype, id=0, data={}):
    if datatype == "objects" and id > 0:
        url = f"{urlbase}/{datatype}/{id}/records"
    print(f"sending data {data} to url {url}")
    response = s.post(url, json=data)
    # results = []
    print(response.text)
    resp_json = response.json()
    # print(resp_json)
    return resp_json


def main():
    # get the list of agent groups
    results = get_freshservice_api("groups")
    # group_names = [ item["name"] for item in results ]
    group_names = [
        item["name"] for item in results if item["workspace_id"] == workspace_id
    ]
    # print(group_names)
    # results_pretty = json.dumps(results, indent=2)
    # print(results_pretty)

    # get custom object table
    patharg = f"workspace_id={workspace_id}"
    objects_results = get_freshservice_api("objects", patharg)
    object_results_filtered = [item["id"] for item in objects_results if item["title"] == custom_object_name]
    if object_results_filtered:
        table_id = object_results_filtered[0]
    # print(object_it_teams_id)
    # results_pretty = json.dumps(results, indent=2)
    # print(results_pretty)

    # print the structure of the table
    # object_results = get_freshservice_api('objects', id=int(object_it_teams_id))
    # object_results_pretty = json.dumps(object_results, indent=2)
    # print(object_results_pretty)

    # read custom object table
    object_results = get_freshservice_api(
        "objects", id=int(table_id), records=True
    )
    # object_results_pretty = json.dumps(object_results, indent=2)
    # print(object_results_pretty)
    teams_in_object_table = [item["data"]["team_name"] for item in object_results]
    # print(teams_in_object_table)

    # form data request to create to add to custom object table
    teams_missing_from_obj_table = list(set(group_names) - set(teams_in_object_table))
    if not teams_missing_from_obj_table:
        print("No agent groups are missing from the custom object table")
        exit(0)
    teams_missing_from_obj_table.sort()
    for teamname in teams_missing_from_obj_table:
        data = {}
        data["data"] = {}
        teamid = [item["id"] for item in results if item["name"] == teamname][0]
        data["data"]["team_name"] = teamname
        data["data"]["teamname"] = teamid
        # send post request to API
        object_results = post_freshservice_api(
            "objects", id=int(table_id), data=data
        )
        print(f"added record: {object_results}")



if __name__ == "__main__":
    main()
