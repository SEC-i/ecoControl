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

        self.execution_successful = True
        self.snippet_folder = "snippets"

    def update(self):
        while True:
            try:
                exec(self.code, self.local_variables)
                self.execution_successful = True
            except:
                if self.env.verbose and self.env.now % self.env.granularity == 0:
                    traceback.print_exc()
                self.execution_successful = False

            yield self.env.timeout(self.env.step_size)

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
        if os.path.splitext(snippet)[1] == ".py":
            with open(self.snippet_folder + "/" + snippet, "w") as snippet_file:
                snippet_file.write(code)
            return True

        return False
