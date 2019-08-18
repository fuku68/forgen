#!/usr/bin/env python3
import sys
import os
import json
import math
import random, string
import urllib.request, urllib.parse

CHUNK_SIZE = 5000000

args = sys.argv
cliend_id = os.environ.get('FORGE_CLIENT_ID')
client_secret = os.environ.get('FORGE_CLIENT_SECRET')

def print_help():
  str = """
Usage: forgen <command>

command:  resumable <bucket> <object> <file>
"""
  print(str)
  
def random_session_id(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

def get_access_token(id, secrett):
  url = "https://developer.api.autodesk.com/authentication/v1/authenticate"
  request_data = {
    "client_id": cliend_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials",
    "scope": "bucket:create bucket:read data:read data:write data:create"
  }
  data = urllib.parse.urlencode(request_data).encode("utf-8")
  res_str = ''
  with urllib.request.urlopen(url, data=data) as res:
    res_str += res.read().decode("utf-8")
  res_obj = json.loads(res_str)
  return res_obj['access_token']

def resumable_upload(token, bucket, object_name, file_name):
  url = "https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s/resumable" % (bucket, object_name)
  upload_data = open(file_name, "rb").read()
  data_len = len(upload_data)
  loop_num = math.ceil(data_len / CHUNK_SIZE)

  headers = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/octet-stream",
    "Session-Id": random_session_id(10)
  }

  for i in range(loop_num):
    data = upload_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
    headers["Content-Range"] = "bytes %d-%d/%d" % (i * CHUNK_SIZE, i * CHUNK_SIZE + len(data) - 1, data_len)

    request = urllib.request.Request(url, data = data, headers = headers, method="PUT")
    response = urllib.request.urlopen(request)
    print(response.read().decode("utf-8"))


args = sys.argv
if len(args) > 5 and args[1] == "resumable":
  access_token = get_access_token(cliend_id, client_secret)
  print(access_token)
  resumable_upload(access_token, args[2], args[3], args[4])
else:
  print_help()
