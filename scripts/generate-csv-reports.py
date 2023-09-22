import csv
from dotenv import load_dotenv
from os import getenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

# load .env settings
load_dotenv()
apikey = getenv("apikey")
tenant = getenv("tenant")

datatypes = ["roles", "agents", "groups", "requester_groups", "requesters"]
roles_results = []

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_freshservice_api(datatype):
    basic = requests.auth.HTTPBasicAuth(apikey, "x")
    url = f"https://{tenant}.freshservice.com/api/v2/{datatype}?per_page=100"
    s = requests.Session()
    s.auth = basic
    s.verify = False
    response = s.get(url)
    results = []
    resp_json = response.json()
    results = resp_json[datatype]
    while response.links.get("next", None) is not None:
        url = response.links["next"]["url"]
        response = s.get(url)
        while response.headers.get("Retry-After") is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                retry_after_secs = int(retry_after)
                sleep(retry_after_secs)
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
            break
        [results.append(item) for item in resp_json[datatype]]
    return results


for datatype in datatypes:
    print(f"\nStarting datatype: {datatype}\n")
    results = get_freshservice_api(datatype)

    print(f"number of results items: {len(results)}")

    if datatype == "roles":
        roles_results = results
        temp_agents_results = get_freshservice_api("agents")
        for role in roles_results:
            print(f'mapping agents to role: {role["name"]}')
            agents_assigned = [
                agent["email"]
                for agent in temp_agents_results
                if role["id"] in agent["role_ids"] and agent["active"] == True
            ]
            agents_assigned_sorted = sorted(agents_assigned)
            role["agents_assigned"] = "\n".join(agents_assigned_sorted)
        results = roles_results

    if datatype == "agents":
        agents_results = [agent for agent in results if agent["active"] == True]

        for agent in agents_results:
            role_names = []
            for role_id in agent["role_ids"]:
                role_name = [
                    role["name"] for role in roles_results if role["id"] == role_id
                ]
                role_names.append(role_name[0])
            role_names_sorted = sorted(role_names)
            agent["role_names"] = "\n".join(role_names_sorted)
        # does the above append update the parent object too?
        results = agents_results

    with open(f"{datatype}.csv", "w", newline="", encoding="utf-8") as f_out:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)

        writer.writeheader()