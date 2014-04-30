import traceback
import os

from helpers import BaseSystem

class CodeExecuter(BaseSystem):

    def __init__(self, system_id, env):
        
        super(CodeExecuter, self).__init__(system_id, env)

        self.local_names = None
        self.local_references = None

        self.execution_successful = True

        parent_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.snippet_folder = parent_directory + "/server/data/snippets"

    def register_local_variables(self, local_variables):
        self.local_names = ['device_%s' % i for i in range(len(local_variables))]
        self.local_references = local_variables

        # initialize code with names of local variables
        self.code = "#"
        for name in self.local_names:
            self.code += " " + name
        self.code += "\n"

        self.create_function(self.code)

    def find_dependent_devices_in(self, system_list):
        self.register_local_variables(system_list)

    def connected(self):
        return not (self.local_names is None and self.local_references is None)

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
            traceback.print_exc()
            self.execution_successful = False

    def snippets_list(self):
        output = []
        for filename in os.listdir(self.snippet_folder):
            if os.path.splitext(filename)[1] == ".py":
                output.append(filename)
        return output

    def get_snippet_code(self, snippet):
        if snippet in self.snippets_list():
            with open(self.snippet_folder + "/" + snippet, "r") as snippet_file:
                return snippet_file.read()
        return ""

    def save_snippet(self, snippet, code):
        if os.path.splitext(snippet)[1] == ".py" and code != "":
            with open(self.snippet_folder + "/" + snippet, "w") as snippet_file:
                snippet_file.write(code)
            return True

        return False
