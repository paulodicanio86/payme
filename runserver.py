#!/usr/bin/env python
from payme import app
from socket import gethostname, gethostbyname

ip_address = gethostbyname(gethostname())
app.run(debug=True, host=ip_address)
