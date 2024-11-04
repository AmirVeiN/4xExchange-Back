from celery import shared_task

from user.models import User
from .models import Deposit, WithdrawEmailConfirmation
import hashlib
import json
import time
from urllib.parse import urlparse
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import requests


class RequestsClient(object):
    access_id = "2BCC8CAAA994489291F1FFEB2735F09B"  # Replace with your access id
    secret_key = "7F37419F334D4F4290A44B5676B8F9ECD0A6C609A88005B2"  # Replace with your secret key
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "X-COINEX-KEY": "",
        "X-COINEX-SIGN": "",
        "X-COINEX-TIMESTAMP": "",
    }

    def __init__(self):
        self.access_id = self.access_id
        self.secret_key = self.secret_key
        self.url = "https://api.coinex.com/v2"
        self.headers = self.HEADERS.copy()

    # Generate your signature string
    def gen_sign(self, method, request_path, body, timestamp):
        prepared_str = f"{method}{request_path}{body}{timestamp}{self.secret_key}"
        signed_str = hashlib.sha256(prepared_str.encode("utf-8")).hexdigest().lower()
        return signed_str

    def get_common_headers(self, signed_str, timestamp):
        headers = self.HEADERS.copy()
        headers["X-COINEX-KEY"] = self.access_id
        headers["X-COINEX-SIGN"] = signed_str
        headers["X-COINEX-TIMESTAMP"] = timestamp
        headers["Content-Type"] = "application/json; charset=utf-8"
        return headers

    def request(self, method, url, params={}, data=""):
        req = urlparse(url)
        request_path = req.path

        timestamp = str(int(time.time() * 1000))
        if method.upper() == "GET":
            # If params exist, query string needs to be added to the request path
            if params:
                query_params = []
                for item in params:
                    if params[item] is None:
                        continue
                    query_params.append(item + "=" + str(params[item]))
                query_string = "?{0}".format("&".join(query_params))
                request_path = request_path + query_string

            signed_str = self.gen_sign(
                method, request_path, body="", timestamp=timestamp
            )
            response = requests.get(
                url,
                params=params,
                headers=self.get_common_headers(signed_str, timestamp),
            )

        else:
            signed_str = self.gen_sign(
                method, request_path, body=data, timestamp=timestamp
            )
            response = requests.post(
                url, data, headers=self.get_common_headers(signed_str, timestamp)
            )

        if response.status_code != 200:
            raise ValueError(response.text)
        return response


request_client = RequestsClient()


def get_deposit_history():
    request_path = "/assets/deposit-history"
    params = {"ccy": "USDT"}

    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response.json()


@shared_task
def delete_email_code(pk, code):

    instance1 = PeriodicTask.objects.filter(name__startswith=f"Delete_EmailCode_{code}")
    for task in instance1:
        task.delete()

    instance2 = WithdrawEmailConfirmation.objects.filter(code=code)
    for task in instance2:
        task.delete()
