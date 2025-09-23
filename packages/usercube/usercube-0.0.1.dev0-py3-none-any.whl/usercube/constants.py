#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConstantConfig:
  base_url: str = "http://localhost:5000"
  OPENID_ENDPOINT: str = "/.well-known/openid-configuration"
  TOKEN_ENDPOINT: str = "/connect/token"

  LANDING: str = "https://www.usercube.com"
  DOCUMENTATION: str = "https://docs.netwrix.com/docs/identitymanager/6_2/"

  CONFIG_FOLDER_PATH: Path = Path().home()
  USERCUBE_CONFIG_PATH: Path = CONFIG_FOLDER_PATH / "settings.json"
