#!/usr/bin/env python3
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2017 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Typer Jenkins CLI commands."""

import configparser
import logging
import os
from urllib.error import HTTPError

import requests
import typer

from lftools_uv import config as lftools_cfg
from lftools_uv.jenkins import Jenkins
from lftools_uv.jenkins.token import get_token

log = logging.getLogger(__name__)

# Create the main Typer app for jenkins commands
jenkins_app = typer.Typer(help="Query information about the Jenkins Server.")

# Create sub-apps for command groups
builds_app = typer.Typer(help="Information regarding current builds and the queue.")
jobs_app = typer.Typer(help="Command to update Jenkins Jobs.")
nodes_app = typer.Typer(help="Find information about builders connected to Jenkins Master.")
plugins_app = typer.Typer(help="Inspect Jenkins plugins on the server.")
token_app = typer.Typer(help="Get API token.")

# Add sub-apps to main app
jenkins_app.add_typer(builds_app, name="builds")
jenkins_app.add_typer(jobs_app, name="jobs")
jenkins_app.add_typer(nodes_app, name="nodes")
jenkins_app.add_typer(plugins_app, name="plugins")
jenkins_app.add_typer(token_app, name="token")


# Global callback for jenkins app to initialize Jenkins client
@jenkins_app.callback()
def jenkins_callback(
    ctx: typer.Context,
    conf: str | None = typer.Option(None, "--conf", "-c", help="Path to jenkins_jobs.ini config."),
    server: str = typer.Option(
        "jenkins",
        "--server",
        "-s",
        envvar="JENKINS_URL",
        help="The URL to a Jenkins server. Alternatively the jenkins_jobs.ini section to parse for url/user/password configuration if available.",
    ),
    user: str = typer.Option("admin", "--user", "-u", envvar="JENKINS_USER"),
    password: str | None = typer.Option(None, "--password", "-p", envvar="JENKINS_PASSWORD"),
):
    """Query information about the Jenkins Server."""
    # Skip initialization if we're just showing help
    if ctx.resilient_parsing:
        return

    try:
        # Initialize the Jenkins object and pass it to sub-commands
        jenkins_client = Jenkins(server, user, password, config_file=conf)
        if ctx.obj is None:
            ctx.obj = {}
        ctx.obj["jenkins"] = jenkins_client

        # Also store credentials for compatibility
        ctx.obj["username"] = user
        ctx.obj["password"] = password

        # Register in AppState if available
        state = ctx.obj.get("state")
        if state:
            state.jenkins = jenkins_client
    except Exception as e:
        log.error(f"Failed to initialize Jenkins client: {e}")
        # For help requests, don't fail - just continue without initializing client
        if ctx.obj is None:
            ctx.obj = {}


# Main jenkins commands
@jenkins_app.command("get-credentials")
def get_credentials(ctx: typer.Context):
    """Print all available Credentials."""
    try:
        jenkins = ctx.obj["jenkins"]
        groovy_script = """
import com.cloudbees.plugins.credentials.*

println "Printing all the credentials and passwords..."
def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardUsernameCredentials.class,
    Jenkins.instance,
    null,
    null
);

for (c in creds) {
    try {
        println(c.id + " : " + c.password )
    } catch (MissingPropertyException) {}
}
"""
        result = jenkins.server.run_script(groovy_script)
        log.info(result)
    except Exception as e:
        log.error(f"Failed to get credentials: {e}")
        raise typer.Exit(1) from None


@jenkins_app.command("get-secrets")
def get_secrets(ctx: typer.Context):
    """Print all available secrets."""
    try:
        jenkins = ctx.obj["jenkins"]
        groovy_script = """
import com.cloudbees.plugins.credentials.*

println "Printing all secrets..."
def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    Jenkins.instance,
    null,
    null
);

