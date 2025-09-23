#!/usr/bin/env python3

# Copyright (c) 2017-2023 California Institute of Technology ("Caltech"). U.S.
# Government sponsorship acknowledged. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

r"""Displays the calibration-time geometry: the cameras and the observed objects

SYNOPSIS

  $ mrcal-show-geometry *.cameramodel
  ... a plot pops up showing the camera arrangement

This tool visualizes the relative geometry between several cameras and the
calibration objects they observed when computing the calibration.

"""

import sys
import argparse
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--axis-scale",
        type=float,
        help="""Scale for the camera axes. By default a
                        reasonable default is chosen (see mrcal.show_geometry()
                        for the logic)""",
    )
    parser.add_argument(
        "--title", type=str, default=None, help="""Title string for the plot"""
    )
    parser.add_argument(
        "--hardcopy",
        type=str,
        help="""Write the output to disk, instead of making an
                        interactive plot. The output filename is given in the
                        option""",
    )
    parser.add_argument(
        "--terminal",
        type=str,
        help=r"""The gnuplotlib terminal. The default is almost
                        always right, so most people don't need this
                        option""",
    )

    parser.add_argument(
        "--show-calobjects",
        action="store_true",
        help="""If given, draw the calibration object
                        observations from the FIRST given camera model that
                        contains the optimization_inputs. Unlike
                        --show-calobjects-thiscamera, this option displays the
                        calibration objects observed by ALL cameras at
                        calibration time. Exclusive with
                        --show-calobjects-thiscamera""",
    )

    parser.add_argument(
        "--show-calobjects-thiscamera",
        action="store_true",
        help="""If given, draw the calibration object
                        observations from the FIRST given camera model that
                        contains the optimization_inputs. Unlike
                        --show-calobjects, this option displays the calibration
                        objects observed ONLY by the FIRST camera at calibration
                        time. Exclusive with --show-calobjects""",
    )

    parser.add_argument(
        "--show-points",
        action="store_true",
        help="""If given, draw the point observations from the
                        FIRST given camera model that contains the
                        optimization_inputs. Unlike --show-points-thiscamera,
                        this option displays the points observed by ALL cameras
                        at calibration time. Exclusive with
                        --show-points-thiscamera""",
    )

    parser.add_argument(
        "--show-points-thiscamera",
        action="store_true",
        help="""If given, draw the point observations from the
                        FIRST given camera model that contains the
                        optimization_inputs. Unlike --show-points, this option
                        displays the calibration objects observed ONLY by the
                        FIRST camera at calibration time. Exclusive with
                        --show-points""",
    )

    parser.add_argument(
        "--transforms",
        type=str,
        help="""Optional transforms.txt. This is a legacy file
                        representing an extra transformation for each camera
                        pair. If you need this, you know what it is""",
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
        "models",
        type=str,
        nargs="+",
        help="""Camera models to visualize. Any N cameras can be given""",
    )

    return parser.parse_args()


args = parse_args()

if args.show_calobjects and args.show_calobjects_thiscamera:
    print(
        "--show-calobjects and --show-calobjects-thiscamera are exclusive",
        file=sys.stderr,
    )
    sys.exit(1)
if args.show_points and args.show_points_thiscamera:
    print("--show-points and --show-points-thiscamera are exclusive", file=sys.stderr)
    sys.exit(1)

# arg-parsing is done before the imports so that --help works without building
# stuff, so that I can generate the manpages and README


import gnuplotlib as gp
import mrcal


def openmodel(f):
    try:
        return mrcal.cameramodel(f)
    except Exception as e:
        print(f"Couldn't load camera model '{f}': {e}", file=sys.stderr)
        sys.exit(1)


models = [openmodel(modelfilename) for modelfilename in args.models]

cameras_Rt_plot_ref = None
if args.transforms is not None:
    import mrcal.cahvor

    transforms = mrcal.cahvor.read_transforms(args.transforms)

    def get_pair(icam):
        f = args.models[icam]
        m = re.search("camera([0-9]+)", f)
        return int(m.group(1))

    def Rt_plot_ref(icam):
        try:
            pair = get_pair(icam)
            Rt_ins_ref = transforms["ins_from_camera"][pair]
            return Rt_ins_ref
        except:
            return None

    cameras_Rt_plot_ref = [Rt_plot_ref(icam) for icam in range(len(models))]

plotkwargs = {}
if args.title is not None:
    plotkwargs["title"] = args.title
if args.hardcopy is not None:
    plotkwargs["hardcopy"] = args.hardcopy
if args.terminal is not None:
    plotkwargs["terminal"] = args.terminal

if args.set is not None:
    gp.add_plot_option(plotkwargs, "set", args.set)
if args.unset is not None:
    gp.add_plot_option(plotkwargs, "unset", args.unset)

if args.show_calobjects:
    show_calobjects = "all"
elif args.show_calobjects_thiscamera:
    show_calobjects = "thiscamera"
else:
    show_calobjects = False
if args.show_points:
    show_points = "all"
elif args.show_points_thiscamera:
    show_points = "thiscamera"
else:
    show_points = False

plot = mrcal.show_geometry(
    models,
    cameranames=args.models,
    cameras_Rt_plot_ref=cameras_Rt_plot_ref,
    show_calobjects=show_calobjects,
    show_points=show_points,
    axis_scale=args.axis_scale,
    **plotkwargs,
)

if args.hardcopy is None:
    plot.wait()
