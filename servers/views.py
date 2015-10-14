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

import sys

def index(request):
    """

    Index page.

    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    else:
        return HttpResponseRedirect(reverse('servers_list'))


def servers_list(request):
    """
    Servers page.
    """
    print >>sys.stderr, 'ssssssssssssssssssssssssssssssssssssssssssssss'
    filter_on = False
    filter_data = ''
    host_group = []
    current_group = ''

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
     
    if request.method == 'POST':
    	if 'next' in request.POST:
		print >>sys.stderr, "Yeppp found test"
	        filter_data = request.POST['next']
                print >>sys.stderr, filter_data
                if filter_data == 'all':
			print >>sys.stderr, "filter data for all"
			fitler_on = False
		else:
			filter_on = True
    	else:
		print >>sys.stderr, 'Filter is off, no filter data found.'

    def filter_hosts_status(hosts, filter_data):
        """
        Function return all hosts all vds on host
        """
        print >>sys.stderr, 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        print >>sys.stderr, filter_data

        all_hosts = []
        for host in hosts:
#	    if host.name[:3] not in host_group:
#		    host_group.append(host.name[:3])
	    print >>sys.stderr, (host.name).split("#")[0]
	    if  (host.name).split("#")[0] == filter_data:
            	all_hosts.append({'id': host.id,
                	          'name': (host.name).split("#")[1],
                        	  'hostname': host.hostname,
                             	  'status': connection_manager.host_is_up(host.type, host.hostname),
                                  'type': host.type,
                                  'login': host.login,
                                  'password': host.password
                                })
        return all_hosts


    def get_hosts_status(hosts):
        """
        Function return all hosts all vds on host
        """
        print >>sys.stderr, 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        

        all_hosts = []
        for host in hosts:
#	    if host.name[:3] not in host_group:
# 	           host_group.append(host.name[:3])
	    if '#' in host.name:
	    	print >>sys.stderr, (host.name).split("#")[1]
		host.name = (host.name).split("#")[1]

            all_hosts.append({'id': host.id,
                              'name': host.name,
                              'hostname': host.hostname,
                              'status': connection_manager.host_is_up(host.type, host.hostname),
                              'type': host.type,
                              'login': host.login,
                              'password': host.password
                              })
        return all_hosts

    print >>sys.stderr, 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'

    computes = Compute.objects.filter()
    print >>sys.stderr, computes
    if filter_on == True:
	current_group = filter_data
	print >>sys.stderr, 'Going to do the filter'
	hosts_info = filter_hosts_status(computes, filter_data)
    else:
        print >>sys.stderr, 'Filter is not required'
	current_group = 'ALL'
        hosts_info = get_hosts_status(computes)

    print >>sys.stderr, host_group
    form = None

    if request.method == 'POST':
        if 'host_del' in request.POST:
            compute_id = request.POST.get('host_id', '')
            try:
                del_inst_on_host = Instance.objects.filter(compute_id=compute_id)
                del_inst_on_host.delete()
            finally:
                del_host = Compute.objects.get(id=compute_id)
                del_host.delete()
            return HttpResponseRedirect(request.get_full_path())
        if 'host_tcp_add' in request.POST:
            form = ComputeAddTcpForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                new_tcp_host = Compute(name=data['name'],
                                       hostname=data['hostname'],
                                       type=CONN_TCP,
                                       login=data['login'],
                                       password=data['password'])
                new_tcp_host.save()
                return HttpResponseRedirect(request.get_full_path())
        if 'host_ssh_add' in request.POST:
            form = ComputeAddSshForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                new_ssh_host = Compute(name=data['name'],
                                       hostname=data['hostname'],
                                       type=CONN_SSH,
                                       login=data['login'])
                new_ssh_host.save()
                return HttpResponseRedirect(request.get_full_path())
        if 'host_tls_add' in request.POST:
            form = ComputeAddTlsForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                new_tls_host = Compute(name=data['name'],
                                       hostname=data['hostname'],
                                       type=CONN_TLS,
                                       login=data['login'],
                                       password=data['password'])
                new_tls_host.save()
                return HttpResponseRedirect(request.get_full_path())

        if 'host_edit' in request.POST:
            form = ComputeEditHostForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                compute_edit = Compute.objects.get(id=data['host_id'])
                compute_edit.name = data['name']
                compute_edit.hostname = data['hostname']
                compute_edit.login = data['login']
                compute_edit.password = data['password']
                compute_edit.save()
                return HttpResponseRedirect(request.get_full_path())

        if 'host_socket_add' in request.POST:
            form = ComputeAddSocketForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                new_socket_host = Compute(name=data['name'],
                                          hostname='localhost',
                                          type=CONN_SOCKET,
                                          login='',
                                          password='')
                new_socket_host.save()
                return HttpResponseRedirect(request.get_full_path())

    return render_to_response('servers.html', locals(), context_instance=RequestContext(request))


def infrastructure(request):
    """
    Infrastructure page.
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    compute = Compute.objects.filter()
    hosts_vms = {}

    for host in compute:
        status = connection_manager.host_is_up(host.type, host.hostname)
        if status:
            try:
                conn = wvmHostDetails(host, host.login, host.password, host.type)
                host_info = conn.get_node_info()
                host_mem = conn.get_memory_usage()
                hosts_vms[host.id, host.name, status, host_info[3], host_info[2],
                          host_mem['percent']] = conn.get_host_instances()
                conn.close()
            except libvirtError:
                hosts_vms[host.id, host.name, status, 0, 0, 0] = None
        else:
            hosts_vms[host.id, host.name, 2, 0, 0, 0] = None

    return render_to_response('infrastructure.html', locals(), context_instance=RequestContext(request))
