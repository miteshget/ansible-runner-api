#!/usr/bin/python

# Copyright: (c) 2024, Mitesh Sharma <mitsharm@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import os
from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.plugins.action import ActionBase

DOCUMENTATION = """
        action: lab_check_fail
        author: Mitesh Sharma <mitsharm@redhat.com>
        version_added: "2.9"
        short_description: Validation fail with custom message and write fail message to file 
        description:
            - Validation fail with custom message and write fail message to file 
        options:
          msg:
            description: Custom message which will be written to file.
            required: True
            type: string
            default: False
"""

EXAMPLES = """
- name: Get stats of hosts file
    ansible.builtin.stat:
    path: /home/rhel/ansible-files/inventory
    register: r_hosts
    
- name: Write msg and fail the task
  when: not r_hosts.stat.exists
  lab_check_fail:
    msg: "Inventory file does not exist"
"""


class ActionModule(ActionBase):

    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(('msg',))
    _requires_connection = False

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        msg = 'Lab failed'
        if self._task.args and 'msg' in self._task.args:
            msg = self._task.args.get('msg')

        # Output Directory Path
        output_dir = task_vars.get('job_info_dir', None)
        if output_dir is None:
            raise AnsibleError("The job_info_dir variable must be defined")
        
        # Output.txt file path
        output_result_path = os.path.join(output_dir, 'output.txt')
        
        try:
            f = open(output_result_path, 'w')
            f.write(msg)
            result['failed'] = True
            result['msg'] = f"{msg} - Message written to log"
            return result
                
        except Exception as e:
                result['failed'] = True
                result['msg'] = f"Failed to write message to log: {e}"
                return result
