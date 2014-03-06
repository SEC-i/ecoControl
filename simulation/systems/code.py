import traceback
import os


class CodeExecuter():

    def __init__(self, env, local_variables):
        self.env = env
        self.local_variables = local_variables

        self.code = "#"
        for key in local_variables.keys():
            self.code += " " + key
        self.code += "\n"
        self.create_function(self.code)
        self.execution_successful = True

        parent_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.snippet_folder = parent_directory + "/snippets"

    def create_function(self, code):
        self.code = code

        lines = []
        lines.append("def user_function(%s):" %
                     (",".join(self.local_variables.keys())))

        for line in self.code.split("\n"):
            lines.append("\t" + line)
        lines.append("\tpass")  # make sure function is not empty

        source = "\n".join(lines)
        namespace = {}
        exec source in namespace  # execute code in namespace

        self._user_function = namespace['user_function']

    def step(self):
        try:
            self._user_function(*self.local_variables.values())
            self.execution_successful = True
        except:
            if self.env.now % self.env.measurement_interval == 0:
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
