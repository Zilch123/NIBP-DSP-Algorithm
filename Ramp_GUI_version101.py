import pandas as pd
import numpy as np
from scipy.signal import find_peaks, savgol_filter
import matplotlib.pyplot as plt
import tkinter as tk
import warnings
warnings.filterwarnings('ignore')
import time
root = tk.Tk()
root.geometry("400x240")



def pressureVsAmplitudeRatio(FileName):
    df = pd.read_csv(FileName+".txt",delimiter='\t',header=None)
    df.columns = ["time","pressure","ppg_I","ppg_D","_"]
    # Pressure between 5 and 180 mmHg
    df = df[:np.argwhere(np.array(df.pressure)>=180)[0][0]]      
    df = df[np.argwhere(np.array(df.pressure)>=5)[0][0]:].reset_index()
    df = df.astype(float)
    ft = 14
    window_length_ppg= 99
    polyorder_ppg= 1
    window_length_AmpRatio = 3
    polyorder_AmpRatio = 1
    # Savgol filter the ppg data 
    ppg_D = savgol_filter(df.ppg_D,window_length_ppg, polyorder_ppg)
    ppg_I = savgol_filter(df.ppg_I,window_length_ppg, polyorder_ppg)
    peak_I, _ = find_peaks(-ppg_I, prominence = 0.002, width = 50)
    plt.figure(101)
    plt.subplot(2, 1, 1)
    plt.plot(ppg_D,'r', label = "D")
    plt.plot(ppg_I,'k',alpha = 0.5, label = "I")
    plt.plot(peak_I,ppg_I[peak_I],'bo')
    plt.ylabel('Amplitude (mV)', fontsize=ft)
    plt.legend(fontsize=ft)
    plt.subplot(2, 1, 2)
    plt.plot(df.pressure)
    plt.xlabel('Time(500sample = 1s)', fontsize=ft)
    plt.ylabel('Pressure (mmHg)', fontsize=ft)
    plt.savefig("Peakdetection"+FileName+".jpeg")
#### amplitude = max(signal between peaks)-min(signal between peaks)
#### amplitude ratio = amplitude Independent PPG/amplitude Dependent PPG 
    amp_I = []
    pressure_between_peaks = []
    fft_max_amp_between_peaks = []
    # find the amplitude ratios and pressure avg between the peaks. 
    for i in range(len(peak_I)-1):
        ppg_D_between_peaks = ppg_D[peak_I[i]:peak_I[i+1]]
        ppg_I_between_peaks = ppg_I[peak_I[i]:peak_I[i+1]]
        pressure_bt_a_peak = df.pressure[peak_I[i]:peak_I[i+1]].mean()
        pressure_between_peaks.append(pressure_bt_a_peak)
        i_amp = max(ppg_D_between_peaks)-min(ppg_D_between_peaks)
        d_amp = max(ppg_I_between_peaks)-min(ppg_I_between_peaks)
        amp_I.append(i_amp/d_amp)
    df_press_amp = pd.DataFrame(columns=['pressure', 'amplitude'])
    df_press_amp.pressure = pressure_between_peaks
    df_press_amp.amplitude = savgol_filter(np.multiply(amp_I,100), window_length_AmpRatio,polyorder_AmpRatio)     
    df_press_amp = df_press_amp.sort_values(by='pressure')
    
    return df_press_amp, df
    
def normalize_min_max_threshold(signal):
    s_min = min(signal)
    s_max = max(signal)
    signal_r = ((signal - s_min) / (s_max - s_min)) * 100   # Normalize signal  
    # Threshold = Standard deviation of signal less than X percent 
    # Vary this Xpercent 
    Xpercent = 8                                             
    signal_SD_lessThanXpercent = round(np.std(signal_r[signal_r<Xpercent]),1)  # This is the threshold  
    SBP = np.where(signal_r<signal_SD_lessThanXpercent)[0][0] # Find the first index of the amplitude ratio less than threshold
    return SBP, signal_r

def calculate_SBP(FileName):
    start = time.time()                    # just to estimate  the processing time.
    # Get amplitude ratios
    df_press_amp, df = pressureVsAmplitudeRatio(FileName) 
    # Energy of the signal     
    energy_of_amp_ratio = df_press_amp.amplitude ** 2  
    # Normalize between 0 to 100 % and find the index of first signal less than threshold
    sbp_index, signal_r = normalize_min_max_threshold(energy_of_amp_ratio)     # 
    plt.figure(101)
    plt.subplot(2, 1, 1)
    plt.axvline(x=df.index[df.pressure.round(0)==df_press_amp.pressure[sbp_index].round(0)][0])
    plt.subplot(2, 1, 2)
    plt.axvline(x=df.index[df.pressure.round(0)==df_press_amp.pressure[sbp_index].round(0)][0])
    plt.figure(102)
    print(sbp_index)
    plt.plot(df_press_amp.pressure, signal_r)
    plt.plot(df_press_amp.pressure[sbp_index], signal_r[sbp_index],'bo',
            label="SBP: "+str(round(df_press_amp.pressure[sbp_index],1))+ " mmHg")
    plt.ylabel("Amplitude Ratios", fontsize=14)
    plt.xlabel("Pressure (mmHg)", fontsize=14)
    plt.title("Pressure Vs Amplitude ratios", fontsize=14)
    plt.legend(fontsize=14)
    end = time.time()                      # just to estimate  the processing time.
    print("Time Taken for processing: ",end - start)       
    plt.show()
    return df_press_amp.pressure[sbp_index]

def getTextInputAndRunRamp():
    FileName=FileName_Input_txtbox.get("1.0","end-1c")
    print("FileName",FileName)
    SBP = calculate_SBP(FileName)
    print("Systolic Blood Pressure = ", SBP)
    
    
# GUI text box and button size and positions
FileName_Input_txtbox=tk.Text(root, height=1)
FileName_Input_txtbox.pack()
btnRamp=tk.Button(root, height=1, width=10, text="Ramp", 
                    command=getTextInputAndRunRamp)
btnRamp.pack()
root.mainloop()