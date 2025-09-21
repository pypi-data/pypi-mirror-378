from os.path import basename

import math
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, least_squares
from scipy.ndimage import gaussian_filter1d
from scipy.linalg import svd
import matplotlib.pyplot as plt

from .utils import fl_guess


k_B = 8.617333262145 * 10 ** -5  # eV/K


def F(E, E_f, T):
    if T == 0:
        return np.heaviside(E_f-E, 0.5)
    return 1/(1+np.exp((E-E_f)/(k_B*T)))


def fermiedge(E, a, b, C, E_f, T):
    return F(E, E_f, T)*(a*(E-E_f) + b) + C


def make_fe(T, step_size):
    def broadened_fermiedge(E, a, b, C, sigma, E_f):
        # extend E by 3 sigma (to avoid edge effects)
        n_ext = math.ceil(3*sigma/step_size)
        E_ext = np.pad(E, mode='linear_ramp', pad_width=n_ext, 
            end_values=(E[0]-n_ext*step_size, E[-1]+n_ext*step_size))
        fe = fermiedge(E_ext, a, b, C, E_f, T)
        if sigma == 0:
            return fe
        return gaussian_filter1d(
            fe,
            sigma/step_size, 
            mode='nearest')[n_ext:-n_ext]
    return broadened_fermiedge


def cut(x, y, window):
    idx_start = (np.abs(x - window[0])).argmin()
    idx_end = (np.abs(x - window[1])).argmin()
    return x[idx_start:idx_end], y[idx_start:idx_end]


def fermi_fit(spec, T, de=1., ax=None, fl=None, sigma='sqrt'):
    fl = fl or fl_guess(spec.energy_scale, spec.edc)
    window = (fl - de / 2, fl + de / 2)
    cut_e_ax, cut_edc = cut(spec.energy_scale, spec.edc, window)
    if sigma == 'sqrt':
        sigma = np.sqrt(cut_edc)

    func = make_fe(T, spec.get_metadata('Step Size'))

    param_names = ["a", "b", "C", "sigma", "E_f"]
    initial_guess = (0, max(cut_edc), min(spec.edc), 0.05, fl)
    bounds = [(0, -np.inf, 0, 0, window[0]),  # restrict a to be positive
              (np.inf, np.inf, np.inf, np.inf, window[1])]
    fit_params, cov = curve_fit(func, cut_e_ax, cut_edc,
                                p0=initial_guess,
                                bounds=bounds, 
                                sigma=sigma,
                                absolute_sigma=False) 
    # curve_fit absolute sigma=fac*np.sqrt(cut_edc); fac, because ADC mode produces many counts

    fit_params_d = dict(zip(param_names, fit_params))
    fit_params_d.update(dict(zip([p + '_err' for p in param_names], np.sqrt(np.diag(cov)))))
    fit_params_d['factor'] = 1.
    fit_params_d['fwhm'] = 2.3548 * fit_params_d['sigma']
    fit_params_d['fwhm_err'] = 2.3548 * fit_params_d['sigma_err']
    
    if ax:
        ax.plot(cut_e_ax, cut_edc, linewidth=0.5, label='spectrum')
        ax.axhline(fit_params_d['C'], linewidth=0.5, ls=':', label='background')
        ax.plot(cut_e_ax, fit_params_d['C']+fit_params_d['a']*(cut_e_ax-fit_params_d['E_f']) + fit_params_d['b'], ls='--', color='k', alpha=0.3, label='DOS')
        ax.axvline(fit_params_d['E_f'], lw=0.5, color='k', alpha=0.3, label='$E_F$')
        ax.plot(cut_e_ax, func(cut_e_ax, *fit_params), label='fit')
        ax.set_xlim(cut_e_ax[0], cut_e_ax[-1])
        # ax.plot(cut_e_ax, func(cut_e_ax, *initial_guess), color='k')

    return fit_params_d


