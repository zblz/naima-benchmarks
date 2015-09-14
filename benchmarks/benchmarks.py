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

ecpl = naima.models.ExponentialCutoffPowerLaw(1e35 * u.Unit('1/eV'),
        1*u.TeV, 2.3, 50*u.TeV)
ic = naima.models.InverseCompton(ecpl)

def IC_2(pars,data):
    ecpl.amplitude = pars[0] / u.eV
    ecpl.alpha = pars[1]
    ecpl.e_cutoff = pars[2]*u.TeV
    return ic.flux(data)


def lnprior(pars):
    return 0


p0 = np.array((1e-12, 2.7, 14.0,))
labels = ['norm', 'index', 'cutoff']

import os
ROOT = os.path.abspath(os.path.dirname(__file__))


class TimeECPL:
    """
    An example benchmark that times the performance of various kinds
    of iterating over dictionaries in Python.
    """
    def setup(self):
        self.energy_g = np.logspace(-3, 3, 500) * u.TeV

        self.ecpl = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)
        self.ecpl._memoize = True
        _ = self.ecpl(self.energy_g)

    def time_ECPL_1start(self):
        ecpl = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)

    def time_ECPL_2memoize(self):
        self.ecpl._memoize = True
        pd = self.ecpl(self.energy_g)

    def time_ECPL_3nomemo(self):
        self.ecpl._memoize = False
        pd = self.ecpl(self.energy_g)


class TimeRadIC:
    def setup(self):
        self.pdist = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)
        self.energy_g = np.logspace(-3, 3, 500) * u.TeV

        self.IC = naima.models.InverseCompton(self.pdist,
                seed_photon_fields=['CMB','FIR'])
        _ = self.IC.sed(self.energy_g)


    def time_IC_1start(self):
        IC = naima.models.InverseCompton(self.pdist,
                seed_photon_fields=['CMB', 'FIR',
                    ['star', 20000*u.K, 1*u.erg/u.cm**3, 90*u.deg],
                    ['NIR', 200*u.K, 1*u.eV/u.cm**3],
                    ])

    def time_IC_2memo(self):
        _ = self.IC.flux(self.energy_g)

    def time_IC_3nomemo(self):
        self.IC._memoize = False
        _ = self.IC.flux(self.energy_g)

class TimeRadPionDecay:
    def setup(self):
        self.pdist = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)
        self.energy_g = np.logspace(-3, 3, 500) * u.TeV

        self.PP = naima.models.PionDecay(self.pdist)
        _ = self.PP.sed(self.energy_g)

    def time_PionDecay_1start(self):
        PP = naima.models.PionDecay(self.pdist)

    def time_PionDecay_2memo(self):
        self.PP._memoize = True
        _ = self.PP.flux(self.energy_g)

    def time_PionDecay_3nomemo(self):
        self.PP._memoize = False
        _ = self.PP.flux(self.energy_g)

    def time_PionDecay_4loadLUT(self):
        self.PP._memoize = False
        self.PP.diffsigma.fname = ''
        _ = self.PP.flux(self.energy_g)

class TimeRadSy:
    def setup(self):
        self.pdist = naima.models.ExponentialCutoffPowerLaw(1e36/u.eV,
                1*u.TeV, 2.7, 50*u.TeV)
        self.energy_x = np.logspace(-1, 6, 500) * u.eV
        self.Sy = naima.models.Synchrotron(self.pdist, B=1*u.mG)
        self.Sy._memoize = False

    def time_Sy_1start(self):
        Sy = naima.models.Synchrotron(self.pdist, B=1*u.mG)

    def time_Sy_2run(self):
        _ = self.Sy.flux(self.energy_x)


class TimePrefit:
    def setup(self):
        self.data = ascii.read(os.path.join(ROOT,'RXJ1713_HESS_2007.dat'))

    def time_prefit_ecpl(self):
        sampler, pos = naima.get_sampler(data_table=self.data, p0=p0,
                labels=labels, model=cutoffexp, prior=lnprior, nwalkers=10,
                nburn=0, prefit=True)

    def time_prefit_ic(self):
        sampler, pos = naima.get_sampler(data_table=self.data, p0=p0,
                labels=labels, model=IC, prior=lnprior, nwalkers=10, nburn=0,
                prefit=True)

    def time_prefit_ic2(self):
        sampler, pos = naima.get_sampler(data_table=self.data, p0=p0,
                labels=labels, model=IC_2, prior=lnprior, nwalkers=10, nburn=0,
                prefit=True)

