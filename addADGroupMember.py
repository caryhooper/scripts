#!/usr/bin/env python3
from pyad import *
pyad.set_defaults(ldap_server="kortana.local", username="sarahpalmer", password="P@ssw0rd")

user = aduser.ADUser.from_cn("sarahpalmer")
print(user)
