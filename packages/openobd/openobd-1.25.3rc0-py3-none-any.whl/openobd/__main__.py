from openobd.core.arguments import Arguments
from openobd.core.session_builder import SessionBuilder
from openobd.functions.function_launcher import FunctionLauncher

if __name__ == "__main__":

    arguments = Arguments()
    if arguments.is_command_run():
        SessionBuilder(arguments).run()

    elif arguments.is_command_serve():
        FunctionLauncher(arguments).serve()
