# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2018, 2023 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Jenkins."""

from __future__ import annotations

__author__ = "Thanh Ha"

import configparser
import logging
import os
from typing import Optional

import jenkins

log: logging.Logger = logging.getLogger(__name__)


def jjb_ini() -> str | None:
    """Return jenkins_jobs.ini file location if it exists, None otherwise."""
    # Check for environment variable first (allows override)
    env_conf = os.environ.get("JENKINS_JOBS_INI")
    if env_conf and os.path.isfile(env_conf):
        return env_conf

    # Standard lftools config location
    lftools_conf = os.path.join(os.path.expanduser("~"), ".config", "lftools", "jenkins_job.ini")

    # Legacy jenkins_jobs locations for backwards compatibility
    global_conf = "/etc/jenkins_jobs/jenkins_jobs.ini"
    user_conf = os.path.join(os.path.expanduser("~"), ".config", "jenkins_jobs", "jenkins_jobs.ini")
    local_conf = os.path.join(os.getcwd(), "jenkins_jobs.ini")

    conf = None
    if os.path.isfile(local_conf):
        conf = local_conf
    elif os.path.isfile(lftools_conf):
        conf = lftools_conf
    elif os.path.isfile(user_conf):
        conf = user_conf
    elif os.path.isfile(global_conf):
        conf = global_conf

    return conf


JJB_INI: str | None = jjb_ini()


class Jenkins:
    """lftools Jenkins object."""

    def __init__(
        self, server: str, user: str | None = None, password: str | None = None, config_file: str | None = None
    ) -> None:
        """Initialize a Jenkins object."""
        self.config_file: str | None = config_file
        if not self.config_file:
            self.config_file = JJB_INI

        if "://" not in server:
            if self.config_file:
                log.debug(f"Using config from {self.config_file}")
                config: configparser.ConfigParser = configparser.ConfigParser()
                config.read(self.config_file)
                if config.has_section(server):
                    user = config.get(server, "user")
                    password = config.get(server, "password")
                    server = config.get(server, "url")
                else:
                    log.error(f"[{server}] section not found in {self.config_file}")
            else:
                log.debug("jenkins_jobs.ini not found in any of the default paths.")
                server = "https://localhost:8080"

        self.server: jenkins.Jenkins = jenkins.Jenkins(server, username=user, password=password)  # type: ignore

        self.url: str = server
