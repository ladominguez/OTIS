import pygmt
import numpy as np
from tqdm import tqdm
#read text file into a numpy array

def create_color_table(amp):
    # Calculate the minimum and maximum values of amp
    min_amp = np.min(amp)
    max_amp = np.max(amp)

    # Create a color table using the minimum and maximum values
    print('min_amp: ', min_amp)
    print('max_amp: ', max_amp)
    color_table = pygmt.makecpt(cmap="matlab/hot", series=[min_amp, max_amp], reverse=True)
    print(color_table)
    return color_table



def main(freq, amp):
    fig = pygmt.Figure()
    fig.basemap(region=[0, amp.shape[0],
                        np.floor(np.min(freq)), 
                        np.ceil(np.max(freq))], projection="X6i/4i", frame=True)
    color_table = create_color_table(amp)
    print(color_table)
    for k, row in tqdm(enumerate(amp)):
        t = np.zeros(row.shape) + k + 1
        # make pen same color as fill
        fig.plot(
            x=t, y=freq, fill=row,
            cmap=True, style="s0.1c", 
            pen=None
        )
    fig.colorbar(frame=["x+lAmplitude", "y+lm"])
    fig.savefig("spectrum.png")



if __name__ == "__main__":
    freq = np.loadtxt('freq.txt')
    T = np.loadtxt('T.txt')
    amp = np.loadtxt('Aspec20.txt')
    # Clipping amp for values larger than -1
    np.clip(amp, -1, None, out=amp)
    # get the next ower 10^n power of the min value of freq

    main(T, amp)

