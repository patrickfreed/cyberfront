import json
import sys
import shutil
import os


with open(os.environ['CF_DIR'] + sys.argv[1] + '.json') as f:
    service = json.load(f)

shutil.copy(sys.argv[2], service['options']['wwwroot'])