for (c in creds) {
    try {
        println(c.id + " : " + c.secret )
    } catch (MissingPropertyException) {}
}
"""
        result = jenkins.server.run_script(groovy_script)
        log.info(result)
    except Exception as e:
        log.error(f"Failed to get secrets: {e}")
        raise typer.Exit(1) from None


@jenkins_app.command("get-private-keys")
def get_private_keys(ctx: typer.Context):
    """Print all available SSH User Private Keys."""
    try:
        jenkins = ctx.obj["jenkins"]
        groovy_script = """
import com.cloudbees.plugins.credentials.*
import com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey

println "Printing all SSH User Private keys ..."
def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.Credentials.class,
    Jenkins.instance,
    null,
    null
);

for (c in creds) {
    if(c instanceof BasicSSHUserPrivateKey) {
        println("SSH Private key ID: " + c.getId())
        println("SSH User name: " + c.getUsername())
        println("SSH Private key passphrase: " + c.getPassphrase())
        println("SSH Private key: " + c.getPrivateKey())
    }
}
"""
        result = jenkins.server.run_script(groovy_script)
        log.info(result)
    except Exception as e:
        log.error(f"Failed to get private keys: {e}")
        raise typer.Exit(1) from None


@jenkins_app.command("groovy")
def groovy(ctx: typer.Context, groovy_file: str = typer.Argument(..., help="Path to groovy script file")):
    """Run a groovy script."""
    try:
        with open(groovy_file) as f:
            data = f.read()

        jenkins = ctx.obj["jenkins"]
        result = jenkins.server.run_script(data)
        log.info(result)
    except FileNotFoundError:
        log.error(f"Groovy file not found: {groovy_file}")
        raise typer.Exit(1) from None
    except Exception as e:
        log.error(f"Failed to run groovy script: {e}")
        raise typer.Exit(1) from None


@jenkins_app.command("quiet-down")
def quiet_down(
    ctx: typer.Context,
    yes: bool = typer.Option(False, "--yes", "-y", help="Proceed without confirmation"),
):
    """Put Jenkins into 'Quiet Down' mode."""
    try:
        jenkins = ctx.obj["jenkins"]
        version = jenkins.server.get_version()

        # Ask permission first if not auto-confirmed
        if not yes:
            confirmed = typer.confirm("Quiet down Jenkins?")
            if not confirmed:
                log.info("Operation cancelled.")
                return

        jenkins.server.quiet_down()
    except HTTPError as m:
        if m.code == 405:
            log.error(
                f"\n[{m}]\nJenkins {version} does not support Quiet Down "
                "without a CSRF Token. (CVE-2017-04-26)\nPlease "
                "file a bug with 'python-jenkins'"
            )
            raise typer.Exit(1) from None
        else:
            log.error(f"HTTP error: {m}")
            raise typer.Exit(1) from None
    except Exception as e:
        log.error(f"Failed to quiet down Jenkins: {e}")
        raise typer.Exit(1) from None


@jenkins_app.command("remove-offline-nodes")
def remove_offline_nodes(
    ctx: typer.Context,
    force: bool = typer.Option(
        False, "--force", help="Forcibly remove nodes, use only if the non-force version fails."
    ),
):
    """Remove any offline nodes."""
    try:
        jenkins = ctx.obj["jenkins"]

        groovy_script = """
import hudson.model.*

def numberOfflineNodes = 0
def numberNodes = 0

slaveNodes = hudson.model.Hudson.instance

for (slave in slaveNodes.nodes) {
    def node = slave.computer
    numberNodes ++
    println ""
    println "Checking node ${node.name}:"
    println '\tcomputer.isOffline: ${slave.getComputer().isOffline()}'
    println '\tcomputer.offline: ${node.offline}'

    if (node.offline) {
        numberOfflineNodes ++
        println '\tRemoving node ${node.name}'
        slaveNodes.removeNode(slave)
    }
}

println "Number of Offline Nodes: " + numberOfflineNodes
println "Number of Nodes: " + numberNodes
"""

        force_script = """
import jenkins.*
import jenkins.model.*
import hudson.*
import hudson.model.*

