#!/usr/bin/env python3

# Copyright (c) 2017-2023 California Institute of Technology ("Caltech"). U.S.
# Government sponsorship acknowledged. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

r"""Visualize the expected projection error due to noise in calibration-time input

SYNOPSIS

  $ mrcal-show-projection-uncertainty left.cameramodel
  ... a plot pops up showing the projection uncertainty of the intrinsics in
  ... this model

The operation of this tool is documented at
https://mrcal.secretsauce.net/uncertainty.html

A calibration process produces the best-fitting camera parameters. To be able to
use these parameters we must know how trustworthy they are. This tool examines
the uncertainty of projection using a given camera model. The projection
operation uses the intrinsics only, but the uncertainty must take into account
the calibration-time extrinsics and the calibration-time observed object poses
as well. This tool visualizes the expected value of projection error across the
imager. Areas with a high expected projection error are unreliable, and
observations in those regions cannot be used for further work (localization,
mapping, etc).

There are several modes of operation:

- By default we look at projection of points some distance away from the camera
  (given by --distance). We evaluate the uncertainty of these projections
  everywhere across the imager, and display the results as a heatmap with
  overlaid contours

- With --vs-distance-at we evaluate the uncertainty along an observation ray
  mapping to a single pixel. We show the uncertainty vs distances from the
  camera along this ray

See https://mrcal.secretsauce.net/uncertainty.html for a full description of
the computation performed here

"""

import sys
import argparse
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--vs-distance-at",
        type=str,
        help="""If given, we don't compute the uncertainty
                        everywhere in the image at a constant distance from the
                        camera, but instead we look at different distances at
                        one pixel. This option takes a single argument: the
                        "X,Y" pixel coordinate we care about, or "center" to
                        look at the center of the imager or "centroid" to look
                        at the center of the calibration-time chessboards. This
                        is exclusive with --gridn and --distance and
                        --observations and --cbmax""",
    )
    parser.add_argument(
        "--gridn",
        type=int,
        default=(60, 40),
        nargs=2,
        help="""How densely we should sample the imager. By default we use a 60x40 grid""",
    )
    parser.add_argument(
        "--distance",
        type=float,
        help="""By default we display the projection uncertainty infinitely far away from the
                        camera. If we want to look closer in, the desired
                        observation distance can be given in this argument""",
    )
    parser.add_argument(
        "--isotropic",
        action="store_true",
        default=False,
        help="""By default I display the expected value of the projection error in the worst
                        possible direction of this error. If we want to plot the
                        RMS of the worst and best directions, pass --isotropic.
                        If we assume the errors will apply evenly in all
                        directions, then we can use this metric, which is
                        potentially easier to compute""",
    )
    parser.add_argument(
        "--method",
        choices=("mean-pcam", "bestq", "cross-reprojection-rrp-Jfp"),
        default="mean-pcam",
        help="""Multiple uncertainty quantification methods are available. We default to 'mean-pcam' """,
    )
    parser.add_argument(
        "--observations",
        action="store_true",
        default=False,
        help="""If given, I display the pixel observations at
                        calibration time. This should correspond to the
                        low-uncertainty regions.""",
    )
    parser.add_argument(
        "--valid-intrinsics-region",
        action="store_true",
        default=False,
        help="""If given, I overlay the valid-intrinsics region onto the plot""",
    )
    parser.add_argument(
        "--cbmax", type=float, default=3, help="""Maximum range of the colorbar"""
    )

    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="""Title string for the plot. Overrides the default
                        title. Exclusive with --extratitle""",
    )
    parser.add_argument(
        "--extratitle",
        type=str,
        default=None,
        help="""Additional string for the plot to append to the
                        default title. Exclusive with --title""",
    )

    parser.add_argument(
        "--hardcopy",
        type=str,
        help="""Write the output to disk, instead of an interactive plot""",
    )
    parser.add_argument(
        "--terminal",
        type=str,
        help=r"""gnuplotlib terminal. The default is good almost always, so most people don't
                        need this option""",
    )
    parser.add_argument(
        "--set",
        type=str,
        action="append",
        help="""Extra 'set' directives to gnuplotlib. Can be given multiple times""",
    )
    parser.add_argument(
        "--unset",
        type=str,
        action="append",
        help="""Extra 'unset' directives to gnuplotlib. Can be given multiple times""",
    )

    parser.add_argument(
        "model",
        type=str,
        help="""Input camera model. If "-' is given, we read standard input""",
    )

    return parser.parse_args()


args = parse_args()

if args.title is not None and args.extratitle is not None:
    print("--title and --extratitle are exclusive", file=sys.stderr)
    sys.exit(1)


# arg-parsing is done before the imports so that --help works without building
# stuff, so that I can generate the manpages and README
import numpy as np
import mrcal


if args.vs_distance_at is not None:
    if args.distance is not None or args.observations:
        print(
            "--vs-distance-at is exclusive with --gridn and --distance and --observations and --cbmax",
            file=sys.stderr,
        )
        sys.exit(1)

    if re.match("center$|centroid$", args.vs_distance_at):
        pass
    elif re.match(r"[0-9\.eEdD+-]+,[0-9\.eEdD+-]+$", args.vs_distance_at):
        # pixel coordinate given
        args.vs_distance_at = np.array(
            [float(x) for x in args.vs_distance_at.split(",")]
        )
    else:
        print(
            "--vs-distance-at must be given 'center' or 'centroid' or X,Y (pixel coordinates)",
            file=sys.stderr,
        )
        sys.exit(1)


plotkwargs_extra = {}
if args.set is not None:
    plotkwargs_extra["set"] = args.set
if args.unset is not None:
    plotkwargs_extra["unset"] = args.unset

if args.title is not None:
    plotkwargs_extra["title"] = args.title
if args.extratitle is not None:
    plotkwargs_extra["extratitle"] = args.extratitle

try:
    model = mrcal.cameramodel(args.model)
except Exception as e:
    print(f"Couldn't load camera model '{args.model}': {e}", file=sys.stderr)
    sys.exit(1)

if model.optimization_inputs() is None:
    print(
        "ERROR: optimization_inputs are unavailable in this model. Uncertainty cannot be computed",
        file=sys.stderr,
    )
    sys.exit()

if args.vs_distance_at is not None:
    plot = mrcal.show_projection_uncertainty_vs_distance(
        model,
        where=args.vs_distance_at,
        isotropic=args.isotropic,
        method=args.method,
        hardcopy=args.hardcopy,
        terminal=args.terminal,
        **plotkwargs_extra,
    )
else:
    plot = mrcal.show_projection_uncertainty(
        model,
        gridn_width=args.gridn[0],
        gridn_height=args.gridn[1],
        distance=args.distance,
        isotropic=args.isotropic,
        method=args.method,
        observations=args.observations,
        valid_intrinsics_region=args.valid_intrinsics_region,
        hardcopy=args.hardcopy,
        terminal=args.terminal,
        cbmax=args.cbmax,
        **plotkwargs_extra,
    )

if args.hardcopy is None:
    plot.wait()
