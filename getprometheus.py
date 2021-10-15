import requests
import json

CONTAINERS_TO_NOT_AUDIT = ["deployment", "docker-build", "git-clone", "sti-build"]
PODS_TO_NOT_AUDIT = []

# Function [prometheus(URL, QUERY, TOKEN)] performs a POST request using the  query [QUERY] on the Prometheus API url [URL]. A token [TOKEN] is necessary to access the Prometheus API.
# Ex: prometheus("https://prometheus-njrar-02.paas.ups.com/api/v1/query", avg_over_time(namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate{namespace='npt-prod', container_name!='POD'}[1d]), "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJvcGVuc2hpZnQtbW9uaXRvcmluZyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cy10b2tlbi1qNXFsOCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjYxMjljOTg2LTA4MjMtMTFlYi05M2VhLTAwNTA1NmE1YTQ4MyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpvcGVuc2hpZnQtbW9uaXRvcmluZzpwcm9tZXRoZXVzLWs4cyJ9.MPOL_QHBe1XK9xlc5mVZ0TG5r2sunnSVUbi_OFS4891KU4Zae0-MU6CmohAejoiLjSPsWdKj-SJPnvoYxa8UTjcTEtYoy8EvbSeBRIkW2CmwYUVt4ZDqfdG-UdsLRizquRdwtBZcqh4xAer-5uP5Zu4WToN1qTeY0JvMz-XIR9J482Mw3TcCT8La6TP7aLLOj8LOY6tlivQJ3PlLqE7Z5mDmm4v8hZ_bMWrHX95sB2c_piuCRjHXE9Vyz72C9ewJ6NrpcQR51KGj-HPon8V5AvGO6s7nsrHCCykt-dzKD1sF5rgGwIw_fRk0mqN3HbqrSRz2BIKyRx_iz4l3OeUqsA")
def prometheus_query_request(URL, QUERY, TOKEN):
    data = {"query": QUERY}
    headers = {"Authorization": TOKEN}
    return requests.post(URL, data=data, headers=headers)


"""def prometheus_query_request(url, query, token):
    data = {"query": query}
    headers = {"Authorization": token}
    try:
        r = requests.post(url, data=data, headers=headers)
    except requests.HTTPError as e:
        print("The prometheus request failed with HTTP error code " + e)
        user_response = input("Would you like to retry the query? Please type Y or N.")
        if user_response == "Y":
            prometheus_query_request(url, query, token)
            
^ This is the unfinished function that would be used to handle HTTP timeouts ^ 
            
"""

# Function [filter_pods_and_containers(metric)] determines whether the given microservice [metric] is part of a container in CONTAINERS_NOT_TO_AUDIT or is a pod in PODS_NOT_TO_AUDIT.
# It returns true if so, and false if not.
def filter_pods_and_containers(metric):
    pod_name = metric.get("pod_name")
    container_name = metric.get("container_name")
    return container_name in CONTAINERS_TO_NOT_AUDIT or pod_name in PODS_TO_NOT_AUDIT


# Function [place_first_query_data(request)] places the microservice and data in the first query request [request] done on a project into a dictionary. It returns a dictionary where the
# keys are the microservice name and the values are arrays of length one containing average cpu usage.
def place_first_query_data(request):
    d = {}
    print(request)
    r_lst = json.loads(request.text).get("data").get("result")
    for i in r_lst:
        key = i.get("metric").get("pod_name")
        key = key[0 : key.rfind("-")]
        key = key[0 : key.rfind("-")]
        value = float(i.get("value")[1])
        data_lst = d.get(key)
        if data_lst == None:
            d.update({key: [value]})
        else:
            cur_value = data_lst[0]
            if value > cur_value:
                d.update({key: [value]})
    return d


# Function [place_additional_data(request, d, query_num)] is used to place any data from additional queries [request] after the first into the dictionary [d]. It ensures that all entries
# have the correct amount of data according to the number query [query_num] that it is. It returns a dictionary where the keys are the microservice name and the values are arrays of
# length four containing average cpu usage, max cpu usage, average memory usage, and max memory usage.
def place_additional_query_data(request, d, query_num):
    r_lst = json.loads(request.text).get("data").get("result")
    for i in r_lst:
        key = i.get("metric").get("pod_name")
        key = key[0 : key.rfind("-")]
        key = key[0 : key.rfind("-")]
        value = float(i.get("value")[1])
        data_lst = d.get(key)
        if data_lst == None:
            break
        else:
            if len(data_lst) == query_num - 1:
                data_lst.append(value)
                d.update({key: data_lst})
            elif len(data_lst) == query_num:
                cur_value = data_lst[query_num - 1]
                if value > cur_value:
                    data_lst.insert(query_num - 1, value)
                    data_lst.pop(query_num)
                    d.update({key: data_lst})
    return d


# Function [remove_bad_microservices(d)] ensures that all of the dictionary [d] entries have 4 values.
def remove_bad_microservices(d):
    for k in list(d.keys()):
        if len(d.get(k)) != 4:
            d.pop(k)
    return d


def get_prometheus_dict(URL, QUERIES, TOKEN):
    r = prometheus_query_request(URL, QUERIES[0], TOKEN)
    d = place_first_query_data(r)
    counter = 1
    while counter < len(QUERIES):
        r = prometheus_query_request(URL, QUERIES[counter], TOKEN)
        d = place_additional_query_data(r, d, counter + 1)
        counter += 1
    d = remove_bad_microservices(d)
    return d
