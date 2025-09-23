#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse
import requests
from .constants import ConstantConfig


class Auth:
  def __init__(self):
    pass

  def get_openid_configuration(self) -> str:
    url: str = f"{ConstantConfig.base_url}{ConstantConfig.OPENID_ENDPOINT}"
    return requests.get(url).text

  def get_access_token(self) -> str:
    openid_conf = json.loads(self.get_openid_configuration())
    body = {
      "client_id": f"Job@{urlparse(openid_conf['issuer']).hostname}",
      "client_secret": "secret",
      "scope": "usercube_api",
      "grant_type": openid_conf["grant_types_supported"][0]
    }
    response = requests.post(
      url=openid_conf["token_endpoint"],
      data=body
    )
    return json.loads(response.text)["access_token"]
