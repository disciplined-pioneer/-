import os
from datetime import datetime

import aiohttp
import requests
from dotenv import load_dotenv

from settings import settings


class NalogRuPython:
    HOST = 'irkkt-mobile.nalog.ru:8888'
    DEVICE_OS = 'iOS'
    CLIENT_VERSION = '2.9.0'
    DEVICE_ID = '7C82010F-16CC-446B-8F66-FC4080C66521'
    ACCEPT = '*/*'
    USER_AGENT = 'billchecker/2.9.0 (iPhone; iOS 13.6; Scale/2.00)'
    ACCEPT_LANGUAGE = 'ru-RU;q=1, en-US;q=0.9'

    def __init__(self):
        load_dotenv()
        self.__session_id = None
        self.set_session_id()

    def set_session_id(self) -> None:
        if os.getenv('CLIENT_SECRET') is None:
            raise ValueError('OS environments not content "CLIENT_SECRET"')
        if os.getenv('INN') is None:
            raise ValueError('OS environments not content "INN"')
        if os.getenv('PASSWORD') is None:
            raise ValueError('OS environments not content "PASSWORD"')

        url = f'https://{self.HOST}/v2/mobile/users/lkfl/auth'
        payload = {
            'inn': os.getenv('INN'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'password': os.getenv('PASSWORD')
        }
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'User-Agent': self.USER_AGENT,
        }

        resp = requests.post(url, json=payload, headers=headers)
        self.__session_id = resp.json()['sessionId']

    def _get_ticket_id(self, qr: str) -> str:
        url = f'https://{self.HOST}/v2/ticket'
        payload = {'qr': qr}
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'sessionId': self.__session_id,
            'User-Agent': self.USER_AGENT,
        }
        resp = requests.post(url, json=payload, headers=headers)
        return resp.json()["id"]

    def get_ticket(self, qr: str) -> dict:
        ticket_id = self._get_ticket_id(qr)
        url = f'https://{self.HOST}/v2/tickets/{ticket_id}'
        headers = {
            'Host': self.HOST,
            'sessionId': self.__session_id,
            'Device-OS': self.DEVICE_OS,
            'clientVersion': self.CLIENT_VERSION,
            'Device-Id': self.DEVICE_ID,
            'Accept': self.ACCEPT,
            'User-Agent': self.USER_AGENT,
            'Accept-Language': self.ACCEPT_LANGUAGE,
        }
        resp = requests.get(url, headers=headers)
        return resp.json()


class CheckApi:
    _base_url = 'https://proverkacheka.com'
    _key = settings.check.TOKEN

    async def info_by_raw(
            self,
            fn: int,
            fp: int,
            fd: int,
            date: datetime,
            sum: float,
            type: int = 1
    ) -> dict:
        async with aiohttp.ClientSession(self._base_url) as s:
            r = await s.post(
                url='/api/v1/check/get',
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "token": self._key,
                    "qrraw": f"t={date.strftime("%Y%m%dT%H%M%S")}&s={sum}&fn={fn}&i={fd}&fp={fp}&n={type}",
                }
            )
            data = await r.json()
            print(data)

            if not data['code'] == 1:
                return {'error': True, 'code': data['code']}

            return data

    async def info_by_img(self, img_url: str) -> dict:
        async with aiohttp.ClientSession(self._base_url) as s:
            r = await s.post(
                url='/api/v1/check/get',
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "token": self._key,
                    "qrurl": img_url
                }
            )
            data = await r.json()
            print(data)

            if not data['code'] == 1:
                return {'error': True, 'code': data['code']}

            return data
