import logging
import hmac
import hashlib
import json
import requests
import time
import uuid

from Crypto.PublicKey import RSA

from .textbook_rsa import new as new_textbook_rsa
from .const import *
from .exceptions import *

PRODUCT_TYPES = {
  "pq860vo9ib50jhud": "switch"
}

logger = logging.getLogger(__name__)

class TuyaDevice:
  def __init__(self, api, info):
    self.api = api

    self._schema = json.loads(info["schema"])
    self._id = info["devId"]
    self._dps = info["dps"]
    self._name = info["name"]
    self._online = info["isOnline"]
    self._product = PRODUCT_TYPES[info["productId"]] if info["productId"] in PRODUCT_TYPES else "unknown"


  @property
  def schema(self):
    return self._schema


  @property
  def id(self):
    return self._id


  @property
  def dps(self):
    return self._dps


  @property
  def name(self):
    return self._name


  @property
  def product(self):
    return self._product


  @property
  def online(self):
    return self._online


  def set_dps(self, dps, value):
    success = self.api.set_dps(self._id, dps, value)
    if success is True:
      self._dps[dps] = value
    return success


  def refresh(self):
    self._online = self.api._device(self._id)["isOnline"]
    self._dps = self.api.get_dps(self._id)



class TuyaAPI:
  def __init__(self,
               email: str,
               password: str,
               client_id: str = TUYA_CLIENT_ID,
               tuya_key: str = TUYA_SECRET_KEY,
               country_code: int = TUYA_COUNTRY_CODE):
    self._email = email
    self._password = password
    self._client_id = client_id
    self._tuya_key = tuya_key
    self._country_code = country_code

    self.session = requests.session()
    self.sid = None


  def _api(self, options, post_data=None, requires_sid=True, do_not_relogin=False):
    headers = {"User-Agent": TUYA_USER_AGENT}
    data = {"postData": json.dumps(post_data)} if post_data is not None else None
    sanitized_options = {**options}
    if "action" in sanitized_options:
      sanitized_options["a"] = options["action"]
      del sanitized_options["action"]

    params = {
      "appVersion": "1.1.6",
      "appRnVersion": "5.14",
      "channel": "oem",
      "deviceId": TUYA_DEVICE_ID,
      "platform": "Linux",
      "requestId": str(uuid.uuid4()),
      "lang": "en",
      "clientId": self._client_id,
      "osSystem": "9",
      "os": "Android",
      "timeZoneId": "America/Bahia",
      "ttid": "sdk_tuya@" + self._client_id,
      "et": "0.0.1",
      "v": "1.0",
      "sdkVersion": "3.10.0",
      "time": str(int(time.time())),
      **sanitized_options
    }

    if requires_sid:
      if self.sid is None:
        raise ValueError("You need to login first.")
      params["sid"] = self.sid

    sanitized_data = data if data is not None else {}
    params["sign"] = self._sign({**params, **sanitized_data})

    try:
      result = self._handle(self.session.post(TUYA_ENDPOINT, params=params, data=data, headers=headers).json())
      logger.debug("Request: options %s, headers %s, params %s, data %s, result %s", options, headers, params, data, result)
    except InvalidUserSession:
      if not do_not_relogin:
        logger.info("Session is no longer valid, logging in again")
        self.login()
        result = self._api(options, post_data, requires_sid, True)

    return result


  def _sign(self, data):
    KEYS_TO_SIGN = ['a', 'v', 'lat', 'lon', 'lang', 'deviceId', 'imei',
                    'imsi', 'appVersion', 'ttid', 'isH5', 'h5Token', 'os',
                    'clientId', 'postData', 'time', 'requestId', 'n4h5', 'sid',
                    'sp', 'et']

    sorted_keys = sorted(list(data.keys()))

    # Create string to sign
    strToSign = ""
    for key in sorted_keys:
      if key not in KEYS_TO_SIGN or key not in data or data[key] is None or len(str(data[key])) == 0:
        continue
      elif key == "postData":
        if len(strToSign) > 0:
          strToSign += "||"
        strToSign += key + "=" + self._mobile_hash(data[key])
      else:
        if len(strToSign) > 0:
          strToSign += "||"
        strToSign += key + "=" + data[key]

    return hmac.new(bytes(self._tuya_key, "utf-8"), msg = bytes(strToSign, "utf-8"), digestmod = hashlib.sha256).hexdigest()


  def _mobile_hash(self, data):
    prehash = hashlib.md5(bytes(data, "utf-8")).hexdigest()
    return prehash[8:16] + prehash[0:8] + prehash[24:32] + prehash[16:24]


  def _handle(self, result):
    if result["success"]:
      return result["result"]
    elif result["errorCode"] == "USER_SESSION_INVALID":
      raise InvalidUserSession
    elif result["errorCode"] == "USER_PASSWD_WRONG":
      raise InvalidAuthentication
    else:
      logger.error("Error! Code: %s, message: %s, result: %s", result["errorCode"], result["errorMsg"], result)
      raise ValueError("Invalid result, check logs")


  def login(self):
    token_info = self._api({"action": "tuya.m.user.email.token.create"}, {"countryCode": self._country_code, "email": self._email}, requires_sid=False, do_not_relogin=True)
    payload = {
      "countryCode": str(self._country_code),
      "email": self._email,
      "ifencrypt":1,
      "options":"{\"group\": 1}",
      "passwd": self._enc_password(token_info["publicKey"], token_info["exponent"], self._password),
      "token": token_info["token"],
    }
    login_info = self._api({"action": "tuya.m.user.email.password.login"}, payload, requires_sid=False, do_not_relogin=True)
    self.sid = login_info["sid"]
  

  def _enc_password(self, public_key, exponent, password):
    key = new_textbook_rsa(RSA.construct((int(public_key), int(exponent))))
    a = "0000000000000000000000000000000000000000000000000000000000000000" + key.encrypt(hashlib.md5(password.encode("utf8")).hexdigest().encode("utf8")).hex()
    return a


  def groups(self):
    return self._api({"action": "tuya.m.location.list"})


  def devices(self, group_id):
    devs = []
    for dev in self._api({"action": "tuya.m.my.group.device.list", "gid": group_id}):
      dev_obj = self.device(dev["devId"])
      if dev_obj is not None:
        devs.append(dev_obj)
    return devs


  def device(self, device_id):
    return TuyaDevice(self, self._device(device_id))

  
  def _device(self, device_id):
    return self._api({"action": "tuya.m.device.get"}, {"devId": device_id})


  def get_dps(self, device_id, dps=None):
    result = self._api({"action": "tuya.m.device.dp.get"}, {"devId": device_id})
    if dps is not None:
      return result[dps]
    else:
      return result


  def set_dps(self, device_id, dps, value=None):
    if isinstance(dps, dict):
      return self._api({"action": "tuya.m.device.dp.publish"}, {"devId": device_id, "gwId": device_id, "dps": json.dumps(dps)})
    else:
      return self._api({"action": "tuya.m.device.dp.publish"}, {"devId": device_id, "gwId": device_id, "dps": json.dumps({dps: value})})
