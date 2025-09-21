import numpy as np
import pandas as pd
import os
import astropy.io.fits as fits
import astropy.units as u
from scipy.integrate import simpson as simps
from einops import repeat, rearrange
import extinction
import pdb

from astropy.modeling.models import Sersic2D, Box2D, Gaussian2D

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata = os.path.join(path, 'refdata/')


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

        if template_filename.endswith('.fits'):

            hdu = fits.open(template_filename)
            template_wave = hdu[1].data['wavelength']   # A
            template_flux = hdu[1].data['flux'] * 1e-12         # erg/s/A/cm2

            # If the data is big endian, swap the byte order to make it little endian
            if template_wave.dtype.byteorder == '>':
                template_wave = template_wave.byteswap().view(template_wave.byteswap().dtype.newbyteorder())

        elif template_filename.endswith('.txt'):

            cat = pd.read_csv(template_filename, sep='\s+', header=None)    # separate by blank space
            template_wave = cat[0]      # unit should be in Angstrom
            template_flux = cat[1]      # unit should be in erg/s/cm^2/A

        else:
            raise ValueError("File name need to be ended with '.fits' or '.txt'. ")

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

        self.wave = template_wave
        self.flux = template_flux


class Grid(object):

    """
    Generate the xy-grid of the IFU FOV under the instrument configuration.

    Args:
        config

    Attributes:

        dx:
            spaxel size in x-direction, unit as arcsec
        dy:
            spaxel size in y-direction, unit as arcsec
        nx:
            the number of elements in xarr
        ny:
            the number of elements in yarr
        spaxel_area:
            dx * dy, unit as arcsec^2
        xarr:
            x-array, unit as integer numbers of 0.2 arcsec
        yarr:
            y-array, unit as integer numbers of 0.2 arcsec
        x2d:
            2d array in x, unit as integer numbers of 0.2 arcsec
        y2d:
            2d array in y, unit as integer numbers of 0.2 arcsec
    """

    def __init__(self, config):

        self.config = config['configuration']
        self.dx = self.config['spaxel_xsize']
        self.dy = self.config['spaxel_ysize']
        self.nx = int(self.config['fov_xsize'] / self.dx)
        self.ny = int(self.config['fov_ysize'] / self.dy)
        self.spaxel_area = self.dx * self.dy

        # in arcsec
        # self.xarr = np.arange(0, self.config['fov_xsize'], self.dx)
        # self.yarr = np.arange(0, self.config['fov_ysize'], self.dy)
        # self.x2d, self.y2d = np.meshgrid(self.xarr, self.yarr)

        # in spaxel in 0.2 step
        self.xarr = np.arange(0, 30, self.dx / 0.2)
        self.yarr = np.arange(0, 30, self.dy / 0.2)
        self.x2d, self.y2d = np.meshgrid(self.xarr, self.yarr)


def get_wavearr(config):

    instr_par = config['configuration']
    wave_start = instr_par['wave_start']
    wave_end = instr_par['wave_end']
    wave_delta = instr_par['ccd_xsize'] * instr_par['readout_xbin']

    ccdspec_wave = np.arange(wave_start, wave_end, wave_delta)

    return ccdspec_wave


class read_filter(object):

    def __init__(self, filter_name=''):
        """

        Args:
            filter_name:
        """

        filter0, filter1 = filter_name.split('_')
        if filter0 == 'sdss':
            filter_file = os.path.join(refdata, 'normalization', 'filters', filter_name+'.par')
            band = pd.read_csv(filter_file, sep='\s+', header=None, comment='#')
            self.wave = band[0].values  # A
            self.throughput = band[1].values  # vaccum_pass, per photon
            self.wavemin = self.wave[0]
            self.wavemax = self.wave[-1]

        elif filter0 == 'Johnson':
            filter_file = os.path.join(refdata, 'normalization', 'filters', filter_name+'.txt')
            band = pd.read_csv(filter_file, sep='\s+', header=None, comment='#')
            self.wave = (band[0].values)[::-1] * 10     # A
            self.throughput = (band[1].values)[::-1]    # no sure per photon, or per energy. (??)
            self.wavemin = self.wave[0]
            self.wavemax = self.wave[-1]

        elif filter0 == 'GALEX':
            filter_file = os.path.join(refdata, 'normalization', 'filters', filter_name+'.par')
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


