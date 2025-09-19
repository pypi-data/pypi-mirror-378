import importlib
import pkgutil
import inspect
import logging
import typing

from openobd_protocol.FunctionBroker.Messages.FunctionBroker_pb2 import FunctionRegistration
from openobd.core.exceptions import OpenOBDException
from openobd.core.function_broker import OpenOBDFunctionBroker
from openobd.core.arguments import Arguments
from openobd.functions.composition import OpenOBDComposition
from openobd.functions.function import OpenOBDFunction


class FunctionExecutor:

    def __init__(self, arguments: Arguments):
        self.arguments = arguments
        self.functions = {}

    def load_modules(self, function_broker: OpenOBDFunctionBroker):
        if self.arguments.unique_function_ids():
            logging.info("[UNIQUE] Generating fresh function id's for all loaded functions")
        modules = self.arguments.get_modules()
        if modules is not None:
            for module in modules:
                mod = importlib.import_module(module)
                for loader, module_name, is_pkg in pkgutil.iter_modules(mod.__path__):
                    self.load_function(f"{mod.__name__}.{module_name}", function_broker)

    def load_function(self, module: str, function_broker: OpenOBDFunctionBroker) -> typing.Type[OpenOBDFunction]:
            logging.info(f"Loading: [{module}]")
            function_reference = None
            unique_function_ids = self.arguments.unique_function_ids()
            function_name_prefix = self.arguments.get_prefix()

            try:
                mod = importlib.import_module(module)
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    # Only include classes defined in this module (not imported ones)
                    if obj.__module__ == module:
                        cls = getattr(mod, name)

                        '''Check for fingerprint of openOBD function or composition'''
                        if hasattr(cls, 'id') and hasattr(cls, 'signature') and hasattr(cls, 'name'):
                            if unique_function_ids:
                                '''Ensure fresh registration'''
                                setattr(cls, 'id', '')
                                setattr(cls, 'signature', '')

                            '''Prefix adjustment is only possible when we now that it is really a function or composition'''
                            if unique_function_ids and function_name_prefix:
                                setattr(cls, 'name', f"[{function_name_prefix}] {getattr(cls, 'name')}")

                            # Initialize the function class (Either a function or a composition)
                            try:
                                function = cls(function_broker=function_broker)
                            except TypeError:
                                logging.debug(f"Not a function or composition class: {name}")
                                continue

                            if isinstance(function, OpenOBDComposition) or isinstance(function, OpenOBDFunction):
                                logging.info(f"Initializing function: [{function.id}] {function.name}")

                                '''Initialize the class in memory with the registered values'''
                                setattr(cls, 'id', function.id)
                                setattr(cls, 'signature', function.signature)
                            else:
                                '''Other classes might be helper classes, we do not need to initialize them'''
                                continue

                            function_registration = function.get_function_registration()  # type: FunctionRegistration
                            self.functions[function_registration.details.id] = (function_registration, module,
                                                                                name)
                        else:
                            '''When the expected fingerprint is not present, we do not initialize'''
                            continue

                        '''
                        First function found in a file is considered the 'main' function
                        General advice is to just define one function per file (to prevent any misunderstanding)
                        '''
                        if function_reference is None:
                            function_reference = cls
            except (ModuleNotFoundError, ValueError) as e:
                logging.critical(f"The module could not be found {module}: {e}")
            except Exception as e:
                logging.error(f"Problem loading functions from module {module}: {e}")
                raise e

            return function_reference

    def get_function_registrations(self):
        function_registrations = []
        for function_id in self.functions.keys():
            function_registrations.append(self.functions[function_id][0])
        return function_registrations

    def instantiate_function_from_uuid(self, id, openobd_session, function_broker=None, dry_run=False):
        if id not in self.functions:
            raise OpenOBDException(f"Function {id} unknown!")

        (function_registration, full_module_name, name) = self.functions[id]
        module = importlib.import_module(full_module_name)

        if dry_run:
            return

        # Instantiate function class
        cls = getattr(module, name)

        logging.debug(f"Instantiate function [{id}]: {name}")
        return cls(openobd_session=openobd_session, function_broker=function_broker)

    @staticmethod
    def run_function(function: OpenOBDFunction):
        with function as f:
            f.run()

    def __str__(self):
        function_list = " Functions ".center(80, "-") + "\n"
        if len(self.functions) == 0:
            function_list += " " * 10 + "<none>\n"
        else:
            for function_id in self.functions.keys():
                function_registration = self.functions[function_id][0]
                function_list += "\n"
                function_list += f"             Id: {function_registration.details.id}\n"
                function_list += f"      Signature: {function_registration.signature}\n"
                function_list += f"           Name: {function_registration.details.name}\n"
                function_list += f"        Version: {function_registration.details.version}\n"
                function_list += f"    Description: {function_registration.details.description}\n"
            function_list += "\n"
        function_list += "-" * 80
        return function_list

