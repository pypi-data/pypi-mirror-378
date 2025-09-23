"""Utilities to handle NUOPC configuration files.

The `nuopc.runconfig` files use by the CESM driver, and thus by ACCESS-OM3, are a mixture of two file formats: Resource
Files and Fortran Namelists.

At the top-level, one has the Resource Files as implemented in ESMF. From the ESMF documentation:

    A Resource File (RF) is a text file consisting of list of label-value pairs. There is a limit of 1024 characters per
    line and the Resource File can contain a maximum of 200 records. Each label should be followed by some data, the
    value. An example Resource File follows. It is the file used in the example below.

     # This is an example Resource File.
     # It contains a list of <label,value> pairs.
     # The colon after the label is required.

     # The values after the label can be an list.
     # Multiple types are authorized.

      my_file_names:         jan87.dat jan88.dat jan89.dat  # all strings
      constants:             3.1415   25                    # float and integer
      my_favorite_colors:    green blue 022


     # Or, the data can be a list of single value pairs.
     # It is simplier to retrieve data in this format:

      radius_of_the_earth:   6.37E6
      parameter_1:           89
      parameter_2:           78.2
      input_file_name:       dummy_input.nc

     # Or, the data can be located in a table using the following
     # syntax:

      my_table_name::
       1000     3000     263.0
        925     3000     263.0
        850     3000     263.0
        700     3000     269.0
        500     3000     287.0
        400     3000     295.8
        300     3000     295.8
      ::

    Note that the colon after the label is required and that the double colon is required to declare tabular data.

See https://earthsystemmodeling.org/docs/release/ESMF_8_6_0/ESMF_refdoc/node6.html#SECTION06090000000000000000 for
further details.

The CESM driver then uses tables as defined in Resource Files to store Fortran Namelists instead of simple values:

    DRIVER_attributes::
     Verbosity = off
     cime_model = cesm
     logFilePostFix = .log
     pio_blocksize = -1
     pio_rearr_comm_enable_hs_comp2io = .true.
     pio_rearr_comm_enable_hs_io2comp = .false.
     reprosum_diffmax = -1.000000D-08
    ::

    ALLCOMP_attributes::
     ATM_model = datm
     GLC_model = sglc
     OCN_model = mom
     ocn2glc_levels = 1:10:19:26:30:33:35
    ::

"""

from pathlib import Path
import re

from .tmp_utils import convert_from_string, convert_to_string


def read_nuopc_config(file_name: str) -> dict:
    """Read a NUOPC config file and return its contents as a dictionary.

    Args:
        file_name (str): File to read.

    Returns:
        dict: Contents of file.
    """
    fname = Path(file_name)
    if not fname.is_file():
        raise FileNotFoundError(f"File not found: {fname.as_posix()}")

    label_value_pattern = re.compile(r"\s*(\w+)\s*:\s*(.+)\s*")
    table_start_pattern = re.compile(r"\s*(\w+)\s*::\s*")
    table_end_pattern = re.compile(r"\s*::\s*")
    assignment_pattern = re.compile(r"\s*(\w+)\s*=\s*(\S+)\s*")

    config = {}
    with open(fname, "r") as stream:
        reading_table = False
        label = None
        table = None
        for line in stream:
            line = re.sub(r"(#).*", "", line)
            if line.strip():
                if reading_table:
                    if re.match(table_end_pattern, line):
                        config[label] = table
                        reading_table = False
                    else:
                        match = re.match(assignment_pattern, line)
                        if match:
                            table[match.group(1)] = convert_from_string(match.group(2))
                        else:
                            raise ValueError(
                                f"Line: {line} in file {file_name} is not a valid NUOPC configuration specification"
                            )

                elif re.match(table_start_pattern, line):
                    reading_table = True
                    match = re.match(label_value_pattern, line)
                    label = match.group(1)
                    table = {}

                elif re.match(label_value_pattern, line):
                    match = re.match(label_value_pattern, line)
                    config[match.group(1)] = [convert_from_string(string) for string in match.group(2).split()]

    return config


def write_nuopc_config(config: dict, file: Path):
    """Write a dictionary to a NUOPC config file.

    Args:
        config (dict): NUOPC configuration to write.
        file (Path): File to write to.
    """
    with open(file, "w") as stream:
        for key, item in config.items():
            if isinstance(item, dict):
                stream.write(key + "::\n")
                for label, value in item.items():
                    stream.write("  " + label + " = " + convert_to_string(value) + "\n")
                stream.write("::\n\n")
            else:
                stream.write(key + ": " + " ".join(map(convert_to_string, item)) + "\n")
