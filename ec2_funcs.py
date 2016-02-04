from boto.ec2.connection import EC2Connection
from time import sleep
import subprocess
import ConfigParser, os, socket
import sys

config = ConfigParser.ConfigParser()
config.read('spot-ec2-proxifier.conf')

def create_client():
        client = EC2Connection(config.get('IAM', 'access'), config.get('IAM', 'secret'))
        regions = client.get_all_regions()
        for r in regions:
                if r.name == config.get('EC2', 'region'):
                        client = EC2Connection(config.get('IAM', 'access'), config.get('IAM', 'secret'), region = r)
                        return client
        return None

def get_existing_instance(client):
        instances = client.get_all_instances(filters = { 'tag-value': config.get('EC2', 'tag') })
        if len(instances) > 0:
                return instances[0].instances[0]
        else:
                return None

def get_spot_price(client):
        print 'Getting spot price'
        price_history = client.get_spot_price_history(instance_type = config.get('EC2', 'type'), product_description = 'Linux/UNIX', availability_zone=config.get('EC2', 'zone'))
        return price_history[0].price

def provision_instance(client):
        # with open(config.get('EC2', 'user_data_file'), 'r') as myfile:
            # user_data=myfile.read()
        req = client.request_spot_instances(
                price = config.get('EC2', 'max_bid'), 
                image_id = config.get('EC2', 'AMI'), 
                instance_type = config.get('EC2', 'type'), 
                key_name = config.get('EC2', 'key_pair'), 
                security_group_ids = [config.get('EC2', 'security_group')],
                placement = config.get('EC2', 'zone'),
                # user_data=user_data,
                )[0]
        print 'Spot request created, status: ' + req.state
        print 'Waiting for spot provisioning',
        while True:
                current_req = client.get_all_spot_instance_requests([req.id])[0]
                if current_req.state == 'active':
                        instance = client.get_all_instances([current_req.instance_id])[0].instances[0]
                        instance.add_tag('Name', config.get('EC2', 'tag'))
                        print 'done.'
                        return instance
                print '.',
                sys.stdout.flush()
                sleep(5)

def destroy_instance(client, inst):
        try:
                print 'Terminating', str(inst.id), '...',
                client.terminate_instances(instance_ids = [inst.id])
                print 'done.'
                inst.remove_tag('Name', config.get('EC2', 'tag'))
        except:
                print 'Failed to terminate:', sys.exc_info()[0]

def attach_volume(client, inst):
    try:
      client.attach_volume(config.get('EBS', 'vol_id'), inst.id, config.get('EBS', 'dev'))
      print 'Volume attached!'
    except Exception as e:
      print 'Could not attach volume: %e'%e

def wait_for_up(client):
  print 'Waiting for instance to start running'

  while True:
    inst = get_existing_instance(client)
    if inst.state == u'running':
      print 'done.'
      attach_volume(client,inst)
      break
    print '.',
    sys.stdout.flush()
    sleep(5)

  print 'Checking connectivity'

  while True:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if inst.ip_address is None:
            inst = get_existing_instance(client)
    try:
      if inst.ip_address is None:
        print 'IP not assigned yet ...',
      else:

        s.connect((inst.ip_address, 22))
        s.shutdown(2)
        print 'Server is up!'

        print 'instance id = %s, IP = %s'%(inst.id,inst.ip_address),
        with open('current_instance_ip_address', 'w') as ipfile:
            ipfile.write('ec2 %s\n'%inst.ip_address)
        with open('current_instance_id', 'w') as ipfile:
            ipfile.write('%s\n'%inst.id)

        # mount the volume to home and run setup script 
        with open(config.get('EC2', 'user_data_file'), 'r') as myfile:
            user_data=myfile.read()
        ret = subprocess.call(["ssh", "-o", "StrictHostKeyChecking no", "ubuntu@%s"%inst.ip_address, user_data]);
        print 'Volume mounted!' if ret == 0 else 'Volume could not be mounted correctly'

        break

    except:
            print '.',
            sys.stdout.flush()
    sleep(5)

