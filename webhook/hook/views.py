import subprocess
import os
import hmac
import requests
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes

from ipaddress import ip_address, ip_network
from hashlib import sha1

ENV = os.environ.copy()
ENV['PATH'] = '/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin' + ENV['PATH']


@require_POST
@csrf_exempt
def r10k_hook(request):
    # Verify if request came from GitHub
    forwarded_for = '{}'.format(request.META.get('X-Forwarded-For'))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        # Try to get the branch to pass through to the script to make the deployments quicker
        request_dict = json.loads(request.body.decode('ASCII'))
        try:
            branch = request_dict['ref']
        except KeyError:
            pass

        if branch:
            short_branch = branch.replace('refs/heads/', '')
            pup_env = short_branch.replace('/', '_')
            pup_env = pup_env.replace('-', '_')

            run_script = subprocess.Popen(
                '/usr/local/bin/sudo {0} {1}'.format(
                    settings.HOOK_SCRIPT,pup_env),
                shell=True)
            run_script.communicate()

            return HttpResponse('success')
        else:
            run_script = subprocess.Popen(
                '/usr/local/bin/sudo {0}'.format(
                    settings.HOOK_SCRIPT),
                shell=True).communicate()
            run_script.communicate()

            return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)


@require_POST
@csrf_exempt
def enc_hook(request):
    # Verify if request came from GitHub
    forwarded_for = '{}'.format(request.META.get('X-Forwarded-For'))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY),
                   msg=force_bytes(request.body), digestmod=sha1)

    if not hmac.compare_digest(force_bytes(mac.hexdigest()),
                               force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        # Deploy some code for example
        p = subprocess.Popen(
            ['sudo git pull'],
            cwd=settings.ENC_DIR, shell=True, env=ENV).communicate()
        p.wait(timeout=30)
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)
