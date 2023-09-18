#!/usr/bin/env python3
"""Extract single-band bxsf from wannier90 bxsf."""
import argparse
import bz2
import datetime
import functools
import os
import traceback
import subprocess

# pylint: skip-file

# Check if this is the value used in skeaf!
BOHR_TO_ANG = 0.529177209  # From the SKEAF code
PI = 3.141592653589793

CONV_FACTOR = 2 * PI / BOHR_TO_ANG  # vectors will need to be DIVIDED by this factor


def removesuffix(text: str, suffix: str) -> str:
    """For python <= 3.8 compatibility.

    :param text: _description_
    :type text: str
    :param suffix: _description_
    :type suffix: str
    :return: _description_
    :rtype: str
    """
    return text[: -len(suffix)] if text.endswith(suffix) and len(suffix) != 0 else text


class InvalidBXSF(Exception):
    """Invalid bxsf file."""

def prepare_bxsf_for_skeaf(
    in_fhandle,
    out_fhandle,
    band_to_keep,
    shift_fermi=0.0,
    verbose=False,
    print_minmax=False,
):
    """
    SKEAF wants:
    - a single band - we're going to filter it
    - expected units are different!!!
      - It expects Ry instead of eV. This does not matter for the frequencies.
      We are NOT changing these in this function. [might be important for DOS]
      - It expects units of 2pi/bohr rather than 1/ang for the reciprocal
      lattice vectors! We are adapting those here.
    """
    # Will be used to know if we are printing the reciprocal vector
    in_recvec_section = False
    recvec_counter = (
        -3
    )  # There are three lines after 'BEGIN_BANDGRID_3D_fermi' before the actual vectors

    print_line = True  # Set to False for bands we don't want to print

    band_found = False

    if print_minmax:
        eigvals = []

    for line in in_fhandle:
        ###### Preliminary checks
        # Adapt the Fermi energy if needed
        if "Fermi Energy:" in line:
            # First of all, I print a few comments above
            out_fhandle.write("       #\n")
            out_fhandle.write("       #" + "*" * 70 + "\n")
            out_fhandle.write("       # IMPORTANT NOTE!\n")
            out_fhandle.write("       #\n")
            out_fhandle.write(
                "       # This file was post-processed at {}\n".format(
                    datetime.datetime.now().isoformat()
                )
            )
            script_name = os.path.basename(__file__)
            out_fhandle.write(
                f"       # by the {script_name} script extracting only one band.\n"
            )
            out_fhandle.write(
                "       # Also, IMPORTANT: the reciprocal lattice vectors were all converted\n"
            )
            out_fhandle.write(
                "       # from units of 1/ang to 2pi/bohr, dividng by the conversion factor {}\n".format(
                    CONV_FACTOR
                )
            )
            if shift_fermi != 0:
                out_fhandle.write(
                    "       # In addition, the Fermi energy was shifted by {}\n".format(
                        shift_fermi
                    )
                )
            out_fhandle.write("       #" + "*" * 70 + "\n")
            new_fermi = float(line.split()[-1]) + shift_fermi
            if verbose:
                print("Old Fermi Energy:", line.split()[-1])
                print("New Fermi Energy:", new_fermi)
            out_fhandle.write(f"  Fermi Energy: {new_fermi}\n")
            continue

        ###### End of preliminary checks
        if line.strip() == "BEGIN_BANDGRID_3D_fermi":
            in_recvec_section = True
            out_fhandle.write(line)
            continue

        if in_recvec_section:
            recvec_counter += 1
            if recvec_counter == -2:
                int(line.strip())
                out_fhandle.write("    1\n")  # Only one band will be written
                continue
            elif recvec_counter == -1:
                n1, n2, n3 = line.split()
                # I validate that these are three integers (grid size)
                int(n1)
                int(n2)
                int(n3)
                out_fhandle.write(line)
                continue
            elif recvec_counter == 0:
                x1, x2, x3 = line.split()
                # I validate that these are three floats and all zero (origin)
                assert float(x1) == 0.0
                assert float(x2) == 0.0
                assert float(x3) == 0.0
                out_fhandle.write(line)
                continue
            elif recvec_counter in [1, 2, 3]:
                # The three lattice vectors. I scale them
                bx, by, bz = line.split()
                bx = float(bx)
                by = float(by)
                bz = float(bz)
                out_fhandle.write(
                    "{:18.10f} {:18.10f} {:18.10f}\n".format(
                        bx / CONV_FACTOR,
                        by / CONV_FACTOR,
                        bz / CONV_FACTOR,
                    )
                )
                continue
            elif recvec_counter == 4:
                in_recvec_section = False
                # I don't continue: I want to go to the rest of the code, this is a new line to print,
                # typically the first line containing 'BAND: '
            else:
                raise ValueError(
                    "Invalid value for recvec_counter: {}, line: {}".format(
                        recvec_counter, line
                    )
                )

        if "BAND:" in line:
            current_band = int(line.split()[-1])
            if current_band == band_to_keep:
                print_line = True
                band_found = True
                if verbose:
                    print(f">>> Extracting band {current_band}")
            else:
                print_line = False
                if verbose:
                    print(f"-   Skipping band {current_band}")

        # Print footer
        if line.strip() == "END_BANDGRID_3D":
            print_line = True

        # Print depending on flag
        if print_line:
            # I remove all the leading spaces, because if there are spaces
            # before the band eigenvalues, skeaf will crash
            out_fhandle.write(line.strip() + "\n")

            if band_found and print_minmax:
                if not any(
                    _ in line
                    for _ in ["BAND:", "END_BANDGRID_3D", "END_BLOCK_BANDGRID_3D"]
                ):
                    e = [float(_) for _ in line.strip().split()]
                    eigvals.extend(e)

    if print_minmax:
        print(f"Min and max of band {band_to_keep} : {min(eigvals)} {max(eigvals)}")

    if not band_found:
        raise InvalidBXSF(
            "A file was written, but you passed some non-existing band to keep, so that the file is probably empty!"
        )


