# Python program to Generate Jenkins Files with data from an openshift audit
import os
import math
# This program requires a Template.txt of the Jenkins file and a .xlsx file from the audit
# ExcelPath must be a raw string
Template = r"Template.txt"
ReqBuffer = 0.5
LimBuffer = 0.25


def round_decimals_up(number: float, decimals: int = 2):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.ceil(number)
    factor = 10 ** decimals
    return math.ceil(number * factor) / factor


def DoIGenerate(Service):
    if Service[0] == "do not generate":
        return False
    else:
        return True


def GenerateNameList(dict):
    List = []
    MicroService = []
    for Name in dict:
            MicroService.append(Name)
            MicroService.append(dict[Name][0])
            List.append(MicroService)
            MicroService = []
    return List


def GenerateFile(Template, Arg):
    if Arg[0] == "do not generate":
        return 0
    FolderName = "JenkinsFiles/"
    if os.path.isdir(FolderName) is False:
        os.mkdir(FolderName)
    os.mkdir(FolderName + Arg[0])
    NewPath = FolderName + Arg[0] + "/Jenkinsfile"
    # opens Template file and stores data in data var
    fileTemplate = open(Template, "rt")
    data = fileTemplate.read()
    # Series of replacements to be made from Template
    for i in range(len(Arg)):
        var = "$" + str(i) + "$"
        data = data.replace(var, str(Arg[i]))
    fileTemplate.close
    # Outputs modified data into new file
    FileOut = open(NewPath, "w+")
    FileOut.write(data)
    FileOut.close
    return 1


def AddElements(sheet, List, rowToAdd, indexOfName):
    for element in range(1, 6):
        cell = sheet.cell(row=rowToAdd, column=element + 1)
        List[indexOfName].append(cell.value)


def RepeatElements(List, IndexOfName, IndexStart, IndexEnd):
    # This function is needed if data is absent from a sheet, but still needs to be printed in the final result
    List[IndexOfName].append("0")
    for element in range(1, (IndexEnd - IndexStart + 1)):
        List[IndexOfName].append(List[IndexOfName][IndexStart + (element - 1)])




def ValidateRatios(Service):
    # This function validates that the CPU ratio of 50:1 is applied to the data
    # the following numbers are the indexs of each item in the Service array
    # CPU Req numbers: 2 7 12 17 22 27
    # CPU Lim numbers: 3 8 13 18 23 28
    indexReq = 2
    indexLim = 3
    # print(Service)
    # if len(Service) < 30:
    #     Service[0] = "do not generate"
    #     return 0
    if Service[0] == "do not generate":
        return 0
    for i in range(1, 7):
        # print(indexLim)
        if Service[indexLim] < 0.05:
            Service[indexLim] = 0.05
        if Service[indexReq] < 0.05:
            Service[indexReq] = 0.05
        ratio = Service[indexLim] / Service[indexReq]
        if ratio > 50:
            Service[indexReq] = round_decimals_up(Service[indexLim] / 50)
            # print(" Bad CPU ratio on " + Service[0])
            # print(
            #     "     ratio changed from "
            #     + str(ratio)
            #     + " to "
            #     + str(Service[indexLim] / Service[indexReq])
            # )
        # print(indexLim)
        indexLim += 5
        indexReq += 5
    return 1


def ValidateDifference(Service):
    # this Function determinds if Req > Limit, if it is it sets the two equal
    # this would cause the file to fail
    # the following numbers are the indexs of each item in the Service array
    # CPU Req numbers: 2 7 12 17 22 27
    # CPU Lim numbers: 3 8 13 18 23 28
    # Mem Req numbers: 4 9  14 19 24 29
    # Mem Lim numbers: 5 10 15 20 25 30
    CpuIndex = 3
    MemIndex = 5
    if Service[0] == "do not generate":
        return 0
    for i in range(1, 7):
        # Test CPU
        if Service[CpuIndex] < Service[CpuIndex - 1]:
            # -----------this print statement outputs any changes made by this function------------
            # print(
            #     "changed CPU difference of " + Service[0] + " at index " + str(CpuIndex)
            # )
            Service[CpuIndex] = Service[CpuIndex - 1]
        # Test Memory
        if Service[MemIndex] < Service[MemIndex - 1]:
            # -----------this print statement outputs any changes made by this function------------
            # print(
            #     "changed Mem difference of " + Service[0] + " at index " + str(MemIndex)
            # )
            Service[MemIndex] = Service[MemIndex - 1]
        MemIndex += 5
        CpuIndex += 5


def FormatWithString(Service):
    CpuIndex = 3
    MemIndex = 5
    for i in range(1, 7):
        Service[MemIndex] = FormatUnits(Service[MemIndex], "MEM")
        Service[MemIndex - 1] = FormatUnits(Service[MemIndex - 1], "MEM")
        Service[CpuIndex] = FormatUnits(Service[CpuIndex], "CPU")
        Service[CpuIndex - 1] = FormatUnits(Service[CpuIndex - 1], "CPU")
        MemIndex += 5
        CpuIndex += 5


