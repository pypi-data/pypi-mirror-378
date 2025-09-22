###
# Copyright 2016-2025 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
"""
This is the main module for Redfish Utility which handles all of the CLI and UI interfaces
"""

# ---------Imports---------
# -*- coding: utf-8 -*-

import collections
import copy
import errno
import glob
import logging
import os
import re
import shlex
import sys
import traceback
import warnings
import importlib
import ctypes
from argparse import ArgumentParser, RawTextHelpFormatter
from builtins import open, str, super

import six
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle
from six.moves import input

import redfish.hpilo
import redfish.rest.v1
import redfish.ris


try:
    import cliutils
    import versioning
    import extensions
    from config.rdmc_config import RdmcConfig
    from rdmc_helper import HARDCODEDLIST
    from rdmc_base_classes import RdmcCommandBase, RdmcOptionParser
except ModuleNotFoundError:
    from ilorest import cliutils
    from ilorest import versioning
    from ilorest import extensions
    from ilorest.config.rdmc_config import RdmcConfig
    from ilorest.rdmc_helper import HARDCODEDLIST
    from ilorest.rdmc_base_classes import RdmcCommandBase, RdmcOptionParser

try:
    from rdmc_helper import (
        LOGGER,
        LOUT,
        UI,
        AlreadyCloudConnectedError,
        BirthcertParseError,
        BootOrderMissingEntriesError,
        CloudConnectFailedError,
        CloudConnectTimeoutError,
        CommandNotEnabledError,
        ConfigurationFileError,
        DeviceDiscoveryInProgress,
        DownloadError,
        Encryption,
        FailureDuringCommitError,
        FirmwareUpdateError,
        IloLicenseError,
        IncompatableServerTypeError,
        IncompatibleiLOVersionError,
        InfoMissingEntriesError,
        InvalidCListFileError,
        InvalidCommandLineError,
        InvalidCommandLineErrorOPTS,
        InvalidFileFormattingError,
        InvalidFileInputError,
        InvalidKeyError,
        InvalidMSCfileInputError,
        InvalidOrNothingChangedSettingsError,
        InvalidPasswordLengthError,
        MultipleServerConfigError,
        NicMissingOrConfigurationError,
        NoChangesFoundOrMadeError,
        NoContentsFoundForOperationError,
        NoCurrentSessionEstablished,
        NoDifferencesFoundError,
        PartitionMoutingError,
        PathUnavailableError,
        ProxyConfigFailedError,
        RdmcError,
        ResourceExists,
        ReturnCodes,
        StandardBlobErrorHandler,
        TabAndHistoryCompletionClass,
        TaskQueueError,
        TfaEnablePreRequisiteError,
        TimeOutError,
        UnableToDecodeError,
        UnabletoFindDriveError,
        UploadError,
        UsernamePasswordRequiredError,
        iLORisCorruptionError,
        ResourceNotReadyError,
        InstallsetError,
        InvalidSmartArrayConfigurationError,
        VnicExistsError,
        GenerateAndSaveAccountError,
        NoAppAccountError,
        RemoveAccountError,
        AppAccountExistsError,
        VnicLoginError,
        SavinginTPMError,
        SavinginiLOError,
        GenBeforeLoginError,
        AppIdListError,
        FlashUnsupportedByIloError,
    )
except ModuleNotFoundError:
    from ilorest.rdmc_helper import (
        ReturnCodes,
        RdmcError,
        ConfigurationFileError,
        CommandNotEnabledError,
        InvalidCommandLineError,
        InvalidCommandLineErrorOPTS,
        UI,
        LOGGER,
        LOUT,
        InvalidFileFormattingError,
        NoChangesFoundOrMadeError,
        InvalidFileInputError,
        NoContentsFoundForOperationError,
        InfoMissingEntriesError,
        MultipleServerConfigError,
        InvalidOrNothingChangedSettingsError,
        NoDifferencesFoundError,
        InvalidMSCfileInputError,
        InvalidPasswordLengthError,
        FirmwareUpdateError,
        DeviceDiscoveryInProgress,
        BootOrderMissingEntriesError,
        NicMissingOrConfigurationError,
        StandardBlobErrorHandler,
        NoCurrentSessionEstablished,
        InvalidCListFileError,
        FailureDuringCommitError,
        IncompatibleiLOVersionError,
        PartitionMoutingError,
        TimeOutError,
        DownloadError,
        UploadError,
        BirthcertParseError,
        ResourceExists,
        IncompatableServerTypeError,
        IloLicenseError,
        InvalidKeyError,
        UnableToDecodeError,
        UnabletoFindDriveError,
        Encryption,
        PathUnavailableError,
        TaskQueueError,
        UsernamePasswordRequiredError,
        TabAndHistoryCompletionClass,
        iLORisCorruptionError,
        TfaEnablePreRequisiteError,
        CloudConnectTimeoutError,
        CloudConnectFailedError,
        ProxyConfigFailedError,
        AlreadyCloudConnectedError,
        ResourceNotReadyError,
        InstallsetError,
        InvalidSmartArrayConfigurationError,
        VnicExistsError,
        GenerateAndSaveAccountError,
        NoAppAccountError,
        RemoveAccountError,
        AppAccountExistsError,
        VnicLoginError,
        SavinginTPMError,
        SavinginiLOError,
        GenBeforeLoginError,
        AppIdListError,
        FlashUnsupportedByIloError,
    )

warnings.filterwarnings("ignore", category=DeprecationWarning)

if os.name != "nt":
    try:
        import setproctitle
    except ImportError:
        pass

# always flush stdout and stderr

try:
    CLI = cliutils.CLI()
except cliutils.ResourceAllocationError:
    RdmcError("Unable to allocate more resources.")
    RdmcError("ILOREST return code: %s\n" % ReturnCodes.RESOURCE_ALLOCATION_ISSUES_ERROR)
    sys.exit(ReturnCodes.RESOURCE_ALLOCATION_ISSUES_ERROR)

try:
    # enable fips mode if our special functions are available in _ssl and OS is
    # in FIPS mode
    FIPSSTR = ""
    if Encryption.check_fips_mode_os():
        LOGGER.info("FIPS mode is enabled in OS!")
    # if Encryption.check_fips_mode_os() and not Encryption.check_fips_mode_ssl():
    #    ssl.FIPS_mode_set(int(1))
    #    if ssl.FIPS_mode():
    #        FIPSSTR = "FIPS mode enabled using openssl version %s.\n" % ssl.OPENSSL_VERSION
    #        LOGGER.info("FIPS mode enabled!")
    #    else:
    #        LOGGER.info("FIPS mode can not be enabled!")
