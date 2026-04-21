import re

html = open('/tmp/metro.html').read()

# Buscar API keys
keys = re.findall(r'[xX]-[aA][pP][iI]-[kK]ey[\"\':s]+([a-zA-Z0-9\-_]{20,})', html)
print('API keys:', keys[:5])

keys2 = re.findall(r'apiKey[\"\':s]+([a-zA-Z0-9\-_]{20,})', html)
print('apiKey:', keys2[:5])

# Buscar JWT tokens
tokens = re.findall(r'eyJ[a-zA-Z0-9\-_\.]{50,}', html)
print('JWT tokens:', tokens[:2])

# Buscar cualquier header de autenticacion
auth = re.findall(r'[Aa]uthorization[\"\':s]+([a-zA-Z0-9\-_\. ]{20,})', html)
print('Authorization:', auth[:3])
