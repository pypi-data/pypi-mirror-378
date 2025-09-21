import pdb

import commentjson as json
import numpy as np
import pandas as pd
import os
import astropy.units as u
import astropy.io.fits as fits
from einops import repeat
from scipy.integrate import simps
from astropy.modeling.models import Gaussian2D
import extinction

ifs_etc_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata_path = os.path.join(ifs_etc_path, 'refdata/')


def flam2fnu(flam, lam):
    cc = 3e18       # speed of light, A/s
    fnu = flam * lam ** 2 / cc
    return fnu


def flam2mag(flam, lam):
    return -2.5 * np.log10(flam2fnu(flam, lam)) - 48.6


def fnu2flam(fnu, lam):
    cc = 3e18       # speed of light, A/s
    flam = fnu / lam ** 2 * cc
    return flam


def mag2fnu(mag):
    fnu = 10**((mag + 48.6) / -2.5)
    return fnu


def mag2flam(mag, lam):
    fnu = 10**((mag + 48.6) / -2.5)
    flam = fnu2flam(fnu, lam)
    return flam


def json2config(jsonfile):
    """读取json文件，获取etc参数"""
    with open(jsonfile, 'r', encoding='utf-8') as fh:
        s = fh.read()
        config = json.loads(s)
    return config


def config2json(jsonfile, config, indent=4):
    """生成json文件"""
    with open(jsonfile, 'w', encoding="utf-8") as fh:
        s = json.dumps(config, ensure_ascii=False, indent=indent, separators=(',', ':'))
        fh.write(s)


def filter_flam2mag(objwave, objflux, filterwave, filterthroughtput, output='mag'):
    """
    Get AB magnitude in a certain filter.

    Args:
        objwave: unit as A
        objflux: unit as erg/s/cm^2/A
        filterwave: unit as A
        filterthroughtput: unit as detector signal "per photon" (use vaccum_pass for space telescope,
                              otherwise select a given airmass)

    Return:
        AB magnitude in this band

    """

    # resample the throughtput to objwave
    ind = (objwave >= np.min(filterwave)) & (objwave <= np.max(filterwave))
    wavetmp = objwave[ind]
    phot_frac = np.interp(wavetmp, filterwave, filterthroughtput)  # phot fraction (/s/A/cm^2?)

    # convert to energy fraction
    # E_frac = E0/hv * N_frac / E0 ~ N_frac/nu ~ N_frac * lambda
    energy_frac = phot_frac * wavetmp  # convert to energy fraction

    # convert the objflux to erg/s/cm^2/Hz
    c = 3e18  # A/s
    objflux_hz = objflux[ind] * (objwave[ind] ** 2) / c  # erg/s/scm^2/Hz

    from scipy.integrate import simps
    integrate_flux = simps(objflux_hz * energy_frac, c / wavetmp) / simps(energy_frac, c / wavetmp)

    if output == 'mag':
        mag = -2.5 * np.log10(integrate_flux) - 48.6
        return mag
    elif output == 'flux':
        return integrate_flux           # erg/s/cm^2/Hz
    else:
        print('Error: output need to be "mag" or "flux". ')
        return np.nan


