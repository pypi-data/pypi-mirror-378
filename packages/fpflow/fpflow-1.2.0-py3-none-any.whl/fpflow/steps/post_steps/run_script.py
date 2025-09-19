#region modules
from typing import List 
from fpflow.io.read_write import str_2_f
import os 
from fpflow.steps.step import Step 
import jmespath 
#endregion

#region variables
#endregion

#region functions
#endregion

#region classes
class RunScriptStep(Step):
    @property
    def file_contents(self) -> dict:

        return {
            'run.sh': f'''#!/usr/bin/env python3

from fpflow.managers.manager import Manager

manager = Manager.from_inputyaml('./input.yaml')
manager.run()
''',
            'rund.sh': f'''#!/bin/bash

./run.sh &> run.out &
'''
        }
    
    @property
    def job_scripts(self) -> List[str]:
        return []

    @property
    def save_inodes(self) -> List[str]:
        return []
    
    @property
    def remove_inodes(self) -> List[str]:
        return ['./run.sh', 'rund.sh']
#endregion