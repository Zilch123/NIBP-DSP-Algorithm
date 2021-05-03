# NIBP Non Invasive Blood Pressure Measurement 
Algorithm to calculated SBP from PPG and cuff pressure for a Ramp method 

* Select PPG values during ramp 
* Savgol filter the ppg signals. 
* Find the troughs. 
* Find the amplitude ratio of Dependent and Independent PPGs between these troughs.
* Savgol Filter the amplitude ratios. 
* Square the amplitude ratio signal. 
* Normalize it to 0 -100 %.  
* Threshold = Standard deviation of signal less than X percent                     
* #Change this  X percent value to suit data. I've observed Xpercent = 8% to be reasonable with the small datasets I've. 
* Find the first instance of pressure at which the amplitude is less than threshold. 
* This pressure is taken as systolic pressure. 
