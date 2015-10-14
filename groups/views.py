from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from servers.models import Compute
from instance.models import Instance
from servers.forms import ComputeAddTcpForm, ComputeAddSshForm, ComputeEditHostForm, ComputeAddTlsForm, ComputeAddSocketForm
from vrtManager.hostdetails import wvmHostDetails
from vrtManager.connection import CONN_SSH, CONN_TCP, CONN_TLS, CONN_SOCKET, connection_manager
from libvirt import libvirtError

from django.views.decorators.csrf import csrf_exempt
from django.middleware import csrf
import json
from django.http import HttpResponse
import sys
from vrtManager import util


def index(request):
    """

    Index page.

    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    else:
        return HttpResponseRedirect(reverse('groups_list'))

def groups_list(request):
    """
    Servers page.
    """
    print >>sys.stderr, 'Inside the groups list module..............'
    filter_on = False
    filter_data = ''
    host_group = []
    current_group = ''

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
     
#    if request.method == 'POST':
#    	if 'next' in request.POST:
#		print >>sys.stderr, "Yeppp found test"
#	        filter_data = request.POST['next']
#                print >>sys.stderr, filter_data
#                if filter_data == 'all':
#			print >>sys.stderr, "filter data for all"
#			fitler_on = False
#		else:
#			filter_on = True
#    	else:
#		print >>sys.stderr, 'Filter is off, no filter data found.'

#    def filter_hosts_status(hosts, filter_data):
#        """
#        Function return all hosts all vds on host
#        """
#        print >>sys.stderr, 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
#
#
#        all_hosts = []
#        for host in hosts:
#	    if host.name[:3] not in host_group:
#		    host_group.append(host.name[:3])
#	    if  host.name[:3] == filter_data:
#            	all_hosts.append({'id': host.id,
#                	          'name': host.name,
#                        	  'hostname': host.hostname,
#                             	  'status': connection_manager.host_is_up(host.type, host.hostname),
#                                  'type': host.type,
#                                  'login': host.login,
#                                  'password': host.password
#                                })
#        return all_hosts


    def get_hosts_status(hosts):
        """
        Function return all hosts all vds on host
        """
        print >>sys.stderr, 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'


#        all_hosts = []
        for host in hosts:
	    if '#' in host.name:
		print >>sys.stderr, host.name
		host.name = (host.name).split("#")[0]
	    else:
		host.name = 'None'

	    print >>sys.stderr, host.name

	    if host.name not in host_group:
 	           host_group.append(host.name)

#            all_hosts.append({'id': host.id,
#                              'name': host.name,
#                              'hostname': host.hostname,
#                              'status': connection_manager.host_is_up(host.type, host.hostname),
#                              'type': host.type,
#                              'login': host.login,
#                              'password': host.password
#                              })
#        return all_hosts

    print >>sys.stderr, 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'

    computes = Compute.objects.filter()
    print >>sys.stderr, computes
#    if filter_on == True:
#	current_group = filter_data
#	print >>sys.stderr, 'Going to do the filter'
#	hosts_info = filter_hosts_status(computes, filter_data)
#    else:
#
    print >>sys.stderr, 'Filter is not required'
    hosts_info = get_hosts_status(computes)
#
    print >>sys.stderr, host_group
    form = None


    return render_to_response('groups.html', locals(), context_instance=RequestContext(request))
