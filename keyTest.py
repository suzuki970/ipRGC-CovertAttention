
import pandas as pd
import glob
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from band_pass_filter import lowpass_filter,lowpass_filter_manual,filtfilt_manual
from zeroInterp import zeroInterp
from scipy.stats import norm

from pre_processing_cls import getPCPDevents

def rejectOutliear(pupil_values):
    
    d = np.diff(pupil_values)
    q75, q25 = np.percentile(d, [75 ,25])
    IQR = q75 - q25

    lower = q25 - IQR*1.5
    upper = q75 + IQR*1.5
    d_witout_outliar = d[(d > lower) & (d < upper)]

    param = norm.fit(d_witout_outliar)
    
    (a,b) = norm.interval(0.99, loc=param[0], scale=param[1])
    
    ind = np.argwhere(abs(np.diff(pupil_values)) > b).reshape(-1)
    
    pupil_values[ind] = 0

    return pupil_values

fs=29
fs=100

# file_list = sorted(glob.glob("results/pupil_data_NEON*.parquet"))[-1]
# file_list1 = sorted(glob.glob("results/pupil_data_[!NEON]*.parquet"))[-1]
# file_list2 = sorted(glob.glob("results/behavioral_data_*.parquet"))[-1]

file_list = sorted(glob.glob("results/pupil_data_Eyelink*.parquet"))[-1]
file_list1 = sorted(glob.glob("results/pupil_data_[!NEON]*.parquet"))[-1]
file_list2 = sorted(glob.glob("results/behavioral_data_*.parquet"))[-1]


df0 = pd.read_parquet(file_list)
df = pd.read_parquet(file_list1)

f = [df.iloc[i]["event_flg"] for i in np.arange(len(df))]

df_bef = pd.read_parquet(file_list2)

f = [df.iloc[i]["event_flg"] for i in np.arange(len(df))]
x = np.arange(len(f)) * (1/fs)

true_indices = [i for i, val in enumerate(f) if val]

pupil_values = df0["pupil_right"].values
pupil_values = rejectOutliear(pupil_values)

pupilData = zeroInterp(pupil_values.copy(),fs,(fs*0.04))
pupilData = pupilData["pupilData"].reshape(-1)

y = lowpass_filter_manual(pupilData,0.15,fs)
# y = lowpass_filter_manual(pupilData,0.2,fs)
x = np.arange(len(y)) * (1/fs)

plt.plot(df0["timestamp_eyetracker"], pupilData,alpha=0.5,label="raw data")
plt.plot(df0["timestamp_eyetracker"], y,alpha=0.5,label="lowpassed")
# plt.xlim([40,60])
# plt.ylim([3.0,5])
# plt.ylim([3,4.5])
# plt.ylim([4,5])

tmp_df = df_bef[df_bef["key"]=="T1T2 onset"]
for i in np.arange(len(tmp_df)):
    x = tmp_df.iloc[i]["timestamp_eyetracker"]
    ind=np.argwhere(df0["timestamp_eyetracker"]==x).reshape(-1)[0]
    
    if i==0:
        plt.plot(x,y[ind],'ro',alpha=0.5, label="saved_onset")
    else:
        plt.plot(x,y[ind],'ro',alpha=0.5)

# %%


tmp = df.iloc[-2900]

y = tmp["pupil_original"]
x = tmp["timestamp_eyetracker"]

plt.plot(x, y,alpha=0.5, label="save_origin")
# plt.plot(x,tmp["pupil_lowpassed"],alpha=0.5, label="save_lowpassed")
# plt.plot(x[tmp["troughs"]],tmp["pupil_lowpassed"][tmp["troughs"]],'bo',alpha=0.5, label="save_detected")

yy = lowpass_filter_manual(y,0.2,fs,4,600)
# plt.plot(x, yy,alpha=0.5, label="save_origin")

sm = getPCPDevents(yy,0.01)

plt.plot(x, yy,alpha=0.5, label="save_origin")
plt.plot(x[sm["troughs"][0]], yy[sm["troughs"][0]],"o")

plt.legend()

# %%

## %%

time=600

plt.plot(df["timestamp"].values[:time], df["pupil_original"].values[:time])
# plt.plot(df["timestamp"], filtfilt(b, a, df["pupil_size"].values))
plt.plot(df["timestamp"].values[:time], lowpass_filter_manual(df["pupil_original"].values[:time],0.3,20))

from pre_processing_cls import getPCPDevents

x = df["timestamp"].values[:time]
x0 = df["timestamp"].values
y0 = df["pupil_original"].values
y = lowpass_filter_manual(df["pupil_original"].values[:time],0.2,20)
# y = lowpass_filter_manual(df["pupil_size"].values[:time],0.15,20)
sm = getPCPDevents(y)


plt.plot(x0, y0)
plt.plot(x, y)
plt.plot(x[sm["troughs"]], y[sm["troughs"]],'o')

plt.xlabel("Time (s)")
plt.ylabel("Pupil size")
plt.title("Pupil size over time")
# plt.show()

# %%

import numpy as np
from scipy.signal import lfilter, lfilter_zi

def odd_mirror(x, padlen):
    """
    padtype='odd' 相当のエッジ反転拡張（scipy風）
    """
    start = 2*x[0] - x[1:padlen+1][::-1]
    end = 2*x[-1] - x[-padlen-1:-1][::-1]
    return np.concatenate((start, x, end))

def filtfilt_clone(b, a, x):
    """
    Scipy の filtfilt() を再現する完全クローン。
    """
    if np.ndim(x) != 1:
        raise ValueError("Only 1D signals are supported.")

    # パディング長
    padlen = 3 * (max(len(a), len(b)) - 1)
    if x.size <= padlen:
        raise ValueError("Input signal length must be > padlen.")

    # パディング（padtype='odd' と同等）
    x_ext = odd_mirror(x, padlen)

    # 初期値を定常状態から求める
    zi = lfilter_zi(b, a)

    # 前方向フィルタ
    z0 = zi * x_ext[0]
    y, _ = lfilter(b, a, x_ext, zi=z0)

    # 後方向（反転してフィルタ）
    z1 = zi * y[-1]
    y_rev, _ = lfilter(b, a, y[::-1], zi=z1)

    # 出力信号（反転して元に戻し、パディング分を切り落とす）
    y_final = y_rev[::-1][padlen:-padlen]
    return y_final

import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

fs = 20
cutoff = 0.15
order = 4
np.random.seed(0)
x = np.random.randn(1000)

x=df["pupil_size"].values

b, a = butter(order, cutoff / (0.5 * fs), btype='low')

y_scipy = filtfilt(b, a, x)
y_manual = filtfilt_clone(b, a, x)

plt.plot(x, color='gray', alpha=0.4, label='original')
plt.plot(y_scipy, label='scipy.filtfilt')
plt.plot(y_manual, '--', label='clone')
plt.legend()
plt.grid()
plt.title('filtfilt: Scipy vs Clone')
plt.show()

print("最大誤差:", np.max(np.abs(y_scipy - y_manual)))
print("平均誤差:", np.mean(np.abs(y_scipy - y_manual)))
