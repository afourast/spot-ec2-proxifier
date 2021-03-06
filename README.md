spot-ec2-proxifier
==================
This is a Python script that brings up a spot EC2 instance (of a specified type, region and maximimum bid), tags it, and then launches an SSH tunnel (via plink subprocess) to that instance for use with software such as Proxifier.

My own personal use for this is using the newly added Sydney EC2 facility as a poor man's pay-as-you-go 'lowerping' service.

Prerequisites
---------
* Python 2.6 (ish)
* [Boto](https://github.com/boto/boto) library
* [plink](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) (needs to be on your system path)

Configuration
---------
A template configuration file is provided in `spot-ec2-proxifier.ini.defaults` (rename it).

These are some important parameters:

- `ami` Unfortunately you will need to manually find the AMI to use in your region
- `key_pair` You will need a named keypair on EC2 for instance creation
- `security_group` Ditto
- `tag` A tag that will be used by the script to identify the spot-ec2-proxifier-purpose instance
- `bind_port` Which port to bind locally for the SSH tunnel
- `key_file` Puttygen'd private key file that plink will use to connect

Some thoughts
--------------
I suggest using *t1.micro* instances as tunneling this way does not really generate any CPU load and I cannot find 
documented evidence that higher tiers brings any benefit.

Your IAM user needs to have access to a number of EC2 API calls, I believe they are:
* DescribeInstances
* DescribeSpotPriceHistoryRequest
* DescribeSpotInstanceRequests
* RequestSpotInstances

The script is written in a fairly platform agnostic way but it's only been tested on Windows so YMMV.

Expected behavior
-------------
First connect  should go something like:
<pre>python main.py
Spot price is 0.004... below maximum bid, continuing
Spot request created, status: open
Waiting for instance to be provisioned (usually takes 1m to be reviewed, another 2m to be fulfilled) ...  . . . Instance is active.
Tagging instance... Done.
Waiting for server to come up ... . . . . Server is up!
Running: plink -N -D 1080 -i key.ppk ec2-user@54.252.5.153
Once connection is established, use Ctrl-C to kill the tunnel
The server's host key is not cached in the registry. You
have no guarantee that the server is the computer you
think it is.
The server's rsa2 key fingerprint is:
ssh-rsa 2048 af:2c:0d:7d:17:f8:99:42:64:4b:8f:99:99:50:7f:a4
If you trust this host, enter "y" to add the key to
PuTTY's cache and carry on connecting.
If you want to carry on connecting just once, without
adding the key to the cache, enter "n".
If you do not trust this host, press Return to abandon the
connection.
Store key in cache? (y/n)</pre>

Subsequent connects:
<pre>python main.py
Instance exists already, we will not be provisioning another one
Waiting for server to come up ... Server is up!
Running: plink -N -D 1080 -i key.ppk ec2-user@54.252.5.153
Once connection is established, use Ctrl-C to kill the tunnel
Using username "ec2-user".</pre>

Terminating (and detagging) the instance:
<pre>python main.py stop
Terminating i-0a1b1930 ... done.
</pre>