def FindFirstNumber(string):
    output = len(string)
    for i in range(0, 9):
        temp = string.find(str(i))
        if temp < output and temp > 0:
            output = temp
    return output


def GenerateDifferences(List, Totals, dict, podIndex):
    Name = List[0]
    PodNum = List[podIndex]
    if Name == "do not generate":
        return 0
    if PodNum == 0:
        return 0
    if Name not in dict:
        # if podIndex != 26:
            # print("error on ", Name, "in enviorment ", podIndex)
            # List[0] = "do not generate"
        return -1

    # Outputfile = CreateXLSX("Output.xlsx")
    CPU_ReqChange = dict[Name][1] - List[podIndex + 1]
    CPU_LimChange = dict[Name][2] - List[podIndex + 2]
    MEM_ReqChange = dict[Name][3] - List[podIndex + 3]
    MEM_LimChange = dict[Name][4] - List[podIndex + 4]
    if CPU_ReqChange < 0:
        List[podIndex + 1] = dict[Name][1]
    if CPU_LimChange < 0:
        List[podIndex + 2] = dict[Name][2]
    if MEM_LimChange < 0:
        List[podIndex + 3] = dict[Name][3]
    if MEM_LimChange < 0:
        List[podIndex + 4] = dict[Name][4]

    Totals["CPU"] += int(PodNum) * (CPU_ReqChange + CPU_LimChange)
    Totals["Memory"] += int(PodNum) * (MEM_ReqChange + MEM_LimChange)


def FormatUnits(value, type):
    value = round_decimals_up(value)
    if type == "CPU":
        output = '"' + str(int(value * 1000)) + "m" + '"'
        return output
        # if value >= 1:
        #     value = math.ceil(value)
        #     return value
    if type == "MEM":
        output = '"' + str(int(value * 1000)) + "Mi" + '"'
        return output
        # if value >= 1:
        #     value = math.ceil(value)
        #     output = '"' + str(int(value)) + "Gi" + '"'
        #     return output



def RepeatList(List, Num):
    # CPU Req numbers: 2 7 12 17 22 27 
    # CPU Lim numbers: 3 8 13 18 23 28
    # Mem Req numbers: 4 9  14 19 24 29
    # Mem Lim numbers: 5 10 15 20 25 30
    for i in range(1, Num):
        List.append(List[1])
        List.append(List[2])
        List.append(List[3])
        List.append(List[4])
        List.append(List[5])


def RetrieveProData(dict, List):
    # ReqBuffer = 0.5
    # LimBuffer = 0.25

    for Name in dict:
        for index in range(0, len(List)):
            if Name == List[index][0]:
                CPUAvg = dict[Name][0]
                CPUMax = dict[Name][1]
                MEMAvg = dict[Name][2]
                MEMMax = dict[Name][3]

                CPUReq = round_decimals_up(CPUAvg + (ReqBuffer * CPUAvg))
                CPULim = round_decimals_up(CPUMax + (LimBuffer * CPUMax))
                MEMReq = round_decimals_up(MEMAvg + (ReqBuffer * MEMAvg))
                MEMLim = round_decimals_up(MEMMax + (LimBuffer * MEMMax))

                List[index].append(CPUReq)
                List[index].append(CPULim)
                List[index].append(MEMReq)
                List[index].append(MEMLim)

    for index in range(0, len(List)):
        if len(List[index]) < 4:
            print(List[index][0])
            List[index][0] = "do not generate"

def GenerateJenkinsFiles(arg):
    TotalSavings = {"CPU": 0, "Memory": 0}
    OutputList = GenerateNameList(arg[6])
    RetrieveProData(arg[10], OutputList)

    for index in range(0, len(OutputList)):
        RepeatList(OutputList[index], 6)
        ValidateRatios(OutputList[index])
        ValidateDifference(OutputList[index])
        if DoIGenerate(OutputList[index]) is False:
            continue
        GenerateDifferences(OutputList[index], TotalSavings, arg[0], 1)
        GenerateDifferences(OutputList[index], TotalSavings, arg[1], 6)
        GenerateDifferences(OutputList[index], TotalSavings, arg[2], 11)
        GenerateDifferences(OutputList[index], TotalSavings, arg[3], 16)
        GenerateDifferences(OutputList[index], TotalSavings, arg[4], 21)
        GenerateDifferences(OutputList[index], TotalSavings, arg[5], 26)
        GenerateDifferences(OutputList[index], TotalSavings, arg[7], 21)
        GenerateDifferences(OutputList[index], TotalSavings, arg[9], 26)
        GenerateDifferences(OutputList[index], TotalSavings, arg[6], 21)
        GenerateDifferences(OutputList[index], TotalSavings, arg[8], 26)
        FormatWithString(OutputList[index])
        GenerateFile(Template, OutputList[index])

    return TotalSavings