def flam2ecounts(diameter, obscure, delta_lambda_per_unit, spaxel_xsize, spaxel_ysize,
                  wavearr, fluxarr, throughtputwave, throughtputvalue):
    """

    Args:
        diameter：diameter of the telescope in cm
        obscure：obscure fraction of the telescope, value within [0, 1]
        spaxel_xsize: spaxel size in dispersion-axis in arcsec
        spaxel_ysize: spaxel size in spatial-axis in arcsec
        wavearr: wavelength range in Angstrom
        fluxarr: erg/s/cm^2/A/arcsec^2 or erg/s/cm^2/Hz/arcsec^2
        throughtputwave: wavelength array of the throughtput curve
        throughtputvalue: throughput fraction
        fluxunit: 'erg/s/cm^2/A' or 'erg/s/cm^2/hz'

    Returns:

    """

    cc = 3.0e18   # speed of light, A/s
    spaxel_area = spaxel_xsize * spaxel_ysize    # arcsec^2
    d = diameter  # diameter of the telescope, in cm unit
    obscure = obscure  # effective central obscuration, no unit
    telarea = 3.14159 / 4.0 * d * d * (1.0 - obscure)  # effective area of the telescope, cm^2
    delta_hz_per_specpixel = delta_lambda_per_unit / wavearr**2 * cc  # s^-1
    planckh = 6.626e-27  # erg*s
    hv = planckh * cc / wavearr  # erg
    QE = 1

    if wavearr.ndim == 3:
        qvalue = np.zeros(shape=wavearr.shape, dtype=float)
        qvalue = np.interp(wavearr[:, 0, 0], throughtputwave, throughtputvalue)
        qvalue = repeat(qvalue, 'h -> h '+str(wavearr.shape[1])+' '+str(wavearr.shape[2]))
    elif wavearr.ndim == 1:
        qvalue = np.interp(wavearr, throughtputwave, throughtputvalue)
    else:
        raise ValueError('check dimension of the input array.')

    isource1 = fluxarr * wavearr ** 2 / cc * spaxel_area  # erg/s/cm^2/Hz per spaxel
    isource2 = isource1 * telarea  # erg/s/Hz per spaxel
    isource3 = qvalue * isource2 * delta_hz_per_specpixel  # erg/s per spaxel
    isource4 = isource3 / hv  # phot/s per spec-element per spaxel
    isource5 = isource4 * QE  # e/s per spec-element per spaxel

    return isource5




def ecounts2flam(diameter, obscure, delta_lambda_per_unit, spaxel_xsize, spaxel_ysize,
                  wavearr, countsarr, throughtputwave, throughtputvalue):
    '''
    :param wavearr: A
    :param countsarr: e-/s
    :return:
    '''


    cc = 3.0e18   # speed of light, A/s
    spaxel_area = spaxel_xsize * spaxel_ysize       # arcsec^2
    telarea = 3.14159 / 4.0 * diameter**2 * (1.0 - obscure)  # effective area of the telescope, cm^2
    delta_hz_per_specpixel = delta_lambda_per_unit / wavearr**2 * cc  # s^-1
    planckh = 6.626e-27  # erg*s
    hv = planckh * cc / wavearr  # erg
    QE = 1

    if wavearr.ndim == 3:
        qvalue = np.interp(wavearr[:, 0, 0], throughtputwave, throughtputvalue)
        qvalue = repeat(qvalue, 'h -> h '+str(wavearr.shape[1])+' '+str(wavearr.shape[2]))
    elif wavearr.ndim == 1:
        qvalue = np.interp(wavearr, throughtputwave, throughtputvalue)
    elif isinstance(wavearr, float):
        qvalue = np.interp(wavearr, throughtputwave, throughtputvalue)
    else:
        raise ValueError('check dimension of the input array.')

    isource4 = countsarr / QE  # phot/s per spec-element per spaxel
    isource3 = isource4 * hv  # erg/s per spec-element per spaxel
    isource2 = isource3 / delta_hz_per_specpixel / qvalue  # erg/s per spaxel
    isource1 = isource2 / telarea  # erg/s/Hz per spaxel
    fluxarr = isource1 / wavearr ** 2 * cc / spaxel_area  # erg/s/cm^2/Hz per spaxel

    return fluxarr



