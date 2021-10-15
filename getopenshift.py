import subprocess

# Function [run(cmd)] runs the powershell command [cmd] and returns the stdout as a string. [cmd] should be written
# as a string exactly how it would be inputted into powershell.
# Ex: run('Test-Path -Path "C:/Users/Admin/Documents/word_doc') runs the powershell command
# 'Test-Path -Path "C:/Users/Admin/Documents/word_doc'.
def run(cmd):
    completed = subprocess.run(
        ["powershell", "-Command", cmd], text=True, capture_output=True
    )
    return completed


# Function [format_get_pods(data)] parses the standard output from an [oc get pods] command and returns the pod's
# names. This information is returned as a list of strings.
# Ex: ['pod_name_1', 'pod_name_2', 'pod_name_3', etc...]
def format_get_pods(data):
    data = data.replace("\n", " ")
    data = data.split(" ")
    data = list(filter(None, data))
    final_lst = []
    for i in range(5, len(data), 5):
        if not (
            data[i].endswith("build")
            or data[i].endswith("deploy")
            or data[i + 1] == "0/1"
        ):
            final_lst.append(data[i])
    return final_lst


# Function [format_describe_pods(data)] parses the standard output from an [oc describe pods <pod name>] command
# and returns the pod's name and burst CPU cores and memory capacity and requested CPU cores and memory capacity.
# This information is returned in the form of a list of string lists.
# Ex: [['Name', 'Burst_CPU', 'Burst_Mem', 'Request_CPU', 'Request_Mem'], [etc...], [etc...]]
def format_describe_pods(data):
    index_one = data.find("Limits:")
    index_two = data.find("Liveness:")
    data = data[index_one:index_two]
    data = data.rsplit(" ")
    data = list(filter(None, data))
    lst = [2, 4, 7, 9]
    final_lst = []
    for i in lst:
        try:
            data[i] = data[i].replace("\n", "")
            x = data[i].strip()
            if "Gi" in x:
                x = x.replace("Gi", "")
            if ("m" in x) or ("Mi" in x):
                x = x.replace("m", "")
                x = x.replace("Mi", "")
                x = int(x) * 0.001
            x = float(x)
            final_lst.append(x)
        except:
            break
    return final_lst


# Function [lst_to_dict(lst)] takes in a list of lists and outputs a dictionary where the keys are the 0th index
# each list and correspond to values that are the remainder of the lists. This function also removes duplicate pods
# by using only the microservice name as the key.
# Ex: lst_to_dict([[1,2,3,4], [2,3,4,5], [3,4,5,6]]) returns {1: [2,3,4], 2: [3,4,5], 3: [4,5,6]}
def lst_to_dict(lst):
    d = {}
    for i in lst:
        key = i[0]
        key = key[0 : key.rfind("-")]
        key = key[0 : key.rfind("-")]
        value = d.get(key)
        if value == None:
            value = i[1:]
            value.insert(0, 1)
            d.update({key: value})
        else:
            value[0] += 1
            d.update({key: value})
    return d


def get_openshift_dict(project_space, login_command):

    # Login to openshift
    run(login_command)

    # Navigate to project_space
    print("Grabbing pod data from " + project_space)
    run("oc project " + project_space)

    # Creates list of pod names
    pods = run("oc get pods").stdout
    name_lst = format_get_pods(pods)

    # Creates list of string lists of format ['name1', 'cpu_burst', 'mem_burst', 'cpu_request', 'mem_burst']
    data_lst = []
    for i in name_lst:
        if i != "NAME":
            command = "oc describe pods " + i
            output = run(command).stdout
            print(i)
            x = format_describe_pods(output)
            x.insert(0, i)
            if len(x) == 1:
                print("PodDataScript was not able to gather the info for pod " + i)
                for i in range(4):
                    x.append("n/a")
            data_lst.append(x)

    return lst_to_dict(data_lst)