except AttributeError:
    pass


class RdmcCommand(RdmcCommandBase):
    """Constructor"""

    def __init__(self, name, usage, summary, aliases, argparser, Args=None):
        super().__init__(name, usage, summary, aliases, argparser)
        self._commands = collections.OrderedDict()
        self.ui = UI(1)
        self.commands_dict = dict()
        self.interactive = False
        self._progname = "%s : %s" % (versioning.__shortname__, versioning.__longname__)
        self.opts = None
        self.encoding = None
        self.config = RdmcConfig()
        self.app = redfish.ris.RmcApp(showwarnings=True)
        self.retcode = 0
        self.candidates = dict()
        self.comm_map = dict()  # point command id names or alias to handle
        self.commlist = list()
        self._redobj = None
        self.log_dir = None
        self.loaded_commands = []

        # import all extensions dynamically
        for name in extensions.classNames:
            pkgName, cName = name.rsplit(".", 1)
            pkgName = "extensions" + pkgName
            try:
                if "__pycache__" not in pkgName and "Command" in cName:
                    try:
                        self.commands_dict[cName] = getattr(importlib.import_module(pkgName, __package__), cName)()
                    except:
                        self.commands_dict[cName] = getattr(
                            importlib.import_module("ilorest." + pkgName, __package__),
                            cName,
                        )()
                    sName = pkgName.split(".")[1]
                    self.add_command(cName, section=sName)
            except cliutils.ResourceAllocationError as excp:
                self.ui.error(excp)
                retcode = ReturnCodes.RESOURCE_ALLOCATION_ISSUES_ERROR
                self.ui.error("Unable to allocate more resources.")
                self.ui.printer(("ILOREST return code: %s\n" % retcode))
                sys.exit(retcode)
            except Exception:
                self.ui.error(("loading command: %s" % cName), None)

        # command mapping
        commands_to_remove = []
        for command in self.commands_dict:
            try:
                self.comm_map[self.commands_dict[command].ident.get("name")] = command
                for alias in self.commands_dict[command].ident.get("aliases"):
                    self.comm_map[alias] = command
            except Exception as excp:
                self.ui.command_not_enabled(
                    ("Command '%s' unable to be " "initialized...Removing" % command),
                    excp,
                )
                commands_to_remove.append(command)

        # removing commands marked for deletion
        for cmd in commands_to_remove:
            del self.commands_dict[cmd]
        del commands_to_remove

        # ---------End of imports---------

    def add_command(self, command_name, section=None):
        """Handles to addition of new commands

        :param command_name: command name
        :type command_name: str.
        :param section: section for the new command
        :type section: str.
        """
        if section not in self._commands:
            self._commands[section] = list()

        self._commands[section].append(command_name)

    def get_commands(self):
        """Retrieves dictionary of commands"""
        return self._commands

    def search_commands(self, cmdname):
        """Function to see if command exist in added commands

        :param cmdname: command to be searched
        :type cmdname: str.
        """

        try:
            tmp = self.comm_map.get(cmdname)
            if not tmp:
                tmp = cmdname
            return self.commands_dict[tmp]
        except KeyError:
            raise cliutils.CommandNotFoundException(cmdname)

    def load_command(self, cmd):
        """Fully Loads command and returns the class instance

        :param cmd: command identifier
        :type opts: class
        :returns: defined class instance

        """
        try:
            cmd.cmdbase = RdmcCommandBase(
                cmd.ident["name"],
                cmd.ident["usage"],
                cmd.ident["summary"],
                cmd.ident["aliases"],
            )
            cmd.parser = ArgumentParser(
                prog=cmd.ident["name"],
                usage=cmd.ident["usage"],
                description=cmd.ident["description"],
                formatter_class=RawTextHelpFormatter,
            )
            cmd.rdmc = self
            cmd.definearguments(cmd.parser)
            for auxcmd in cmd.ident["auxcommands"]:
                auxcmd = self.search_commands(auxcmd)
                if auxcmd not in self.loaded_commands:
                    self.loaded_commands.append(auxcmd)
                    cmd.auxcommands[auxcmd.ident["name"]] = self.load_command(auxcmd)
                else:
                    cmd.auxcommands[auxcmd.ident["name"]] = self.commands_dict[self.comm_map[auxcmd.ident["name"]]]
            return cmd
        except Exception as excp:
            raise RdmcError("Unable to load command {}: {}".format(cmd.ident["name"], excp))

    def mask_passwords(self, args):
        """Replaces password values in a command argument list with '****'."""
        masked_args = []
        sensitive_keywords = {"--password", "--pass", "-p"}

        for i, arg in enumerate(args):
            # Mask if it's a known password flag or follows a flag
            if arg in sensitive_keywords:
                masked_args.append(arg)  # Keep flag
                masked_args.append("****")  # Mask value
            elif any(arg.startswith(key + "=") for key in sensitive_keywords):
                # Handle inline passwords like --password=mypassword
                masked_args.append(re.sub(r"=(.*)", "=****", arg))
            elif i > 0 and args[i - 1] in sensitive_keywords:
                # If previous argument was a password flag, mask this value
                masked_args.append("****")
            else:
                masked_args.append(arg)

        return masked_args

    def _run_command(self, opts, args, help_disp):
        """Calls the command's run function.

        :param opts: Command options.
        :type opts: argparse.Namespace
        :param args: List of entered arguments.
        :type args: list
        :param help_disp: Help display flag.
        :type help_disp: bool
        :returns: Command execution result.
        """
        if opts.noinfolog and opts.debug:
            opts.noinfolog = False
        if not args:
            LOGGER.error("No command provided. Exiting execution.")
            raise ValueError("No command provided.")

        masked_args = self.mask_passwords(args)

        LOGGER.info(f"Executing command: {args[0]} with arguments: {masked_args}")

        cmd = self.search_commands(args[0])
        if cmd is None:
            LOGGER.error(f"Command '{args[0]}' not found.")
            raise ValueError(f"Command '{args[0]}' not found.")

        self.load_command(cmd)
        LOGGER.debug(f"Command '{args[0]}' loaded successfully.")

        if opts.noinfolog:
            LOGGER.setLevel(logging.ERROR)
        else:
            LOGGER.setLevel(logging.INFO)

        # Enable debug logging if needed
        if opts.debug:
            LOGGER.setLevel(logging.DEBUG)
            if not opts.nostdoutlog:
                LOUT.setLevel(logging.DEBUG)
            LOGGER.debug("Debug mode enabled.")

        # Handle JSON output flag
        if any(a in ("-j", "--json") for a in args):
            opts.nologo = True
            LOGGER.debug("JSON output mode enabled.")

        # Show version information if needed
        if not opts.nologo and not self.interactive:
            LOGGER.info("Displaying version information.")
            CLI.version(self._progname, versioning.__version__, versioning.__extracontent__)

        # Execute the command with remaining arguments
        LOGGER.info(f"Running command: {args[0]} with arguments: {masked_args if len(args) > 1 else 'None'}")
        return cmd.run(args[1:], help_disp=help_disp) if len(args) > 1 else cmd.run([], help_disp=help_disp)

    def run(self, line, help_disp=False):
        """Main rdmc command worker function

        :param line: entered command line
        :type line: list.
        """
        if os.name == "nt":
            if not ctypes.windll.shell32.IsUserAnAdmin() != 0:
                self.app.typepath.adminpriv = False
        elif not os.getuid() == 0:
            self.app.typepath.adminpriv = False

        if "--version" in line or "-V" in line:
            CLI.printer("%s %s\n" % (versioning.__longname__, versioning.__version__))
            sys.exit(self.retcode)

        help_disp = False
        all_opts = True
        help_indx = None
        help_list = ["-h", "--help"]
        for indx, elem in enumerate(line):
            if elem in help_list:
                help_indx = indx
            if "-" in elem:
                continue
            else:
                all_opts = False
        if all_opts and (("-h" in line) or ("--help" in line)):
            line = ["-h"]
        elif help_indx:
            # for comm in self.commands_dict:
            #    if self.commands_dict[comm].ident['name'] == line[0]:
            #        self.ui.printer(self.commands_dict[comm].ident['usage'])
            #        return ReturnCodes.SUCCESS
            del line[help_indx]
            help_disp = True

        if line and line[0] in ["-h", "--help"]:
            cmddict = self.get_commands()
            sorted_keys = sorted(list(cmddict.keys()))

            for key in sorted_keys:
                if key[0] == "_":
                    continue
                else:
                    self.parser.epilog = self.parser.epilog + "\n\n" + key + "\n"
                for cmd in cmddict[key]:
                    c_help = "%-25s - %s\n" % (
                        self.commands_dict[cmd].ident["name"],
                        self.commands_dict[cmd].ident["summary"],
                    )
                    self.parser.epilog = self.parser.epilog + c_help

        (self.opts, nargv) = self.parser.parse_known_args(line)

        if self.opts.redirect:
            try:
                sys.stdout = open("console.log", "w")
            except:
                print("Unable to re-direct output for STDOUT.\n")
            else:
                print("Start of stdout file.\n\n")
            try:
                sys.stderr = open("console_err.log", "w")
            except IOError:
                print("Unable to re-direct output for STDERR.\n")
            else:
                print("Start of stderr file.\n\n")

        self.app.verbose = self.ui.verbosity = self.opts.verbose

        try:
            # Test encoding functions are there
            Encryption.encode_credentials("test")
            self.app.set_encode_funct(Encryption.encode_credentials)
            self.app.set_decode_funct(Encryption.decode_credentials)
            self.encoding = True
        except redfish.hpilo.risblobstore2.ChifDllMissingError:
            self.encoding = False

        if self.opts.config is not None and len(self.opts.config) > 0:
            if not os.path.isfile(self.opts.config):
                self.retcode = ReturnCodes.CONFIGURATION_FILE_ERROR
                sys.exit(self.retcode)

            self.config.configfile = self.opts.config
        else:
            # Default locations: Windows: executed directory Linux: /etc/ilorest/redfish.conf
            self.config.configfile = (
                os.path.join(os.path.dirname(sys.executable), "redfish.conf")
                if os.name == "nt"
                else "/etc/ilorest/redfish.conf"
            )

        if not os.path.isfile(self.config.configfile):
            LOGGER.warning("Config file '%s' not found\n\n", self.config.configfile)

        self.config.load()

        cachedir = None
        if not self.opts.nocache:
            self.config.cachedir = os.path.join(self.opts.config_dir, "cache")
            cachedir = self.config.cachedir

        if cachedir:
            self.app.cachedir = cachedir
            try:
                os.makedirs(cachedir)
            except OSError as ex:
                if ex.errno == errno.EEXIST:
                    pass
                else:
                    raise
        if self.opts.noinfolog and self.opts.debug:
            self.opts.noinfolog = False
        if self.opts.logdir and (self.opts.debug or not self.opts.noinfolog):
            logdir = self.opts.logdir
        else:
            logdir = self.config.logdir

        if logdir:
            try:
                os.makedirs(logdir)
            except OSError as ex:
                if ex.errno == errno.EEXIST:
                    pass
                else:
                    raise
        self.log_dir = logdir
        logfile = os.path.join(logdir, versioning.__shortname__ + ".log")
        # Create a file logger since we got a logdir
        try:
            if self.opts.debug or not self.opts.noinfolog:
                lfile = logging.FileHandler(filename=logfile)
        except (OSError, PermissionError, IOError) as e:
            fallback_dir = os.getenv("APPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
            os.makedirs(fallback_dir, exist_ok=True)
            logfile = os.path.join(fallback_dir, versioning.__shortname__ + ".log")
            lfile = logging.FileHandler(filename=logfile)

        formatter = logging.Formatter("%(asctime)s %(levelname)s\t: %(message)s")
        if self.opts.debug or not self.opts.noinfolog:
            lfile.setFormatter(formatter)

        if getattr(self.opts, "noinfolog", False):
            default_level = logging.ERROR
        else:
            default_level = logging.INFO

        # Apply the base log level
        if self.opts.debug or not self.opts.noinfolog:
            lfile.setLevel(default_level)
        LOGGER.setLevel(default_level)

        # Override logging level for debug
        if getattr(self.opts, "debug", False):
            lfile.setLevel(logging.DEBUG)
            LOGGER.setLevel(logging.DEBUG)
            if not getattr(self.opts, "nostdoutlog", False):
                LOUT.setLevel(logging.DEBUG)
        if self.opts.debug or not self.opts.noinfolog:
            LOGGER.addHandler(lfile)
        self.app.LOGGER = LOGGER

        if ("login" in line or any(x.startswith("--url") for x in line) or not line) and not (
            any(x.startswith(("-h", "--h")) for x in nargv) or "help" in line
        ):
            if not any(x.startswith("--sessionid") for x in line):
                self.app.logout()
        else:
            creds, enc = self._pull_creds(nargv)
            self.app.restore(creds=creds, enc=enc)
            self.opts.is_redfish = self.app.typepath.updatedefinesflag(redfishflag=self.opts.is_redfish)

        if nargv:
            try:
                self.retcode = self._run_command(self.opts, nargv, help_disp)
                if self.app.cache:
                    if ("logout" not in line) and ("--logout" not in line):
                        self.app.save()
                        self.app.redfishinst = None
                else:
                    self.app.logout()
            except AttributeError:
                self.retcode = 0
                pass
            except Exception as excp:
                self.handle_exceptions(excp)

            return self.retcode
        else:
            self.cmdloop(self.opts)

            if self.app.cache:
                self.app.save()
            else:
                self.app.logout()

    def cmdloop(self, opts):
        """Interactive mode worker function.

        :param opts: Command options.
        :type opts: argparse.Namespace
        """
        if opts.noinfolog and opts.debug:
            opts.noinfolog = False
        if opts.noinfolog:
            LOGGER.setLevel(logging.ERROR)
        else:
            LOGGER.setLevel(logging.INFO)
        LOGGER.info("Starting interactive mode.")
        self.interactive = True

        if not opts.nologo:
            sys.stdout.write(FIPSSTR)
            CLI.version(self._progname, versioning.__version__, versioning.__extracontent__)
            LOGGER.info("Displayed version information.")

        if not self.app.typepath.adminpriv:
            self.ui.user_not_admin()
            LOGGER.warning("User does not have admin privileges.")

        if opts.debug:
            LOGGER.setLevel(logging.DEBUG)
            if not opts.nostdoutlog:
                LOUT.setLevel(logging.DEBUG)
            LOGGER.debug("Debug mode enabled.")

        LOGGER.info("Loading available commands.")
        for command, values in self.commands_dict.items():
            self.commlist.append(values.ident["name"])

        for item in self.commlist:
            self.candidates[item] = self.commlist if item == "help" else []

        self._redobj = TabAndHistoryCompletionClass(dict(self.candidates))

        def bottom_toolbar():
            return HTML("<b>Restful Interface Tool</b>")

        try:
            session = PromptSession(
                completer=self._redobj,
                auto_suggest=AutoSuggestFromHistory(),
                complete_style=CompleteStyle.READLINE_LIKE,
                complete_while_typing=True,
            )
            session.output.disable_bracketed_paste()
            LOGGER.info("Tab completion enabled.")
        except Exception as e:
            LOGGER.exception("Console error: Tab complete is unavailable.")
            session = None

        if self.opts.notab:
            LOGGER.info("Tab completion is disabled as per user settings.")
            session = None

        while True:
            try:
                prompt_string = str(versioning.__shortname__) + " > "
                if session:
                    if self.opts.toolbar:
                        line = session.prompt(prompt_string, bottom_toolbar=bottom_toolbar)
                    else:
                        line = session.prompt(prompt_string)
                else:
                    line = input(prompt_string)

                LOGGER.debug(f"User input: {line}")

            except (EOFError, KeyboardInterrupt):
                LOGGER.info("User exited interactive mode.")
                line = "quit\n"

            if not line.strip():
                continue
            elif line.endswith(os.linesep):
                line = line.rstrip(os.linesep)

            shlex.escape = ""
            nargv = shlex.shlex(line, posix=True)
            nargv.escape = ""
            nargv.whitespace_split = True
            nargv = list(nargv)

            LOGGER.debug(f"Parsed command arguments: {nargv}")

            try:
                if not (
                    any(x.startswith("-h") for x in nargv) or any(x.startswith("--h") for x in nargv) or "help" in line
                ):
                    if "login " in line or line == "login" or any(x.startswith("--url") for x in nargv):
                        self.app.logout()
                        LOGGER.info("User triggered logout.")

                self.retcode = self._run_command(opts, nargv, help_disp=False)
                LOGGER.info(f"Command executed with return code: {self.retcode}")

                self.check_for_tab_lists(nargv)

            except Exception as excp:
                LOGGER.exception("Exception occurred while executing command.")
                self.handle_exceptions(excp)

            if self.opts.verbose:
                sys.stdout.write(f"iLOrest return code: {self.retcode}\n")

        LOGGER.info("Exiting interactive mode.")
        return self.retcode

    def handle_exceptions(self, excp):
        """Main exception handler for both shell and interactive modes

        :param excp: captured exception to be handled
        :type excp: exception.
        """
        # pylint: disable=redefined-argument-from-local
        try:
            if not getattr(excp, "_already_logged", False):
                LOGGER.info(f"Exception: {type(excp).__name__}: {excp}")
                setattr(excp, "_already_logged", True)
            raise
        # ****** RDMC ERRORS ******
        except ConfigurationFileError as excp:
            self.retcode = ReturnCodes.CONFIGURATION_FILE_ERROR
            self.ui.error(excp)
            sys.exit(excp.errcode)
        except InstallsetError as excp:
            self.retcode = ReturnCodes.INSTALLSET_ERROR
            self.ui.error(excp)
        except InvalidCommandLineError as excp:
            self.retcode = ReturnCodes.INVALID_COMMAND_LINE_ERROR
            self.ui.invalid_commmand_line(excp)
        except NoCurrentSessionEstablished as excp:
            self.retcode = ReturnCodes.NO_CURRENT_SESSION_ESTABLISHED
            self.ui.error(excp)
        except TfaEnablePreRequisiteError as excp:
            self.retcode = ReturnCodes.TFA_ENABLED_ERROR
            self.ui.error(excp)
        except iLORisCorruptionError as excp:
            self.retcode = ReturnCodes.ILO_RIS_CORRUPTION_ERROR
            self.ui.error(excp)
        except ResourceNotReadyError as excp:
            self.retcode = ReturnCodes.RESOURCE_NOT_READY_ERROR
            self.ui.error(excp)
        except CloudConnectTimeoutError as excp:
            self.retcode = ReturnCodes.CLOUD_CONNECT_TIMEOUT
            self.ui.error(excp)
        except CloudConnectFailedError as excp:
            self.retcode = ReturnCodes.CLOUD_CONNECT_FAILED
            self.ui.error(excp)
        except AlreadyCloudConnectedError as excp:
            self.retcode = ReturnCodes.CLOUD_ALREADY_CONNECTED
            self.ui.error(excp)
        except ProxyConfigFailedError as excp:
            self.retcode = ReturnCodes.PROXY_CONFIG_FAILED
            self.ui.error(excp)
        except UsernamePasswordRequiredError as excp:
            self.retcode = ReturnCodes.USERNAME_PASSWORD_REQUIRED_ERROR
            self.ui.error(excp)
        except InvalidPasswordLengthError as excp:
            self.retcode = ReturnCodes.INVALID_PASSWORD_LENGTH_ERROR
            self.ui.error(excp)
        except NoChangesFoundOrMadeError as excp:
            self.retcode = ReturnCodes.NO_CHANGES_MADE_OR_FOUND
            self.ui.invalid_commmand_line(excp)
        except StandardBlobErrorHandler as excp:
            self.retcode = ReturnCodes.GENERAL_ERROR
            self.ui.standard_blob_error(excp)
        except InvalidFileInputError as excp:
            self.retcode = ReturnCodes.INVALID_FILE_INPUT_ERROR
            self.ui.invalid_commmand_line(excp)
        except InvalidCommandLineErrorOPTS as excp:
            self.retcode = ReturnCodes.INVALID_COMMAND_LINE_ERROR
            self.ui.invalid_commmand_line(excp)
        except InvalidFileFormattingError as excp:
            self.retcode = ReturnCodes.INVALID_FILE_FORMATTING_ERROR
            self.ui.invalid_file_formatting(excp)
        except NoContentsFoundForOperationError as excp:
            self.retcode = ReturnCodes.NO_CONTENTS_FOUND_FOR_OPERATION
            self.ui.no_contents_found_for_operation(excp)
        except InfoMissingEntriesError as excp:
            self.retcode = ReturnCodes.NO_VALID_INFO_ERROR
            self.ui.error(excp)
        except (
            InvalidOrNothingChangedSettingsError,
            redfish.ris.rmc_helper.IncorrectPropValue,
        ) as excp:
            self.retcode = ReturnCodes.SAME_SETTINGS_ERROR
            self.ui.error(excp)
        except NoDifferencesFoundError as excp:
            self.retcode = ReturnCodes.NO_CHANGES_MADE_OR_FOUND
            self.ui.no_differences_found(excp)
        except MultipleServerConfigError as excp:
            self.retcode = ReturnCodes.MULTIPLE_SERVER_CONFIG_FAIL
            self.ui.multiple_server_config_fail(excp)
        except InvalidMSCfileInputError as excp:
            self.retcode = ReturnCodes.MULTIPLE_SERVER_INPUT_FILE_ERROR
            self.ui.multiple_server_config_input_file(excp)
        except FirmwareUpdateError as excp:
            self.retcode = ReturnCodes.FIRMWARE_UPDATE_ERROR
            self.ui.error(excp)
        except FailureDuringCommitError as excp:
            self.retcode = ReturnCodes.FAILURE_DURING_COMMIT_OPERATION
            self.ui.error(excp)
        except BootOrderMissingEntriesError as excp:
            self.retcode = ReturnCodes.BOOT_ORDER_ENTRY_ERROR
            self.ui.error(excp)
        except NicMissingOrConfigurationError as excp:
            self.retcode = ReturnCodes.NIC_MISSING_OR_INVALID_ERROR
            self.ui.error(excp)
        except (
            IncompatibleiLOVersionError,
            redfish.ris.rmc_helper.IncompatibleiLOVersionError,
        ) as excp:
            self.retcode = ReturnCodes.INCOMPATIBLE_ILO_VERSION_ERROR
            self.ui.printer(excp)
        except IncompatableServerTypeError as excp:
            self.retcode = ReturnCodes.INCOMPATIBLE_SERVER_TYPE
            self.ui.printer(excp)
        except IloLicenseError as excp:
            self.ui.printer(excp)
            self.retcode = ReturnCodes.ILO_LICENSE_ERROR
        except InvalidCListFileError as excp:
            self.retcode = ReturnCodes.INVALID_CLIST_FILE_ERROR
            self.ui.error(excp)
        except PartitionMoutingError as excp:
            self.retcode = ReturnCodes.UNABLE_TO_MOUNT_BB_ERROR
            self.ui.error(excp)
        except TimeOutError as excp:
            self.retcode = ReturnCodes.UPDATE_SERVICE_BUSY
            self.ui.error(excp)
        except DownloadError as excp:
            self.retcode = ReturnCodes.FAILED_TO_DOWNLOAD_COMPONENT
            self.ui.error(excp)
        except UploadError as excp:
            self.retcode = ReturnCodes.FAILED_TO_UPLOAD_COMPONENT
            self.ui.error(excp)
        except FlashUnsupportedByIloError as excp:
            self.retcode = ReturnCodes.ILO_UNSUPPORTED_FLASH
            self.ui.error(excp)
        except BirthcertParseError as excp:
            self.retcode = ReturnCodes.BIRTHCERT_PARSE_ERROR
            self.ui.error(excp)
        except ResourceExists as excp:
            self.retcode = ReturnCodes.RESOURCE_EXISTS_ERROR
            self.ui.error(excp)
        except InvalidKeyError as excp:
            self.retcode = ReturnCodes.ENCRYPTION_ERROR
            self.ui.error("Invalid key has been entered for encryption/decryption.\n")
        except UnableToDecodeError as excp:
            self.retcode = ReturnCodes.ENCRYPTION_ERROR
            self.ui.error(excp)
        except UnabletoFindDriveError as excp:
            self.retcode = ReturnCodes.DRIVE_MISSING_ERROR
            self.ui.error(excp)
            self.ui.printer("Error occurred while reading device labels.\n")
        except PathUnavailableError as excp:
            self.retcode = ReturnCodes.PATH_UNAVAILABLE_ERROR
            if excp:
                self.ui.error(excp)
            else:
                self.ui.printer("Requested path is unavailable.")
        except TaskQueueError as excp:
            self.retcode = ReturnCodes.TASKQUEUE_ERROR
            self.ui.error(excp)
        except DeviceDiscoveryInProgress as excp:
            self.retcode = ReturnCodes.DEVICE_DISCOVERY_IN_PROGRESS
            self.ui.error(excp)
        except InvalidSmartArrayConfigurationError as excp:
            self.retcode = ReturnCodes.INVALID_SMART_ARRAY_PAYLOAD
        except GenBeforeLoginError as excp:
            self.retcode = ReturnCodes.GEN_BEFORE_LOGIN_ERROR
            if not getattr(excp, "_already_logged", False):
                self.ui.error(f"{type(excp).__name__}: {excp}")
                setattr(excp, "_already_logged", True)
        # ****** CLI ERRORS ******
        except (CommandNotEnabledError, cliutils.CommandNotFoundException) as excp:
            self.retcode = ReturnCodes.UI_CLI_COMMAND_NOT_FOUND_EXCEPTION
            self.ui.command_not_found(excp)
            # try:
            #    self.commands_dict['HelpCommand'].run('-h')
            # except KeyError:
            #    pass

        # ****** RMC/RIS ERRORS ******
        except redfish.ris.UndefinedClientError:
            self.retcode = ReturnCodes.RIS_UNDEFINED_CLIENT_ERROR
            self.ui.error("Please login before making a selection.")
        except (
            redfish.ris.InstanceNotFoundError,
            redfish.ris.RisInstanceNotFoundError,
        ) as excp:
            self.retcode = ReturnCodes.RIS_INSTANCE_NOT_FOUND_ERROR
            self.ui.printer(excp)
        except redfish.ris.CurrentlyLoggedInError as excp:
            self.retcode = ReturnCodes.RIS_CURRENTLY_LOGGED_IN_ERROR
            self.ui.error(excp)
        except redfish.ris.NothingSelectedError as excp:
            self.retcode = ReturnCodes.RIS_NOTHING_SELECTED_ERROR
            self.ui.nothing_selected()
        except redfish.ris.NothingSelectedFilterError as excp:
            self.retcode = ReturnCodes.RIS_NOTHING_SELECTED_FILTER_ERROR
            self.ui.nothing_selected_filter()
        except redfish.ris.NothingSelectedSetError as excp:
            self.retcode = ReturnCodes.RIS_NOTHING_SELECTED_SET_ERROR
            self.ui.nothing_selected_set()
        except redfish.ris.InvalidSelectionError as excp:
            self.retcode = ReturnCodes.RIS_INVALID_SELECTION_ERROR
            self.ui.error(excp)
        except redfish.ris.rmc_helper.UnableToObtainIloVersionError as excp:
            self.retcode = ReturnCodes.INCOMPATIBLE_ILO_VERSION_ERROR
            self.ui.error(excp)
        except redfish.ris.IdTokenError as excp:
            if hasattr(excp, "message"):
                self.ui.printer(excp.message)
            else:
                self.ui.printer(
                    "Logged-in account does not have the privilege"
                    " required to fulfill the request or a required"
                    " token is missing."
                    "\nEX: biospassword flag if bios password present "
                    "or tpmenabled flag if TPM module present.\n"
                )
            self.retcode = ReturnCodes.RIS_MISSING_ID_TOKEN
        except redfish.ris.SessionExpired as excp:
            self.retcode = ReturnCodes.RIS_SESSION_EXPIRED
            self.app.logout()
            self.ui.printer(
                "Current session has expired or is invalid, "
                "please login again with proper credentials to continue.\n"
            )
        except redfish.ris.ValidationError as excp:
            self.retcode = ReturnCodes.RIS_VALIDATION_ERROR
        except redfish.ris.ValueChangedError as excp:
            self.retcode = ReturnCodes.RIS_VALUE_CHANGED_ERROR
        except redfish.ris.ris.SchemaValidationError as excp:
            self.ui.printer("Error found in schema, try running with the " "--latestschema flag.\n")
            self.retcode = ReturnCodes.RIS_SCHEMA_PARSE_ERROR
        # ****** RMC/RIS ERRORS ******
        except redfish.rest.connections.RetriesExhaustedError as excp:
            self.retcode = ReturnCodes.V1_RETRIES_EXHAUSTED_ERROR
            self.ui.retries_exhausted_attemps()
        except redfish.rest.connections.VnicNotEnabledError as excp:
            self.retcode = ReturnCodes.VNIC_NOT_ENABLED_ERROR
            self.ui.retries_exhausted_vnic_not_enabled()
        except redfish.rest.v1.InvalidCredentialsError as excp:
            self.retcode = ReturnCodes.V1_INVALID_CREDENTIALS_ERROR
            self.ui.invalid_credentials(excp)
        except redfish.rest.v1.JsonDecodingError as excp:
            self.retcode = ReturnCodes.JSON_DECODE_ERROR
            self.ui.error(excp)
        except redfish.rest.v1.ServerDownOrUnreachableError as excp:
            self.retcode = ReturnCodes.V1_SERVER_DOWN_OR_UNREACHABLE_ERROR
            self.ui.error(excp)
        except redfish.rest.connections.ChifDriverMissingOrNotFound as excp:
            self.retcode = ReturnCodes.V1_CHIF_DRIVER_MISSING_ERROR
            self.ui.printer(
                "Chif driver not found, please check that the iLO channel interface" " driver (Chif) is installed.\n"
            )
        except redfish.rest.connections.SecurityStateError as excp:
            self.retcode = ReturnCodes.V1_SECURITY_STATE_ERROR
            self.ui.printer(
                "High security mode [%s] or Host Authentication has been enabled. "
                "Please provide valid credentials.\n" % str(excp)
            )
        except redfish.rest.connections.OneTimePasscodeError:
            self.retcode = ReturnCodes.TFA_OTP_EMAILED
            self.ui.printer(
                "One Time Passcode Sent to registered email.\n"
                "Retry the login command by including -o/--otp tag along with the OTP received.\n"
            )
        except redfish.rest.connections.UnauthorizedLoginAttemptError as excp:
            self.retcode = ReturnCodes.TFA_WRONG_OTP
            self.ui.error(excp)
        except redfish.rest.connections.TokenExpiredError as excp:
            self.retcode = ReturnCodes.TFA_OTP_TIMEDOUT
            self.ui.error(excp)
        except redfish.hpilo.risblobstore2.ChifDllMissingError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_CHIF_DLL_MISSING_ERROR
            self.ui.printer(
                "iLOrest Chif library not found, please check that the chif " "ilorest_chif.dll/.so is present.\n"
            )
        except redfish.hpilo.risblobstore2.UnexpectedResponseError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_UNEXPECTED_RESPONSE_ERROR
            self.ui.printer("Unexpected data received from iLO.\n")
        except redfish.hpilo.risblobstore2.HpIloError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_ILO_ERROR
            self.ui.printer("iLO returned a failed error code.\n")
        except redfish.hpilo.risblobstore2.Blob2CreateError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_CREATE_BLOB_ERROR
            self.ui.printer("Blob create operation failed.\n")
        except redfish.hpilo.risblobstore2.Blob2ReadError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_READ_BLOB_ERROR
            self.ui.printer("Blob read operation failed.\n")
        except redfish.hpilo.risblobstore2.Blob2WriteError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_WRITE_BLOB_ERROR
            self.ui.printer("Blob write operation failed.\n")
        except redfish.hpilo.risblobstore2.Blob2DeleteError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_BLOB_DELETE_ERROR
            self.ui.printer("Blob delete operation failed.\n")
        except redfish.hpilo.risblobstore2.Blob2OverrideError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_BLOB_OVERRIDE_ERROR
            self.ui.error(excp)
            self.ui.printer(
                "\nAnother user access in progress. Pease ensure only one user is accessing at a time locally.\n"
            )
        except redfish.hpilo.risblobstore2.BlobRetriesExhaustedError as excp:
            self.retcode = ReturnCodes.REST_BLOB_RETRIES_EXHAUSETED_ERROR
            self.ui.printer("\nBlob operation still fails after max retries.\n")
        except redfish.hpilo.risblobstore2.Blob2FinalizeError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_BLOB_FINALIZE_ERROR
            self.ui.printer("Blob finalize operation failed.")
        except redfish.hpilo.risblobstore2.BlobNotFoundError as excp:
            self.retcode = ReturnCodes.REST_ILOREST_BLOB_NOT_FOUND_ERROR
            self.ui.printer("Blob not found with key and namespace provided.\n")
        except redfish.ris.rmc_helper.InvalidPathError as excp:
            self.retcode = ReturnCodes.RIS_REF_PATH_NOT_FOUND_ERROR
            self.ui.printer("Reference path not found.")
        except redfish.ris.rmc_helper.IloResponseError as excp:
            self.retcode = ReturnCodes.RIS_ILO_RESPONSE_ERROR
        except redfish.ris.rmc_helper.UserNotAdminError as excp:
            self.ui.user_not_admin()
            self.retcode = ReturnCodes.USER_NOT_ADMIN
        except redfish.hpilo.rishpilo.HpIloInitialError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RIS_ILO_INIT_ERROR
        except redfish.hpilo.rishpilo.HpIloChifAccessDeniedError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RIS_ILO_CHIF_ACCESS_DENIED_ERROR
        except redfish.hpilo.rishpilo.HpIloPrepareAndCreateChannelError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RIS_CREATE_AND_PREPARE_CHANNEL_ERROR
        except redfish.hpilo.rishpilo.HpIloChifPacketExchangeError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RIS_ILO_CHIF_PACKET_EXCHANGE_ERROR
        except redfish.hpilo.rishpilo.HpIloNoDriverError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RIS_ILO_CHIF_NO_DRIVER_ERROR
        except redfish.hpilo.rishpilo.HpIloWriteError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RESOURCE_ALLOCATION_ISSUES_ERROR
        except redfish.hpilo.rishpilo.HpIloReadError as excp:
            self.ui.error(excp)
            self.retcode = ReturnCodes.RESOURCE_ALLOCATION_ISSUES_ERROR
        # ****** RIS OBJECTS ERRORS ******
        except redfish.ris.ris.BiosUnregisteredError as excp:
            self.retcode = ReturnCodes.RIS_RIS_BIOS_UNREGISTERED_ERROR
            self.ui.bios_unregistered_error()
        # ****** FILE/IO ERRORS ******
        except IOError:
            self.retcode = ReturnCodes.INVALID_FILE_INPUT_ERROR
            self.ui.printer(
                "Error accessing the file path. Verify the file path is correct and " "you have proper permissions.\n"
            )
        # ****** VNIC ERRORS ****** #
        except VnicExistsError as excp:
            self.retcode = ReturnCodes.VNIC_DOES_NOT_EXIST_ERROR
            self.ui.error(excp)
        except GenerateAndSaveAccountError as excp:
            self.retcode = ReturnCodes.GENERAL_ACCOUNT_GENERATE_SAVE_ERROR
            self.ui.error(excp)
        except NoAppAccountError as excp:
            self.retcode = ReturnCodes.ACCOUNT_DOES_NOT_EXIST_ERROR
            self.ui.error(excp)
        except RemoveAccountError as excp:
            self.retcode = ReturnCodes.ACCOUNT_REMOVE_ERROR
            self.ui.error(excp)
        except AppAccountExistsError as excp:
            self.retcode = ReturnCodes.ACCOUNT_EXISTS_CHECK_ERROR
            self.ui.error(excp)
        except VnicLoginError as excp:
            self.retcode = ReturnCodes.VNIC_LOGIN_ERROR
            self.ui.error(excp)
        except SavinginTPMError as excp:
            self.retcode = ReturnCodes.ACCOUNT_SAVE_ERROR_TPM
            self.ui.error(excp)
        except SavinginiLOError as excp:
            self.retcode = ReturnCodes.ACCOUNT_SAVE_ERROR_ILO
            self.ui.error(excp)
        except AppIdListError as excp:
            self.retcode = ReturnCodes.APPID_LIST_ERROR
            self.ui.error(excp)
        # ****** GENERAL ERRORS ******
        except SystemExit:
            self.retcode = ReturnCodes.GENERAL_ERROR
            raise
        except Exception as excp:
            self.retcode = ReturnCodes.GENERAL_ERROR
            sys.stderr.write("ERROR: %s\n" % excp)

            if self.opts.debug:
                traceback.print_exc(file=sys.stderr)

    def check_for_tab_lists(self, command=None):
        """Function to generate available options for tab tab
        :param command: command for auto tab completion
        :type command: string.
        """
        # TODO: don't always update, only when we have a different selector.
        # Try to use args to get specific nested posibilities?
        changes = dict()

        # select options
        typeslist = list()

        try:
            typeslist = sorted(set(self.app.types()))
            changes["select"] = typeslist
        except:
            pass

        # get/set/info options
        getlist = list()

        try:
            if self.app.typepath.defs:
                typestr = self.app.typepath.defs.typestring
            templist = self.app.getprops()
            dictcopy = copy.copy(templist[0])

            for content in templist:
                for k in list(content.keys()):
                    if k.lower() in HARDCODEDLIST or "@odata" in k.lower():
                        del content[k]
            if "Bios." in dictcopy[typestr]:
                if hasattr(
                    templist[0],
                    "Attributes",
                ):
                    templist = templist[0]["Attributes"]
                else:
                    templist = templist[0]
            else:
                templist = templist[0]
            for key, _ in templist.items():
                getlist.append(key)

            getlist.sort()

            # if select command, get possible values
            infovals = dict()

            if "select" in command:
                if typestr in dictcopy:
                    (_, attributeregistry) = self.app.get_selection(setenable=True)
                    schema, reg = self.app.get_model(dictcopy, attributeregistry)

                    if reg:
                        if "Attributes" in reg:
                            reg = reg["Attributes"]
                        for item in getlist:
                            for attribute in reg:
                                if item == attribute:
                                    infovals.update({item: reg[attribute]})
                                    break

                        changes["nestedinfo"] = infovals

                    elif schema:
                        changes["nestedinfo"] = schema

            changes["get"] = getlist
            changes["nestedprop"] = dictcopy["Attributes"] if "Attributes" in dictcopy else dictcopy
            changes["set"] = getlist
            changes["info"] = getlist
            changes["val"] = []

            readonly_list = []

            for info in schema:
                for checkread in schema[info]:
                    if "readonly" in checkread and schema[info]["readonly"] is True:
                        readonly_list.append(info)

            set_list = [x for x in getlist if x not in readonly_list]

            changes["set"] = set_list

        except:
            pass

        if changes:
            self._redobj.updates_tab_completion_lists(changes)

    def _pull_creds(self, args):
        """Pull creds from the arguments for blobstore"""
        cred_args = {}
        enc = False
        arg_iter = iter(args)
        try:
            for arg in arg_iter:
                if arg in ("--enc", "-e"):
                    enc = True
                if arg in ("-u", "--user"):
                    cred_args["username"] = next(arg_iter)
                elif arg in ("-p", "--password"):
                    cred_args["password"] = next(arg_iter)
        except StopIteration:
            return {}, False
        return cred_args, enc

    def rdmc_parse_arglist(self, cmdinstance, line=None, default=False):
        """
        Parses command-line arguments with special consideration for quoting and optional arguments.

        :param cmdinstance: Command instance to be referenced.
        :type cmdinstance: class object
        :param line: String of arguments passed in.
        :type line: str or list
        :param default: Flag to determine if the parsed command requires the default workaround for
                        argparse in Python 2. Argparse incorrectly assumes a sub-command is always
                        required, so we have to include a default sub-command for no arguments.
        :type default: bool
        :returns: Parsed argument list
        """

        def checkargs(argopts):
            """Check for invalid optional args."""
            (_, args) = argopts
            for arg in args:
                if arg.startswith("-") or arg.startswith("--"):
                    try:
                        cmdinstance.parser.error(
                            "The option %s is not available for %s" % (arg, cmdinstance.ident["name"])
                        )
                    except SystemExit:
                        raise InvalidCommandLineErrorOPTS("")
            return argopts

        # Ensure `None` does not cause errors
        if line is None:
            return checkargs(cmdinstance.parser.parse_known_args([]))

        # Parse argument list correctly
        if isinstance(line, six.string_types):
            arglist = shlex.split(line, posix=False)
            arglist = [val.strip("\"'") for val in arglist]  # Strip surrounding quotes
        elif isinstance(line, list):
            arglist = line
        else:
            raise ValueError("Invalid type for 'line'. Expected str or list.")

        # Handle Windows-specific globbing
        exarglist = []
        if os.name == "nt":
            for arg in arglist:
                try:
                    matches = glob.glob(arg)
                    exarglist.extend(matches if matches else [arg])
                except Exception as e:
                    if arg:
                        exarglist.append(arg)
        else:
            exarglist = [arg for arg in arglist if arg]

        # Insert 'default' if needed
        if default and not any(_opt in ["-h", "--h", "-help", "--help"] for _opt in exarglist):
            exarglist.insert(0, "default")

        return checkargs(cmdinstance.parser.parse_known_args(exarglist))


def ilorestcommand():
    # Initialization of main command class
    ARGUMENTS = sys.argv[1:]

    RDMC = RdmcCommand(
        Args=ARGUMENTS,
        name=versioning.__shortname__,
        usage=versioning.__shortname__ + " [command]",
        summary="HPE RESTful Interface Tool",
        aliases=[versioning.__shortname__],
        argparser=RdmcOptionParser(),
    )

    # Main execution function call wrapper
    if "setproctitle" in sys.modules:
        FOUND = False
        VARIABLE = setproctitle.getproctitle()

        for items in VARIABLE.split(" "):
            if FOUND:
                VARIABLE = VARIABLE.replace(items, "xxxxxxxx")
                break

            if items == "--password" or items == "-p":
                FOUND = True

        setproctitle.setproctitle(VARIABLE)

    RDMC.retcode = RDMC.run(ARGUMENTS)

    if RDMC.opts:
        if RDMC.opts.verbose:
            RDMC.ui.printer(("iLORest return code: %s\n" % RDMC.retcode))
    else:
        RDMC.ui.printer(("iLORest return code: %s\n" % RDMC.retcode))

    # Return code
    sys.exit(RDMC.retcode)


if __name__ == "__main__":
    ilorestcommand()
