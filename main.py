import json
from tqdm import tqdm  # 进度条
import requests

# 关闭https证书警告
try:
    import requests.packages.urllib3

    requests.packages.urllib3.disable_warnings()
except Exception as e:
    print(e)
    pass


def saveErrors(content: str, filename="errors.log"):
    return _saveFile(filename, content)


def saveSubdomain(content: str, filename="result.txt"):
    return _saveFile(filename, content)

def saveOriginData(content: str, filename="data.json"):
    return _saveFile(filename, content)

def _saveFile(filename: str, content: str):
    try:
        with open(filename, 'a+') as file:
            file.write(str(content) + "\n")
    except FileExistsError or FileNotFoundError as e:
        print(e)


def getContent(school, key):
    url = "https://open.beianx.cn/api/query_icp_v3"
    data = {
        "keyword": school,
        "api_key": key
    }
    try:
        response = requests.post(url=url, data=data).text
        response = json.loads(response)

    except Exception as e:
        print(e, school)
        saveErrors(f"{school}:{e}")
    return response


def _loadfiletolist(filename: str) -> list:
    _list = []
    try:
        with open(filename) as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                _list.append(line)
    except FileExistsError or FileNotFoundError:
        print("打开文件错误")
        exit(-1)
    return _list


def getKey(filename):
    return _loadfiletolist(filename)


def getSchool(filename):
    return _loadfiletolist(filename)


if __name__ == '__main__':

    schools = getSchool("schools.txt")
    keyList = getKey("key.txt")

    key = keyList.pop()
    errorList = []
    for school in tqdm(schools, desc="催啥催"):
        try:
            response = getContent(school, key)
            # print(response["data"])

            if response["code"] == 200:

                # 保存原始数据json
                saveOriginData(response)
                results = response["data"]
                # infoDict = {}
                # infoList = []
                for result in results:
                    # unit = result["unit"]
                    domain = result["domain"]
                    # infoList.append(domain)
                    saveSubdomain(domain)
            elif response["code"] == 402 or response["code"] == 401:
                key = keyList.pop()
                response = getContent(school, key)
                if response["code"] == 200:
                    # 保存原始数据json
                    saveOriginData(response)
                    results = response["data"]
                    # infoDict = {}
                    # infoList = []
                    for result in results:
                        # unit = result["unit"]
                        domain = result["domain"]
                        # infoList.append(domain)
                        saveSubdomain(domain)
                else:
                    errorList.append(school)
            else:
                errorList.append(school)
        except Exception as e:
            print(e)
            errorList.append(school)
    saveErrors(errorList, "schoolsErrors.log")
