import os
import logging

from server.systems import BaseSystem

logger = logging.getLogger('simulation')
SNIPPET_FOLDER = 'snippets/'

class CodeExecuter(BaseSystem):

    def __init__(self, system_id, env):
        
        super(CodeExecuter, self).__init__(system_id, env)

        self.local_names = None
        self.local_references = None

        self.execution_successful = True

    def find_dependent_devices_in(self, system_list):
        self.register_local_variables(system_list)

    def connected(self):
        return not (self.local_names is None and self.local_references is None)

    def register_local_variables(self, system_list):
        self.local_names = ['device_%s' % system.id for system in system_list]
        self.local_references = system_list

        # initialize code with names of local variables
        self.code = "#"
        for name in self.local_names:
            self.code += " " + name
        self.code += "\n"

        self.create_function(self.code)

    def create_function(self, code):
        self.code = code

        lines = []
        lines.append("def user_function(%s):" %
                     (",".join(self.local_names)))

        for line in self.code.split("\n"):
            lines.append("\t" + line)
        lines.append("\tpass")  # make sure function is not empty

        source = "\n".join(lines)
        namespace = {}
        exec source in namespace  # execute code in namespace

        self._user_function = namespace['user_function']

    def step(self):
        try:
            self._user_function(*self.local_references)
            self.execution_successful = True
        except:
            logger.error("CodeExecuter: Could not execute user code")
            self.execution_successful = False