class read_template(object):

    r"""
    get spectrum template using the input parameters

    .. todo::
        enable to add emission lines


    Args:
        isource (dict, including 3 keys):
            name:
                the spectrum filename
            redshift:
                the redshift applied to the template
            ebv:
                the extinction applied to the template

    Attributes:

        wave (`numpy.ndarray`, unit in Angstrom):
            the wavelength of the spectrum, redshift applied.
        flux (`numpy.ndarray`, unit in erg/s/cm^2/A)
            the flux of the spectrum, redshift and extinction considered.

    """

    def __init__(self, isource):

        # self.source = isource
        # self.line_definitions = self.source['lines']

        # snpp_path = '/Users/linlin/Pro/snpp_v1_05/refdata/'
        # template_filename = snpp_refdata + 'sed/' + self.source['name']
        # filtera = snpp_path + 'normalization/filters/sdss_g0.par'
        # result = input_mag_model(self.source['normalization']['value'],
        #                          galtpl, filtera)  # scale the template to given brightness

        template_filename = isource['name']
        template_redshift = isource['redshift']
        template_ebv = isource['ebv']

        # if template_filename.endswith('.fits'):
        #
        #     if template_filename in ['SFgal_texp_FeH0_tau5_Ew10_AGN1.fits',
        #                              'SFgal_texp_FeH0_tau1_Ewd.fits',
        #                              'SFgal_texp_FeH0_tau5_Ew5.fits',
        #                              'SFgal_texp_FeH-2_tau10_Ew50.fits']:
        #         template_filename = os.path.join(refdata_path, 'sed', template_filename)
        #         hdu = fits.open(template_filename)
        #         template_wave = hdu[1].data['wavelength']   # A
        #         template_flux = hdu[1].data['flux'] * 1e-12         # erg/s/cm^2/A
        #
        #     if template_filename in ['ckp00_6000.fits.fits.fits']:
        #         template_filename = os.path.join(refdata_path, 'stellar_library', template_filename)
        #         hdu = fits.open(template_filename)
        #         template_wave = hdu[1].data['WAVELENGTH']   # A
        #         template_flux = hdu[1].data['g00']          # erg/s/cm^2/A
        #
        #     # If the data is big endian, swap the byte order to make it little endian
        #     if template_wave.dtype.byteorder == '>':
        #         template_wave = template_wave.byteswap().newbyteorder()
        #
        # elif template_filename.endswith('.txt'):        # can be a local file.
        #
        #     cat = pd.read_csv(template_filename, sep='\s+', header=None)
        #     template_wave = cat[0]      # unit should be in Angstrom
        #     template_flux = cat[1]      # unit should be in erg/s/cm^2/A
        #
        # else:
        #     raise ValueError("File name need to be ended with '.fits' or '.txt'. ")

        if os.path.isfile(os.path.join(refdata_path, 'sed', template_filename)):   # use template in refdata_path
            filename = os.path.join(refdata_path, 'sed', template_filename)
            if filename.endswith('.fits'):
                cat = fits.getdata(filename)
                template_wave = cat['WAVELENGTH']   # A
                template_flux = cat['FLUX']         # flam

            elif filename.endswith('.dat') or filename.endswith('.asc'):
                cat = pd.read_csv(filename, sep='\s+', comment='#', header=None)
                template_wave = cat[0]      # A
                template_flux = cat[1]      # flam

        elif os.path.isfile(os.path.join('./', template_filename)):         # use a local file
            if template_filename.endswith('.fits'):
                cat = pd.read_csv(template_filename, sep='\s+', comment='#', header=None)
                template_wave = cat[0]      # A
                template_flux = cat[1]      # flam

        else:
            raise ValueError("File do not find: ", template_filename)

        # extinction require the dtype should be double.
        template_wave = np.array(template_wave, dtype='float64')

        # extinction correction
        # assuming Calzetti-00 extinction law.
        r_v = 4.5
        extinction_mag = extinction.calzetti00(template_wave,
                                               template_ebv * r_v,
                                               r_v, unit='aa')
        template_flux = extinction.apply(extinction_mag, template_flux)

        # redshift correction
        template_wave = template_wave * (1 + template_redshift)
        template_flux = template_flux / (1 + template_redshift)

        # 检查输入flux是否有负值，避免噪声sqrt(n)之后会出现nan.
        ind = template_flux < 0
        template_flux[ind] = 0

        self.wave = template_wave
        self.flux = template_flux


