from __future__ import division
import numpy as np
# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
cimport cython
# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.float64
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.float64_t DTYPE_t


@cython.boundscheck(False) # turn of bounds-checking for entire function
def Cdouble_seasonal(x,unsigned int m,unsigned int m2,int forecast,DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta,
                    DTYPE_t autocorrelation):
 

    test_series = []
    ## type ALL variables
    cdef DTYPE_t Y_i, a_i, a_next, autocorr, s_i, s2_i
    #these are declared as unsigned, to avoid negative check. 
    #We have to avoid negative indices now
    cdef unsigned int i,i_s2, i_s, k, all_length, len_x

    ## init variables
    all_length = len(x) + forecast+len(test_series)
    a_i = sum(x[0:m]) / float(m)
    i_s2 = len(range(0,m2,m))
    i_s = m
    len_x = len(x)


    ## alloc arrays, using cython numpy arrays for fast access, also typed
    cdef np.ndarray[DTYPE_t, ndim=1] Y = np.zeros([all_length], dtype = DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] s = np.zeros([m+all_length], dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] s2 = np.zeros([m2/m+all_length], dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] y = np.zeros([all_length +1], dtype=DTYPE)
    
    #init arrays
    for k in xrange(len_x):
        #copy input into typed array
        Y[k] = x[k]
        #init seasonal variables
        if k % m == 0 and k < m2:
            s2[k] = Y[k] / a_i
        if k < m:
            s[k] = Y[k] / a_i


    # first forecast
    y[0] = a_i + s[0] + s2[0]
    
    ## use cython memory views for consistent indexing
    cdef DTYPE_t [:] Y_view = Y
    cdef DTYPE_t [:] y_view = y
    i = 0
    while i < all_length:

        if i >= len_x:
            Y[i] = a_next + s[i_s-m] + s2[i_s2-m2]
        
        Y_i = Y[i]
        s_i = s[i]
        s2_i = s2[i]
        
        a_next =  alpha * (Y_i - s2_i - s_i) + (1 - alpha) * (a_i)
        s[i_s] =  delta *  (Y_i - a_i - s2_i) + (1 - delta) * s_i
        s2[i_s2] = gamma * (Y_i - a_i - s_i) + (1 - gamma) * s2_i
        autocorr = autocorrelation * (Y_i - (a_i + s_i + s2_i))
        y[i+1] = a_next + s[i + 1] + s2[i + 1] + autocorr
        
        i_s2 += 1
        i_s += 1
        i += 1
        a_i = a_next
    

    return Y_view[-forecast:], (alpha, beta, gamma, delta, autocorrelation), y_view[:-forecast]