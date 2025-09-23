#!/usr/bin/env python3

r"""Display the imager resolution"""

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
        help="""How densely we should sample the imager. By default we use a 60x40 grid""",
    )

    parser.add_argument("--cbmin", type=float, help="""Minimum range of the colorbar""")
    parser.add_argument("--cbmax", type=float, help="""Maximum range of the colorbar""")

    parser.add_argument(
        "--title", type=str, default=None, help="""Title string for the plot"""
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
        help="""Extra 'set' directives to gnuplotlib. Can be given multiple times""",
    )
    parser.add_argument(
        "--unset",
        type=str,
        action="append",
        help="""Extra 'unset' directives to gnuplotlib. Can be given multiple times""",
    )

    parser.add_argument("model", type=str, help="""Camera model""")

    args = parser.parse_args()

    return args


args = parse_args()


import numpy as np
import numpysane as nps
import gnuplotlib as gp
import mrcal


def mean_resolution__rad_pixel(q, model):
    r"""Find the mean resolution in rad/pixel at q

    v = unproject(q). Let a rotation R = [u0 u1 v]

    dq = dqdv dv
       = dqdv R Rt dv

    I have about dv normal to v (the space spanned by (u0,u1)), so let's assume
    that v is in this space: inner(dv,v) = 0

    Rt dv = [u0t dv] = [a]
            [u1t dv]   [b]
            [ 0    ]   [0]

    Let ab = [a b]t

    dq = M ab where M = dqdv [u0 u1]. M is (2,2)

    norm2(dq) = abt MtM ab

    minmax(norm2(dq)) = eig(MtM)

    dq = sqrt(eig(MtM)) pixels/rad

    """

    v = mrcal.unproject(q, *model.intrinsics(), normalize=True)
    _, dq_dv, _ = mrcal.project(v, *model.intrinsics(), get_gradients=True)

    # Use R_aligned_to_vector(). Add broadcasting to that function?
    @nps.broadcast_define(((3,),), (3, 3))
    def rotation_any_v_to_z(v):
        r"""Return any rotation matrix that maps the given unit vector v to [0,0,1]"""
        z = v
        if np.abs(v[0]) < 0.9:
            x = np.array((1, 0, 0), dtype=float)
        else:
            x = np.array((0, 1, 0), dtype=float)
        x -= nps.inner(x, v) * v
        x /= nps.mag(x)
        y = np.cross(z, x)
        return nps.cat(x, y, z)

    # shape (...,3,3)
    Rt = rotation_any_v_to_z(v)

    # shape (...,2,2)
    M = nps.matmult(dq_dv, nps.transpose(Rt)[..., :, :2])

    # Let MtM = (a b). If l is an eigenvalue then
    #           (b c)
    #
    #     (a-l)*(c-l) - b^2 = 0 --> l^2 - (a+c) l + ac-b^2 = 0
    #
    #     --> l = (a+c +- sqrt( a^2 + 2ac + c^2 - 4ac + 4b^2)) / 2 =
    #           = (a+c +- sqrt( a^2 - 2ac + c^2 + 4b^2)) / 2 =
    #           = (a+c)/2 +- sqrt( (a-c)^2/4 + b^2)
    a = nps.inner(M[..., :, 0], M[..., :, 0])
    b = nps.inner(M[..., :, 0], M[..., :, 1])
    c = nps.inner(M[..., :, 1], M[..., :, 1])
    sqrt_discriminant = np.sqrt((a - c) * (a - c) / 4 + b * b)
    l0 = (a + c) / 2 + sqrt_discriminant
    l1 = (a + c) / 2 - sqrt_discriminant
    resolution_pix_rad_max = np.sqrt(l0)

    # real in case roundoff error makes l1<0
    resolution_pix_rad_min = np.real(np.sqrt(l1))

    # The resolution is an ellipse (different directions could have different
    # resolutions). Here I assume it's a circle, and take the average of the
    # axis lengths
    resolution_pix_rad = (resolution_pix_rad_min + resolution_pix_rad_max) / 2
    return 1.0 / resolution_pix_rad


plot_options = dict(hardcopy=args.hardcopy, terminal=args.terminal)
if args.set is not None:
    plot_options["set"] = args.set
if args.unset is not None:
    plot_options["unset"] = args.unset

if args.title is not None:
    plot_options["title"] = args.title


def openmodel(f):
    try:
        return mrcal.cameramodel(f)
    except Exception as e:
        print(f"Couldn't load camera model '{f}': {e}", file=sys.stderr)
        sys.exit(1)


model = openmodel(args.model)


W, H = model.imagersize()
q = np.ascontiguousarray(
    nps.mv(
        nps.cat(
            *np.meshgrid(
                np.linspace(0, W - 1, args.gridn[0]),
                np.linspace(0, H - 1, args.gridn[1]),
            )
        ),
        0,
        -1,
    )
)


resolution__deg_pixel = mean_resolution__rad_pixel(q, model) * 180.0 / np.pi

if args.cbmax is None:
    # ceil x * 10^n where x is an integer in [1,9] and n is an integer
    args.cbmax = np.max(resolution__deg_pixel)
    base10_floor = np.power(10.0, np.floor(np.log10(args.cbmax)))
    args.cbmax = np.ceil(args.cbmax / base10_floor) * base10_floor
if args.cbmin is None:
    # floor x * 10^n where x is an integer in [1,9] and n is an integer
    args.cbmin = np.min(resolution__deg_pixel)
    base10_floor = np.power(10.0, np.floor(np.log10(args.cbmin)))
    args.cbmin = np.floor(args.cbmin / base10_floor) * base10_floor

curve_options = mrcal.visualization._options_heatmap_with_contours(
    # update these plot options
    plot_options,
    contour_min=args.cbmin,
    contour_max=args.cbmax,
    imagersize=model.imagersize(),
    gridn_width=args.gridn[0],
    gridn_height=args.gridn[1],
)

gp.plot(
    (resolution__deg_pixel, curve_options),
    **plot_options,
    title="Camera resolution in deg/pixel",
    wait=args.hardcopy is None,
)
