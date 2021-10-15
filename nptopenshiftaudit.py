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
    "x",
    "x",
    "x",
    "x",
    "x",
]

URL = "https://prometheus-njrar-02.paas.ups.com/api/v1/query"

TOKEN = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJvcGVuc2hpZnQtbW9uaXRvcmluZyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cy10b2tlbi1qNXFsOCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJwcm9tZXRoZXVzLWs4cyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjYxMjljOTg2LTA4MjMtMTFlYi05M2VhLTAwNTA1NmE1YTQ4MyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpvcGVuc2hpZnQtbW9uaXRvcmluZzpwcm9tZXRoZXVzLWs4cyJ9.MPOL_QHBe1XK9xlc5mVZ0TG5r2sunnSVUbi_OFS4891KU4Zae0-MU6CmohAejoiLjSPsWdKj-SJPnvoYxa8UTjcTEtYoy8EvbSeBRIkW2CmwYUVt4ZDqfdG-UdsLRizquRdwtBZcqh4xAer-5uP5Zu4WToN1qTeY0JvMz-XIR9J482Mw3TcCT8La6TP7aLLOj8LOY6tlivQJ3PlLqE7Z5mDmm4v8hZ_bMWrHX95sB2c_piuCRjHXE9Vyz72C9ewJ6NrpcQR51KGj-HPon8V5AvGO6s7nsrHCCykt-dzKD1sF5rgGwIw_fRk0mqN3HbqrSRz2BIKyRx_iz4l3OeUqsA"

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
