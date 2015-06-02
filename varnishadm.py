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
short_description: Control varnish
description:
  - Control varnish
options:
  secret:
    required: false
    default: /etc/varnish/secret
    aliases: []
  backend:
    required: false
    default: null
    aliases: []
  state:
    required: false
    default: null
    choices: ['auto', 'healthy', 'sick']
    aliases: []
'''

EXAMPLES = '''
# Disable a backend from varnish

- varnishadm:
    backend=web_backend_broken
    state=sick

# Enable a backend from varnish

- varnishadm:
    backend=web_backend_working
    state=auto
'''


def get_state(module, secret, backend):
    cmd = "varnishadm -S '%s' backend.list %s" % (secret, backend)

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


def change_state(module, secret, state, backend):

    current_state = get_state(module, secret, backend)

    if state == current_state:
        return module.exit_json(changed=False)

    cmd = "varnishadm -S '%s' backend.set_health %s %s" % (secret, backend, state)

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
        ),
        supports_check_mode=False,
    )

    state = module.params['state']
    secret = module.params['secret']
    backend = module.params['backend']

    if (state):
        if (not backend):
            module.fail_json(msg="Need to specify backend with the state")

        change_state(module, secret, state, backend)

    return module.fail_json(msg="Unknown usage")


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

main()
