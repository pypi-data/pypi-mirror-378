import numpy as np
from scipy.special import factorial
from joblib import Parallel, delayed

def simulate_pch_1c_mc_ntimes(psf, concentration, brightness, n_samples, n_hist_max=10, max_bin=101, err=1e-5):
    hist_all = np.zeros((max_bin, n_hist_max))
    continue_simulation = True
    current_simulation = 1
    while continue_simulation:
        counts, bin_edges = simulate_pch_1c_mc(psf, concentration, brightness, n_samples, max_bin)
        hist_all[:,current_simulation-1] = counts / n_samples
        if current_simulation > 3:
            hist_av = np.mean(hist_all[:,0:current_simulation], 1)
            hist_std_err = np.mean(np.std(hist_all[:,0:current_simulation], 1) / np.sqrt(current_simulation))
            print(hist_std_err)
            if hist_std_err < err or current_simulation >= n_hist_max:
                continue_simulation = False
        current_simulation += 1
    
    n_simulations = current_simulation - 1
    return hist_av, bin_edges, hist_std_err, hist_all[:,0:n_simulations], n_simulations
    
    
def simulate_pch_1c_mc(psf, concentration, brightness, n_samples, max_bin=101):
    """
    Simulate photon counting histogram with Monte Carlo, assuming 1 component

    Parameters
    ----------
    psf : np.array()
        3D array with the PSF, normalized to sum=1.
    concentration : float
        Emitter concentration. The default is 1.
    brightness : float
        Brighness of the emitter. The default is 1.
    n_samples : int
        Number of simulations. Each simulation is a single int with the detected
        number of photons
    max_bin : int, optional
        Maximum bin number for the histogram. The default is 101.

    Returns
    -------
    counts : np.array()
        1D array with the photon counts per bin.
    bin_edges : np.array()
        1D array with the bin edges.

    """
    list_of_photons = simulate_photon_counts_1c_mc(psf, concentration, brightness, n_samples)
    bins = np.arange(0, max_bin+1, 1)  # center bins on integers
    counts, bin_edges = np.histogram(list_of_photons, bins=bins)
    return counts, bin_edges


def simulate_pch_nc_mc(psf, concentration, brightness, n_samples, max_bin=101):
    """
    Simulate photon counting histogram with Monte Carlo, assuming 1 component

    Parameters
    ----------
    psf : np.array()
        3D array with the PSF, normalized to sum=1.
    concentration : list of float
        Emitter concentration for each component.
    brightness : list of float
        Brighness of the emitter for each component.
    n_samples : int
        Number of simulations. Each simulation is a single int with the detected
        number of photons
    max_bin : int, optional
        Maximum bin number for the histogram. The default is 101.

    Returns
    -------
    counts : np.array()
        1D array with the photon counts per bin.
    bin_edges : np.array()
        1D array with the bin edges.

    """
    n_comp = len(concentration)
    list_of_photons = np.zeros((n_samples))
    
    for c in range(n_comp):
        list_of_photons += simulate_photon_counts_1c_mc(psf, concentration[c], brightness[c], n_samples)
    bins = np.arange(0, max_bin+1, 1)  # center bins on integers
    counts, bin_edges = np.histogram(list_of_photons, bins=bins)
    return counts, bin_edges
    

def simulate_photon_counts_1c_mc(psf, concentration, brightness, n_samples, n_jobs=-1):
    """
    Simulate photon counts with a MC approach, assuming 1 component

    Parameters
    ----------
    psf : np.array()
        3D array with the PSF, normalized to sum=1.
    concentration : float
        Emitter concentration (particles per voxel). The default is 1.
    brightness : float
        Brighness of the emitter. The default is 1.
    n_samples : int
        Number of simulations. Each simulation is a single int with the detected
        number of photons

    Returns
    -------
    det_photons : np.array()
        1D array with the total detected photon counts for each simulation.

    """
    nx = np.shape(psf)[0]

    def one_simulation(_):
        # Generate random 3D positions for particles
        n_particles = np.random.poisson(concentration * nx * nx * nx)
        positions = np.random.randint(0, nx, size=(n_particles, 3)).astype(int)
        x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]

        expected_photons = brightness * psf[x, y, z]

        # Add shot noise (Poisson distributed photon counts)
        emitted_photons = np.random.poisson(expected_photons)
        detected_photons = np.sum(emitted_photons)
        return detected_photons

    # Run in parallel
    det_photons = Parallel(n_jobs=n_jobs)(
        delayed(one_simulation)(j) for j in range(n_samples)
    )

    return np.array(det_photons)


def simulate_pch_1c(psf, dV=1, k_max=30, c=1, q=1, T=1, dV0=1):
    """
    Recover the photon counting histogram P(k) from the generating function G(xi)
    Assume 1 component

    Parameters
    ----------
    psf : np.array()
        3D array with the PSF, normalized to np.max(psf)=1.
    k_max : int, optional
        Number of histogram bins to simulate. The default is 30.
    c : float, optional
        Emitter concentration. The default is 1.
    q : float, optional
        Brighness of the emitter. The default is 1.
    T : float, optional
        Bin time. The default is 1.
    dV : float, optional
        Voxel volume. The default is 1.

    Returns
    -------
    coeffs
        P(k) for k=0..n-1.

    """
    
    
    G = np.zeros(k_max, dtype=complex)
    int_B = q * psf * T
    k_array = np.linspace(0, k_max-1, k_max)
    phi = 2 * np.pi * k_array / k_max
    xi_minus1 = np.exp(-1j * phi) - 1
    
    for idx in range(int(k_max)):
        G[idx] = dV0 * np.sum(dV * (np.exp(xi_minus1[idx] * int_B) - 1))
        
    G = np.exp(c * G)
    
    pch = np.abs(np.fft.ifft(G))
    pch /= np.sum(pch)
    
    return pch


def simulate_pch_nc(psf, dV=1, k_max=30, c=[1], q=[1], T=1, dV0=1, b=0):
    """
    Recover the photon counting histogram P(k) from the generating function G(xi)
    Assume n components

    Parameters
    ----------
    psf : np.array()
        3D array with the PSF, normalized to np.max(psf)=1.
    k_max : int, optional
        Number of histogram bins to simulate. The default is 30.
    c : list, optional
        List of emitter concentration for all components. The default is [1].
    q : list, optional
        List of brighness for all components. The default is [1].
    T : float, optional
        Bin time. The default is 1.
    dV : float, optional
        Voxel volume. The default is 1.

    Returns
    -------
    pch
        P(k) for k=0..n-1.

    """
    n_comp = len(c)
    
    log_G_tot = np.zeros(k_max, dtype=complex)
    k_array = np.linspace(0, k_max-1, k_max)
    phi = 2 * np.pi * k_array / k_max
    xi_minus1 = np.exp(-1j * phi) - 1
    
    # all components
    for i in range(n_comp):
        G_single_comp = np.zeros(k_max, dtype=complex)
        int_B = q[i] * psf * T
        
        for idx in range(int(k_max)):
            G_single_comp[idx] = dV0 * np.sum(dV * (np.exp(xi_minus1[idx] * int_B) - 1))
        
        log_G_tot += c[i] * G_single_comp
    
    # background
    b *= T # convert dark counts rate to absolute counts in time T
    bg = np.asarray([b**k*np.exp(-b)/factorial(k) for k in range(k_max)])
    bg_fft = np.fft.fft(bg)
    log_bg_G = np.log(bg_fft)
    
    log_G_tot += log_bg_G
    
    G = np.exp(log_G_tot)
    
    pch = np.abs(np.fft.ifft(G))
    pch /= np.sum(pch)
    
    return pch