def opt_global(fits, T, *specs, de=1., plot_fits=False):
    func = make_fe(T, specs[0]['Step Size']) # todo implement separate global err function for each

    def global_err(p, *xys, verbose=False):
        assert len(xys) % 2 == 0 and len(xys) > 0
        assert len(p) == 3 + 3 * (len(xys)//2)

        errs = []
        for i in range(len(xys)//2):
            factor = p[3+3*i] # factor
            p_i = p[0], p[1], p[2], p[3+3*i+1], p[3+3*i+2] # a, b, C, sigma, E_f
            x, y = xys[2*i:2*i+2]
            errs.extend(factor*func(x, *p_i) - y)
            errs.append(1000*(factor-1))
            if verbose:
                print("subfit", i)
                print(factor)
                print(p_i)

        return np.array(errs)

    a_global = np.average(fits["a"], weights=1/fits["a_err"])
    b_global = np.average(fits["b"], weights=1/fits["b_err"])
    C_global = np.average(fits["C"], weights=1/fits["C_err"])
    p_global = [a_global, b_global, C_global]
    bounds_g = [(0, np.inf), (-np.inf, np.inf), (0, np.inf)]

    xys = []
    for i, fit in fits.iterrows():
        p_global.append(1) # factor
        bounds_g.append((0, np.inf))

        p_global.append(fit["sigma"]*10)
        bounds_g.append((0, np.inf))

        p_global.append(fit["E_f"])
        edc = specs[i].edc
        e_ax = np.linspace(specs[i]['Start K.E.'], specs[i]['End K.E.'], len(edc))
        fl = fit["E_f"]
        window = (fl - de / 2, fl + de / 2)
        bounds_g.append(window)
        xys.extend(cut(e_ax, edc, window))

    result = least_squares(global_err, p_global, args=xys, bounds=np.array(bounds_g).T)
    if not result.success:
        print("global fit result", result)
        raise Exception('global fit failed')
    else:
        p_best = result.x

    # FROM SCIPY # Do Moore-Penrose inverse discarding zero singular values.
    _, s, VT = svd(result.jac, full_matrices=False)
    threshold = np.finfo(float).eps * max(result.jac.shape) * s[0]
    s = s[s > threshold]
    VT = VT[:s.size]
    pcov = np.dot(VT.T / s**2, VT)
    warn_cov = False
    if pcov is None:
        # indeterminate covariance
        pcov = zeros((len(popt), len(popt)), dtype=float)
        pcov.fill(inf)
        warn_cov = True
    else: # elif not absolute sigma (default False)
        ysize = len(result.fun)
        cost = 2 * result.cost
        p0 = np.atleast_1d(p_global)
        if ysize > p0.size:
            s_sq = cost / (ysize - p0.size)
            pcov = pcov * s_sq
        else:
            pcov.fill(inf)
            warn_cov = True
    #############
    
    perr = np.sqrt(np.diag(pcov))

    fits_global = []
    for i, p in fits.iterrows():
        factor = p_best[3+3*i] # factor
        p_i = p_best[0], p_best[1], p_best[2], p_best[3+3*i+1], p_best[3+3*i+2] # a, b, C, sigma, E_f
        
        factor_err = perr[3+3*i]
        perr_i = perr[0], perr[1], perr[2], perr[3+3*i+1], perr[3+3*i+2] # a, b, C, sigma, E_f
        
        x, y = xys[2*i:2*i+2]

        #print('factor', repr(factor))
        param_names = ["factor", "a", "b", "C", "sigma", "E_f"]
        fit = dict(zip(param_names, (factor,)+p_i))
        fit.update(dict(zip([p+'_err' for p in param_names], (factor_err,)+perr_i)))
        
        fit['fwhm'] = 2.3548 * fit['sigma']
        fit['fwhm_err'] = 2.3548 * fit['sigma_err']
        fits_global.append(fit)

        if plot_fits:
            plt.figure(figsize=(3, 1))
            plt.plot(np.linspace(specs[i]['Start K.E.'],
                                 specs[i]['End K.E.'], len(edc)), specs[i].edc)
            plt.plot(x, factor*func(x, *p_i))
            plt.xlim(x[0], x[-1])
            plt.show()

    return pd.DataFrame(fits_global)


def plot_opt(specs, params, T, de=1., param_name='measurement param', plot_param="sigma", fit_global=False, plot_fits=False,
             zip_fname=None, fl=None, **plot_kwargs):
    fits = []
    for spec in specs:
        if plot_fits:
            plt.figure(figsize=(3, 1))
            plt.title(str(spec))
            fit = fermi_fit(spec, T=T, de=de, fl=fl, ax=plt.gca())
            plt.show()
        else:
            fit = fermi_fit(spec, T=T, de=de, fl=fl)
        fit['spectrum'] = str(spec)
        fits.append(fit)
    fits = pd.DataFrame(fits)

    plot_kwargs.setdefault('label', 'individual fit')
    plot_kwargs.setdefault('marker', 'x')
    plot_kwargs.setdefault('linestyle', '')
    plot_kwargs.setdefault('capsize', 4)
    y = fits[plot_param]
    yerr = fits[plot_param+'_err']
    markers, caps, bars = plt.errorbar(params, y, yerr=yerr, **plot_kwargs)
    
    dy = max(y) - min(y)
    plt.ylim([min(y)-dy/20, max(y)+dy/20])
    
    [c.set_alpha(0.2) for c in caps]
    [b.set_alpha(0.2) for b in bars]
    plt.xlabel(param_name)
    plt.ylabel(plot_param)

    if fit_global:
        print('starting global fit')
        if plot_kwargs['label'] == 'individual fit':
            del plot_kwargs['label']
        fits_global = opt_global(fits, T, *specs, de=de, plot_fits=plot_fits)
        fits_global['filename'] = fits['filename']
        plot_kwargs.setdefault('label', 'global fit')
        
        y = fits_global[plot_param]
        yerr = fits_global[plot_param+'_err']
        markers, caps, bars = plt.errorbar(params, y, yerr=yerr, **plot_kwargs)
        [c.set_alpha(0.2) for c in caps]
        [b.set_alpha(0.2) for b in bars]
        plt.legend()
        return fits_global

    return fits