for (node in Jenkins.instance.computers) {
    try {
        println "Checking node: ${node.name}"
        println "\tdisplay-name: ${node.properties.displayName}"
        println "\toffline: ${node.properties.offline}"
        println "\ttemporarily-offline: ${node.properties.temporarilyOffline}"
        if (node.properties.offline) {
            println "Removing bad node: ${node.name}"
            Jenkins.instance.removeComputer(node)
        }
        println ""
    }
    catch (NullPointerException nullPointer) {
        println "NullPointerException caught"
        println ""
    }
}
"""

        if force:
            result = jenkins.server.run_script(force_script)
        else:
            result = jenkins.server.run_script(groovy_script)
        log.info(result)
    except Exception as e:
        log.error(f"Failed to remove offline nodes: {e}")
        raise typer.Exit(1) from None


# Builds subcommands
@builds_app.command("running")
def builds_running(ctx: typer.Context):
    """Show all the currently running builds."""
    try:
        jenkins = ctx.obj["jenkins"]
        running_builds = jenkins.server.get_running_builds()

        for build in running_builds:
            log.info("- %s on %s", build["name"], build["node"])
    except Exception as e:
        log.error(f"Failed to get running builds: {e}")
        raise typer.Exit(1) from None


@builds_app.command("queued")
def builds_queued(ctx: typer.Context):
    """Show all jobs waiting in the queue and their status."""
    try:
        jenkins = ctx.obj["jenkins"]
        queue = jenkins.server.get_queue_info()

        queue_length = len(queue)
        log.info("Build Queue (%s)", queue_length)
        for build in queue:
            status_flags = []
            if build.get("stuck"):
                status_flags.append("[Stuck]")
            if build.get("blocked"):
                status_flags.append("[Blocked]")
            log.info(" - %s%s", build["task"]["name"], (" " + " ".join(status_flags)) if status_flags else "")
    except Exception as e:
        log.error(f"Failed to get queued builds: {e}")
        raise typer.Exit(1) from None


# Jobs subcommands
enable_disable_jobs = """
import jenkins.*
import jenkins.model.*
import hudson.*
import hudson.model.*

def jobTypes = [hudson.model.FreeStyleProject.class]

def filter = {{job->
    if (job.disabled == true) {{
        println("${{job.fullName}}")
    }}
    job.getDisplayName().contains("{0}")
}}

def disableClosure = {{job->job.{1}()}}

jobTypes.each{{ className->
    jenkins.model.Jenkins.instance.getAllItems(className).findAll(filter).each(disableClosure)}}
