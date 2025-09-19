#!/usr/bin/env python
"""
This bescli module provides a command line interface to interact with besapi.

MIT License
Copyright (c) 2014 Matt Hansen
Maintained by James Stewart since 2021

Simple command line interface for the BES (BigFix) REST API.
"""

import getpass
import json
import logging
import os
import site
from configparser import ConfigParser as SafeConfigParser

import requests.exceptions
from cmd2 import Cmd

try:
    from besapi import besapi
except ModuleNotFoundError:
    # add the module path
    site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from besapi import besapi
except ImportError:
    # this is for the case in which we are calling bescli from besapi
    import besapi  # type: ignore[no-redef]

try:
    from besapi.besapi import __version__
except ImportError:
    from besapi import __version__  # type: ignore[attr-defined, no-redef]


class BESCLInterface(Cmd):
    """BigFix command-line interface processor."""

    def __init__(self, **kwargs):
        Cmd.__init__(self, **kwargs)

        # set an intro message
        self.intro = (
            f"\nWelcome to the BigFix REST API Interactive Python Module v{__version__}"
        )

        # sets the prompt look:
        self.prompt = "BigFix> "

        self.num_errors = 0
        self.BES_ROOT_SERVER = None
        self.BES_USER_NAME = None
        self.BES_PASSWORD = None
        self.bes_conn = None
        # set default config file path
        self.conf_path = os.path.expanduser("~/.besapi.conf")
        self.CONFPARSER = SafeConfigParser()
        # for completion:
        self.api_resources = []
        self.do_conf()

    def parse_help_resources(self):
        """Get api resources from help."""
        if self.bes_conn:
            help_result = self.bes_conn.get("help")
            help_result = help_result.text.split("\n")
            # print(help_result)
            help_resources = []
            for item in help_result:
                if "/api/" in item:
                    _, _, res = item.partition("/api/")
                    # strip whitespace just in case:
                    help_resources.append(res.strip())

            return help_resources
        else:
            return [
                "actions",
                "clientqueryresults",
                "dashboardvariables",
                "help",
                "login",
                "query",
                "relaysites",
                "serverinfo",
                "sites",
            ]

    def complete_api_resources(self, text, line, begidx, endidx):
        """Define completion for apis."""

        # only initialize once
        if not self.api_resources:
            self.api_resources = self.parse_help_resources()

        # TODO: make this work to complete only the first word after get/post/delete
        # return the matching subset:
        return [name for name in self.api_resources if name.startswith(text)]

    complete_get = complete_api_resources

    def do_get(self, line):
        """Perform get request to BigFix server using provided api endpoint
        argument.
        """

        # remove any extra whitespace
        line = line.strip()

        # Remove root server prefix:
        # if root server prefix is not removed
        # and root server is given as IP Address,
        # then `robjs` will not work
        if "/api/" in line:
            line = str(line).split("/api/", 1)[1]
            self.pfeedback("get " + line)

        # allow use of `get resource/path.obj_attribute.attribute`
        robjs = line.split(".")

        if self.bes_conn:
            if len(robjs) > 1:
                b = self.bes_conn.get(robjs[0])
                # print objectify.ObjectPath(robjs[1:])
                if b:
                    self.poutput(eval("b()." + ".".join(robjs[1:])))
            else:
                output_item = self.bes_conn.get(line)
                # self.poutput(type(output_item))
                self.poutput(output_item)
                # self.poutput(output_item.besdict)
                # self.poutput(output_item.besjson)
        else:
            self.pfeedback("Not currently logged in. Type 'login'.")

    complete_delete = complete_api_resources

    def do_delete(self, line):
        """Perform delete request to BigFix server using provided api endpoint
        argument.
        """

        # remove any extra whitespace
        line = line.strip()

        # Remove root server prefix:
        if "/api/" in line:
            line = str(line).split("/api/", 1)[1]
            self.pfeedback("get " + line)

        if self.bes_conn:
            output_item = self.bes_conn.delete(line)

            self.poutput(output_item)
            # self.poutput(output_item.besdict)
            # self.poutput(output_item.besjson)
        else:
            self.pfeedback("Not currently logged in. Type 'login'.")

    complete_post = complete_api_resources

    def do_post(self, statement):
        """Post file as data to path."""
        self.poutput(statement)
        self.poutput("not yet implemented")

    def do_config(self, conf_file=None):
        """Attempt to load config info from file and login."""
        self.do_conf(conf_file)

    def do_loadconfig(self, conf_file=None):
        """Attempt to load config info from file and login."""
        self.do_conf(conf_file)

    def do_conf(self, conf_file=None):
        """Attempt to load config info from file and login."""
        config_path = [
            "/etc/besapi.conf",
            os.path.expanduser("~/besapi.conf"),
            os.path.expanduser("~/.besapi.conf"),
            "besapi.conf",
        ]
        if self.conf_path not in config_path:
            config_path.append(self.conf_path)
        # if conf_file specified, then only use that:
        if conf_file:
            config_path = [conf_file]

        found_config_files = self.CONFPARSER.read(config_path)
        if found_config_files:
            self.pfeedback(f" - Found Config File(s):\n{found_config_files}")
            if found_config_files[0] != self.conf_path:
                self.conf_path = found_config_files[0]

        if self.CONFPARSER:
            try:
                self.BES_ROOT_SERVER = self.CONFPARSER.get("besapi", "BES_ROOT_SERVER")
            except BaseException:
                self.BES_ROOT_SERVER = None

            try:
                self.BES_USER_NAME = self.CONFPARSER.get("besapi", "BES_USER_NAME")
            except BaseException:
                self.BES_USER_NAME = None

            try:
                self.BES_PASSWORD = self.CONFPARSER.get("besapi", "BES_PASSWORD")
            except BaseException:
                self.BES_PASSWORD = None

        if self.BES_USER_NAME and self.BES_PASSWORD and self.BES_ROOT_SERVER:
            self.pfeedback(" - all values loaded from config file - ")
            # self.do_ls()
            self.pfeedback(" - attempt login using config parameters - ")
            self.do_login()

    def do_login(self, user=None):
        """Login to BigFix Server."""

        if not user:
            if self.BES_USER_NAME:
                user = self.BES_USER_NAME
            else:
                user = str(input("User [%s]: " % getpass.getuser()))
                if not user:
                    user = getpass.getuser()

            self.BES_USER_NAME = user
            if not self.CONFPARSER.has_section("besapi"):
                self.CONFPARSER.add_section("besapi")
            self.CONFPARSER.set("besapi", "BES_USER_NAME", user)

        if self.BES_ROOT_SERVER:
            root_server = self.BES_ROOT_SERVER
            if not root_server:
                root_server = str(input("Root Server [%s]: " % self.BES_ROOT_SERVER))

            self.BES_ROOT_SERVER = root_server

        else:
            root_server = str(
                input("Root Server (ex. %s): " % "https://server.institution.edu:52311")
            )
            if root_server:
                self.BES_ROOT_SERVER = root_server
                if not self.CONFPARSER.has_section("besapi"):
                    self.CONFPARSER.add_section("besapi")
                self.CONFPARSER.set("besapi", "BES_ROOT_SERVER", root_server)
            else:
                self.BES_ROOT_SERVER = None

        if len(self.BES_PASSWORD if self.BES_PASSWORD else "") < 1:
            self.BES_PASSWORD = getpass.getpass()
            if not self.CONFPARSER.has_section("besapi"):
                self.CONFPARSER.add_section("besapi")
            self.CONFPARSER.set("besapi", "BES_PASSWORD", self.BES_PASSWORD)

        if self.BES_USER_NAME and self.BES_ROOT_SERVER and self.BES_PASSWORD:
            try:
                self.bes_conn = besapi.BESConnection(
                    self.BES_USER_NAME, self.BES_PASSWORD, self.BES_ROOT_SERVER
                )
                if self.bes_conn.login():
                    self.pfeedback("Login Successful!")
                else:
                    self.perror("Login Failed!")
                    # clear likely bad password
                    self.BES_PASSWORD = None
                    # clear failed connection
                    self.bes_conn = None
            except requests.exceptions.HTTPError as err:
                self.perror(err)
                self.num_errors += 1
                self.pfeedback("-- clearing likely bad password --")
                self.BES_PASSWORD = None
                # clear failed connection
                self.bes_conn = None
                self.do_ls()
                if self.debug:
                    # this will allow the stacktrace to be printed
                    raise
            except requests.exceptions.ConnectionError as err:
                self.perror(err)
                self.num_errors += 1
                self.pfeedback("-- clearing likely bad root server --")
                self.BES_ROOT_SERVER = None
                # clear failed connection
                self.bes_conn = None
                self.do_ls()
                if self.debug:
                    # this will allow the stacktrace to be printed
                    raise
        else:
            self.perror("Login Error!")

    def do_logout(self, _=None):
        """Logout and clear session."""
        if self.bes_conn:
            self.bes_conn.logout()
            # del self.bes_conn
            # self.bes_conn = None
        self.pfeedback("Logout Complete!")

    def do_debug(self, setting):
        """Enable or Disable Debug Mode."""
        self.poutput(bool(setting))
        self.debug = bool(setting)
        self.echo = bool(setting)
        self.quiet = bool(setting)
        self.timing = bool(setting)
        if bool(setting):
            logging.getLogger("besapi").setLevel(logging.DEBUG)
        else:
            logging.getLogger("besapi").setLevel(logging.WARNING)

    def do_clear(self, arg=None):
        """Clear current config and logout."""
        if self.bes_conn:
            self.bes_conn.logout()
            # self.bes_conn = None
        if arg and "root" in arg.lower():
            self.pfeedback(" - clearing root server parameter -")
            self.BES_ROOT_SERVER = None
        if arg and "user" in arg.lower():
            self.pfeedback(" - clearing user parameter -")
            self.BES_USER_NAME = None
        if arg and "pass" in arg.lower():
            self.pfeedback(" - clearing password parameter -")
            self.BES_PASSWORD = None
        if not arg:
            self.pfeedback(" - clearing all parameters -")
            self.BES_ROOT_SERVER = None
            self.BES_USER_NAME = None
            self.BES_PASSWORD = None

    def do_saveconfig(self, arg=None):
        """Save current config to file."""
        self.do_saveconf(arg)

    def do_saveconf(self, _=None):
        """Save current config to file."""
        if not self.bes_conn:
            self.do_login()
        if not self.bes_conn:
            self.poutput("Can't save config without working login")
        else:
            conf_file_path = self.conf_path
            self.pfeedback(f"Saving Config File to: {conf_file_path}")
            with open(conf_file_path, "w") as configfile:
                self.CONFPARSER.write(configfile)

    def do_showconfig(self, arg=None):
        """List the current settings and connection status."""
        self.do_ls(arg)

    def do_ls(self, _=None):
        """List the current settings and connection status."""
        self.poutput("        Connected: " + str(bool(self.bes_conn)))
        self.poutput(
            "  BES_ROOT_SERVER: "
            + (self.BES_ROOT_SERVER if self.BES_ROOT_SERVER else "")
        )
        self.poutput(
            "    BES_USER_NAME: " + (self.BES_USER_NAME if self.BES_USER_NAME else "")
        )
        self.poutput(
            "  Password Length: "
            + str(len(self.BES_PASSWORD if self.BES_PASSWORD else ""))
        )
        self.poutput(" Config File Path: " + self.conf_path)
        if self.bes_conn:
            self.poutput(
                "Current Site Path: " + self.bes_conn.get_current_site_path(None)
            )

    def do_error_count(self, _=None):
        """Output the number of errors."""
        self.poutput(f"Error Count: {self.num_errors}")

    def do_exit(self, _=None):
        """Exit this application."""
        self.exit_code = self.num_errors
        # no matter what I try I can't get anything but exit code 0 on windows
        return self.do_quit("")

    def do_am_i_main_operator(self, _=None):
        """Check if the connection user is a main operator user."""
        if not self.bes_conn:
            self.do_login()
        if not self.bes_conn:
            self.poutput("ERROR: can't check without login")
        else:
            self.poutput(f"Am I Main Operator? {self.bes_conn.am_i_main_operator()}")

    def do_query(self, statement):
        """Get Session Relevance Results."""
        if not self.bes_conn:
            self.do_login()
        if not self.bes_conn:
            self.poutput("ERROR: can't query without login")
        else:
            if statement.raw:
                # get everything after `query `
                rel_text = statement.raw.split(" ", 1)[1]
                self.pfeedback(f"Q: {rel_text}")
                rel_result = self.bes_conn.session_relevance_string(rel_text)
                self.pfeedback("A: ")
                self.poutput(rel_result)

    def do_version(self, _=None):
        """Output version of besapi."""
        self.poutput(f"besapi version: {__version__}")

    def do_get_action(self, statement=None):
        """Usage: get_action 123."""
        result_op = self.bes_conn.get(f"action/{statement}")
        self.poutput(result_op)

    def do_get_operator(self, statement=None):
        """Usage: get_operator ExampleOperatorName."""
        result_op = self.bes_conn.get_user(statement)
        self.poutput(result_op)

    def do_get_current_site(self, _=None):
        """Output current site path context."""
        self.poutput(
            f"Current Site Path: `{self.bes_conn.get_current_site_path(None)}`"
        )

    def do_set_current_site(self, statement=None):
        """Set current site path context."""
        self.poutput(
            f"New Site Path: `{self.bes_conn.set_current_site_path(statement)}`"
        )

    def do_get_content(self, resource_url):
        """Get a specific item by resource url."""
        self.poutput(self.bes_conn.get_content_by_resource(resource_url))

    def do_export_item_by_resource(self, statement):
        """Export content itemb to current folder."""
        self.poutput(self.bes_conn.export_item_by_resource(statement))

    def do_export_site(self, site_path):
        """Export site contents to current folder."""
        self.bes_conn.export_site_contents(
            site_path, verbose=True, include_site_folder=False, include_item_ids=False
        )

    def do_export_all_sites(self, _=None):
        """Export site contents to current folder."""
        self.bes_conn.export_all_sites(verbose=False)

    complete_import_bes = Cmd.path_complete

    def do_import_bes(self, statement):
        """Import bes file."""

        bes_file_path = str(statement.args).strip()

        site_path = self.bes_conn.get_current_site_path(None)

        self.poutput(f"Import file: {bes_file_path}")

        self.poutput(self.bes_conn.import_bes_to_site(bes_file_path, site_path))

    complete_upload = Cmd.path_complete

    def do_upload(self, file_path):
        """Upload file to root server."""
        if not os.access(file_path, os.R_OK):
            self.poutput(file_path, "is not a readable file")
        else:
            upload_result = self.bes_conn.upload(file_path)
            self.poutput(upload_result)
            self.poutput(self.bes_conn.parse_upload_result_to_prefetch(upload_result))

    complete_create_group = Cmd.path_complete

    def do_create_group(self, file_path):
        """Create bigfix group from bes file."""
        if not os.access(file_path, os.R_OK):
            self.poutput(file_path, "is not a readable file")
        else:
            self.poutput(self.bes_conn.create_group_from_file(file_path))

    complete_create_user = Cmd.path_complete

    def do_create_user(self, file_path):
        """Create bigfix user from bes file."""
        if not os.access(file_path, os.R_OK):
            self.poutput(file_path, "is not a readable file")
        else:
            self.poutput(self.bes_conn.create_user_from_file(file_path))

    complete_create_site = Cmd.path_complete

    def do_create_site(self, file_path):
        """Create bigfix site from bes file."""
        if not os.access(file_path, os.R_OK):
            self.poutput(file_path, "is not a readable file")
        else:
            self.poutput(self.bes_conn.create_site_from_file(file_path))

    complete_update_item = Cmd.path_complete

    def do_update_item(self, file_path):
        """Update bigfix content item from bes file."""
        if not os.access(file_path, os.R_OK):
            self.poutput(file_path, " is not a readable file")
        else:
            self.poutput(self.bes_conn.update_item_from_file(file_path))

    def do_serverinfo(self, _=None):
        """Get server info and return formatted."""

        # not sure what the minimum version for this is:
        result = self.bes_conn.get("serverinfo")

        result_json = json.loads(result.text)

        self.poutput(f"\nServer Info for {self.BES_ROOT_SERVER}")
        self.poutput(json.dumps(result_json, indent=2))


def main():
    """Run the command loop if invoked."""
    BESCLInterface().cmdloop()


if __name__ == "__main__":
    logging.basicConfig()
    main()
