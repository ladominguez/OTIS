import pygmt
import numpy as np
#read text file into a numpy array

def create_color_table(amp):
    # Calculate the minimum and maximum values of amp
    min_amp = np.min(amp)
    max_amp = np.max(amp)

    # Create a color table using the minimum and maximum values
    print('min_amp: ', min_amp)
    print('max_amp: ', max_amp)
    color_table = pygmt.makecpt(cmap="rainbow", series=[min_amp, max_amp])
    print(color_table)
    return color_table



def main(freq, amp):
    fig = pygmt.Figure()
    fig.basemap(region=[np.floor(np.min(freq)), 
                        np.ceil(np.max(freq)), 
                        np.floor(np.min(amp)), 
                        np.ceil(np.max(amp))], projection="X6i/6i", frame=True)
    color_table = create_color_table(amp)
    print(color_table)
    for row in amp: 
        fig.plot(
            x=freq, y=row, fill=row,
            cmap=True, style="c0.1c", 
            pen="black"
        )
    fig.show()



if __name__ == "__main__":
    freq = np.loadtxt('freq.txt')
    amp = np.loadtxt('Aspec.txt')
    # get the next ower 10^n power of the min value of freq

    main(freq, amp)

