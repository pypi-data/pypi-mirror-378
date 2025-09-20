class ProjectDefinition:
    def __init__(self, binary_path = "", makefile_path = ".", make_targets = None, project_name = "", global_timeout = 20):
        self.binary_path = binary_path
        self.makefile_path = makefile_path
        if make_targets is None:
            self.make_targets = ["all"]
        else:
            self.make_targets = make_targets
        self.project_name = project_name
        self.global_timeout = global_timeout

    def to_dict(self):
        return {
            "binary_path" : self.binary_path,
            "makefile_path" : self.makefile_path,
            "make_targets" : self.make_targets,
            "project_name" : self.project_name,
            "global_timeout" : self.global_timeout,
        }