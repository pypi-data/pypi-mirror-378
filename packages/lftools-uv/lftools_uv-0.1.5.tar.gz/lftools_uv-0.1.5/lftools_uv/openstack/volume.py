# -*- code: utf-8 -*-
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""volume related sub-commands for openstack command."""

__author__ = "Thanh Ha"

import sys
from datetime import datetime, timedelta

import openstack
import openstack.config
from openstack.cloud.exc import OpenStackCloudException


def _filter_volumes(volumes, days=0):
    """Filter volume data and return list."""
    filtered = []
    for volume in volumes:
        if days and (
            datetime.strptime(volume.created_at, "%Y-%m-%dT%H:%M:%S.%f") >= datetime.now() - timedelta(days=days)
        ):
            continue

        filtered.append(volume)
    return filtered


def list(os_cloud, days=0):
    """List volumes found according to parameters."""
    cloud = openstack.connection.from_config(cloud=os_cloud)
    volumes = cloud.list_volumes()

    filtered_volumes = _filter_volumes(volumes, days)
    for volume in filtered_volumes:
        print(volume.name)


def cleanup(os_cloud, days=0):
    """Remove volume from cloud.

    :arg str os_cloud: Cloud name as defined in OpenStack clouds.yaml.
    :arg int days: Filter volumes that are older than number of days.
    """

    def _remove_volumes_from_cloud(volumes, cloud):
        print(f"Removing {len(volumes)} volumes from {cloud.cloud_config.name}.")
        for volume in volumes:
            try:
                result = cloud.delete_volume(volume.name)
            except OpenStackCloudException as e:
                if str(e).startswith("Multiple matches found for"):
                    print(f"WARNING: {str(e)}. Skipping volume...")
                    continue
                else:
                    print(f"ERROR: Unexpected exception: {str(e)}")
                    raise

            if not result:
                print(
                    f'WARNING: Failed to remove "{volume.name}" from {cloud.cloud_config.name}. Possibly already deleted.'
                )
            else:
                print(f'Removed "{volume.name}" from {cloud.cloud_config.name}.')

    cloud = openstack.connection.from_config(cloud=os_cloud)
    volumes = cloud.list_volumes()
    filtered_volumes = _filter_volumes(volumes, days)
    _remove_volumes_from_cloud(filtered_volumes, cloud)


def remove(os_cloud, volume_id, minutes=0):
    """Remove a volume from cloud.

    :arg str os_cloud: Cloud name as defined in OpenStack clouds.yaml.
    :arg str volume_id: Volume ID to delete
    :arg int minutes: Only delete volume if it is older than number of minutes.
    """
    cloud = openstack.connection.from_config(cloud=os_cloud)
    volume = cloud.get_volume_by_id(volume_id)

    if not volume:
        print("ERROR: volume not found.")
        sys.exit(1)

    if datetime.strptime(volume.created_at, "%Y-%m-%dT%H:%M:%S.%f") >= datetime.utcnow() - timedelta(minutes=minutes):
        print(f'WARN: volume "{volume.name}" is not older than {minutes} minutes.')
    else:
        cloud.delete_volume(volume.id)