class read_filter(object):

    def __init__(self, filter_name=''):
        """

        Args:
            filter_name:
        """

        filter0, filter1 = filter_name.split('_')
        if filter0 == 'sdss':
            filter_file = os.path.join(refdata_path, 'normalization', 'filters', filter_name+'.par')
            band = pd.read_csv(filter_file, sep='\s+', header=None, comment='#')
            self.wave = band[0].values  # A
            self.throughput = band[1].values  # vaccum_pass, per photon
            self.wavemin = self.wave[0]
            self.wavemax = self.wave[-1]

        elif filter0 == 'Johnson':
            filter_file = os.path.join(refdata_path, 'normalization', 'filters', filter_name+'.txt')
            band = pd.read_csv(filter_file, sep='\s+', header=None, comment='#')
            self.wave = (band[0].values)[::-1] * 10     # A
            self.throughput = (band[1].values)[::-1]    # no sure per photon, or per energy. (??)
            self.wavemin = self.wave[0]
            self.wavemax = self.wave[-1]

        elif filter0 == 'GALEX':
            filter_file = os.path.join(refdata_path, 'normalization', 'filters', filter_name+'.par')
            band = pd.read_csv(filter_file, sep='\s+', header=None, comment='#')
            self.wave = band[0].values             # A
            self.throughput = band[1].values       # no sure per photon, or per energy. (??)
            self.wavemin = self.wave[0]
            self.wavemax = self.wave[-1]

        else:
            print('un_recognized filter system.')

        # find the central wavelength, effective wavelength, and FWHM of the given filter
        # filtermid = (self.wavemax - self.wavemin) * 0.5  # A, central wavelength
        dwave = self.wave[1:] - self.wave[:-1]
        self.waveeff = np.nansum(dwave * self.wave[1:] * self.throughput[1:]) / \
                       np.nansum(dwave * self.throughput[1:])
        # A, effective wavelength
        rmax = np.max(self.throughput)
        nnn = np.where(self.throughput > 0.5 * rmax)[0]
        self.FWHMmin = self.wave[nnn[0]]      # wave range at FWHM
        self.FWHMmax = self.wave[nnn[-1]]
        self.wavefwhm = self.FWHMmax - self.FWHMmin  # A, FWHM


def normalized(template_wave, template_flux, normalize_config):
    """
    normalized to a fixed band or a certain wavelength at given AB magnitude.

    Args:
        template_wave: A
        template_flux: f_lambda
        normalize_config: {'value', 'unit', 'band' or 'wavelength'}

    Returns:
        normalize_wave: same as template wave
        normalize_flux: normalized f_lambda
    """

    if 'band' in normalize_config.keys():

        # normlized at certain filter
        filter = read_filter(normalize_config['band'])
        normalized_wave = filter.waveeff
        ind_filter = (template_wave >= filter.wavemin) & (template_wave <= filter.wavemax)
        filter_wave = template_wave[ind_filter]
        filter_flux = np.interp(filter_wave, filter.wave, filter.throughput)
        filter_constant = simps(filter_flux * filter_wave, filter_wave)

        template_constant = simps(filter_flux * template_wave[ind_filter] * template_flux[ind_filter],
                                  template_wave[ind_filter])

        template_flux_norm = template_flux / (template_constant / filter_constant)

    elif 'wavelength' in normalize_config.keys():

        # normlized at certain wavelength
        normalized_wave = normalize_config['wavelength']
        template_flux0 = np.interp(normalized_wave, template_wave, template_flux)
        template_flux_norm = template_flux / template_flux0

    else:
        raise ValueError('Need to specify normalized at certain band or wavelength.')

    # get scaled factor at the normalized wave
    # convert the unit to erg/s/cm^2/A
    if normalize_config['unit'] == 'erg/s/cm^2/Hz':
        u0 = (normalize_config['value'] * u.erg / u.s / u.cm ** 2 / u.Hz).to(
            u.erg / u.s / u.cm ** 2 / u.AA, equivalencies=u.spectral_density(normalized_wave * u.AA)
        )
        u0 = u0.value
    elif normalize_config['unit'] == 'erg/s/cm^2/A':
        u0 = normalize_config['value']
    elif (normalize_config['unit'] == 'AB magnitude') or (normalize_config['unit'] == 'AB magnitude/arcsec^2'):
        u0 = (10**((normalize_config['value'] + 48.6)/(-2.5)) * u.erg / u.s / u.cm ** 2 / u.Hz).to(
            u.erg / u.s / u.cm ** 2 / u.AA, equivalencies=u.spectral_density(normalized_wave * u.AA)
        )
        u0 = u0.value
    else:
        raise ValueError('Unrecognized unit of the source.')

    norm_wave = template_wave                  # A
    norm_flux = template_flux_norm * u0           # erg/s/cm^2/A

    # check the normalized magnitude should be normalized.value - 2.5*log(0.04)
    mag = filter_flam2mag(norm_wave, norm_flux, filter_wave, filter_flux)

    return norm_wave, norm_flux, mag


