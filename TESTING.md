== How to test ==

'test.vol' is a simple volfile with the helloworld.py translator on top
of a brick. The volfile can be mounted using the the following command.

    # glusterfs --debug -f test.vol /path/to/mountpoint

Each time a file operation is performed in the mount point, debug
logging information will appear on standard output.

For more in depth logging information, change the helloworld module
name in test.vol to "debug-trace".  This will use the "debug-trace.py"
translator file instead, which outputs much for information.