def filter_mag(objwave, objflux, filterwave, filterthroughtput, output='mag'):

    """
    Get AB magnitude in a certain filter.
    
    Args:
        objwave: unit as A
        objflux: unit as erg/s/cm^2/A
        filterwave: unit as A
        filterthroughtput: unit as detector signal per photon (use vaccum_pass for space telescope,
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
    c = 3e18    # A/s
    objflux_hz = objflux[ind] * (objwave[ind]**2) / c    # erg/s/scm^2/Hz

    from scipy.integrate import simps
    integrate_flux = simps(objflux_hz * energy_frac, c/wavetmp) / simps(energy_frac, c/wavetmp)

    if output == 'mag':
        mag = -2.5 * np.log10(integrate_flux) - 48.6
        if integrate_flux < 0:
            print('Warning: the intergrate_flux less than 0, the return mag will be NaN.')
        return mag
    elif output == 'flux':
        return integrate_flux
    else:
        print('Error: output need to be "mag" or "flux". ')
        return np.nan


def normalized(template_wave, template_flux, config):
    """
    Scale the spectrum template to the given value.

    Args:
        template_wave:
            unit in A
        template_flux:
            unit in erg/s/cm^2/A
        config:
            the normalization dict: {'value', 'unit', 'band' or 'wavelength'}
            the geometry info to generate the 2D surface brightness map

    Returns:
        the scaled spectrum cube.

    """

    grid = Grid(config)

    source = config['source']
    n_source = len(source)
    cube_flux = 0

    for i in range(n_source):

        inormalize = source[i]['normalization']

        if 'band' in inormalize.keys():

            # normlized at certain filter
            filter = read_filter(inormalize['band'])
            normalized_wave = filter.waveeff
            ind_filter = (template_wave >= filter.wavemin) & (template_wave <= filter.wavemax)
            filter_wave = template_wave[ind_filter]
            filter_flux = np.interp(filter_wave, filter.wave, filter.throughput)
            filter_constant = simps(filter_flux * filter_wave, filter_wave)

            template_constant = simps(filter_flux * template_wave[ind_filter] * template_flux[ind_filter],
                                      template_wave[ind_filter])

            template_flux_norm = template_flux / (template_constant / filter_constant)

        else:

            # normlized at certain wavelength
            normalized_wave = inormalize['wavelength']
            template_flux0 = np.interp(normalized_wave, template_wave, template_flux)
            template_flux_norm = template_flux / template_flux0


        # get scaled factor at the normalized wave
        # convert the unit to erg/s/cm^2/A
        if inormalize['unit'] == 'erg/s/cm^2/Hz':
            u0 = (inormalize['value'] * u.erg / u.s / u.cm ** 2 / u.Hz).to(
                u.erg / u.s / u.cm ** 2 / u.AA, equivalencies=u.spectral_density(normalized_wave * u.AA)
            )
            u0 = u0.value
        elif inormalize['unit'] == 'erg/s/cm^2/A':
            u0 = inormalize['value']
        elif (inormalize['unit'] == 'AB magnitude') or (inormalize['unit'] == 'AB magnitude/arcsec^2'):
            u0 = (10**((inormalize['value'] + 48.6)/(-2.5)) * u.erg / u.s / u.cm ** 2 / u.Hz).to(
                u.erg / u.s / u.cm ** 2 / u.AA, equivalencies=u.spectral_density(normalized_wave * u.AA)
            )
            u0 = u0.value
        else:
            raise ValueError('Unrecognized unit of the source.')


        # get scaled 2d image
        # https://docs.astropy.org/en/stable/modeling/predef_models2D.html
        # input xy-offset unit as arcsec
        # input FWHM unit as arcsec
        # output xy-grid unit in spaxels (0.2" per grid)

        geometry = source[i]['geometry']
        xcen = grid.nx / 2 + source[i]['position']['x_offset'] / grid.dx
        ycen = grid.ny / 2 + source[i]['position']['y_offset'] / grid.dy

        if geometry['shape'] == 'sersic':

            rmaj = geometry['Re_maj'] / grid.dx
            rmin = geometry['b2a'] * rmaj
            sersicn = geometry['sersic_n']
            ellip = 1 - rmin/rmaj
            theta = (geometry['PA'] + 90) / 180 * np.pi
            u_re = u0

            mod = Sersic2D(amplitude=u_re, r_eff=rmaj,
                           n=sersicn, x_0=xcen, y_0=ycen,
                           ellip=ellip, theta=theta)

        elif geometry['shape'] == 'flatbox':

            xwidth = geometry['xwidth'] / grid.dx
            ywidth = geometry['ywidth'] / grid.dy

            mod = Box2D(amplitude=u0, x_0=xcen, y_0=ycen,
                        x_width=xwidth, y_width=ywidth)


        elif geometry['shape'] == 'gaussian':

            u_peak = u0
            x_stddev = geometry['x_fwhm'] / 2.35 / grid.dx
            y_stddev = geometry['y_fwhm'] / 2.35 / grid.dy
            theta = (geometry['PA'] + 90) / 180 * np.pi
            mod = Gaussian2D(amplitude=u_peak, x_mean=xcen, y_mean=ycen,
                        x_stddev=x_stddev, y_stddev=y_stddev,
                        theta=theta)

        elif geometry['shape'] == 'PSF':

            # only valid for point source, FWHM = 0.2", u0 is the total flux.
            # the normalized value is thought to be the integral value.
            # for gaussian integral flux = 2 * pi * A * sigma_x * sigma_y
            # grid.dx = 0.2"
            x_stddev = 0.2 / 2.35 / grid.dx
            y_stddev = 0.2 / 2.35 / grid.dy
            # surface brightness at the peak
            u_peak = u0 / 2 / np.pi / x_stddev / y_stddev / (grid.dx * grid.dy)
            mod = Gaussian2D(amplitude=u_peak, x_mean=xcen, y_mean=ycen,
                        x_stddev=x_stddev, y_stddev=y_stddev)

        else:
                print(geometry['shape'] + ' is not defined.')
                mod = None

        # generate the xy grid
        # unit in spaxel (0.2" per grid)
        scaled_img = mod(grid.x2d, grid.y2d)

        # make to a cube for each component
        tmp_template_flux = repeat(template_flux_norm, 'h -> h w c', w=grid.ny, c=grid.nx)
        tmp_factor = repeat(scaled_img, 'w c -> h w c', h=len(template_wave))
        norm_flux = tmp_template_flux * tmp_factor

        cube_flux = cube_flux + norm_flux


    # generate the wavelength cube
    cube_wave = repeat(template_wave, 'h -> h w c', w=grid.ny, c=grid.nx)


    # check the magnitude
    filter = read_filter('sdss_g')
    mag2d = np.zeros(shape=(grid.ny, grid.nx), dtype=float)
    for j in range(grid.ny):
        for i in range(grid.nx):
            mag2d[j, i] = filter_mag(cube_wave[:, j, i], cube_flux[:, j, i],
                                   filter.wave, filter.throughput, output='mag')


    return cube_wave, cube_flux, mag2d


class ModelCube(object):

    def __init__(self, config):
        # 生成的cube（波长和flux）对应了ccd上数据点（按config设置）

        self.ccdspec_wave = get_wavearr(config)
        self.ccdspec_nw = len(self.ccdspec_wave)

        if config['source_mode'] == 2:      # 按参数生成的模型

            n_source = len(config['source'])
            for i in range(n_source):

                iobject = config['source'][i]

                template = read_template(iobject['spectrum'])
                template_wave_interp = self.ccdspec_wave
                template_flux_interp = np.interp(template_wave_interp, template.wave, template.flux)

                # self.ccdspec_flux = np.zeros(shape=(self.ccdspec_nw, grid.ny, grid.nx), dtype=np.float32)

                self.wavecube, self.fluxcube, self.mag2d = normalized(template_wave_interp, template_flux_interp,
                                                                      config)
                # 这部分循环有问题，这里n_source循环一次，normalized对n_source又循环一次
                # 不同template并没有起作用。
                # todo: 把normalized里的循环取消，在这里增加循环，以及流量叠加。

        elif config['source_mode'] == 1:    # 冯帅生成的模型作为输入

            import astropy.io.fits as fits
            dat = fits.open(config['source']['filename'])
            template_hdr = dat[1].header
            wave_start = template_hdr['CRVAL1'] * 1e10
            wave_delta = template_hdr['CDELT1'] * 1e10
            wave_end = wave_start + template_hdr['NAXIS1']*wave_delta
            template_wave = np.arange(wave_start, wave_end, wave_delta)
            template_flux = dat[1].data * 1e-17 / 0.04      # erg/s/cm^/A / arcsec^2
            nx = template_hdr['NAXIS2']
            ny = template_hdr['NAXIS3']

            wavecube = repeat(template_wave, 'h -> h w c', w=ny, c=nx)
            wavecube_interp = repeat(self.ccdspec_wave, 'h -> h w c', w=ny, c=nx)

            from scipy.interpolate import interp1d
            fluxcube_reshape = rearrange(template_flux, 'h w c -> c h w')
                                                # c: wavelength, h: dec, w: ra
            fluxcube_interp = wavecube_interp.copy()
            filter = read_filter('sdss_g')
            mag2d = np.zeros(shape=(ny, nx), dtype=float)  # here is surface brightness

            # pdb.set_trace()

            for i in range(nx):
                for j in range(ny):
                    f = interp1d(wavecube[:, j, i], fluxcube_reshape[:, j, i], fill_value='extrapolate')
                    fluxcube_interp[:, j, i] = f(wavecube_interp[:, j, i])
                    mag2d[j, i] = filter_mag(wavecube_interp[:, j, i], fluxcube_interp[:, j, i],
                                             filter.wave, filter.throughput, output='mag')

                    # if np.isnan(mag2d[j, i]) == True:
                    #     pdb.set_trace()

            self.wavecube = wavecube_interp
            self.fluxcube = fluxcube_interp
            self.mag2d = mag2d


    # def export_to_fits(self, fitsfile='ModelCube'):


    def ConvolvedCube(self):
        
        from astropy.convolution import convolve
        
        psf = fits.getdata(refdata+'source/psf_026.fits', 0)
        lsf = fits.getdata(refdata+'source/lsf_13.fits', 0)

        nw, ny, nx = self.fluxcube.shape
        flux_conv1 = np.zeros(shape=self.fluxcube.shape, dtype=float)
        flux_conv2 = np.zeros(shape=self.fluxcube.shape, dtype=float)
        
        # psf convolve
        for i in range(nw):
            flux_conv1[i, :, :] = convolve(self.fluxcube[i, :, :], psf)
            
        # lsf convolve
        for i in range(nx):
            for j in range(ny):
                flux_conv2[:, j, i] = convolve(flux_conv1[:, j, i], lsf)
        
        self.fluxcube = flux_conv2
        
        # update the magnitude
        filter = read_filter('sdss_g')
        mag2d = np.zeros(shape=(ny, nx), dtype=float)
        for j in range(ny):
            for i in range(nx):
                mag2d[j, i] = filter_mag(self.wavecube[:, j, i], self.fluxcube[:, j, i],
                                    filter.wave, filter.throughput, output='mag')
        self.mag2d = mag2d


        
           
        

