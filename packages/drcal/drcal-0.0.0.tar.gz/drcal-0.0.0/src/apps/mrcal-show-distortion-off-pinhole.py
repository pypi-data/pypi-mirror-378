#!/usr/bin/env python3

# Copyright (c) 2017-2023 California Institute of Technology ("Caltech"). U.S.
# Government sponsorship acknowledged. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

r"""Visualize the behavior or a lens model

SYNOPSIS

  $ mrcal-show-distortion-off-pinhole --vectorfield left.cameramodel

  ... a plot pops up showing the vector field of the difference from a pinhole
  projection

This tool is used to examine how a lens model behaves. Depending on the model,
the vectors could be very large or very small, and we can scale them by passing
'--vectorscale s'. By default we sample in a 60x40 grid, but this spacing can be
controlled by passing '--gridn w h'.

By default we render a heat map of the lens effects. We can also see the
vectorfield by passing in --vectorfield. Or we can see the radial distortion
curve by passing --radial

"""

import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--gridn",
        type=int,
        default=(60, 40),
        nargs=2,
        help="""How densely we should sample the imager. By default we report a 60x40 grid""",
    )

    parser.add_argument(
        "--vectorscale",
        type=float,
        default=1.0,
        help="""Scale the vectors by this factor. Default is 1.0 (report the truth), but this is often too small to see""",
    )

    parser.add_argument(
        "--radial",
        action="store_true",
        help="""Show the radial distortion scale factor instead of a colormap/vectorfield""",
    )
    parser.add_argument(
        "--vectorfield",
        action="store_true",
        default=False,
        help="""Plot the diff as a vector field instead of as a heat map. The vector field
                        contains more information (magnitude AND direction), but
                        is less clear at a glance""",
    )

    parser.add_argument(
        "--show-fisheye-projections",
        action="store_true",
        help="""If given, the radial plots include the behavior of common fisheye
                        projections, in addition to the behavior of THIS lens""",
    )
    parser.add_argument(
        "--cbmax", type=float, default=10, help="""Maximum range of the colorbar"""
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
        help="""Write the output to disk, instead of making an interactive plot""",
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
        help="""Extra 'set' directives to pass to gnuplotlib. May be given multiple
                        times""",
    )
    parser.add_argument(
        "--unset",
        type=str,
        action="append",
        help="""Extra 'unset' directives to pass to gnuplotlib. May be given multiple
                        times""",
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


import mrcal


try:
    model = mrcal.cameramodel(args.model)
except Exception as e:
    print(f"Couldn't load camera model '{args.model}': {e}", file=sys.stderr)
    sys.exit(1)

if args.radial and args.vectorfield:
    sys.stderr.write(
        "Usage error: at most one of --radial and --vectorfield can be given\n"
    )
    sys.exit(1)

plotkwargs = {}
if args.set is not None:
    plotkwargs["set"] = args.set
if args.unset is not None:
    plotkwargs["unset"] = args.unset

if args.title is not None:
    plotkwargs["title"] = args.title
if args.extratitle is not None:
    plotkwargs["extratitle"] = args.extratitle

if args.radial:
    try:
        plot = mrcal.show_distortion_off_pinhole_radial(
            model,
            show_fisheye_projections=args.show_fisheye_projections,
            hardcopy=args.hardcopy,
            terminal=args.terminal,
            **plotkwargs,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
else:
    plot = mrcal.show_distortion_off_pinhole(
        model,
        vectorfield=args.vectorfield,
        vectorscale=args.vectorscale,
        cbmax=args.cbmax,
        gridn_width=args.gridn[0],
        gridn_height=args.gridn[1],
        hardcopy=args.hardcopy,
        terminal=args.terminal,
        **plotkwargs,
    )

if args.hardcopy is None:
    plot.wait()