def resample_lambda(wave_resample, wave, flux):

    flux_resample = np.interp(wave_resample, wave, flux)

    return flux_resample



def get_throughput(filename):

    """
    read throughput file

    Returns:
        throughputwave: unit in Angstrom
        throughputvalue: unit in photon fraction (sdss), energy frac = phot_frac * wavetmp
                        # photon fraction convert to energy fraction
                        # E_frac = E0/hv * N_frac / E0 ~ N_frac/nu ~ N_frac * lambda
    """

    cat = pd.read_csv(filename, comment='#', sep='\s+', header=None, names=['A', 'q'])
    throughputwave = cat['A'].values        # A
    throughputvalue = cat['q'].values       # photon fraction

    return throughputwave, throughputvalue



def pointsource_box_frac(psf_fwhm, box_dx, box_dy, box_xoff, box_yoff):
    '''

    Args:
        psf_fwhm: PSF FWHM, unit in arcsec
        grid_dx: grid size in x-axis, unit in arcsec
        grid_dy: grid size in y-axis, unit in arcsec

    Returns:

    '''
    from scipy import integrate

    x_stddev = psf_fwhm / 2.35482
    y_stddev = psf_fwhm / 2.35482
    f = lambda y, x: 1/(2*np.pi*x_stddev*y_stddev) * np.exp(-(x ** 2 / (2 * x_stddev**2) + y ** 2 / (2 * y_stddev**2)))

    x_range = (box_xoff - box_dx/2, box_xoff + box_dx/2)
    y_range = (box_yoff - box_dy/2, box_yoff + box_dy/2)
    fraction, error = integrate.dblquad(f, x_range[0], x_range[1], y_range[0], y_range[1])

    return fraction


def sharpness(psf_fwhm=0.26):

    dx = 0.2
    dy = 0.2
    nx = 30
    ny = 30
    img2d_center = np.zeros(shape=(nx, ny), dtype=float)
    img2d_corner = np.zeros(shape=(nx, ny), dtype=float)
    x = np.arange(-15, 15, 1) * dx
    y = np.arange(-15, 15, 1) * dy

    for i in range(nx):
        for j in range(ny):
            img2d_center[j, i] = pointsource_box_frac(psf_fwhm, dx, dy, x[i], y[j])
            img2d_corner[j, i] = pointsource_box_frac(psf_fwhm, dx, dy, x[i]+0.5*dx, y[j]+0.5*dy)

    sharpness_center = np.sum(img2d_center**2)
    sharpness_corner = np.sum(img2d_corner**2)

    return sharpness_center, sharpness_corner


