import sys

from openobd.core.exceptions import OpenOBDException
from openobd.core.session import OpenOBDSession
from openobd.functions.function import OpenOBDFunction
from openobd.core.arguments import ConnectionArguments
from openobd_protocol.FunctionBroker.Messages.FunctionBroker_pb2 import FunctionUpdate, FunctionUpdateType, FunctionUpdateResponse, FunctionCall

from openobd.core.function_broker import OpenOBDFunctionBroker
from openobd.core.stream_handler import StreamHandler
from openobd.core.exceptions import OpenOBDStreamStoppedException

from openobd.functions.function_executor import FunctionExecutor

import threading
import logging

class FunctionLauncher:

    def __init__(self, connection_arguments: ConnectionArguments, function_executor: FunctionExecutor):
        """
        Handles communication with the function broker about functions that are available for execution.

        :param connection_arguments: Function launcher arguments
        :param function_executor: Functions that can be executed by the launcher
        """
        self.function_broker = OpenOBDFunctionBroker(connection_arguments)
        self.function_executor = function_executor
        self.function_executor.load_modules(self.function_broker)
        self.stream_handler = None
        self.process_function_updates_thread = None
        self.threads = []

    def serve(self):
        """
        Starts serving functions to the function broker
        """
        function_registrations = self.function_executor.get_function_registrations()
        if len(function_registrations) == 0:
            logging.critical("No functions to serve!")
            logging.critical("A function should be defined according to the following pattern:\n" + '''
class ECUReset(OpenOBDFunction):

    version = "v0.1"
    name = "ECU Reset"
    description = "Reset ECU"

    def run(self):
        logging.info("Reset ECU")                        

            ''')
            sys.exit(1)

        '''Establish function update stream'''
        self.stream_handler = StreamHandler(self.function_broker.open_function_stream, outgoing_stream=True)

        for function_registration in function_registrations:
            self.stream_handler.send(FunctionUpdate(type=FunctionUpdateType.FUNCTION_UPDATE_TYPE_REQUEST, function_registration=function_registration))

        self.process_function_updates_thread = threading.Thread(target=self._process_function_updates,
                                                                name="Process function updates",
                                                                daemon=True)
        self.process_function_updates_thread.start()

        try:
            self.process_function_updates_thread.join()
        except KeyboardInterrupt as e:
            self._interrupt_launcher()

    def _process_function_updates(self):
        try:
            while True:
                function_update = self.stream_handler.receive()
                self._function_update(function_update)
        except OpenOBDStreamStoppedException:
            pass
        except OpenOBDException as e:
            logging.error(f"Stopped processing function updates due to an exception.")
            logging.error(e)
        finally:
            self.stream_handler.stop_stream()

    def _interrupt_launcher(self):
        for (function_reference, function_thread) in self.threads:
            if function_reference.__is_active__():
                logging.info(f"Stopping {function_reference}...")
                function_reference.interrupt()

        self.stream_handler.stop_stream()

    def _function_update(self, function_update: FunctionUpdate):
        if function_update.type == FunctionUpdateType.FUNCTION_UPDATE_TYPE_REQUEST:
            if function_update.HasField('function_call'):
                call = function_update.function_call
                logging.info(f"Received a function call for function id [{function_update.function_call.id}]")

                try:
                    # Test if function is available
                    self._available(call)

                    function_reference = self._get_function_instance(call)

                    function_thread = threading.Thread(target=self._call,
                                                     name=f"Function [{function_update.function_call.id}]",
                                                     args=[function_reference],
                                                     daemon=True)

                    self.threads.append((function_reference, function_thread))
                    function_thread.start()

                    # Immediately report back that we successfully received the function call and started the function
                    self.stream_handler.send(
                        FunctionUpdate(
                            type=FunctionUpdateType.FUNCTION_UPDATE_TYPE_RESPONSE,
                            function_call=function_update.function_call,
                            response=FunctionUpdateResponse.FUNCTION_UPDATE_SUCCESS
                        ))

                except Exception as e:
                    self.stream_handler.send(
                        FunctionUpdate(
                            type=FunctionUpdateType.FUNCTION_UPDATE_TYPE_RESPONSE,
                            function_call=function_update.function_call,
                            response=FunctionUpdateResponse.FUNCTION_UPDATE_FAILED,
                            response_description=str(e)
                        ))

            elif function_update.HasField('function_registration'):
                raise OpenOBDException("We do not expect a 'function_registration' as request from the function broker.")

            elif function_update.HasField('function_broker_token'):
                logging.info(f"Function update stream is still open")
                logging.debug(f"Received a new function broker token")

            elif function_update.HasField('function_broker_reconnect'):
                raise OpenOBDException("Received a reconnect request from the function broker. We do not support it yet.")

            else:
                raise OpenOBDException("Unsupported request from the function broker")

        elif function_update.type == FunctionUpdateType.FUNCTION_UPDATE_TYPE_RESPONSE:
            logging.debug("Received function update response...")

            if function_update.HasField('function_registration') and function_update.HasField('response'):
                logging.debug(f"Received a function update for function id [{function_update.function_registration.details.id}]")

                if function_update.response == FunctionUpdateResponse.FUNCTION_UPDATE_SUCCESS:
                    logging.info(f"Function [{function_update.function_registration.details.id}] registration was successful")
                elif function_update.response == FunctionUpdateResponse.FUNCTION_UPDATE_UNAUTHORIZED:
                    logging.warning(f"Function [{function_update.function_registration.details.id}] signature check failed!")
                else:
                    logging.warning(f"Function [{function_update.function_registration.details.id}] registration failed!")


    def _get_function_instance(self, call: FunctionCall):
        return self.function_executor.instantiate_function_from_uuid(id=call.id,
                                                                     openobd_session=OpenOBDSession(call.session_info),
                                                                     function_broker=self.function_broker)

    def _call(self, function: OpenOBDFunction):
        self.function_executor.run_function(function)

    def _available(self, call: FunctionCall):
        self.function_executor.instantiate_function_from_uuid(id=call.id,
                                                              openobd_session=OpenOBDSession(call.session_info),
                                                              function_broker=self.function_broker,
                                                              dry_run=True)




