#!/usr/bin/python

# Copyright: (c) 2024, Mitesh Sharma <mitsharm@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}

        result = super(ActionModule, self).run(tmp, task_vars)

        # Output Directory Path
        output_dir = task_vars.get('job_info_dir', None)
        if output_dir is None:
            raise AnsibleError("The job_info_dir variable must be defined")
        
        # Output.txt file path
        output_result_path = os.path.join(output_dir, 'output.txt')

        # Error message
        message = self._task.args.get('error_msg', None)
        if message is None:
            raise AnsibleError("You must provide a error_msg")

        # Write the message to the file
        try:
            with open(output_result_path, 'w') as f:
                f.write(message)
            result['changed'] = True
            result['msg'] = f"Message written to log"
        except Exception as e:
            result['failed'] = True
            result['msg'] = f"Failed to write message to log: {e}"

        return result
