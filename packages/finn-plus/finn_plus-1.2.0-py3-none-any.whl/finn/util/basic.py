# Copyright (C) 2024, Advanced Micro Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of FINN nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from qonnx.util.basic import roundup_to_integer_multiple

from finn.util.logging import log

# test boards used for bnn pynq tests
test_board_map = ["Pynq-Z1", "KV260_SOM", "ZCU104", "U55C"]

# mapping from PYNQ board names to FPGA part names
pynq_part_map = dict()
pynq_part_map["Ultra96"] = "xczu3eg-sbva484-1-e"
pynq_part_map["Ultra96-V2"] = "xczu3eg-sbva484-1-i"
pynq_part_map["Pynq-Z1"] = "xc7z020clg400-1"
pynq_part_map["Pynq-Z2"] = "xc7z020clg400-1"
pynq_part_map["ZCU102"] = "xczu9eg-ffvb1156-2-e"
pynq_part_map["ZCU104"] = "xczu7ev-ffvc1156-2-e"
pynq_part_map["ZCU111"] = "xczu28dr-ffvg1517-2-e"
pynq_part_map["RFSoC2x2"] = "xczu28dr-ffvg1517-2-e"
pynq_part_map["RFSoC4x2"] = "xczu48dr-ffvg1517-2-e"
pynq_part_map["KV260_SOM"] = "xck26-sfvc784-2LV-c"
pynq_part_map["AUP-ZU3_8GB"] = "xczu3eg-sfvc784-2-e"


# native AXI HP port width (in bits) for PYNQ boards
pynq_native_port_width = dict()
pynq_native_port_width["Pynq-Z1"] = 64
pynq_native_port_width["Pynq-Z2"] = 64
pynq_native_port_width["Ultra96"] = 128
pynq_native_port_width["Ultra96-V2"] = 128
pynq_native_port_width["ZCU102"] = 128
pynq_native_port_width["ZCU104"] = 128
pynq_native_port_width["ZCU111"] = 128
pynq_native_port_width["RFSoC2x2"] = 128
pynq_native_port_width["RFSoC4x2"] = 128
pynq_native_port_width["KV260_SOM"] = 128
pynq_native_port_width["AUP-ZU3_8GB"] = 128

# Alveo device and platform mappings
alveo_part_map = dict()
alveo_part_map["U50"] = "xcu50-fsvh2104-2L-e"
alveo_part_map["U200"] = "xcu200-fsgd2104-2-e"
alveo_part_map["U250"] = "xcu250-figd2104-2L-e"
alveo_part_map["U280"] = "xcu280-fsvh2892-2L-e"
alveo_part_map["U55C"] = "xcu55c-fsvh2892-2L-e"

alveo_default_platform = dict()
alveo_default_platform["U50"] = "xilinx_u50_gen3x16_xdma_5_202210_1"
alveo_default_platform["U200"] = "xilinx_u200_gen3x16_xdma_2_202110_1"
alveo_default_platform["U250"] = "xilinx_u250_gen3x16_xdma_2_1_202010_1"
alveo_default_platform["U280"] = "xilinx_u280_gen3x16_xdma_1_202211_1"
alveo_default_platform["U55C"] = "xilinx_u55c_gen3x16_xdma_3_202210_1"

# Create a joint part map, encompassing other boards too
part_map = {**pynq_part_map, **alveo_part_map}
part_map["VEK280"] = "xcve2802-vsvh1760-2MP-e-S"
part_map["VCK190"] = "xcvc1902-vsva2197-2MP-e-S"
part_map["V80"] = "xcv80-lsva4737-2MHP-e-s"


def get_rtlsim_trace_depth():
    """Return the trace depth for rtlsim. Controllable
    via the RTLSIM_TRACE_DEPTH environment variable. If the env.var. is
    undefined, the default value of 1 is returned. A trace depth of 1
    will only show top-level signals and yield smaller .vcd files.

    The following depth values are of interest for whole-network stitched IP
    rtlsim:
    - level 1 shows top-level input/output streams
    - level 2 shows per-layer input/output streams
    - level 3 shows per full-layer I/O including FIFO count signals
    """

    try:
        return int(os.environ["RTLSIM_TRACE_DEPTH"])
    except KeyError:
        return 1


def get_finn_root():
    raise Exception("get_finn_root() should not be used anymore.")


def get_vivado_root():
    "Return the root directory that Vivado is installed into."

    try:
        return os.environ["XILINX_VIVADO"]
    except KeyError:
        raise Exception(
            """Environment variable XILINX_VIVADO must be set
        correctly. Please ensure you have launched the Docker contaier correctly.
        """
        )


def get_liveness_threshold_cycles():
    """Return the number of no-output cycles rtlsim will wait before assuming
    the simulation is not finishing and throwing an exception."""

    return int(os.getenv("LIVENESS_THRESHOLD", 1000000))


def make_build_dir(prefix: str = "", return_as_path: bool = False) -> str | Path:
    """Creates a folder with given prefix to be used as a build dir.
    Use this function instead of tempfile.mkdtemp to ensure any generated files
    will survive on the host after the FINN Docker container exits."""
    try:
        build_dir = Path(os.environ["FINN_BUILD_DIR"])
    except KeyError as keyerror:
        raise Exception("""Environment variable FINN_BUILD_DIR is missing!""") from keyerror

    if not build_dir.exists():
        raise Exception(
            f"FINN_BUILD_DIR at {build_dir} does not exist! "
            "Make sure the FINN setup ran properly!"
        )

    tmpdir = Path(tempfile.mkdtemp(prefix=prefix, dir=build_dir))
    if return_as_path:
        return tmpdir
    return str(tmpdir)


