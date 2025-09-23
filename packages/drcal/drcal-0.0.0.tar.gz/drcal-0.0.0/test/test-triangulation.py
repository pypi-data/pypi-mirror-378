#!/usr/bin/env python3
import sys
import numpy as np
import numpysane as nps
import os

testdir = os.path.dirname(os.path.realpath(__file__))

# I import the LOCAL mrcal since that's what I'm testing
sys.path[:0] = (f"{testdir}/..",)
import mrcal
import testutils
from test_calibration_helpers import grad

import scipy.optimize


# I want the RNG to be deterministic
np.random.seed(0)


############### World layout

# camera0 is the "reference"
model0 = mrcal.cameramodel(
    intrinsics=("LENSMODEL_PINHOLE", np.array((1000.0, 1000.0, 500.0, 500.0))),
    imagersize=np.array((1000, 1000)),
)
model1 = mrcal.cameramodel(
    intrinsics=("LENSMODEL_PINHOLE", np.array((1100.0, 1100.0, 500.0, 500.0))),
    imagersize=np.array((1000, 1000)),
)


# All the callback functions can broadcast on p,v
@nps.broadcast_define(((3,), (3,), (3,), (3,)), ())
def callback_l2_geometric(p, v0, v1, t01):
    if p[2] < 0:
        return 1e6
    distance_p_v0 = nps.mag(p - nps.inner(p, v0) / nps.norm2(v0) * v0)
    distance_p_v1 = nps.mag(p - t01 - nps.inner(p - t01, v1) / nps.norm2(v1) * v1)
    return np.abs(distance_p_v0) + np.abs(distance_p_v1)


@nps.broadcast_define(((3,), (3,), (3,), (3,)), ())
def callback_l2_angle(p, v0, v1, t01):
    costh0 = nps.inner(p, v0) / np.sqrt(nps.norm2(p) * nps.norm2(v0))
    costh1 = nps.inner(p - t01, v1) / np.sqrt(nps.norm2(p - t01) * nps.norm2(v1))
    th0 = np.arccos(min(costh0, 1.0))
    th1 = np.arccos(min(costh1, 1.0))
    return th0 * th0 + th1 * th1


@nps.broadcast_define(((3,), (3,), (3,), (3,)), ())
def callback_l1_angle(p, v0, v1, t01):
    costh0 = nps.inner(p, v0) / np.sqrt(nps.norm2(p) * nps.norm2(v0))
    costh1 = nps.inner(p - t01, v1) / np.sqrt(nps.norm2(p - t01) * nps.norm2(v1))
    th0 = np.arccos(min(costh0, 1.0))
    th1 = np.arccos(min(costh1, 1.0))
    return np.abs(th0) + np.abs(th1)


@nps.broadcast_define(((3,), (3,), (3,), (3,)), ())
def callback_linf_angle(p, v0, v1, t01):
    costh0 = nps.inner(p, v0) / np.sqrt(nps.norm2(p) * nps.norm2(v0))
    costh1 = nps.inner(p - t01, v1) / np.sqrt(nps.norm2(p - t01) * nps.norm2(v1))

    # Simpler function that has the same min
    return (1 - min(costh0, costh1)) * 1e9
    # th0 = np.arccos(min(costh0, 1.0))
    # th1 = np.arccos(min(costh1, 1.0))
    # return max(np.abs(th0), np.abs(th1))


@nps.broadcast_define(((3,), (3,), (3,), (4, 3)), ())
def callback_l2_reprojection(p, v0local, v1local, Rt01):
    dq0 = mrcal.project(p, *model0.intrinsics()) - mrcal.project(
        v0local, *model0.intrinsics()
    )
    dq1 = mrcal.project(
        mrcal.transform_point_Rt(mrcal.invert_Rt(Rt01), p), *model1.intrinsics()
    ) - mrcal.project(v1local, *model1.intrinsics())
    return nps.norm2(dq0) + nps.norm2(dq1)


