
import numpy as np
import matplotlib.pyplot as plt

def plot2d(pmap, fp=None, ax=None, **kw):
    if fp is not None:
        assert len(pmap.names) - len(fp) == 2
    if ax is None:
        ax = plt.gca()
    A = pmap.extract_array(fp)
    cm = ax.pcolormesh(np.array(pmap.values[1]),
                       np.array(pmap.values[0]),
                       A, **kw)
    ax.set_xlabel(pmap.names[1])
    ax.set_ylabel(pmap.names[0])
    ax.axis('tight')
    plt.colorbar(cm)
    return ax

