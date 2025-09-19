import logging
import os
import typing

from openobd.core.openobd import OpenOBD
from openobd.core.function_broker import OpenOBDFunctionBroker
from openobd.core.grpc_factory import GrpcFactory, NetworkGrpcFactory
from openobd.core.session import OpenOBDSession
from openobd.core.arguments import Arguments
from openobd_protocol.SessionController.Messages.SessionController_pb2 import SessionInfo
from openobd.functions.composition import OpenOBDComposition
from openobd.functions.function import OpenOBDFunction
from openobd.functions.bypass_function_broker import NetworkGrpcFactoryBypassingFunctionBroker
from openobd.functions.function_executor import FunctionExecutor


class SessionBuilder:

    bypass_function_broker = False
    openobd_session = None
    function_broker = None
    arguments = None

    def __init__(self, arguments: Arguments = None, function_executor: FunctionExecutor = None):
        self.arguments = arguments if arguments else Arguments()
        self.bypass_function_broker = self.arguments.bypass_function_broker()
        self.function_executor = FunctionExecutor(self.arguments) if function_executor is None else function_executor
        self.function_executor.load_modules(self._get_default_broker())

    def _create_grpc_factory(self, grpc_host, grpc_port=443) -> GrpcFactory:
        if self.bypass_function_broker:
            '''Return gRPC network factory that is bypassing the function broker calls'''
            return NetworkGrpcFactoryBypassingFunctionBroker(arguments=self.arguments,
                                                             executor=self.function_executor,
                                                             grpc_host=grpc_host,
                                                             grpc_port=grpc_port)
        else:
            '''Return regular gRPC network factory'''
            return NetworkGrpcFactory(grpc_host=grpc_host, grpc_port=grpc_port)

    def _get_default_broker(self):
        return OpenOBDFunctionBroker(self.arguments,
                              grpc_factory=self._create_grpc_factory(
                                  grpc_host=self.arguments.get_grpc_host(),
                                  grpc_port=self.arguments.get_grpc_port())
                              )

    def _create_session(self) -> OpenOBDSession:

        if self.arguments.get_ticket_id(required=False) is not None:
            return OpenOBD(self.arguments).start_session_on_ticket(ticket_id=self.arguments.get_ticket_id())

        elif self.arguments.get_connector_id(required=False) is not None:
            return OpenOBD(self.arguments).start_session_on_connector(connector_id=self.arguments.get_connector_id())

        elif self.arguments.get_token(required=False) is not None:
            session_info = SessionInfo("", "", "", self.arguments.get_grpc_host(), self.arguments.get_token())
            return OpenOBDSession(session_info)

        raise AssertionError("Please provide a ticket id (--ticket-id), connector id (--connector-id) or a token (--token) to initialize the session.")

    def _create(self):
        openobd_session = self._create_session()
        grpc_factory = self._create_grpc_factory(openobd_session.session_info.grpc_endpoint)
        self.openobd_session = OpenOBDSession(openobd_session.session_info, grpc_factory=grpc_factory)
        self.function_broker = OpenOBDFunctionBroker(self.arguments, grpc_factory=grpc_factory)

    def function(self) -> OpenOBDFunction:
        self._create()
        return OpenOBDFunction(self.openobd_session, self.function_broker)

    def composition(self) -> OpenOBDComposition:
        self._create()
        return OpenOBDComposition(self.openobd_session, self.function_broker)

    def run(self, function: typing.Type[OpenOBDFunction] = None):
        '''Check if relative script path has been set, convert to module path'''
        if function is None:
            file = self._script_file_to_module_path(self.arguments.get_file())
            if file is not None and self.function_executor is not None:
                '''
                Use the default broker instance using the provided arguments.
                This broker endpoint does not depend on the session info and therefore can be created
                before the openOBD session is created. Saving time in the case a function initialization fails.
                '''
                function = self.function_executor.load_function(file, self._get_default_broker())

        if function is None:
            logging.warning("Could not load function! No file reference given.")
            return

        '''First create the session and then run the function'''
        self._create()
        self.function_executor.run_function(function(self.openobd_session, self.function_broker))

    @staticmethod
    def _script_file_to_module_path(script):
        if script is None:
            return None
        return script.replace(os.sep, '.').replace('.py', '').lstrip(".")
