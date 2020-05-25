import sys
import json
try:
    print(json.load(sys.stdin)['server']['up'])
except:
    print('False')
