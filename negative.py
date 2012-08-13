import sys
from gluster import *

# Negative-lookup-caching example.  If a file wasn't there the last time we
# looked, it's probably still not there.  This translator keeps track of
# those failed lookups for us, and returns ENOENT without needing to pass the
# call any further for repeated requests.

# If we were doing this for real, we'd need separate caches for each xlator
# instance.  The easiest way to do this would be to have xlator.__init__
# "register" each instance in a module-global dict, with the key as the C
# translator address and the value as the xlator object itself.  For testing
# and teaching, it's sufficient just to have one cache.  The keys are parent
# GFIDs, and the entries are lists of names within that parent that we know
# don't exist.
cache = {}

# TBD: we need a better way of handling per-request data (frame->local in C).
requests = {}
dl.get_id.restype = c_long
dl.get_id.argtypes = [ POINTER(call_frame_t) ]

def uuid2str (orig):
	return "%08x%08x%08x%08x" % (orig[0], orig[1], orig[2], orig[3])

@lookup_fop_t
def lookup_fop (frame, this, loc, xdata):
	pargfid = uuid2str(loc.contents.pargfid)
	print "lookup FOP: %s:%s" % (pargfid, loc.contents.name)
	# Check the cache.
	if cache.has_key(pargfid) and (loc.contents.name in cache[pargfid]):
		print "short-circuiting for %s:%s" % (pargfid, loc.contents.name)
		dl.unwind_lookup(frame,0,this,-1,2,None,None,None,None)
		return 0
	key = dl.get_id(frame)
	requests[key] = (pargfid, loc.contents.name[:])
	# TBD: get real child xl from init, pass it here
	dl.wind_lookup(frame,POINTER(xlator_t)(),loc,xdata)
	return 0

@lookup_cbk_t
def lookup_cbk (frame, cookie, this, op_ret, op_errno,
				inode, buf, xdata, postparent):
	print "lookup CBK: %d (%d)" % (op_ret, op_errno)
	key = dl.get_id(frame)
	pargfid, name = requests[key]
	# Update the cache.
	if op_ret == 0:
		print "found %s, removing from cache" % name
		if cache.has_key(pargfid):
			cache[pargfid].discard(name)
	elif op_errno == 2:	# ENOENT
		print "failed to find %s, adding to cache" % name
		if cache.has_key(pargfid):
			cache[pargfid].add(name)
		else:
			cache[pargfid] = set([name])
	del requests[key]
	dl.unwind_lookup(frame,cookie,this,op_ret,op_errno,
					 inode,buf,xdata,postparent)
	return 0

class xlator ():
	def __init__ (self, xl):
		dl.set_lookup_fop(xl,lookup_fop)
		dl.set_lookup_cbk(xl,lookup_cbk)

