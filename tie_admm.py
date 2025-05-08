import numpy as np
from numpy.fft import fftfreq, fft2, ifft2

def op_L_fd(p):
    nx, ny = p.shape
    p12 = np.zeros((2, nx, ny))
    p12[0] = np.roll(p, -1, axis=0) - p  # forward difference along rows
    p12[1] = np.roll(p, -1, axis=1) - p  # forward difference along columns
    return p12


def update_admm(x,z,u,beta,lbda_tv,denom_f,HTb_f,kkr2,kkx,kky):
    
    def ST(v,k):
        
        return np.select([v>k, np.abs(v)<=k, v<(-k)],
                          [v-k, 0            , v+k])
        
    
    v = z - u
    KK = np.where(kkr2 == 0., 0., (HTb_f + 
                                        beta * ((np.exp(- 1j * kkx) - 1) * fft2(v[0]) + 
                                               (np.exp(- 1j * kky) - 1) * fft2(v[1])))
                   / denom_f )
    
    
    
    x = ifft2(KK).real
    v = op_L_fd(x) + u
    z = ST(v,lbda_tv/beta)
    u = u + op_L_fd(x) - z
    
    return x,z,u


def recon(lbda_tv,beta,denom_f,HTb_f,maxiter,kkr2,kkx,kky):
    
    def body_fun(i,val):
        
        x,z,u = val
        return update_admm(x,z,u,beta,lbda_tv,denom_f,HTb_f,kkr2,kkx,kky)
    nx,ny = HTb_f.shape
    phi = np.zeros((nx,ny))
    z = np.zeros((2,nx,ny))
    u = np.zeros((2,nx,ny))
    
    for i in range(maxiter):
        phi, z, u = body_fun(i, (phi, z, u))
    
    return phi 

class TIE_ADMM(object):

    def __init__(self,nx,ny):

        self.nx = nx
        self.ny = ny
        self.kx = fftfreq(self.nx) * 2 * np.pi
        self.ky = fftfreq(self.ny) * 2 * np.pi
        self.kkx,self.kky = np.meshgrid(self.kx,self.ky,indexing='ij')
        self.kkx_jnp,self.kky_jnp = np.asarray(self.kkx), np.asarray(self.kky)
        self.kkr2_jnp = self.kkx_jnp**2 + self.kky_jnp**2

    def solve_tie(self, dI_dz, maxiter=10, lambda_tv=1e-7):

        self.dI_dz_jnp = np.asarray(dI_dz)
        self.HTb_f = - self.kkr2_jnp * fft2(self.dI_dz_jnp)    
        self.BETA = 1e1 * lambda_tv
        self.denom_f = (np.square(self.kkr2_jnp) + 
        self.BETA * ((np.exp(-1j * self.kkx_jnp) - 1.) * (np.exp(1j * self.kkx_jnp) - 1.) +
                     (np.exp(-1j * self.kky_jnp) - 1.) * (np.exp(1j * self.kky_jnp) - 1.)))


        return recon(lambda_tv,
                     self.BETA,
                     self.denom_f,
                     self.HTb_f,
                     maxiter,
                     self.kkr2_jnp,
                     self.kkx_jnp,
                     self.kky_jnp)


        

    
