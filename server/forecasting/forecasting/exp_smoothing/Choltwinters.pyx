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

from scipy.optimize import fmin_l_bfgs_b

""" executes one run of holt winters. For very fast runs with the same initialisation data, 
instantiate a HoltWinters Object and the repeatedly call HoltWinters.double_seasonal(alpha,beta,gamma,delta,autocorr)"""
def double_seasonal(x, m, m2, forecast, alpha, beta, gamma, delta, autocorrelation):
    if (None in (alpha,beta,gamma,delta,autocorrelation)):
        alpha, beta, gamma, delta, autocorrelation = optimize_parameters(x, m, m2, forecast)

    hw = CHoltWinters(x,m,m2,forecast)
    hw._double_seasonal(alpha,beta,gamma,delta,autocorrelation)
    return hw.forecast_series, (alpha, beta, gamma, delta, autocorrelation), hw.y[:-forecast-1]


""" optimize first globally and then locally. The trend component is ignored"""
@cython.initializedcheck(False)
@cython.boundscheck(False) # turn of bounds-checking for entire function
@cython.wraparound(False) #dont wrap around arrays
def optimize_parameters(x,unsigned int m,unsigned int m2,int forecast):
    cdef CHoltWinters holtwinters = CHoltWinters(x,m,m2,forecast)
    cdef int min_index
    cdef unsigned int a_i,g_i,d_i,ac_i = 0
    cdef int steps = 9

    cdef np.ndarray[DTYPE_t,ndim=1] linsp = np.linspace(0,1.0,steps)
    cdef np.ndarray[DTYPE_t, ndim=4] MSEs = np.ndarray(shape=(steps,steps,steps,steps), dtype=DTYPE)
    for a_i in range(0,steps):
        for g_i in range(0,steps):
            for d_i in range(0,steps):
                for ac_i in range(0,steps):
                    MSEs[a_i,g_i,d_i,ac_i] = holtwinters._MSE(linsp[a_i],0.0,linsp[g_i],linsp[d_i],linsp[ac_i])

    min_index = MSEs.argmin() #index of minimum in flattened array
    indices = np.unravel_index(min_index, (steps,steps,steps,steps)) #find original indices
    min_MSE = MSEs[indices] #get minimum mse

    found_parameters = [linsp[i] for i in indices] #map indices back to parameters
    found_parameters.insert(1,0) #insert unused trend
    
    cdef np.ndarray[DTYPE_t,ndim=1] initial_values = np.array(found_parameters, dtype=DTYPE)
    cdef np.ndarray[DTYPE_t,ndim=2] boundaries = np.array([(0, 1), (0, 0.0), (0, 1), (0,1), (0,1)], dtype=DTYPE)
    
    # set to search with very high accuracy.. optimum cant be far..
    optimized_parameters = fmin_l_bfgs_b(holtwinters.MSE, x0 = initial_values, bounds = boundaries, 
                                approx_grad = True,factr=10, epsilon=0.01, maxfun=2000, maxiter=100)


    return optimized_parameters[0]




cdef class CHoltWinters:

    ## type ALL variables
    #these are declared as unsigned, to avoid negative check. 
    #We have to avoid negative indices now
    cdef int forecast
    cdef unsigned int all_length, len_x, m ,m2
    cdef DTYPE_t a_0

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
        self.a_0 = np.sum(x[0:m]) / float(m)

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
                self.s2[k] = self.Y[k] / self.a_0
            if k < m:
                self.s[k] = self.Y[k] / self.a_0
            if k < len(test_data):
                self.test_series[k] = test_data[k]
    
    """thin wrapper for _MSE function. Use this for calls from python, f.e for an optimization routine
        :params: DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation"""
    def MSE(self, params):
        return self._MSE(params[0],params[1],params[2],params[3],params[4])



    @cython.initializedcheck(False)
    @cython.boundscheck(False) # turn of bounds-checking for entire function
    @cython.cdivision(True) #disables checks for zerodivision and other division checks
    @cython.wraparound(False) #dont wrap around arrays
    @cython.nonecheck(False)
    cdef inline DTYPE_t _MSE(self, DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
        cdef DTYPE_t mse_outofsample, mse_insample, sum1, sum2
        cdef unsigned int k, lengthfc

        self._double_seasonal(alpha, beta, gamma, delta, autocorrelation)

        mse_outofsample = ((self.forecast_series.base - self.test_series.base) ** 2).mean(axis=None,dtype=DTYPE)
        mse_insample = ((np.asarray(self.y[:-self.forecast-1],dtype=DTYPE) - self.Y.base) ** 2).mean(axis=None ,dtype=DTYPE)

        return 2 *  mse_insample + 3 * mse_outofsample #weight out of sample more

    #callable from python
    def double_seasonal(self, DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
        self._double_seasonal(alpha, beta, gamma, delta, autocorrelation)
        return self.forecast_series, self.y[:-self.forecast-1]


    @cython.initializedcheck(False)
    @cython.boundscheck(False) # turn of bounds-checking for entire function
    @cython.cdivision(True) #disables checks for zerodivision and other division checks
    @cython.wraparound(False) #dont wrap around arrays
    @cython.nonecheck(False) #do not check for None values
    cdef inline void _double_seasonal(self, DTYPE_t alpha,DTYPE_t beta,DTYPE_t gamma,DTYPE_t delta, DTYPE_t autocorrelation):
        
        cdef DTYPE_t a_i, a_next, s_i, s2_i, autocorr, Y_i
        cdef unsigned int i,i_s2, i_s, m, m2
        cdef np.ndarray[DTYPE_t, ndim=1] Y,s,s2,y

        Y = self.Y.base;s = self.s.base
        s2 = self.s2.base;y = self.y.base
        m = self.m;m2 = self.m2
     
        ## reset variables
        a_i = self.a_0
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
        
