#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .auth import Auth


class Usercube:
  def __init__(self) -> None:
    self.auth = Auth()


def main() -> int:
  print("Hello, to the usercube python package.")
  usercube = Usercube()
  token = usercube.auth.get_access_token()
  print("Access token:", token)
  return 0


if __name__ == "__main__":
  main()
