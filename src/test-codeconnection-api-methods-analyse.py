import csv

codeconnection_requests = []
codestar_requests = []

codeconnection_iam_requests = []
codestar_iam_requests = []
codestar_ccc_iam_requests = []

OUTPUT_ALL_DIFFERENCES = True

with open('results.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    first_line = True
    headers = []
    for row in csv_reader:
        if first_line:
            headers = row 
            first_line = False 
        else:
            connection_name = row[headers.index("connection_name")]
            role_arn_short = row[headers.index("role_arn_short")]
           
            operation_short = row[headers.index("operation_short")]
            api_name = operation_short.split(".")[0]
            operation = operation_short.split(".")[1]
            
            status = row[headers.index("status")]

            if role_arn_short.startswith("CodeConnectionUseConnection"):
                role_type = "CodeConnection"
                role_limitation = role_arn_short.replace("CodeConnectionUseConnection", "")
            elif role_arn_short.startswith("CodeStarConnectionCCC"):
                role_type = "CodeStarConnectionCCC"
                role_limitation = role_arn_short.replace("CodeStarConnectionCCC", "")
            elif role_arn_short.startswith("CodeStarConnection"):
                role_type = "CodeStarConnection"
                role_limitation = role_arn_short.replace("CodeStarConnection", "")   

            item = {
                "connection_name": connection_name,
                "role_type": role_type,
                "role_limitation": role_limitation,
                "role_arn_short": role_arn_short,
                "operation": operation,
                "status": status
            }

            if api_name == "CodeConnection":
                codeconnection_requests.append(item)
                if item["role_type"] == "CodeConnection":
                    codeconnection_iam_requests.append(item)
                elif item["role_type"] == "CodeStarConnection":
                    codestar_iam_requests.append(item)
                elif item["role_type"] == "CodeStarConnectionCCC":
                    codestar_ccc_iam_requests.append(item)          
            else:
                codestar_requests.append(item)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'  

def colour_status(text):
    if text == "200":
        return f"{bcolors.OKGREEN}{text}{bcolors.ENDC}"
    elif text == "400":
        return f"{bcolors.FAIL}{text}{bcolors.ENDC}"
    elif text == "500":
        return f"{bcolors.WARNING}{text}{bcolors.ENDC}"

print("=========================================================")
print("Difference between CodeConnection API Requests and CodeStar API Requests")
print("=========================================================")
for codeconnection_item in codeconnection_requests:
    codestar_item = next((i for i in codestar_requests if i['connection_name'] == codeconnection_item['connection_name'] and i['role_arn_short'] == codeconnection_item['role_arn_short'] and i['operation'] == codeconnection_item['operation']), None) 

    if not codestar_item:
        raise ValueError("Cannot match item")

    if codestar_item["status"] != codeconnection_item["status"] and (codestar_item["status"]=="200" or OUTPUT_ALL_DIFFERENCES):
        print(f"{codeconnection_item['connection_name']} {codeconnection_item['role_arn_short']} {codeconnection_item['operation']}")
        print(f"CodeConnection: {codeconnection_item['status']}, CodeStar: {colour_status(codestar_item['status'])}")

print("=========================================================")
print("Difference between CodeConnection IAM permission, CodeStar IAM permission API Requests")
print("=========================================================")

for codeconnection_item in codeconnection_iam_requests:
    codestar_item = next((i for i in codestar_iam_requests if i['connection_name'] == codeconnection_item['connection_name'] and i['role_limitation'] == codeconnection_item['role_limitation'] and i['operation'] == codeconnection_item['operation']), None) 

    if not codestar_item:
        raise ValueError("Cannot match item codestar_item")

    if codeconnection_item["status"] != codestar_item["status"]  and (codestar_item["status"]=="200" or OUTPUT_ALL_DIFFERENCES):
        print(f"{codeconnection_item['connection_name']} {codeconnection_item['role_limitation']} {codeconnection_item['operation']}")
        print(f"CodeConnection: {codeconnection_item['status']}, CodeStar: {colour_status(codestar_item['status'])}")


print("=========================================================")
print("Difference between CodeConnection IAM permission and CodeStar IAM permission with CodeConnection Conditions API Requests")
print("=========================================================")

for codeconnection_item in codeconnection_iam_requests:

    codestar_ccc_item = next((i for i in codestar_ccc_iam_requests if i['connection_name'] == codeconnection_item['connection_name'] and i['role_limitation'] == codeconnection_item['role_limitation'] and i['operation'] == codeconnection_item['operation']), None) 

    if not codestar_ccc_item:
        raise ValueError("Cannot match item codestar_ccc_item")

    if codeconnection_item["status"] != codestar_ccc_item["status"]  and (codestar_ccc_item["status"]=="200" or OUTPUT_ALL_DIFFERENCES):
        print(f"{codeconnection_item['connection_name']} {codeconnection_item['role_limitation']} {codeconnection_item['operation']}")
        print(f"CodeConnection: {codeconnection_item['status']}, CodeStarCCC: {colour_status(codestar_ccc_item['status'])}")