# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import naima
import astropy.units as u
from astropy.io import ascii
import numpy as np

import astropy
astropy.log.setLevel(astropy.logging.CRITICAL)


# Model definition

def cutoffexp(pars, data):
    ecpl = naima.models.ExponentialCutoffPowerLaw(pars[0] * u.Unit('1/(cm2 s TeV)'),
            1*u.TeV, pars[1], pars[2]*u.TeV)
    return ecpl(data)

def IC(pars,data):
    ecpl = naima.models.ExponentialCutoffPowerLaw(pars[0] * u.Unit('1/eV'),
            1*u.TeV, pars[1], pars[2]*u.TeV)
    ic = naima.models.InverseCompton(ecpl)
    return ic.sed(data)

def lnprior(pars):
    return 0


p0 = np.array((1e-12, 2.7, 14.0,))
labels = ['norm', 'index', 'cutoff']

import os
ROOT = os.path.abspath(os.path.dirname(__file__))


class TimeSuite:
    """
    An example benchmark that times the performance of various kinds
    of iterating over dictionaries in Python.
    """
    def setup(self):
        self.pdist = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)
        self.energy_g = np.logspace(-3, 3, 500) * u.TeV
        self.energy_x = np.logspace(-1, 6, 500) * u.eV
        self.ecpl = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)

        self.data = ascii.read(os.path.join(ROOT,'RXJ1713_HESS_2007.dat'))

    def time_prefit_ecpl(self):
        sampler, pos = naima.get_sampler(data_table=self.data, p0=p0,
                labels=labels, model=cutoffexp, prior=lnprior, nwalkers=10,
                nburn=0, prefit=True)

    def time_prefit_ic(self):
        sampler, pos = naima.get_sampler(data_table=self.data, p0=p0,
                labels=labels, model=IC, prior=lnprior, nwalkers=10, nburn=0,
                prefit=True)

    def time_ECPL(self):
        self.ecpl._memoize = False
        for i in range(10):
            pd = self.ecpl(self.energy_g)

    def time_ECPL_memoize(self):
        self.ecpl._memoize = True
        for i in range(10):
            pd = self.ecpl(self.energy_g)

    def time_Sy(self):
        Sy = naima.models.Synchrotron(self.pdist, B=1*u.mG)
        sed = Sy.sed(self.energy_x)

    def time_IC(self):
        IC = naima.models.InverseCompton(self.pdist,
                seed_photon_fields=['CMB','FIR'])
        sed = IC.sed(self.energy_g)

    def time_ICx5(self):
        IC = naima.models.InverseCompton(self.pdist,
                seed_photon_fields=['CMB','FIR'])
        for i in range(5):
            sed = IC.sed(self.energy_g)

    def time_ICx5_nomemoize(self):
        IC = naima.models.InverseCompton(self.pdist,
                seed_photon_fields=['CMB','FIR'])
        IC._memoize = False
        for i in range(5):
            sed = IC.sed(self.energy_g)

    def time_PionDecay(self):
        PP = naima.models.PionDecay(self.pdist)
        sed = PP.sed(self.energy_g)
