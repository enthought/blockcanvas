def zero_offset_times(top_depths, vels):
    """ Computes two-way zero-offset travel times for a series of layers.

    Parameters
    ----------
    top_depths :
        depths at the top of each layer.  These will be
        subtracted to determine layer thicknesses.
    vels :
        P-wave velocities in each layer.

    Returns
    -------
    An array of 2-way traveltimes (in seconds) at layer interfaces.

    Discussion
    ----------
    A)  Distance units must be consistent in top_depths and vels (e.g.,
        feet and feet/second).
    B)  Velocity units must be distance units per SECOND.
    C)  Top_depths[0] serves as the datum.  If this value is not zero,
        times will be computed relative to this depth.
    D)  Follows the indexing convention that interface 'i' is at the
        top of interval 'i'.
    """

    top_depths = force_contiguous(top_depths, Float64)
    vels = force_contiguous(vels, Float64)

    if len(top_depths) != len(vels):
        msg = "Function zero_offset_times: top_depths and vels must be the same length."
        raise ValueError, msg

    times = zeros(len(top_depths), Float64)

    _copsyn.wrap_zero_offset_times(top_depths, vels, times)

    return times

def rhob_from_ggg(vp, cons=.23, expn=.25):
    ''' Estimates Rhob from Vp using Gardner, Gardner, Gregory.

    Parameters
    ----------
    vp : sequence : units=km/s
      P-velocity in km/s
    cons : scalar
      Multiplicative constant, default is .32
    expn : scalar
      Exponential constant, default is .23

    Returns
    -------
    rhob : sequence
      Bulk density in g/cc

    Description
    -----------
    Estimates bulk density from vp using Gardner, Gardner, Gregory equation ::

               Rhob = cons * (Vp**expn)  in g/cc

    where the default value of 'cons' is .32 and the default value of 'expn' is
    .23 for Vp in ft/sec.
    '''

    #########################################################################
    # Algorithm
    #########################################################################
    vp = vp * 3280.8  # Convert from km/s to f/s
    rhob = cons * (vp ** expn)  # in g/cc

    return rhob

def fix_density_log(density_log, index, water_depth, kb, td, density_fill_value):
    """
        Fixes the density log

           Parameters
           ----------
           density_log : array : units=g/cc
               The Density
           index : array : units=ft
               The index for the density
           water_depth : scalar : units=ft
               How much water are we in?
           kb : scalar : units=ft
               The Kelly Bushing
           td : scalar : units=ft
               Total Depth
           density_fill_value : scalar : units=g/cc
               Value for missing densities

           Returns
           -------
           density_log : array : units=g/cc
               The new density log
           index : array : units=ft
               The new index
    """
    return

def integrate_ob(density_array, density_index, water_depth, kb, sea_water_grad):
    """
        Integrates the density log

           Parameters
           ----------
           density_array : array : units=g/cc
               The Density
           density_index : array : units=m
               The index for the density
           water_depth : scalar : units=m
               How much water are we in?
           kb : scalar : units=m
               The Kelly Bushing
           sea_water_grad : scalar : units=psi/m
               Density of sea water

           Returns
           -------
           overburden_log : array : units=psi
               The new density log
    """
    return

def dt_to_rhob(dt, method, a, b):
    """
        Integrates the density log

           Parameters
           ----------
           dt : array : units=us/foot
               The dt
           method : scalar
               Which method should we use (Linear or Power)
           a : scalar
               Parameter A to the equation
           b : scalar
               Parameter B to the equation


           Returns
           -------
           density_log : array : units=gram/cc
               The new density log
    """
    return

def change_salt_velocities(dt, density, salt_density, salt_speed):
    """
        Integrates the density log

           Parameters
           ----------
           dt : array : units=us/foot
               The dt
           density : array : units=gram/cc
               The current density log
           salt_density : scalar  : units=gram/cc
               the replacement density
           salt_speed : scalar: units= us/foot
               speed to replace at


           Returns
           -------
           density_log : array : units=gram/cc
               The new density log
    """
    return
