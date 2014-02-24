class CodeExecuter():

    def __init__(self, env, local_variables):
        self.env = env
        self.local_variables = local_variables

        self.code = "# Available variables:"
        for key in local_variables.keys():
            self.code += " " + key
        self.code += "\n"

        self.execution_successful = True

    def update(self):
        while True:
            try:
                exec(self.code, self.local_variables)
                self.execution_successful = True
            except:
                self.env.log('Code could not be executed.')
                self.execution_successful = False
            yield self.env.timeout(self.env.step_size)
