import json
from dotenv import load_dotenv
from os import getenv
import requests
from sys import exit
from time import sleep
from urllib3.exceptions import InsecureRequestWarning

# load .env settings
load_dotenv()
apikey = getenv("apikey")
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


def put_freshservice_api(datatype, id=0, action=None):
    if datatype == "objects" and id > 0:
        url = f"{urlbase}/{datatype}/{id}/records"
    elif id > 0 and action != None:
        url = f"{urlbase}/{datatype}/{id}/{action}"
    print(f"putting to url {url}")
    response = s.put(url)
    # results = []
    print(response.text)
    resp_json = response.json()
    # print(resp_json)
    return resp_json


def main():
    # get the list of agents
    results = get_freshservice_api("agents")
    # group_names = [ item["name"] for item in results ]
    agent_emails = [
        item["email"] for item in results  if item["active"] == True
    ]
    agents_to_keep = ["madeline.coluccio@embecta.com", "david.thiele@embecta.com", "zach.taylor@embecta.com", "danielle.dispoto@embecta.com","katherine.karshner@embecta.com","kiruthiga.muthuswamy@embecta.com","kvist.annika@embecta.com"]
    filtered_agent_emails = [ agent for agent in agent_emails if agent not in agents_to_keep]
    # results_pretty = json.dumps(results, indent=2)
    # print(results_pretty)
    # get just the first item in the list to test with
    # filtered_agent_emails = filtered_agent_emails[0:1]
    print(filtered_agent_emails)
    print(len(filtered_agent_emails))

    # get user IDs for agents to remove
    user_ids_to_remove = []
    for email in filtered_agent_emails:
        agent_results = next(agent for agent in results if agent["email"] == email)
        user_ids_to_remove.append(agent_results["id"])
    print(user_ids_to_remove)
    print(len(user_ids_to_remove))

    # convert each agent in the list of IDs to requester
    headers = {"Content-Type": "application/json"}
    s.headers.update(headers)
    for user_id in user_ids_to_remove:
        conversion_results = put_freshservice_api(
            "agents", id=user_id, action="convert_to_requester"
        )
        print(f"agent converted to requester: {conversion_results}")
    exit(0)


if __name__ == "__main__":
    main()
