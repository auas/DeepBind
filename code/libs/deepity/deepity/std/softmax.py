# Copyright (c) 2015, Andrew Delong and Babak Alipanahi All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# Author's note: 
#     This file was distributed as part of the Nature Biotechnology 
#     supplementary software release for DeepBind. Users of DeepBind
#     are encouraged to instead use the latest source code and binaries 
#     for scoring sequences at
#        http://tools.genes.toronto.edu/deepbind/
# 
from ..node import node
from smat import *
from . import globals

class softmax(node):
    """
    Softmax node.
    Computes Z = softmax(X) wher softmax is applied row-wise.
    If ngroup > 1, then each row is broken down into 'ngroup'
    softmax computations (X.ncol must be divisible by ngroup).
    """
    def __init__(self,ngroup=1):
        super(softmax,self).__init__(["X"],["Z"])
        self.ngroup = ngroup

    def _fprop(self,X):
        if globals.flags.get("disable_softmax",False):
            return X

        # Compute softmax on entire rows.
        # If ngroup > 1, then softmax is applied separately to
        #  groups of elements within each row.
        nchunk = self.ngroup * self.ninst
        if nchunk == X.shape[1]:
            # One output per target, which means we're doing logistic regression
            # and can just pass each value through the logistic function.
            Z = logistic(X)
        elif nchunk == 1: 
            Z  = exp(X-max(X,axis=1))  # Subtract max for numerical stability.
            Z /= sum(Z,axis=1)         # Normalize
        else:
            assert X.ncol % nchunk == 0, "Number of columns in X must be divisible by ngroup * ninst."
            A = X.reshape((-1,X.ncol//nchunk))
            Z  = exp(A-max(A,axis=1))  # Subtract max for numerical stability.
            Z /= sum(Z,axis=1)         # Normalize
            Z = Z.reshape(X.shape)  # Put back in proper shape.
        return Z

    def _requirements(self):
        return { "target" : "logistic" }

    def _bprop(self,dZ):
        return dZ                      # softmax must be used at final output, and does not alter the backpropagated error

    def _calc_shapes(self,X,Z):
        if   X._shape: Z._shape = X._shape  # All elemwise functions have same output dim as input dim
        elif Z._shape: X._shape = Z._shape

softmaxnode = softmax