import numpy as np
import jax
import jax.numpy as jnp
from functools import partial

@jax.jit
def op_L_fd(p):
    
    nx,ny = p.shape
    p12 = jnp.zeros((2,nx,ny))
    p12 = p12.at[0].set(jnp.roll(p,-1,axis=0) - p)
    p12 = p12.at[1].set(jnp.roll(p,-1,axis=1) - p)

    return p12

@jax.jit
def update_admm(x,z,u,beta,lbda_tv,denom_f,HTb_f,kkr2,kkx,kky):
    
    def ST(v,k):
        
        return jnp.select([v>k, jnp.abs(v)<=k, v<(-k)],
                          [v-k, 0            , v+k])
        
    
    v = z - u
    KK = jnp.where(kkr2 == 0., 0., (HTb_f + 
                                        beta * ((jnp.exp(- 1j * kkx) - 1) * jnp.fft.fft2(v[0]) + 
                                               (jnp.exp(- 1j * kky) - 1) * jnp.fft.fft2(v[1])))
                   / denom_f )
    
    
    
    x = jnp.fft.ifft2(KK).real
    v = op_L_fd(x) + u
    z = ST(v,lbda_tv/beta)
    u = u + op_L_fd(x) - z
    
    return x,z,u


@partial(jax.jit,static_argnames='maxiter')
def recon(lbda_tv,beta,denom_f,HTb_f,maxiter,kkr2,kkx,kky):
    
    def body_fun(i,val):
        
        x,z,u = val
        return update_admm(x,z,u,beta,lbda_tv,denom_f,HTb_f,kkr2,kkx,kky)
    nx,ny = HTb_f.shape
    phi = jnp.zeros((nx,ny))
    z = jnp.zeros((2,nx,ny))
    u = jnp.zeros((2,nx,ny))
    
    phi,z,u = jax.lax.fori_loop(0,maxiter,body_fun,(phi,z,u))
    
    return phi 

class TIE_ADMM(object):

    def __init__(self,nx,ny):

        self.nx = nx
        self.ny = ny
        self.kx = np.fft.fftfreq(self.nx) * 2 * np.pi
        self.ky = np.fft.fftfreq(self.ny) * 2 * np.pi
        self.kkx,self.kky = np.meshgrid(self.kx,self.ky,indexing='ij')
        self.kkx_jnp,self.kky_jnp = jnp.asarray(self.kkx),jnp.asarray(self.kky)
        self.kkr2_jnp = self.kkx_jnp**2 + self.kky_jnp**2

    def solve_tie(self, dI_dz, maxiter=10, lambda_tv=1e-7):

        self.dI_dz_jnp = jnp.asarray(dI_dz)
        self.HTb_f = - self.kkr2_jnp * jnp.fft.fft2(self.dI_dz_jnp)    
        self.BETA = 1e1 * lambda_tv
        self.denom_f = (jnp.square(self.kkr2_jnp) + 
        self.BETA * ((jnp.exp(-1j * self.kkx_jnp) - 1.) * (jnp.exp(1j * self.kkx_jnp) - 1.) +
                     (jnp.exp(-1j * self.kky_jnp) - 1.) * (jnp.exp(1j * self.kky_jnp) - 1.)))


        return recon(lambda_tv,
                     self.BETA,
                     self.denom_f,
                     self.HTb_f,
                     maxiter,
                     self.kkr2_jnp,
                     self.kkx_jnp,
                     self.kky_jnp)


        

    
