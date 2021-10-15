import writejenkins
import getopenshift
import getprometheus

# Sets up projects to audit
test_net_project_list = [
    "npt-develop",
    "npt-release",
    "npt-release-qa",
    "npt-sprint-qa",
]
ramapo_stress_project_list = ["npt-release-stress"]
windward_stress_project_list = ["npt-release-stress"]
ramapo_prod_project_list = ["npt-prod", "npt-staging"]
windward_prod_project_list = ["npt-prod", "npt-staging"]

# Combines project lists
project_list = [
    test_net_project_list,
    ramapo_stress_project_list,
    windward_stress_project_list,
    ramapo_prod_project_list,
    windward_prod_project_list,
]

login_commands = [
    "x", # Paste login commands for each environment
    "x",
    "x",
    "x",
    "x",
]

URL = "https://prometheus-njrar-02.paas.ups.com/api/v1/query"

TOKEN = "x" # Paste Bearer token

QUERIES = [
    "avg_over_time(namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate{namespace='npt-prod', container_name!='POD'}[1d])",
    "max_over_time(namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate{namespace='npt-prod', container_name!='POD'}[1d])",
    "avg_over_time(container_memory_usage_bytes{namespace='npt-prod', container_name!='POD'}[1d])",
    "max_over_time(container_memory_usage_bytes{namespace='npt-prod', container_name!='POD'}[1d])",
]

dict_list = []
i = 0
for pl in project_list:
    login_command = login_commands[i]
    i += 1
    for p in pl:
        d = getopenshift.get_openshift_dict(p, login_command)
        dict_list.append(d)
d = getprometheus.get_prometheus_dict(URL, QUERIES, TOKEN)
dict_list.append(d)
writejenkins.GenerateJenkinsFiles(dict_list)
