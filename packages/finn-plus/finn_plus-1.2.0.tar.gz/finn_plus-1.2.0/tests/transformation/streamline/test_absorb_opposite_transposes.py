# Copyright (c) 2020, Xilinx
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

import pytest

import numpy as np
import onnx.parser as oprs
from qonnx.core.modelwrapper import ModelWrapper
from qonnx.transformation.infer_shapes import InferShapes

import finn.core.onnx_exec as ox
from finn.transformation.streamline.absorb import AbsorbConsecutiveTransposes


@pytest.mark.streamline
def test_absorb_opposite_transposes():
    np.random.seed(0)
    shp = [1, 3, 4, 2]
    shp_str = str(shp)
    input = f"""
    <
        ir_version: 7,
        opset_import: ["" : 9]
    >
    agraph (float{shp_str} in0) => (float{shp_str} out0)
    <
        float[1] add0_param = {{1.0}},
        float[1] add1_param = {{3.0}},
        float[1] mul0_param = {{2.0}}
    >
    {{
        add0_out = Add(in0, add0_param)
        t0_out = Transpose<perm=[0,2,3,1]>(add0_out)
        t1_out = Transpose<perm=[0,3,1,2]>(t0_out)
        add1_out = Add(t1_out, add1_param)
        t2_out = Transpose<perm=[0,2,3,1]>(add1_out)
        t3_out = Transpose<perm=[0,3,1,2]>(t2_out)
        add2_out = Add(t1_out, t3_out)
        t4_out = Transpose<perm=[0,2,3,1]>(add2_out)
        t5_out = Transpose<perm=[0,3,1,2]>(t4_out)
        t6_out = Transpose<perm=[0,3,1,2]>(t4_out)
        m0_out = Mul(t5_out, mul0_param)
        m1_out = Mul(t6_out, mul0_param)
        out0 = Mul(m0_out, m1_out)
    }}
    """
    model = oprs.parse_model(input)
    model = ModelWrapper(model)
    model = model.transform(InferShapes())
    new_model = model.transform(AbsorbConsecutiveTransposes())
    new_model = new_model.transform(InferShapes())
    inp_dict = {"top_in": np.random.rand(*shp).astype(np.float32)}
    assert ox.compare_execution(model, model, inp_dict)
    assert len(new_model.graph.node) == 6
    for n in new_model.graph.node:
        assert new_model.graph.node[0].op_type != "Transpose"
