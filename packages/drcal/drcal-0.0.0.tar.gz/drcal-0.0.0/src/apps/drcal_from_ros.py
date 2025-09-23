### THIS IS LARGELY A COPY OF mrcal-from-cahvor. Please consolidate

r"""Converts a ROS/OpenCV-formatted camera model to the .cameramodel file format

SYNOPSIS

  $ mrcal-from-ros model1.yaml model2.yaml
  Wrote model1.cameramodel
  Wrote model2.cameramodel


  $ rostopic echo -n1 -b tst.bag /camera/camera_info \
    | head -n -1                                     \
    | mrcal-from-ros                                 \
    > model.cameramodel

File formats supported by mrcal are described at
https://mrcal.secretsauce.net/cameramodels.html#cameramodel-file-formats

This tool converts the given model(s) to the cameramodel file format. No changes
to the content are made; this is purely a format converter (the
mrcal-convert-lensmodel tool fits different lens models instead). Model
filenames are given on the commandline. Output is written to the same directory,
with the same filename, but with a .cameramodel extension.

If the model is omitted or given as "-", the input is read from standard input,
and the output is written to standard output.

Note: there's no corresponding mrcal-to-ros tool at this time, because the
behavior of such a tool isn't well-defined. Talk to me if this would be useful
to you, to clarify what it should do, exactly.

"""

import sys
import argparse
import os
import drcal


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        default=False,
        help="""By default existing files are not overwritten. Pass --force to overwrite them
                        without complaint""",
    )
    parser.add_argument(
        "--outdir",
        required=False,
        type=lambda d: d
        if os.path.isdir(d)
        else parser.error(
            "--outdir requires an existing directory as the arg, but got '{}'".format(d)
        ),
        help="""Directory to write the output models into. If omitted, we write the output
                        models to the same directory as the input models""",
    )
    parser.add_argument(
        "model", default=["-"], nargs="*", type=str, help="""Input camera model"""
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # arg-parsing is done before the imports so that --help works without building
    # stuff, so that I can generate the manpages and README

    Nstdin = sum(1 for m in args.model if m == "-")
    if Nstdin > 1:
        print(
            f"At most one model can be read from standard input ('-'), but I got {Nstdin}",
            file=sys.stderr,
        )
        sys.exit(1)

    for model in args.model:
        if model == "-":
            try:
                m = drcal.cameramodel(model)
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                print(e, file=sys.stderr)
                sys.exit(1)
            m.write(sys.stdout)
        else:
            base, extension = os.path.splitext(model)
            if extension.lower() == ".cameramodel":
                print(
                    "Input file is already in the cameramodel format (judging from the filename). Doing nothing",
                    file=sys.stderr,
                )
                sys.exit(0)

            if args.outdir is not None:
                base = args.outdir + "/" + os.path.split(base)[1]
            filename_out = base + ".cameramodel"
            if not args.force and os.path.exists(filename_out):
                print(
                    f"Target model '{filename_out}' already exists. Doing nothing with this model. Pass -f to overwrite",
                    file=sys.stderr,
                )
            else:
                m = drcal.cameramodel(model)
                m.write(filename_out)
                print("Wrote " + filename_out)


if __name__ == "__main__":
    main()
