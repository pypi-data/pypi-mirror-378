import numpy as np
from scipy.signal import find_peaks
from librosa import frames_to_samples, samples_to_frames
from .utils import *


# TODO : create base class
class MultiGranularSegmentation():
    def __init__(self, sr, n_fft, peak_detection, L=20, I=1, T=2, min_segment_duration=0.1, normalize = True):
        
        self.sr = sr
        self.n_fft = n_fft 

        self.peak_detection = peak_detection

        if peak_detection == "easy":
            self.peak_detection_kwargs = {"min_segment_duration":min_segment_duration}
        elif peak_detection == "robust":
            self.peak_detection_kwargs = {"L":L, "I":I, "T":T}
        else :
            raise NotImplementedError()
        
        self.min_segment_duration = min_segment_duration
        self.normalize = normalize




    def _compute_causal_dssm(self,y):
        #compute SSM from STFT
        ssm = compute_ssm(y, self.n_fft)
        #remove future events from SSM
        ssm_causal = ssm
        for i in range(ssm.shape[0]):
            ssm_causal[i,:i]=0

        dssm = 1-ssm_causal #dissimilarity matrix

        return dssm
    
    def compute_novelty(self, y):
        
        dssm = self._compute_causal_dssm(y)

        nov = np.zeros(dssm.shape[0])
        scales=np.zeros_like(nov)
        #contrasts=np.zeros_like(nov)
        #at each time t 
        for t in range(1,dssm.shape[0]):
            #check the lines below t to asses temporal scale
            for i in range(1,t+1):
                s_t=dssm[t-i,t]
                
                #1) check if ssm(t-i,t)<ssm(t-i,t-1) 
                if s_t>=dssm[t-i,t-1]: 
                    #print(s_t,ssm_causal[t-i,t-1])
                    break 
                #2) check if ssm(t,t)<mean(line)-2*std(line)
                line = dssm[t-i,t-i:t]
                mu, std = np.mean(line), np.std(line)
                
                
                if s_t >= mu - 2*std : 
                    #print("s_t",s_t,", mean - 2*std:",mu-2*std)
                    break
            
            #print(t,i)
            t_scale=i
            c_prev = dssm[t-1-t_scale:t-1,t-1]
            c = dssm[t-1-t_scale:t-1,t]
            contrast = np.linalg.norm(c-c_prev,ord=1)
            #print(f"scale and contrast at time {t} : {t_scale}, {contrast}")
            
            nov[t]=contrast #the novelty curve is the contrast between the two columns t-1 and t in the range of the temporal scale
            scales[t]=t_scale
            #contrasts[t]=contrast
        
        if self.normalize : nov = (nov-min(nov))/(max(nov)-min(nov))

        return nov, scales
    
    def find_peaks_easy(self,nov, min_segment_duration=0.1):
       #nov, scales = self.compute_novelty(y, n_fft)
        

        #easy peak detection
        mu, std = np.mean(nov), np.std(nov)
        thresh = mu+2*std
        peaks, _ = find_peaks(nov, height=thresh, distance=time_to_frames(min_segment_duration,sr=self.sr,hop_length=self.n_fft,n_fft=self.n_fft))


        return peaks
    
    def find_peaks_robust(self, nov, L, I, T):
        #nov, scales = self.compute_novelty(y, n_fft)

        peaks = robust_peak_detection(nov, L, I, T)

        # peaks_samples = frames_to_samples(peaks,hop_length=self.n_fft, n_fft=self.n_fft)
        # peaks_samples = np.concatenate([[0],peaks_samples])

        return peaks
    
    def find_peaks(self, nov):
        
        peaks = self.find_peaks_easy(nov, **self.peak_detection_kwargs) if self.peak_detection == "easy" else self.find_peaks_robust(nov,**self.peak_detection_kwargs)

        delta = samples_to_frames(int(self.min_segment_duration*self.sr))
        peaks = non_maximum_suppression_1d(peaks, nov, delta)

        peaks_samples = frames_to_samples(peaks,hop_length=self.n_fft, n_fft=self.n_fft)
        peaks_samples = np.concatenate([[0],peaks_samples])

        return peaks_samples

    
    def segment(self, y):
        nov, scales = self.compute_novelty(y)

        nov = (nov-min(nov))/(max(nov)-min(nov)) #normalize

        peaks = self.find_peaks(nov)

        #peaks = non_maximum_suppression_1d(peaks, nov, self.min_segment_duration)

        segments = [y[t0:t1] for t0,t1 in zip(peaks[:-1],peaks[1:])]

        return segments