import argparse
import os
import re
import sys
import textwrap
import logging
from colorlog import ColoredFormatter
from typing import Literal

'''The openOBD environment variables that can be set'''
arg = {
    "client_id":        "OPENOBD_PARTNER_CLIENT_ID",
    "client_secret":    "OPENOBD_PARTNER_CLIENT_SECRET",
    "cluster_id":       "OPENOBD_CLUSTER_ID",
    "grpc_host":        "OPENOBD_GRPC_HOST",
    "grpc_port":        "OPENOBD_GRPC_PORT",
    "token":            "OPENOBD_TOKEN",
    "ticket_id":        "OPENOBD_TICKET_ID",
    "connector_id":     "OPENOBD_CONNECTOR_ID",
    "log_level":        "OPENOBD_LOG_LEVEL",
}

_program = 'python -m openobd'

def _env_help(arg_key):
    return f"\n - Environment variable: [{arg[arg_key]}]\n "

def _get_env_var(env_key, default=None):
    return os.environ.get(env_key, default)

def _filter_prefix(prefix):
    if prefix is None:
        return None
    '''Only alphanumeric'''
    filtered = re.sub(r'[^a-zA-Z0-9]', '', prefix)
    '''Max 4 chars'''
    return filtered[:4]


class Arguments:

    _args = None
    _constructor_args = None

    def __init__(self,
                 command: Literal['run', 'serve'] = 'run',

                 # openOBD gRPC server credentials
                 client_id: str = None,
                 client_secret: str = None,
                 cluster_id: str = None,
                 grpc_host: str = None,
                 grpc_port: int = None,

                 # Load the following modules with openOBD scripts
                 modules: list[str] = None,
                 unique: bool = None,
                 prefix: str = None,

                 # Specific 'run' arguments
                 file: str = None,
                 bypass_function_broker: bool = None,
                 ticket: str = None,
                 connector: str = None,
                 token: str = None,
                 ):
        """
        Initialize arguments according to the following priorities:
         - keyword argument, if not available we use:
         - command line argument, if not available we use:
         - environment variable

        :param command: Either 'run' or 'serve'.
                        'run': Runs an openOBD script
                        'serve': Serves openOBD scripts to the function broker
        :param client_id: Client id of the Jifeline Partner (Partner API credentials)
        :param client_secret: Client secret of the Jifeline Partner (Partner API credentials)
        :param cluster_id: Server cluster ('001' for Europe, '002' for USA)
        :param grpc_host: gRPC host of the openOBD service (default is 'grpc.openobd.com')
        :param grpc_port: gRPC port of the openOBD service (default is 443)
        :param modules: List of modules (paths to openOBD scripts) that need to be initialized
        :param unique: Generate a fresh openOBD script id every time we initialize the scripts (Development)
        :param prefix: Prefix the script names with a short string (max 4 characters) (Development)
        :param file: The file containing an openOBD script or composition that needs to be run
        :param bypass_function_broker: Calls to other openOBD functions are not routed through the function broker when
            they are locally known.
        :param ticket: Create an openOBD session based on a ticket
        :param connector: Create an openOBD session based on a connector (Development)
        :param token: Create an openOBD session based in an authentication token
        """
        self._constructor_args = []
        command = self._set_command(command)

        self._set_constructor_arg('--client-id', client_id)
        self._set_constructor_arg('--client-secret', client_secret)
        self._set_constructor_arg('--cluster-id', cluster_id)
        self._set_constructor_arg('--host', grpc_host)
        self._set_constructor_arg('--port', grpc_port)

        self._set_constructor_arg('--modules', modules)
        self._set_constructor_arg('--unique', unique)
        self._set_constructor_arg('--prefix', prefix)

        self._set_file(command, file)
        self._set_constructor_arg('--ticket', ticket)
        self._set_constructor_arg('--connector', connector)
        self._set_constructor_arg('--token', token)
        self._set_constructor_arg('--bypass-function-broker', bypass_function_broker)

        parser = _get_openobd_parser()
        combined_args = sys.argv[1:] + self._constructor_args
        self._args = parser.parse_args(combined_args)

        self._set_log_level()

    '''Make host adjustable for custom session builder configurations'''
    def set_grpc_host(self, host, port=443):
        self._args.grpc_host = host
        self._args.grpc_port = port

    '''Set values when defined in constructor (considering if they override any cli or env vars)'''
    def _set_constructor_arg(self, argument, value, override=True):
        if value is None:
            return
        if argument in sys.argv and not override:
            return

        self._constructor_args.append(argument)

        '''When the argument is a flag on the commandline we are done, just return'''
        if isinstance(value, bool):
            return

        '''When the argument is a list of values'''
        if isinstance(value, list):
            for val in value:
                self._constructor_args.append(val)
            return

        self._constructor_args.append(value)

    def _set_file(self, command: str, file_path: str = None):
        if command != 'run':
            return
        if file_path is None:
            script_path = os.path.abspath(sys.argv[0])
            cwd = os.getcwd()
            file_path = os.path.relpath(script_path, cwd)
        self._set_constructor_arg('--file', file_path, False)

    @staticmethod
    def _set_command(command):
        # Inject default command if none is provided
        if len(sys.argv) == 1:
            sys.argv.insert(1, command)
        return sys.argv[1]

    def _set_log_level(self):
        log_level = self._get_argument('log_level')
        if log_level is None:
            log_level = "INFO"
        if not isinstance(log_level, str):
            log_level = "INFO"

        handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(threadName)s: %(white)s%(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        handler.setFormatter(formatter)
        logging.basicConfig(handlers=[handler], level=log_level.upper())

    def _get_argument(self, argument, required=False):
        value = getattr(self._args, argument, None)
        if value is not None:
            return value

        if required:
            message = f"Argument '{argument}' could not be found. Pass it explicitly using '--{argument.replace('_', '-')}', or ensure it is available as an environment variable named '{arg[argument]}'."
            logging.error(message)
            raise AssertionError(message)

        return None

    def _get_boolean_argument(self, argument, required=False):
        result = self._get_argument(argument, required)
        if result is None:
            return False
        return result

    def is_command_run(self) -> bool:
        if self._args.command == "run":
            return True
        return False

    def is_command_serve(self) -> bool:
        if self._args.command == "serve":
            return True
        return False

    def get_client_id(self, required=True):
        return self._get_argument('client_id', required)

    def get_client_secret(self, required=True):
        return self._get_argument('client_secret', required)

    def get_cluster_id(self, required=True):
        return self._get_argument('cluster_id', required)

    def get_grpc_host(self, required=True):
        return self._get_argument('grpc_host', required)

    def get_grpc_port(self, required=True):
        return self._get_argument('grpc_port', required)

    def get_token(self, required=True):
        return self._get_argument('token', required)

    def get_ticket_id(self, required=True):
        return self._get_argument('ticket_id', required)

    def get_connector_id(self, required=True):
        return self._get_argument('connector_id', required)

    def bypass_function_broker(self):
        return self._get_boolean_argument('bypass_function_broker')

    def get_modules(self):
        return self._args.modules

    def unique_function_ids(self):
        return self._args.unique

    def get_prefix(self):
        if hasattr(self._args, 'prefix'):
            if self._args.prefix:
                return _filter_prefix(self._args.prefix).upper()
        return None

    def get_file(self):
        return self._args.file

    def __str__(self):
        arguments = ""
        for key in arg:
            value = self._get_argument(key, False)
            if key == "client_secret" and value is not None:
                value = "***"
            arguments += f"{key}: {value}\n"
        return arguments

def _get_openobd_parser():
    parser = argparse.ArgumentParser(add_help=False,
                                     prog=_program,
                                     description="Run openOBD on the remote diagnostics network of Jifeline Networks",
                                     epilog=f"For detailed help for a subcommand, run \n {os.path.basename(__file__)} <command> -h")

    subparsers = parser.add_subparsers(help='Command')
    subparsers.required = False
    subparsers.dest = 'command'

    _add_command_run(subparsers)
    _add_command_serve(subparsers)

    return parser

'''Run command'''
def _add_command_run(subparsers):
    parser_cmd_run = subparsers.add_parser('run',
                                           help='Run a openOBD function or composition',
                                           formatter_class=argparse.RawTextHelpFormatter,
                                           )

    description = textwrap.dedent('''\
        
        [ Run options ]
        ''')

    parent_group = parser_cmd_run.add_argument_group(description=description)
    parent_group.add_argument('--file', metavar='<filename>', dest="file", help='The path to a Python file. The file should contain a class based on the OpenOBDFunction or OpenOBDComposition class.',required=True)
    _add_modules_arguments(parent_group)
    parent_group.add_argument('--bypass-function-broker', action='store_true', dest="bypass_function_broker", help='Bypass the function broker for functions that are locally available (loaded with --modules flag).')

    description=textwrap.dedent('''\
        
        [ Session options ]
        
          An openOBD session can be instantiated by
                 <ticket id>,
            OR   <connector id> (for development),
            OR   <token>.''')

    _add_session_argument_group(parser_cmd_run, description)

    description=textwrap.dedent('''\
        
        [ openOBD server settings ]
        
          Required when session needs to be created or subsequent function calls
          need to be made (e.g. through the function broker when hosting functions).''')
    _add_grpc_argument_group(parser_cmd_run, description)

    _log_level_help(parser_cmd_run)

    description = textwrap.dedent('''\

        -------------------------------------------------------------------------------
        
        Example:
        
            {program} run --file example_functions/test.py --modules example_functions
            
            {program} run --file example_functions/test.py --ticket 8832507 --modules example_functions --bypass-function-broker
            
        '''.format(program=_program))

    parser_cmd_run.add_argument_group(description=description)


'''Serve command'''
def _add_command_serve(subparsers):
    '''Serve'''
    parser_cmd_serve = subparsers.add_parser('serve',
                                             help='Host openOBD functions or compositions on the Jifeline network.',
                                             formatter_class=argparse.RawTextHelpFormatter
                                             )

    _add_modules_arguments(parser_cmd_serve, add_prefix_option=True)

    description = textwrap.dedent('''\

        [ openOBD server settings ]
        
          Required to authenticate to the function broker.''')
    _add_grpc_argument_group(parser_cmd_serve, description)

    _log_level_help(parser_cmd_serve)

    description = textwrap.dedent('''\

        -------------------------------------------------------------------------------

        Example:
        
            {program} serve --modules example_functions
        '''.format(program=_program))

    parser_cmd_serve.add_argument_group(description=description)


def _add_grpc_argument_group(parser, description):
    group = parser.add_argument_group(description=description)
    group.add_argument('--host', metavar='<grpc_host>', type=str,
                       dest="grpc_host",
                       default=_get_env_var(arg['grpc_host'], 'grpc.openobd.com'),
                       help=f"The gRPC host of the openOBD service (default is 'grpc.openobd.com'){_env_help('grpc_host')}")

    group.add_argument('--port', metavar='<grpc_port>', type=int,
                       dest="grpc_port",
                       default=_get_env_var(arg['grpc_port'], "443"),
                       help=f"The gRPC port of the openOBD service (default is 443){_env_help('grpc_port')}")

    group.add_argument('--cluster-id', metavar='<cluster_id>', type=str,
                       dest="cluster_id",
                       default=_get_env_var(arg['cluster_id'], "001"),
                       help=f"The cluster id of the Jifeline partner (001=EU, 002=USA, default is '001'){_env_help('cluster_id')}")

    group.add_argument('--client-id', metavar='<client_id>', type=str,
                       dest="client_id",
                       default=_get_env_var(arg['client_id']),
                       help=f"The client id of the Jifeline partner.{_env_help('client_id')}")

    group.add_argument('--client-secret', metavar='<client_secret>', type=str,
                       dest="client_secret",
                       default=_get_env_var(arg['client_secret']),
                       help=f"The client secret of the Jifeline partner.{_env_help('client_secret')}")

    return parser

def _add_session_argument_group(parser, description):
    group = parser.add_argument_group(description=description)
    group.add_argument('--ticket', metavar='<ticket id>', type=str,
                       dest='ticket_id',
                       default=_get_env_var(arg['ticket_id']),
                       help=f"Create an openOBD session on a specific ticket{_env_help('ticket_id')}")

    group.add_argument('--connector', metavar='<connector id>', type=str,
                       dest='connector_id',
                       default=_get_env_var(arg['connector_id']),
                       help=f"Create an openOBD session using a specific connector (only for development){_env_help('connector_id')}")

    group.add_argument('--token', metavar='<token>', type=str,
                       dest='token',
                       default=_get_env_var(arg['token']),
                       help=f"Authentication token of an available openOBD session{_env_help('token')}")

    return parser

def _add_modules_arguments(parser, add_prefix_option=False):
    parser.add_argument('--modules', dest="modules", nargs='+', metavar='<module>', default=None, help="Path to modules containing openOBD scripts (multiple paths can be provided)", required=False)
    parser.add_argument('--unique', action='store_true', dest="unique",
                              help='Generate fresh function ids for all functions that are loaded. Guarantees unique function registrations at the function broker.')
    if not add_prefix_option:
        return

    parser.add_argument('--prefix', metavar='<prefix>', dest="prefix", default=None, help='Prepend the name of every function with this prefix (max 4 alphanumeric characters and only in combination with --unique).',required=False)


def _log_level_help(parser):
    log_help_group = parser.add_argument_group(description='[ Set log level ]')

    log_help = textwrap.dedent('''\
        Possible log levels:
         [CRITICAL, ERROR, WARNING, INFO, DEBUG] (Default is 'INFO')''')

    log_help_group.add_argument('--log-level', metavar='<log level>', type=str,
                       dest='log_level',
                       default=_get_env_var(arg['log_level']),
                       help=f"{log_help}{_env_help('log_level')}")


