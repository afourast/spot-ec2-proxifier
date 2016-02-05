#!/usr/bin/env python
from ec2_funcs import *

# Entry

client = create_client()
if client is None:
        print 'Unable to create EC2 client'
        sys.exit(0)

spot_price = get_spot_price(client)
print 'Spot price is ' + str(spot_price) + ' ...',


