#!/usr/bin/env python

# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
import sys

from assemble_workflow.assemble_args import AssembleArgs
from assemble_workflow.bundle_recorder import BundleRecorder
from assemble_workflow.bundles import Bundles
from manifests.build_manifest import BuildManifest
from system import console


def main():
    args = AssembleArgs()

    console.configure(level=args.logging_level)

    build_manifest = BuildManifest.from_file(args.manifest)
    build = build_manifest.build
    artifacts_dir = os.path.dirname(os.path.realpath(args.manifest.name))
    output_dir = os.path.join(os.getcwd(), "dist")
    os.makedirs(output_dir, exist_ok=True)

    logging.info(f"Bundling {build.name} ({build.architecture}) on {build.platform} into {output_dir} ...")

    bundle_recorder = BundleRecorder(build, output_dir, artifacts_dir, args.base_url)

    with Bundles.create(build_manifest, artifacts_dir, bundle_recorder, args.keep) as bundle:
        bundle.install_min()
        bundle.install_plugins()
        logging.info(f"Installed plugins: {bundle.installed_plugins}")

        #  Save a copy of the manifest inside of the tar
        bundle_recorder.write_manifest(bundle.min_dist.archive_path)
        bundle.package(output_dir)

        bundle_recorder.write_manifest(output_dir)

    logging.info("Done.")


if __name__ == "__main__":
    sys.exit(main())