def launch_process_helper(args, proc_env=None, cwd=None, print_stdout=True):
    """Helper function to launch a process in a way that facilitates logging
    stdout/stderr with Python loggers.
    Returns (cmd_out, cmd_err) if successful, raises CalledProcessError otherwise."""
    process = subprocess.run(args, capture_output=True, env=proc_env, cwd=cwd, text=True)
    cmd_out = process.stdout.strip()
    cmd_err = process.stderr.strip()

    # Handle stdout
    if cmd_out:
        if print_stdout is True:
            log.info(cmd_out)
        else:
            # Print with DEBUG level regardless
            log.debug(cmd_out)

    # Handle stderr, depending on return code
    if process.returncode == 0:
        # Process completed successfully, log stderr only as WARNING
        if cmd_err:
            log.warning(cmd_err)
    else:
        # Process failed, log stderr as ERROR
        if cmd_err:
            log.error(cmd_err)

        # Log additional ERROR message
        if isinstance(args, list):
            cmd = " ".join(args)
        else:
            cmd = args
        log.error(f"Launched process returned non-zero exit code ({process.returncode}): {cmd}")

    # Raise CalledProcessError for non-zero return code
    process.check_returncode()
    return (cmd_out, cmd_err)


def which(program):
    "Python equivalent of the shell cmd 'which'."

    # source:
    # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class CppBuilder:
    """Builds the g++ compiler command to produces the executable of the c++ code
    in code_gen_dir which is passed to the function build() of this class."""

    def __init__(self):
        self.include_paths = []
        self.cpp_files = []
        self.executable_path = ""
        self.code_gen_dir = ""
        self.compile_components = []
        self.compile_script = ""

    def append_includes(self, library_path):
        """Adds given library path to include_paths list."""
        self.include_paths.append(library_path)

    def append_sources(self, cpp_file):
        """Adds given c++ file to cpp_files list."""
        self.cpp_files.append(cpp_file)

    def set_executable_path(self, path):
        """Sets member variable "executable_path" to given path."""
        self.executable_path = path

    def build(self, code_gen_dir):
        """Builds the g++ compiler command according to entries in include_paths
        and cpp_files lists. Saves it in bash script in given folder and
        executes it."""
        # raise error if includes are empty
        self.code_gen_dir = code_gen_dir
        self.compile_components.append("g++ -o " + str(self.executable_path))
        for cpp_file in self.cpp_files:
            self.compile_components.append(cpp_file)
        for lib in self.include_paths:
            self.compile_components.append(lib)
        bash_compile = ""
        for component in self.compile_components:
            bash_compile += str(component) + " "
        self.compile_script = str(self.code_gen_dir) + "/compile.sh"
        with open(self.compile_script, "w") as f:
            f.write("#!/bin/bash \n")
            f.write(bash_compile + "\n")
        bash_command = ["bash", self.compile_script]
        launch_process_helper(bash_command, print_stdout=False)


mem_primitives_versal = {
    "URAM_72x4096": (72, 4096),
    "URAM_36x8192": (36, 8192),
    "URAM_18x16384": (18, 16384),
    "URAM_9x32768": (9, 32768),
    "BRAM18_36x512": (36, 512),
    "BRAM18_18x1024": (18, 1024),
    "BRAM18_9x2048": (9, 2048),
    "LUTRAM": (1, 64),
}


def get_memutil_alternatives(
    req_mem_spec, mem_primitives=mem_primitives_versal, sort_min_waste=True
):
    """Computes how many instances of a memory primitive are necessary to
    implement a desired memory size, where req_mem_spec is the desired
    size and the primitive_spec is the primitve size. The sizes are expressed
    as tuples of (mem_width, mem_depth). Returns a list of tuples of the form
    (primitive_name, (primitive_count, efficiency, waste)) where efficiency in
    range [0,1] indicates how much of the total capacity is utilized, and waste
    indicates how many bits of storage are wasted. If sort_min_waste is True,
    the list is sorted by increasing waste.
    """
    ret = [
        (primitive_name, memutil(req_mem_spec, primitive_spec))
        for (primitive_name, primitive_spec) in mem_primitives.items()
    ]
    if sort_min_waste:
        ret = sorted(ret, key=lambda x: x[1][2])
    return ret


def memutil(req_mem_spec, primitive_spec):
    """Computes how many instances of a memory primitive are necessary to
    implemented a desired memory size, where req_mem_spec is the desired
    size and the primitive_spec is the primitve size. The sizes are expressed
    as tuples of (mem_width, mem_depth). Returns (primitive_count, efficiency, waste)
    where efficiency in range [0,1] indicates how much of the total capacity is
    utilized, and waste indicates how many bits of storage are wasted."""

    req_width, req_depth = req_mem_spec
    prim_width, prim_depth = primitive_spec

    match_width = roundup_to_integer_multiple(req_width, prim_width)
    match_depth = roundup_to_integer_multiple(req_depth, prim_depth)
    count_width = match_width // prim_width
    count_depth = match_depth // prim_depth
    count = count_depth * count_width
    eff = (req_width * req_depth) / (count * prim_width * prim_depth)
    waste = (count * prim_width * prim_depth) - (req_width * req_depth)
    return (count, eff, waste)


def is_versal(fpgapart):
    """Returns whether board is part of the Versal family"""
    return fpgapart[0:4] in ["xcvc", "xcve", "xcvp", "xcvm", "xqvc", "xqvm"] or fpgapart[0:5] in [
        "xqrvc",
        "xcv80",
    ]


def get_dsp_block(fpgapart):
    if is_versal(fpgapart):
        return "DSP58"
    elif fpgapart[2] == "7":
        return "DSP48E1"
    else:
        return "DSP48E2"
