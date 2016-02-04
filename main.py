from ec2_funcs import *

# Entry
action = 'start' if len(sys.argv) == 1 else sys.argv[1]

client = create_client()
if client is None:
        print 'Unable to create EC2 client'
        sys.exit(0)

inst = get_existing_instance(client)

if action == 'start':
        if inst is None:
                spot_price = get_spot_price(client)
                print 'Spot price is ' + str(spot_price) + ' ...',
                if spot_price > float(config.get('EC2', 'max_bid')):
                        print 'too high!'
                        sys.exit(0)
                else:
                        print 'below maximum bid, continuing'
                        provision_instance(client)
        wait_for_up(client)
elif action == 'stop' and inst is not None:
        inst = get_existing_instance(client)
        destroy_instance(client, inst)
else:
        print 'No action taken'