def estimate_fermi(
    in_fhandle,
    num_electrons,
    spin_deg,
    verbose=False,
    plot_dos=False,
):
    fermi_from_file = None
    next_is_count = False
    next_is_gridsize = False
    num_bands = None
    grid_shape = None
    in_band = False
    counter_band = 0
    counter_num_gridpoints_per_band = None

    band_energies = []

    for line in in_fhandle:
        ###### Preliminary checks
        # Adapt the Fermi energy
        if fermi_from_file is None and "Fermi Energy:" in line:
            fermi_from_file = float(line.split()[-1])
            if verbose:
                print("Fermi Energy from file:", line.split()[-1])
            continue
        if num_bands is None and line.strip().startswith("BEGIN_BANDGRID_3D_"):
            next_is_count = True
            continue
        if next_is_count:
            next_is_count = False
            next_is_gridsize = True
            num_bands = int(line.strip())
            if verbose:
                print("Number of bands:", num_bands)
            continue
        if next_is_gridsize:
            next_is_gridsize = False
            grid_shape = [int(piece) for piece in line.strip().split()]
            assert len(grid_shape) == 3
            if verbose:
                print("Grid shape: {}x{}x{}".format(*grid_shape))
            continue

        ###### End of preliminary checks
        if "BAND:" in line:
            counter_band += 1
            assert (
                counter_num_gridpoints_per_band is None
                or counter_num_gridpoints_per_band
                == grid_shape[0] * grid_shape[1] * grid_shape[2]
            )
            # current_band = int(line.split()[-1])
            counter_num_gridpoints_per_band = 0
            in_band = True
            continue
        if in_band:
            if (
                counter_num_gridpoints_per_band
                == grid_shape[0] * grid_shape[1] * grid_shape[2]
            ):
                in_band = False
            else:
                e = [float(_) for _ in line.strip().split()]
                counter_num_gridpoints_per_band += len(e)
                band_energies.extend(e)

    # Final checks
    assert counter_band == num_bands
    assert (
        counter_num_gridpoints_per_band is None
        or counter_num_gridpoints_per_band
        == grid_shape[0] * grid_shape[1] * grid_shape[2]
    )

    assert (
        len(band_energies) == num_bands * grid_shape[0] * grid_shape[1] * grid_shape[2]
    )
    band_energies.sort()
    print("Length of band-energies array:", len(band_energies))
    print("~" * 72)

    if num_electrons < 0:
        num_electrons_list = list(
            range(abs(num_electrons) // 2, abs(num_electrons) + 1)
        )
        print(
            "Requested a negative number of electrons, inspecting for a range"
            f" from {num_electrons_list[0]} to {num_electrons_list[-1]}"
        )
    else:
        num_electrons_list = [num_electrons]
        print(f"Requested number of electrons: {num_electrons}")

    print(f"Requested a spin degeneracy per band: {spin_deg}")

    print("-" * 72)

    for num_elec_local in num_electrons_list:
        num_expected_occupied_points = (
            grid_shape[0] * grid_shape[1] * grid_shape[2] * num_elec_local / spin_deg
        )

        # There is half occupation for even number of electrons and double spin degeneracy per band
        half_occupation = spin_deg == 2 and num_elec_local % 2 == 1
        num_expected_occupied_points = int(num_expected_occupied_points)

        # print("Closest index to Fermi energy position:", num_expected_occupied_points)
        print(f"### Considering {num_elec_local} electrons:")
        if half_occupation:
            print("   Energy of the two half-occupied points:")
        else:
            print("   Energy of the last occupied and first unoccupied points:")
        print(band_energies[num_expected_occupied_points - 1])
        print(band_energies[num_expected_occupied_points])
        computed_fermi = (
            band_energies[num_expected_occupied_points - 1]
            + band_energies[num_expected_occupied_points]
        ) / 2.0
        print(f"Computed Fermi energy: {computed_fermi}")
        print("-" * 72)

    if plot_dos:
        if num_electrons <= 0:
            raise ValueError(
                "Cannot plot DOS for negative value of electrons [used for scanning]"
            )
        import numpy as np
        import pylab as pl

        band_energies = np.array(band_energies)
        # plot_range = [band_energies.min(), band_energies.max()]
        # energy_resolution = 0.01
        plot_range = [fermi_from_file - 1.5, fermi_from_file + 1.5]
        energy_resolution = 0.001
        bins = int((plot_range[1] - plot_range[0]) / energy_resolution)
        print(f"Using {bins} bins in {plot_range} (en. resol.: {energy_resolution})")
        pl.hist(band_energies, bins=bins, range=plot_range, alpha=0.5)
        pl.axvline(fermi_from_file, color="orange", linewidth=0.5, label="Fermi (SCF)")
        pl.axvline(computed_fermi, color="green", linewidth=0.5, label="Fermi (grid)")
        pl.xlim(plot_range)
        pl.xlabel("Energy (eV)")
        pl.ylabel("DOS (a.u.)")
        pl.legend(loc="best")
        pl.show()


def parse_args(args=None):
    def int_or_str(value):
        try:
            return int(value)
        except:
            return value

    parser = argparse.ArgumentParser(
        description="Extract a specified band from bxsf, and/or recalculate Fermi energy from grid of eigenvalues.",
    )
    parser.add_argument(
        "filename",
        metavar="FILE",
        type=str,
        help="Filename of Wannier90 generated bxsf, can be bz2 compressed.",
    )
    parser.add_argument(
        "-ne",
        "--num_electrons",
        type=int,
        help="number of electrons.",
    )
    parser.add_argument(
        "-ns",
        "--num_spin",
        type=int,
        default=2,
        help="spin degeneracy.",
    )
    parser.add_argument(
        "-ib",
        "--band_index",
        # type=int,
        type=int_or_str,
        help=(
            "The band index to keep (integer, 1-based, the same as the "
            "content of the source BXSF. "
            "Use `all` to write each band to a single bxsf."
        ),
    )
    parser.add_argument(
        "-o",
        "--out_filename",
        type=str,
        default="skeaf.bxsf",
        help=(
            "The output filename for the selected band. "
            "I will append a string `_band_INDEX.bxsf`; "
            "if the filename endswith `.bxsf`, I will replace the "
            "extension by `_band_INDEX.bxsf`."
        ),
    )

    parsed_args = parser.parse_args(args)

    return parsed_args


def get_bxsf_band_indexes(fhandle) -> list:
    idxs = []

    for line in fhandle:
        if "BAND:" in line:
            idx = int(line.strip().split(":")[1])
            idxs.append(idx)

    return idxs


if __name__ == "__main__":
    args = parse_args()
    print(f"Started on {datetime.datetime.now()}")

    in_fname = args.filename
    num_electrons = args.num_electrons
    num_spin = args.num_spin
    band_index = args.band_index
    out_fname = args.out_filename

    print("cmdline args:")
    print(f"  {in_fname = }")
    print(f"  {num_electrons = }")
    print(f"  {num_spin = }")
    print(f"  {band_index = }")
    print(f"  {out_fname = }")
    print()

    if not os.path.isfile(in_fname):
        import sys
        print(f"ERROR: Input file {in_fname} does not exist.")
        sys.exit(2)

    if in_fname.endswith(".bz2"):
        open_function = functools.partial(
            bz2.open,
            mode="rt",
            encoding="ascii",
        )
        print("INFO: Auto-decompressing input bz2 file.")
    elif in_fname.endswith(".7z"):
        import sys, re
        try:
            import py7zr
            print("INFO: Decompressing input 7z file using py7zr.")
            filter_pattern = re.compile(r'.*\.bxsf')
            with py7zr.SevenZipFile(in_fname, 'r') as zip:
                allfiles = zip.getnames()
                targets = [f for f in allfiles if filter_pattern.match(f)]
                if len(targets) > 1:
                    print("More than one bxsf file in archive")
                    sys.exit(2)
                elif len(targets) == 0:
                    print("No bxsf file in archive")
                    sys.exit(2)
            with py7zr.SevenZipFile(in_fname, 'r') as zip:
                zip.extract(targets=targets)
                bxsf_filename = targets[0]
                dst_filename = "input.bxsf" # default name accepted by SKEAF, the bxsf file in the archive will be renamed to this

                os.rename(bxsf_filename, dst_filename)
                in_fname = dst_filename        
        except ImportError:
            print("INFO: Decompressing input 7z file.")
            ret_code = subprocess.run(['7z', 'x', in_fname]) # if in_fname has strange characters, this will fail. TODO: implement a function to convert to a safe filename
            if ret_code != 0:
                print(f"ERROR: file not found {in_fname}")
                sys.exit(ret_code)
            bxsf_files = [f for f in os.listdir() if f.endswith(".bxsf")]
            if len(bxsf_files) > 1:
                print("More than one bxsf file in the working directory")
                sys.exit(2)
            elif len(bxsf_files) == 0:
                print("No bxsf file in the working directory")
                sys.exit(2)
            bxsf_filename = bxsf_files[0]
            dst_filename = "input.bxsf" # default name accepted by SKEAF, the bxsf file in the archive will be renamed to this
            os.rename(bxsf_filename, dst_filename)
            in_fname = dst_filename
        open_function = open
    else:
        open_function = open

    print(f"Using BXSF with filename: {os.path.realpath(in_fname)}\n")

    with open_function(in_fname) as in_fhandle:
        try:
            if num_electrons is not None and num_spin is not None:
                print("#" * 5 + " Calculate Fermi energy from kmesh " + "#" * 5)
                estimate_fermi(
                    in_fhandle,
                    num_electrons,
                    num_spin,
                    verbose=True,
                )
        except Exception as exc:
            print("*" * 72)
            print("* ERROR! *")
            print("* when recalculating Fermi energy")
            traceback.print_exc()
            print("*" * 72)

        in_fhandle.seek(0)
        if band_index == "all":
            indexes = get_bxsf_band_indexes(in_fhandle)
            print(f'Bands in bxsf: {" ".join([str(_) for _ in indexes])}')
        else:
            indexes = [band_index]

        try:
            for idx in indexes:
                in_fhandle.seek(0)
                fname = removesuffix(out_fname, ".bxsf") + f"_band_{idx}.bxsf"
                if idx is None or fname is None:
                    continue

                print("#" * 5 + f" Write single-band bxsf for band {idx} " + "#" * 5)
                with open(fname, "w") as out_fhandle:
                    prepare_bxsf_for_skeaf(
                        in_fhandle,
                        out_fhandle,
                        band_to_keep=idx,
                        verbose=True,
                        print_minmax=True,
                    )
            print(f"Job done at {datetime.datetime.now()}")
        except Exception as exc:
            os.remove(fname)
            print("*" * 72)
            print("* ERROR! *")
            print("* when writing output bxsf")
            traceback.print_exc()
            print("* I THEREFORE DELETED THE OUTPUT FILE.")
            print("*" * 72)
