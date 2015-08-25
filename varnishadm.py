#!/usr/bin/python

import datetime
import base64
import pprint
try:
    import json
except ImportError:
    import simplejson as json

DOCUMENTATION = '''
---
module: varnishadm
short_description: Control varnish using varnishadm
description:
  - Control varnish
options:
  secret:
    description:
      - Path to the varnish secret file
    required: false
    default: /etc/varnish/secret
    aliases: []
  backend:
    description:
      - The name of the backend to change
    required: false
    default: null
    aliases: []
  state:
    description:
      - Set the state of the backend.
      - C(healthy) and C(sick) force the state of the backend to that particular value.
      - C(auto) tells varnish to use it's standard health check probes to determine the health.
    required: false
    default: null
    choices: ['auto', 'healthy', 'sick']
    aliases: []
  name:
    description:
      - Connect to the instance of varnishd with this name
    required: false
    default: null
    aliases: []
'''

EXAMPLES = '''
# Disable a backend from varnish

- varnishadm:
    backend=web_backend_broken state=sick

# Enable a backend from varnish

- varnishadm:
    backend=web_backend_working state=auto
'''


def get_state(module, secret, backend, name):
    args = ''

    if name:
      args += ' -n %s ' % name

    cmd = "varnishadm -S '%s' %s backend.list %s" % (secret, args, backend)

    (rc, out, err) = module.run_command(cmd)
    if rc:
        return module.fail_json(msg=err, rc=rc, cmd=cmd)
    else:
        out_lines = out.split('\n')
        data = out_lines[1]
        print data
        state = data.split()[2]

        if state == 'probe':
            return 'auto'
        if state == 'healthy' or state == 'sick':
            return state


def change_state(module, secret, state, backend, name):

    args = ''

    if name:
      args += ' -n %s ' % name

    current_state = get_state(module, secret, backend, name)

    if state == current_state:
        return module.exit_json(changed=False)

    cmd = "varnishadm -S '%s' %s backend.set_health %s %s" % (secret, args, backend, state)

    (rc, out, err) = module.run_command(cmd)

    if rc:
        return module.fail_json(msg=err, rc=rc, cmd=cmd)
    else:
        return module.exit_json(changed=True)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=False, choices=['sick', 'healthy', 'auto']),
            secret=dict(required=False, default='/etc/varnish/secret', type='str'),
            backend=dict(required=False, default=None, type='str'),
            name=dict(required=False, default=None, type='str'),
        ),
        supports_check_mode=False,
    )

    state = module.params['state']
    secret = module.params['secret']
    backend = module.params['backend']
    name = module.params['name']

    if (state):
        if (not backend):
            module.fail_json(msg="Need to specify backend with the state")

        change_state(module, secret, state, backend, name)

    return module.fail_json(msg="Unknown usage")


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

main()
