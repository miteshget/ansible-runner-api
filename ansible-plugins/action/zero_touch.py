#!/usr/bin/python

# Copyright: (c) 2024, Mitesh Sharma <mitsharm@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import os
from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.plugins.action import ActionBase
from ansible.playbook.conditional import Conditional
from ansible.module_utils.six import string_types
from ansible.module_utils.parsing.convert_bool import boolean

class ActionModule(ActionBase):
    
    _VALID_ARGS = frozenset(('error_msg', 'pass_msg', 'condition'))
    
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        
        if 'condition' not in self._task.args:
            raise AnsibleError('conditional required in "condition" string')
        
        error_msg = None
        pass_msg = None
        e_message = self._task.args.get('error_msg')
        p_message = self._task.args.get('pass_msg')
        
        # Check error and pass, one of them should be used
        if e_message is None and p_message is None:
            raise AnsibleError('At least one of error_msg or pass_msg parameter required')
        
        # Error message validation
        if e_message != None:
            e_message = e_message
            if isinstance(e_message, list):
                if not all(isinstance(x, string_types) for x in e_message):
                    raise AnsibleError('Type of one of the elements in error_msg list is not string type')
            elif not isinstance(e_message, (string_types, list)):
                raise AnsibleError('Incorrect type for error_msg, expected a string or list and got %s' % type(e_message))
            
        # Pass message validation
        if p_message != None:
            p_message = p_message
            if isinstance(p_message, list):
                if not all(isinstance(x, string_types) for x in p_message):
                    raise AnsibleError('Type of one of the elements in pass_msg list is not string type')
            elif not isinstance(p_message, (string_types, list)):
                raise AnsibleError('Incorrect type for pass_msg, expected a string or list and got %s' % type(p_message))
        
        # make sure the 'condition' items are a list
        conditions = self._task.args['condition']
        if not isinstance(conditions, list):
            conditions = [conditions]

         # ----------------------------------------------
        # Output Directory Path
        output_dir = task_vars.get('job_info_dir', None)
        if output_dir is None:
            raise AnsibleError("The job_info_dir variable must be defined")
        
        # Output.txt file path
        output_result_path = os.path.join(output_dir, 'output.txt')
        
        cond = Conditional(loader=self._loader)
        result['_ansible_verbose_always'] = True
        
        for condition in conditions:
            cond.when = [condition]
            test_result = cond.evaluate_conditional(templar=self._templar, all_vars=task_vars)
            try:
                
                if not test_result and e_message != None:
                    f = open(output_result_path, 'w')
                    f.write(e_message)
                    result['failed'] = True
                    result['evaluated_to'] = test_result
                    result['condition'] = condition
                    result['msg'] = f"{e_message} : Message written to log"
                    return result
                
                if test_result and p_message != None:
                    f = open(output_result_path, 'w')
                    f.write(p_message)
                    result['changed'] = True
                    result['evaluated_to'] = test_result
                    result['condition'] = condition
                    result['msg'] = f"{p_message} : Message written to log"
                    return result
                
            except Exception as e:
                    result['failed'] = True
                    result['msg'] = f"Failed to write message to log: {e}"
                    return result

        result['skipped'] = True
        result['msg'] = "Task is skipped due to condition and parameters used"
        return result
