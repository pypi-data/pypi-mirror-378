import numpy as np
from librosa import stft, load, frames_to_time, clicks, time_to_frames, frames_to_samples

#compute similarity matrix
def compute_ssm(y, w_size):
    #compute stft with window size w_size and no overlapping segments
    fft = np.abs(stft(y,n_fft=w_size,hop_length=w_size)) #(freq_bins=nfft//2+1, frames)
    
    X = fft.T #(frames, freq_bins)
    X_norm = X/(np.linalg.norm(X, axis=1, keepdims=True)+1e-9)
    
    ssm = np.dot(X_norm, X_norm.T) #cosine similarity

    return ssm

def compute_kernel_checkerboard_gaussian(L, var=1, normalize=True):
    """Compute Guassian-like checkerboard kernel [FMP, Section 4.4.1].
    See also: https://scipython.com/blog/visualizing-the-bivariate-gaussian-distribution/

    Notebook: C4/C4S4_NoveltySegmentation.ipynb

    Args:
        L (int): Parameter specifying the kernel size M=2*L+1
        var (float): Variance parameter determing the tapering (epsilon) (Default value = 1.0)
        normalize (bool): Normalize kernel (Default value = True)

    Returns:
        kernel (np.ndarray): Kernel matrix of size M x M
    """
    taper = np.sqrt(1/2) / (L * var)
    axis = np.arange(-L, L+1)
    gaussian1D = np.exp(-taper**2 * (axis**2))
    gaussian2D = np.outer(gaussian1D, gaussian1D)
    kernel_box = np.outer(np.sign(axis), np.sign(axis))
    kernel = kernel_box * gaussian2D
    if normalize:
        kernel = kernel / np.sum(np.abs(kernel))
    return kernel

def compute_novelty_ssm(S, kernel=None, L=10, var=0.5, exclude=False):
    """Compute novelty function from SSM [FMP, Section 4.4.1]

    Notebook: C4/C4S4_NoveltySegmentation.ipynb

    Args:
        S (np.ndarray): SSM
        kernel (np.ndarray): Checkerboard kernel (if kernel==None, it will be computed) (Default value = None)
        L (int): Parameter specifying the kernel size M=2*L+1 (Default value = 10)
        var (float): Variance parameter determing the tapering (epsilon) (Default value = 0.5)
        exclude (bool): Sets the first L and last L values of novelty function to zero (Default value = False)

    Returns:
        nov (np.ndarray): Novelty function
    """
    if kernel is None:
        kernel = compute_kernel_checkerboard_gaussian(L=L, var=var)
    N = S.shape[0]
    M = 2*L + 1
    nov = np.zeros(N)
    # np.pad does not work with numba/jit
    S_padded = np.pad(S, L, mode='constant')

    for n in range(N):
        # Does not work with numba/jit
        nov[n] = np.sum(S_padded[n:n+M, n:n+M] * kernel)
    if exclude:
        right = np.min([L, N])
        left = np.max([0, N-L])
        nov[0:right] = 0
        nov[left:N] = 0

    return nov

def non_maximum_suppression_1d(peaks, values, delta):
    """
    Keep only the maximum peak within a neighborhood of ±delta.

    Parameters:
    - peaks: array of peak indices (e.g., from find_peaks)
    - values: array of novelty values at those peak indices
    - delta: minimum distance (in samples) between accepted peaks

    Returns:
    - suppressed_peaks: filtered list of peak indices
    """
    if len(peaks) == 0:
        return []

    # Sort peaks by descending value
    order = np.argsort(values[peaks])[::-1]
    selected = []
    suppressed = np.zeros(len(peaks), dtype=bool)

    for i in order:
        if suppressed[i]:
            continue
        p = peaks[i]
        selected.append(p)

        # Suppress all peaks within ±delta
        for j in range(len(peaks)):
            if not suppressed[j] and abs(peaks[j] - p) <= delta:
                suppressed[j] = True

    return np.array(sorted(selected))

def robust_peak_detection(nov, L, I, T):
    filteredY = nov[:L].tolist()
    avgFilter = [np.mean(nov[:L])]*L
    stdFilter = [np.std(nov[:L])]*L

    peaks = []

    for i in range(L,len(nov)):
        if abs(nov[i]-avgFilter[i-1]) > T*stdFilter[i-1]:
            #peak detected at timestep i
            peaks.append(i) 
            #update moving average
            filteredY.append(I*nov[i]+(1-I)*filteredY[i-1])
        else :
            filteredY.append(nov[i])#(I*nov[i]+(1-I)*filteredY[i-1])
        
        avgFilter.append(np.mean(filteredY[-L:]))
        stdFilter.append(np.std(filteredY[-L:]))
        
    #clean peaks
    #peaks_values = nov[peaks]
    #cleaned_peaks = non_maximum_suppression_1d(peaks, nov,5)

    return peaks
