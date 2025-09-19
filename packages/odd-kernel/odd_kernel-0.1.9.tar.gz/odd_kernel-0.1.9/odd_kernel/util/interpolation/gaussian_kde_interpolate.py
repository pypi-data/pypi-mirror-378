import numpy as np

def add_padding(x, y, padding):
    amplitude = np.abs(y-x)
    return x - padding*amplitude, y + padding*amplitude

def gaussian_kde_interpolate(x_p, y_p, z_p, mesh_size, padding = 0.1, h=None):
    """
    Perform Gaussian kernel density estimation (KDE) based interpolation of scattered 3D data 
    over a regular 2D grid.

    Parameters
    ----------
    x_p : array-like of shape (n_samples,)
        X-coordinates of the input data points.

    y_p : array-like of shape (n_samples,)
        Y-coordinates of the input data points.

    z_p : array-like of shape (n_samples,)
        Z-values (scalar field) corresponding to each (x_p, y_p) point.

    mesh_size : int
        Number of grid points along each axis in the output mesh.

    padding : float, optional, default=0.1
        Extra margin added to the data range in both X and Y directions. 
        Expressed as a fraction of the total range.

    h : float, optional, default=None
        Bandwidth (smoothing parameter) of the Gaussian kernel. 
        If None, it is estimated as half the mean grid spacing 
        (using both x and y axis resolutions).

    Returns
    -------
    x : ndarray of shape (mesh_size,)
        1D array containing the grid values along the X-axis.

    y : ndarray of shape (mesh_size,)
        1D array containing the grid values along the Y-axis.

    X : ndarray of shape (mesh_size, mesh_size)
        2D array containing the X-coordinates of the interpolation grid.

    Y : ndarray of shape (mesh_size, mesh_size)
        2D array containing the Y-coordinates of the interpolation grid.

    Z : ndarray of shape (mesh_size, mesh_size)
        Interpolated Z-values on the (X, Y) grid, smoothed using Gaussian weights.

    Notes
    -----
    - The interpolation is performed by weighting each input point (x_p[i], y_p[i]) 
      with a Gaussian kernel centered at that point.
    - The Z-values are normalized by the sum of weights to produce a smooth surface.
    - Adding padding prevents boundary effects and ensures that points near the edges 
      of the data are properly represented.
    - Compared to the previous version, the bandwidth `h` is chosen as the minimum 
      of the average grid spacings along X and Y, divided by 2.

    Examples
    --------
    >>> x = np.random.rand(50)
    >>> y = np.random.rand(50)
    >>> z = np.sin(x*10) + np.cos(y*10)
    >>> xg, yg, X, Y, Z = gaussian_kde_interpolate(x, y, z, mesh_size=100)
    """
    
    x_l, x_r = add_padding(np.min(x_p), np.max(x_p), padding)
    y_l, y_r = add_padding(np.min(y_p), np.max(y_p), padding)
    x = np.linspace(x_l, x_r, mesh_size)
    y = np.linspace(y_l, y_r, mesh_size)
    X, Y = np.meshgrid(x, y)

    if h is None:
        effective_h = min(np.mean(np.diff(x)), np.mean(np.diff(y))) / 2
    else:
        effective_h = h 

    z_mean = np.mean(z_p)
    Z = np.zeros_like(X)
    W = np.zeros_like(X)

    for i in range(len(x_p)):
        dx = X - x_p[i]
        dy = Y - y_p[i]
        weight = np.exp(-(dx*dx + dy*dy) / (2*effective_h*effective_h))
        W += weight
        Z += (z_p[i] - z_mean) * weight
    Z[W != 0.0] /= W[W != 0.0]
    Z += z_mean

    return x, y, X, Y, Z