"""


@jobs_app.command("enable")
def jobs_enable(ctx: typer.Context, regex: str = typer.Argument(..., help="Regex pattern to match job names")):
    """Enable all Jenkins jobs matching REGEX."""
    try:
        jenkins = ctx.obj["jenkins"]
        result = jenkins.server.run_script(enable_disable_jobs.format(regex, "enable"))
        log.info(result)
    except Exception as e:
        log.error(f"Failed to enable jobs: {e}")
        raise typer.Exit(1) from None


@jobs_app.command("disable")
def jobs_disable(ctx: typer.Context, regex: str = typer.Argument(..., help="Regex pattern to match job names")):
    """Disable all Jenkins jobs matching REGEX."""
    try:
        jenkins = ctx.obj["jenkins"]
        result = jenkins.server.run_script(enable_disable_jobs.format(regex, "disable"))
        log.info(result)
    except Exception as e:
        log.error(f"Failed to disable jobs: {e}")
        raise typer.Exit(1) from None


# Nodes subcommands
def offline_str(status):
    """Convert the offline node status from a boolean to a string."""
    if status:
        return "Offline"
    return "Online"


@nodes_app.command("list")
def nodes_list(ctx: typer.Context):
    """List Jenkins nodes."""
    try:
        jenkins = ctx.obj["jenkins"]
        node_list = jenkins.server.get_nodes()

        for node in node_list:
            log.info("%s [%s]", node["name"], offline_str(node["offline"]))
    except Exception as e:
        log.error(f"Failed to list nodes: {e}")
        raise typer.Exit(1) from None


# Plugins subcommands
def checkmark(truthy):
    """Return a UTF-8 Checkmark or Cross depending on the truthiness of the argument."""
    if truthy:
        return "\u2713"
    return "\u2717"


def print_plugin(plugin, namefield="longName"):
    """Log the plugin longName and version."""
    log.info("%s:%s", plugin[namefield], plugin["version"])


@plugins_app.command("list")
def plugins_list(ctx: typer.Context):
    """List installed plugins.

    Defaults to listing all installed plugins and their current versions
    """
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list plugins: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("pinned")
def plugins_pinned(ctx: typer.Context):
    """List pinned plugins."""
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if plugin["pinned"]:
                print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list pinned plugins: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("dynamic")
def plugins_dynamic(ctx: typer.Context):
    """List dynamically reloadable plugins."""
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if plugin["supportsDynamicLoad"] == "YES":
                print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list dynamic plugins: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("needs-update")
def plugins_needs_update(ctx: typer.Context):
    """List pending plugin updates."""
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if plugin["hasUpdate"]:
                print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list plugins needing updates: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("enabled")
def plugins_enabled(ctx: typer.Context):
    """List enabled plugins."""
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if plugin["enabled"]:
                print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list enabled plugins: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("disabled")
def plugins_disabled(ctx: typer.Context):
    """List disabled plugins.

    TODO: In the future this should be part of a command alias and pass a flag
    to 'enabled' so that we don't duplicate code.
    """
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if not plugin["enabled"]:
                print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list disabled plugins: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("active")
def plugins_active(ctx: typer.Context):
    """List active plugins."""
    try:
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if plugin["active"]:
                print_plugin(plugin)
    except Exception as e:
        log.error(f"Failed to list active plugins: {e}")
        raise typer.Exit(1) from None


@plugins_app.command("sec")
def plugins_sec(ctx: typer.Context):
    """List plugins with a known vulnerability.

    Output is in the format:

    Vulnerable Version\t Installed Version\t Link.
    """
    try:
        r = requests.get("http://updates.jenkins-ci.org/update-center.actual.json")
        warn = r.json()["warnings"]

        # create a dict of relevant info from jenkins update center
        secdict = {}
        for w in warn:
            name = w["name"]
            url = w["url"]
            for version in w["versions"]:
                lastversion = version.get("lastVersion")
            nv = {name: lastversion}
            secdict.update(nv)

        # create a dict of our active plugins
        activedict = {}
        jenkins = ctx.obj["jenkins"]
        plugins = jenkins.server.get_plugins()
        for key in plugins.keys():
            _, plugin_name = key
            plugin = plugins[plugin_name]
            if plugin["active"]:
                name = plugin["shortName"]
                version = plugin["version"]
                nv = {name: version}
                activedict.update(nv)

        # find the delta
        shared = []
        for key in set(secdict.keys()) & set(activedict.keys()):
            shared.append(key)
            ourversion = activedict[key]
            theirversion = secdict[key]
            t1 = (ourversion,)
            t2 = (theirversion,)
            if t1 <= t2:
                # Print Vulnerable Version\t Installed Version\t Link
                for w in warn:
                    name = w["name"]
                    url = w["url"]
                    for version in w["versions"]:
                        lastversion = version.get("lastVersion")
                    if name == key and secdict[key] == lastversion:
                        log.info("%s:%s\t%s:%s\t%s", key, secdict[key], key, activedict[key], url)
    except Exception as e:
        log.error(f"Failed to check plugin security: {e}")
        raise typer.Exit(1) from None


# Token subcommands
def _require_jjb_ini(config):
    if not os.path.isfile(config):
        log.error("jenkins_jobs.ini not found in any of the search paths. Please provide one before proceeding.")
        raise typer.Exit(1)


@token_app.command("change")
def token_change(
    ctx: typer.Context,
    name: str = typer.Option("token-created-by-lftools", "--name", help="set token name"),
):
    """Generate a new API token."""
    try:
        jenkins = ctx.obj["jenkins"]
        username = ctx.obj["username"]
        password = ctx.obj["password"]

        if not username or not password:
            log.error("Username or password not set.")
            raise typer.Exit(1)

        log.info(get_token(name, jenkins.url, change=True, username=username, password=password))
    except Exception as e:
        log.error(f"Failed to change token: {e}")
        raise typer.Exit(1) from None


@token_app.command("init")
def token_init(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Server name for configuration"),
    url: str = typer.Argument(..., help="Jenkins server URL"),
):
    """Initialize jenkins_jobs.ini config for new server section."""
    try:
        jenkins = ctx.obj["jenkins"]
        username = ctx.obj["username"]
        password = ctx.obj["password"]

        if not username or not password:
            log.error("Username or password not set.")
            raise typer.Exit(1)

        _require_jjb_ini(jenkins.config_file)

        config = configparser.ConfigParser()
        config.read(jenkins.config_file)

        token = get_token(name, url, username, password, change=True)
        try:
            config.add_section(name)
        except configparser.DuplicateSectionError as e:
            log.error(e)
            raise typer.Exit(1) from None

        config.set(name, "url", url)
        username_setting = lftools_cfg.get_setting("global", "username")
        username_str = username_setting if isinstance(username_setting, str) else str(username_setting)
        config.set(name, "user", username_str)
        # Ensure token is a string for config.set
        token_str = str(token) if token is not None else ""
        config.set(name, "password", token_str)

        with open(jenkins.config_file, "w") as configfile:
            config.write(configfile)
    except Exception as e:
        log.error(f"Failed to initialize token: {e}")
        raise typer.Exit(1) from None


@token_app.command("print")
def token_print(ctx: typer.Context):
    """Print current API token."""
    try:
        jenkins = ctx.obj["jenkins"]
        username = ctx.obj["username"]
        password = ctx.obj["password"]

        if not username or not password:
            log.error("Username or password not set.")
            raise typer.Exit(1)

        log.info(get_token("token", jenkins.url, username, password))
    except Exception as e:
        log.error(f"Failed to print token: {e}")
        raise typer.Exit(1) from None


@token_app.command("reset")
def token_reset(
    ctx: typer.Context,
    servers: list[str] | None = typer.Argument(None, help="Server names to reset tokens for"),
):
    """Regenerate API tokens for configurations in jenkins_jobs.ini.

    This command has 2 modes to reset API tokens:

    1. Single-server: Resets the API token and returns the new token value.
    2. Multi-server: Resets the API token for a provided list of servers and
       returns a summary of the outcome.

    If the server parameter is NOT passed then all servers listed in the
    configuration file will be reset via multi-server mode.
    """
    try:
        jenkins = ctx.obj["jenkins"]
        username = ctx.obj["username"]
        password = ctx.obj["password"]

        if not username or not password:
            log.error("Username or password not set.")
            raise typer.Exit(1)

        _require_jjb_ini(jenkins.config_file)

        def _reset_key(config, server):
            url = config.get(server, "url")

            try:
                token = get_token(url, change=True, username=username, password=password)
                config.set(server, "password", token)
                with open(jenkins.config_file, "w") as configfile:
                    config.write(configfile)
                return token
            except requests.exceptions.ConnectionError:
                return None

        fail = 0
        success = 0
        config = configparser.ConfigParser()
        config.read(jenkins.config_file)

        if not servers or len(servers) == 0:
            cfg_sections = config.sections()
        elif len(servers) == 1:
            key = _reset_key(config, servers[0])
            log.info(key)
            return
        else:
            cfg_sections = list(servers)

        for section in cfg_sections:
            if not config.has_option(section, "url"):
                log.debug("Section does not contain a url, skipping...")
                continue

            log.info(f"Resetting API key for {section}")
            if _reset_key(config, section):
                success += 1
            else:
                fail += 1
                log.error(f"Failed to reset API key for {section}")

        log.info("Update configurations complete.")
        log.info(f"Success: {success}")
        log.info(f"Failed: {fail}")
    except Exception as e:
        log.error(f"Failed to reset tokens: {e}")
        raise typer.Exit(1) from None
