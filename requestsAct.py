import requests
import json

import requests

import uuid

import ssl
from urllib3 import poolmanager
from requests.adapters import HTTPAdapter


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # Create a custom SSL context
        context = ssl.create_default_context()
        context.set_ciphers("HIGH:!DH:!aNULL")
        # Disable hostname checking
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

# page_url = "https://www.parliament.lk/en/business-of-parliament/acts-bills#current"
# requests.packages.urllib3.disable_warnings()
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

# try:
#     requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += (
#         ":HIGH:!DH:!aNULL"
#     )
# except AttributeError:
#     # no pyopenssl support used / needed / available
#     pass


def load_bills(start_pagination,id):
    request_url = "https://www.parliament.lk/business-of-parliament/"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Cookie": "c2c41549d73f81fa91097e85b68c21df=8r9q8ljd5hap5r759p9as3afj2; jfcookie[lang]=en; _gid=GA1.2.2023837324.1718211583; _gat_gtag_UA_238382738_1=1; _ga_N9CBBXSN9G=GS1.1.1718211582.3.1.1718211593.0.0.0; _ga=GA1.2.173125640.1718086442",
        "Host": "www.parliament.lk",
        "Origin": "https://www.parliament.lk",
        "Referer": "https://www.parliament.lk/en/business-of-parliament/acts-bills",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
    }

    payload = {
        "option": "com_actsandbills",
        "task": "acts",
        "tmpl": "component",
        "start": f"{start_pagination}",
        "legis": f"{id}",
        "year": "",
        "keyword": "",
        "id": "undefined",
    }

    session = requests.Session()
    session.mount('https://', SSLAdapter())  # Mount the custom SSL adapter

    response = session.post(request_url, headers=headers,
                            data=payload, verify=False)

    # response = requests.post(
    #     request_url, headers=headers, data=payload, verify=False)

    # print("response content: ", response.content)

    # check status code
    if response.status_code != 200:
        print("Error: ", response.status_code)
        print("Error: ", response.content)
        return None

    else:
        print("Success: ", response.status_code)

        # print("response content: ", response.content)

    return response.content


if __name__ == "__main__":

    load_bills()
