import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def neutron_density_plot(nphi, rhob, color=None, labels=None, title=None, figsize=(8,8)):
    """Create a neutron-density crossplot with lithology overlay lines.
    
    Args:
        nphi (array-like): Neutron porosity values (v/v)
        rhob (array-like): Bulk density values (g/cc)
        color (array-like, optional): Color values for points
        labels (list, optional): Labels for legend
        title (str, optional): Plot title
        figsize (tuple, optional): Figure size. Defaults to (8,8)
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig = Figure(figsize=figsize)
    ax = fig.add_subplot(111)
    
    # Plot data points
    if color is not None:
        scatter = ax.scatter(nphi, rhob, c=color, alpha=0.6)
        if labels is not None:
            fig.colorbar(scatter, label=labels)
    else:
        ax.scatter(nphi, rhob, alpha=0.6)
    
    # Add lithology lines
    # Sandstone line
    nphi_sand = np.array([0, 0.45])
    rhob_sand = np.array([2.65, 1.9])
    ax.plot(nphi_sand, rhob_sand, 'r--', label='Sandstone')
    
    # Limestone line
    nphi_ls = np.array([0, 0.45])
    rhob_ls = np.array([2.71, 2.0])
    ax.plot(nphi_ls, rhob_ls, 'b--', label='Limestone')
    
    # Dolomite line
    nphi_dol = np.array([0, 0.45])
    rhob_dol = np.array([2.85, 2.2])
    ax.plot(nphi_dol, rhob_dol, 'g--', label='Dolomite')
    
    # Customize plot
    ax.set_xlabel('Neutron Porosity (v/v)')
    ax.set_ylabel('Bulk Density (g/cc)')
    ax.set_xlim(-0.05, 0.45)
    ax.set_ylim(3.0, 1.8)
    ax.grid(True)
    ax.legend()
    
    if title:
        ax.set_title(title)
        
    return fig

def density_pe_plot(rhob, pef, color=None, labels=None, title=None, figsize=(8,8)):
    """Create a density-photoelectric factor crossplot with lithology overlay.
    
    Args:
        rhob (array-like): Bulk density values (g/cc)
        pef (array-like): Photoelectric factor values (barns/e-)
        color (array-like, optional): Color values for points
        labels (list, optional): Labels for legend
        title (str, optional): Plot title
        figsize (tuple, optional): Figure size. Defaults to (8,8)
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig = Figure(figsize=figsize)
    ax = fig.add_subplot(111)
    
    # Plot data points
    if color is not None:
        scatter = ax.scatter(rhob, pef, c=color, alpha=0.6)
        if labels is not None:
            fig.colorbar(scatter, label=labels)
    else:
        ax.scatter(rhob, pef, alpha=0.6)
    
    # Add lithology points
    minerals = {
        'Quartz': (2.65, 1.81),
        'Calcite': (2.71, 5.08),
        'Dolomite': (2.85, 3.14),
        'Anhydrite': (2.98, 5.05),
        'Halite': (2.03, 4.65),
        'Gypsum': (2.35, 4.0)
    }
    
    for mineral, (dens, pe) in minerals.items():
        ax.plot(dens, pe, 'r*', markersize=10, label=mineral)
    
    # Customize plot
    ax.set_xlabel('Bulk Density (g/cc)')
    ax.set_ylabel('Photoelectric Factor (barns/e-)')
    ax.set_xlim(2.0, 3.0)
    ax.set_ylim(0, 6)
    ax.grid(True)
    ax.legend()
    
    if title:
        ax.set_title(title)
        
    return fig

def m_n_plot(rhob, nphi, dtc, color=None, labels=None, title=None, figsize=(8,8)):
    """Create an M-N crossplot for lithology identification.
    
    Args:
        rhob (array-like): Bulk density values (g/cc)
        nphi (array-like): Neutron porosity values (v/v)
        dtc (array-like): Sonic transit time values (us/ft)
        color (array-like, optional): Color values for points
        labels (list, optional): Labels for legend
        title (str, optional): Plot title
        figsize (tuple, optional): Figure size. Defaults to (8,8)
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Calculate M and N values
    # M = (dtf - dtc)/(rhob - rhof) * 0.01
    # N = (nphi - phif)/(rhob - rhof)
    
    dtf = 189  # fluid transit time (us/ft)
    rhof = 1.0  # fluid density (g/cc)
    phif = 1.0  # fluid porosity (v/v)
    
    M = (dtf - dtc)/(rhob - rhof) * 0.01
    N = (nphi - phif)/(rhob - rhof)
    
    fig = Figure(figsize=figsize)
    ax = fig.add_subplot(111)
    
    # Plot data points
    if color is not None:
        scatter = ax.scatter(M, N, c=color, alpha=0.6)
        if labels is not None:
            fig.colorbar(scatter, label=labels)
    else:
        ax.scatter(M, N, alpha=0.6)
    
    # Add mineral points
    minerals = {
        'Quartz': (0.80, -0.02),
        'Calcite': (0.85, 0.03),
        'Dolomite': (0.70, -0.01),
        'Anhydrite': (0.65, -0.05),
        'Gypsum': (0.75, 0.00)
    }
    
    for mineral, (m, n) in minerals.items():
        ax.plot(m, n, 'r*', markersize=10, label=mineral)
    
    # Customize plot
    ax.set_xlabel('M = (dtf - dtc)/(rhob - rhof) * 0.01')
    ax.set_ylabel('N = (nphi - phif)/(rhob - rhof)')
    ax.set_xlim(0.4, 1.0)
    ax.set_ylim(-0.15, 0.15)
    ax.grid(True)
    ax.legend()
    
    if title:
        ax.set_title(title)
        
    return fig