def get_sky_counts_rate(throughput_wave, throughput_value, diameter, obscure, delta_lambda_per_unit,
                   zodia_level, earthshine_level, wavearr, spaxel_xsize, spaxel_ysize):

    """
    Consider zodiacal background and earth shine background in different levels.

    Args:
        zodia_level:
            zodiacal level, 'low', 'med', 'high', corresponding index from 1-3.
        earthshine_level:
            earth shine level, 'low', 'med', 'high', corresponding index from 1-3.
        wavearr:
            wave array to be returned.

    Returns:
        sky counts (e-/s) in each spaxel element (spaxel_xsize * spaxel_ysize), in 1d array.

    """

    # get IFS throughtput
    # throughtputwave, throughtputvalue = get_throughput(throughputfile)

    # get the zodia spectrum, convert to e/s/spaxel/spec-elements
    filename = os.path.join(refdata_path, 'csst', 'background', 'zodi_spec.csv')
    cat = pd.read_csv(filename, comment='#')
    zodia_wave = cat['wave']
    zodia_spec = cat['zodi_' + zodia_level]       # erg/s/cm^2/A/arcsec^2
    zodia_spec_interp = np.interp(wavearr, zodia_wave, zodia_spec)
    zodia_counts_interp = flam2ecounts(diameter, obscure, delta_lambda_per_unit,
                                        spaxel_xsize, spaxel_ysize,
                                        wavearr, zodia_spec_interp,
                                        throughput_wave, throughput_value)

    # get the earth shine spectrum, convert to e/s/spaxel/spec-elements
    filename = os.path.join(refdata_path, 'csst', 'background', 'earthshine_spec.csv')
    cat = pd.read_csv(filename, comment='#')
    earthshine_wave = cat['wave']
    earthshine_spec = cat['earthshine_' + earthshine_level]       # erg/s/cm^2/A/arcsec^2
    earthshine_spec_interp = np.interp(wavearr, earthshine_wave, earthshine_spec)
    earthshine_counts_interp = flam2ecounts(diameter, obscure, delta_lambda_per_unit,
                                             spaxel_xsize, spaxel_ysize,
                                             wavearr, earthshine_spec_interp,
                                             throughput_wave, throughput_value)

    nsky_rate = zodia_counts_interp + earthshine_counts_interp

    return nsky_rate







def source_counts_rate_per_spaxel(template_config, normalize_config, instru_config,
                                  throughput_config, point_source=False):

    """

    Args:
        template_config: dict('wave', 'flam')
        normalize_config: dict('value', 'unit', 'band' or 'wavelength')
        instru_config: dict('diameter', 'obscure', 'spaxel_xsize', 'spaxel_ysize',
                            'wave_start', 'wave_end', 'wave_delta', 'psf_fwhm' (if point_source=True))
        throughput_config: dict('wave', 'photon_frac')
        point_source: default=False, if True, it will calculate the flux fraction in one spaxel.

    Returns:
        source_counts_rate: e_counts/s/spaxel

    """

    # only for point source, estimate total flux in one spaxel.
    if point_source is True:
        if normalize_config['unit'] == 'AB magnitude':
            fnu_center = mag2fnu(normalize_config['value']) / \
                     (instru_config['spaxel_xsize'] * instru_config['spaxel_ysize'])  # erg/s/cm^2/Hz/arcsec^2
            mag_per_arcsec2 = -2.5 * np.log10(fnu_center) - 48.6
            normalize_config['value'] = mag_per_arcsec2
        else:
            raise ValueError('convert the normlized unit to "AB magnitude".')


    # resample to the template to ccd_wavelength
    template_wave_resample = np.arange(instru_config['wave_start'],
                                       instru_config['wave_end'],
                                       instru_config['wave_delta'])
    template_flam_resample = resample_lambda(template_wave_resample,
                                             template_config['wave'],
                                             template_config['flam'])

    # normalize
    norm_wave, norm_flux, mag_per_arcsec2 = normalized(template_wave_resample, template_flam_resample, normalize_config)


    # flam to counts_rate
    source_counts_rate = flam2ecounts(instru_config['diameter'], instru_config['obscure'],
                                      instru_config['wave_delta'],
                                      instru_config['spaxel_xsize'],
                                      instru_config['spaxel_ysize'],
                                      norm_wave, norm_flux,
                                      throughput_config['wave'],
                                      throughput_config['photon_frac'])

    # pdb.set_trace()

    return source_counts_rate





