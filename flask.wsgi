import os, sys

# edit your username below
sys.path.append("/home/tycoon59/public_html")
os.chdir("/home/tycoon59/public_html/")

sys.path.insert(0, os.path.dirname(__file__))
from myapp import app as application

# make the secret code a little better
application.secret_key = 'aUYk3irAGGSlpFCQrfII1TbsDYigCWY2Xg2etTRTTi1OwLbnX2'