# can broadcast on p
def test_geometry(Rt01, p, whatgeometry, out_of_bounds=False, check_gradients=False):
    R01 = Rt01[:3, :]
    t01 = Rt01[3, :]

    # p now has shape (Np,3). The leading dims have been flattened
    p = p.reshape(p.size // 3, 3)
    Np = len(p)

    # p has shape (Np,3)
    # v has shape (Np,2)
    (
        v0local_noisy,
        v1local_noisy,
        v0_noisy,
        v1_noisy,
        q0_ref,
        q1_ref,
        q0_noisy,
        q1_noisy,
    ) = [
        v[..., 0, :]
        for v in mrcal.synthetic_data._noisy_observation_vectors_for_triangulation(
            p, Rt01, model0.intrinsics(), model1.intrinsics(), 1, sigma=0.1
        )
    ]

    scenarios = (
        (mrcal.triangulate_geometric, callback_l2_geometric, v0_noisy, v1_noisy, t01),
        (mrcal.triangulate_leecivera_l1, callback_l1_angle, v0_noisy, v1_noisy, t01),
        (
            mrcal.triangulate_leecivera_linf,
            callback_linf_angle,
            v0_noisy,
            v1_noisy,
            t01,
        ),
        (mrcal.triangulate_leecivera_mid2, None, v0_noisy, v1_noisy, t01),
        (mrcal.triangulate_leecivera_wmid2, None, v0_noisy, v1_noisy, t01),
        (
            mrcal.triangulate_lindstrom,
            callback_l2_reprojection,
            v0local_noisy,
            v1local_noisy,
            Rt01,
        ),
        (mrcal.triangulated_error, None, v0_noisy, v1_noisy, t01),
    )

    for scenario in scenarios:
        f, callback = scenario[:2]
        args = scenario[2:]

        result = f(*args, get_gradients=True)
        p_reported = result[0]

        what = f"{whatgeometry} {f.__name__}"

        def do_check_gradient(*grads):
            for ip in range(Np):
                args_cut = (args[0][ip], args[1][ip], args[2])
                for ivar in range(len(args)):
                    if grads[ivar] is not None:
                        grad_empirical = grad(
                            lambda x: f(*args_cut[:ivar], x, *args_cut[ivar + 1 :]),
                            args_cut[ivar],
                            step=1e-6,
                        )
                        testutils.confirm_equal(
                            grads[ivar][ip],
                            grad_empirical,
                            relative=True,
                            worstcase=True,
                            msg=f"{what}: grad(ip={ip}, ivar = {ivar})",
                            eps=2e-2,
                        )

        if f is mrcal.triangulated_error:
            # triangulated_error() gets lots of special treatment since it's a
            # scalar, and works just fine with divergent rays and doesn't report
            # the derr/dv0 gradient
            if not out_of_bounds:
                err_reported = p_reported
                p_mid2 = mrcal.triangulate_leecivera_mid2(*args)

                def angle_error__assume_small(v0, v1):
                    costh = nps.inner(v0, v1) / np.sqrt(nps.norm2(v0) * nps.norm2(v1))
                    # The angle is assumed small, so cos(th) ~ 1 - th*th/2.
                    # -> th ~ sqrt( 2*(1 - cos(th)) )
                    th_sq = costh * (-2.0) + 2.0
                    th_sq[th_sq < 0] *= 0.0
                    return np.sqrt(th_sq)

                err_mid2 = 2 * angle_error__assume_small(args[0], p_mid2)

                testutils.confirm_equal(
                    err_reported,
                    err_mid2,
                    relative=True,
                    worstcase=True,
                    msg=f"{what}: result should be close to triangulate_leecivera_mid2()",
                    eps=1e-8,
                )

            # I do this regardless of if check_gradients. Because I want to
            # check the divergent cases too
            do_check_gradient(
                None,  # no derr/dv0 gradient
                *result[1:],
            )
            continue

        if out_of_bounds:
            p_optimized = np.zeros(p_reported.shape)

            testutils.confirm_equal(
                p_reported,
                p_optimized,
                relative=False,
                worstcase=True,
                msg=what,
                eps=1e-3,
            )
        else:
            # Check all the gradients
            if check_gradients:
                do_check_gradient(*result[1:])

            if callback is not None:
                # I run an optimization to directly optimize the quantity each triangulation
                # routine is supposed to be optimizing, and then I compare
                p_optimized = nps.cat(
                    *[
                        scipy.optimize.minimize(
                            callback,
                            p_reported[ip],  # seed from the "right" value
                            args=(args[0][ip], args[1][ip], args[2]),
                            method="Nelder-Mead",
                            # options = dict(disp  = True)
                        )["x"]
                        for ip in range(Np)
                    ]
                )

                # print( f"{what} p reported,optimized:\n{nps.cat(p_reported, p_optimized)}" )
                # print( f"{what} p_err: {p_reported - p_optimized}" )
                # print( f"{what} optimum reported/optimized:\n{callback(p_reported, *args)/callback(p_optimized, *args)}" )

                testutils.confirm_equal(
                    p_reported,
                    p_optimized,
                    relative=True,
                    worstcase=True,
                    msg=what,
                    eps=1e-3,
                )
            else:
                # No callback defined. Compare projected q
                q0 = mrcal.project(p_reported, *model0.intrinsics())
                q1 = mrcal.project(
                    mrcal.transform_point_Rt(mrcal.invert_Rt(Rt01), p_reported),
                    *model1.intrinsics(),
                )

                testutils.confirm_equal(
                    q0,
                    q0_ref,
                    relative=False,
                    worstcase=True,
                    msg=f"{what} q0",
                    eps=25.0,
                )
                testutils.confirm_equal(
                    q1,
                    q1_ref,
                    relative=False,
                    worstcase=True,
                    msg=f"{what} q1",
                    eps=25.0,
                )


# square camera layout
t01 = np.array((1.0, 0.1, -0.2))
R01 = mrcal.R_from_r(np.array((0.001, -0.002, -0.003)))
Rt01 = nps.glue(R01, t01, axis=-2)

p = np.array(
    (
        (300.0, 20.0, 2000.0),  # far away AND center-ish
        (-310.0, 18.0, 2000.0),
        (30.0, 290.0, 1500.0),  # far away AND center-ish
        (-31.0, 190.0, 1500.0),
        (3000.0, 200.0, 2000.0),  # far away AND off to either side
        (-3100.0, 180.0, 2000.0),
        (300.0, 2900.0, 1500.0),  # far away AND off up/down
        (-310.0, 1980.0, 1500.0),
        (3000.0, -200.0, 20.0),  # very close AND off to either side
        (-3100.0, 180.0, 20.0),
        (300.0, 2900.0, 15.0),  # very close AND off up/down
        (-310.0, 1980.0, 15.0),
    )
)
test_geometry(Rt01, p, "square-camera-geometry", check_gradients=True)

# Not checking gradients anymore. If the above all pass, the rest will too.
# Turning on the checks will slow stuff down and create more console spew. AND
# some test may benignly fail because of the too-small or too-large central
# difference steps

# cameras facing at each other
t01 = np.array((0, 0, 100.0))
R01 = mrcal.R_from_r(np.array((0.001, np.pi + 0.002, -0.003)))
Rt01 = nps.glue(R01, t01, axis=-2)

p = np.array(
    (
        (3.0, 2.0, 20.0),  # center-ish
        (-1000.0, 18.0, 20.0),  # off to various sides
        (1000.0, 29.0, 50.0),
        (-31.0, 1900.0, 70.0),
        (-11.0, -2000.0, 95.0),
    )
)
test_geometry(Rt01, p, "cameras-facing-each-other", check_gradients=False)

p = np.array(
    (
        (3.0, 2.0, 101.0),  # center-ish
        (-11.0, -2000.0, -5.0),
    )
)
test_geometry(Rt01, p, "cameras-facing-each-other out-of-bounds", out_of_bounds=True)

# cameras at 90 deg to each other
t01 = np.array((100.0, 0, 100.0))
R01 = mrcal.R_from_r(np.array((0.001, -np.pi / 2.0 + 0.002, -0.003)))
Rt01 = nps.glue(R01, t01, axis=-2)

p = np.array(
    (
        (30.0, 5.0, 40.0),  # center-ish
        (-2000.0, 25.0, 50.0),  # way left in one cam, forward in the other
        (80.0, -10.0, 2000.0),  # forward one, right the other
        (75.0, 5.0, 4.0),  # corner on both
    )
)

test_geometry(Rt01, p, "cameras-90deg-to-each-other", check_gradients=False)


p = np.array(
    (
        (110.0, 25.0, 50.0),
        (90.0, -100.0, -5.0),
    )
)
test_geometry(Rt01, p, "cameras-90deg-to-each-other out-of-bounds", out_of_bounds=True)

testutils.finish()
