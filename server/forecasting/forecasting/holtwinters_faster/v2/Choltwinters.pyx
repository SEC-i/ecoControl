#asdf cython: profile = True
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



def Cdouble_seasonal(x,unsigned int m,unsigned int m2,int forecast,DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
    hw = CHoltWinters(x,m,m2,forecast)
    return hw.double_seasonal(alpha,beta,gamma,delta,autocorrelation)

cdef class CHoltWinters:

    ## type ALL variables
    #these are declared as unsigned, to avoid negative check. 
    #We have to avoid negative indices now
    cdef int forecast
    cdef unsigned int all_length, len_x, m ,m2

    cdef DTYPE_t [:] Y #input
    cdef DTYPE_t [:] s #seasonality1
    cdef DTYPE_t [:] s2 #seasonality2
    cdef DTYPE_t [:] y #onestep forecasts
    cdef DTYPE_t [:] forecast_series #forecasting
    cdef DTYPE_t [:] test_series #test series to compare with forecasting

        

    def __init__(self,x, unsigned int m,unsigned int m2,int forecast, test_data=[]):
        
        #init variables
        self.m = m
        self.m2 = m2
        self.forecast = forecast
        self.len_x = len(x)
        self.all_length = len(x) + forecast
        a_i = np.sum(x[0:m]) / float(m)

        ## alloc arrays, using cython numpy arrays for fast access, also typed


        cdef np.ndarray[DTYPE_t, ndim=1] Y = np.zeros([len(x)], dtype = DTYPE)
        cdef np.ndarray[DTYPE_t, ndim=1] s = np.zeros([self.m+self.all_length], dtype=DTYPE)
        cdef np.ndarray[DTYPE_t, ndim=1] s2 = np.zeros([self.m2/self.m+self.all_length], dtype=DTYPE)
        cdef np.ndarray[DTYPE_t, ndim=1] y = np.zeros([self.all_length +1], dtype=DTYPE)
        cdef np.ndarray[DTYPE_t, ndim=1] forecast_series = np.zeros([forecast], dtype=DTYPE)
        cdef np.ndarray[DTYPE_t, ndim=1] test_series = np.zeros([forecast], dtype=DTYPE)
        self.Y = Y
        self.s = s
        self.s2 = s2
        self.y = y
        self.forecast_series = forecast_series
        self.test_series = test_series


        cdef unsigned int k
        #init arrays
        for k in xrange(len(x)):
            #copy input into typed array
            self.Y[k] = x[k]
            #init seasonal variables
            if k % self.m == 0 and k < self.m2:
                self.s2[k] = self.Y[k] / a_i
            if k < m:
                self.s[k] = self.Y[k] / a_i
            if k < len(test_data):
                self.test_series[k] = test_data[k]

    @cython.initializedcheck(False)
    @cython.boundscheck(False) # turn of bounds-checking for entire function
    @cython.cdivision(True) #disables checks for zerodivision and other division checks
    def MSE(self, DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
        cdef DTYPE_t mse_outofsample, mse_insample, sum1, sum2
        cdef unsigned int k, lengthfc

        self._double_seasonal(alpha, beta, gamma, delta, autocorrelation)

        mse_outofsample = ((self.forecast_series.base - self.test_series.base) ** 2).mean(axis=None,dtype=DTYPE)
        mse_insample = ((np.asarray(self.y[:-self.forecast-1],dtype=DTYPE) - self.Y.base) ** 2).mean(axis=None ,dtype=DTYPE)

        return mse_insample + mse_outofsample

    def double_seasonal(self, DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
        self._double_seasonal(alpha, beta, gamma, delta, autocorrelation)
        return self.forecast_series, self.y[:-self.forecast-1]


    @cython.initializedcheck(False)
    @cython.boundscheck(False) # turn of bounds-checking for entire function
    @cython.cdivision(True) #disables checks for zerodivision and other division checks
    def _double_seasonal(self, DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
        
        cdef DTYPE_t a_i, a_next, s_i, s2_i, autocorr, Y_i
        cdef unsigned int i,i_s2, i_s, m, m2
        cdef np.ndarray[DTYPE_t, ndim=1] Y,s,s2,y

        Y = self.Y.base
        s = self.s.base
        s2 = self.s2.base
        y = self.y.base


        m = self.m
        m2 = self.m2
     
        ## reset variables
        a_i = sum(Y[0:m]) / float(m)
        i_s2 = int(m2 / m)
        i_s = m

        # first forecast
        #y = np.zeros([all_length +1], dtype=DTYPE)
        y[0] = a_i + s[0] + s2[0]
        

        i = 0
        while i < self.all_length:

            if i >= self.len_x:
                self.forecast_series[i- self.len_x] = a_next + s[i_s-m] + s2[i_s2-m2]
                Y_i = self.forecast_series[i- self.len_x]
            else:
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
        
