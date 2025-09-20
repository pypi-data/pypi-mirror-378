#!/usr/bin/env python3
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Typer Gerrit CLI commands."""

import logging
from pprint import pformat

import typer

from lftools_uv.api.endpoints import gerrit
from lftools_uv.git.gerrit import Gerrit as git_gerrit

log = logging.getLogger(__name__)

# Create the Typer app for gerrit commands
gerrit_app = typer.Typer(help="GERRIT TOOLS.")


@gerrit_app.command("addfile")
def addfile(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
    filename: str = typer.Argument(..., help="Filename to add"),
    issue_id: str | None = typer.Option(
        None, "--issue-id", help="For projects that enforce an issue id for changesets"
    ),
    file_location: str | None = typer.Option(None, "--file-location", help="File path within the repository"),
):
    """Add a file for review to a Project.

    Requires gerrit directory.

    Example:

    gerrit_url gerrit.o-ran-sc.org/r
    gerrit_project test/test1
    """
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.add_file(gerrit_fqdn, gerrit_project, filename, issue_id, file_location)
        log.info(pformat(data))
    except Exception as e:
        log.error(f"Failed to add file: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("addinfojob")
def addinfojob(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
    jjbrepo: str = typer.Argument(..., help="JJB repository name"),
    issue_id: str | None = typer.Option(
        None, "--issue-id", help="For projects that enforce an issue id for changesets"
    ),
    agent: str | None = typer.Option(None, "--agent", help="Specify the Jenkins agent label to run the job on"),
):
    """Add an INFO job for a new Project.

    Adds info verify jenkins job for project.
    result['id'] can be used to amend a review
    so that multiple projects can have info jobs added
    in a single review

    Example:

    gerrit_url gerrit.o-ran-sc.org/r
    gerrit_project test/test1
    jjbrepo ci-mangement
    """
    try:
        git = git_gerrit(fqdn=gerrit_fqdn, project=jjbrepo)
        git.add_info_job(gerrit_fqdn, gerrit_project, issue_id, agent)
    except Exception as e:
        log.error(f"Failed to add info job: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("addgitreview")
def addgitreview(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
    issue_id: str | None = typer.Option(
        None, "--issue-id", help="For projects that enforce an issue id for changesets"
    ),
):
    """Add git review to a project.

    Example:
    gerrit_url gerrit.o-ran-sc.org
    gerrit_project test/test1
    """
    try:
        git = git_gerrit(fqdn=gerrit_fqdn, project=gerrit_project)
        git.add_git_review(gerrit_fqdn, gerrit_project, issue_id)
    except Exception as e:
        log.error(f"Failed to add git review: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("addgithubrights")
def addgithubrights(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
):
    """Grant Github read for a project.

    gerrit_url gerrit.o-ran-sc.org
    gerrit_project test/test1
    """
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.add_github_rights(gerrit_fqdn, gerrit_project)
        log.info(pformat(data))
    except Exception as e:
        log.error(f"Failed to add github rights: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("abandonchanges")
def abandonchanges(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
):
    """Abandon all OPEN changes for a gerrit project.

    gerrit_url gerrit.o-ran-sc.org
    gerrit_project test/test1
    """
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.abandon_changes(gerrit_fqdn, gerrit_project)
        log.info(pformat(data))
    except Exception as e:
        log.error(f"Failed to abandon changes: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("createproject")
def createproject(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
    ldap_group: str = typer.Argument(..., help="LDAP group name"),
    description: str = typer.Option(..., "--description", help="Project Description"),
    check: bool = typer.Option(False, "--check", help="just check if the project exists"),
):
    """Create a project via the gerrit API.

    Creates a gerrit project.
    Sets ldap group as owner.

    Example:

    gerrit_url gerrit.o-ran-sc.org/r
    gerrit_project test/test1
    ldap_group oran-gerrit-test-test1-committers
    """
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.create_project(gerrit_fqdn, gerrit_project, ldap_group, description, check)
        log.info(pformat(data))
    except Exception as e:
        log.error(f"Failed to create project: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("create-saml-group")
def create_saml_group(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    ldap_group: str = typer.Argument(..., help="LDAP group name"),
):
    """Create saml group based on ldap group."""
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.create_saml_group(gerrit_fqdn, ldap_group)
        log.info(pformat(data))
    except Exception as e:
        log.error(f"Failed to create SAML group: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("list-project-permissions")
def list_project_permissions(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    project: str = typer.Argument(..., help="Project name"),
):
    """List Owners of a Project."""
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.list_project_permissions(project)
        for ldap_group in data:
            log.info(pformat(ldap_group))
    except Exception as e:
        log.error(f"Failed to list project permissions: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("list-project-inherits-from")
def list_project_inherits_from(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
):
    """List who a project inherits from."""
    try:
        g = gerrit.Gerrit(fqdn=gerrit_fqdn)
        data = g.list_project_inherits_from(gerrit_project)
        log.info(data)
    except Exception as e:
        log.error(f"Failed to list project inheritance: {e}")
        raise typer.Exit(1) from None


@gerrit_app.command("addmavenconfig")
def addmavenconfig(
    gerrit_fqdn: str = typer.Argument(..., help="Gerrit FQDN"),
    gerrit_project: str = typer.Argument(..., help="Gerrit project name"),
    jjbrepo: str = typer.Argument(..., help="JJB repository name"),
    issue_id: str | None = typer.Option(
        None, "--issue-id", help="For projects that enforce an issue id for changesets"
    ),
    nexus3: str | None = typer.Option(None, "--nexus3", help="Specify a Nexus 3 server, e.g. nexus3.example.org"),
    nexus3_ports: str | None = typer.Option(
        None,
        "--nexus3-ports",
        help="Comma-separated list of ports supported by the Nexus 3 server specified",
    ),
):
    """Add maven config file for JCasC.

    The following options can be set in the gerrit server's entry in lftools.ini:
      * default_servers: Comma-separated list of servers using the <projectname>
        credential. Default: releases,snapshots,staging,site
      * additional_credentials: JSON-formatted string containing
        servername:credentialname pairings. This should be on a single line,
        without quotes surrounding the string.
      * nexus3: The nexus3 server url for a given project.
      * nexus3_ports: Comma-separated list of ports used by Nexus3.
        Default: 10001,10002,10003,10004
    """
    try:
        git = git_gerrit(fqdn=gerrit_fqdn, project=jjbrepo)
        git.add_maven_config(gerrit_fqdn, gerrit_project, issue_id, nexus3, nexus3_ports)
    except Exception as e:
        log.error(f"Failed to add maven config: {e}")
        raise typer.Exit(1) from None
