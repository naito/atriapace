
from setup0D import create_module, find_steadycycle
import numpy as np
import matplotlib.pyplot as plt

def pacing_dynamic(ode, BCL_range, dt, threshold=0.1, offset=10, plot=False,
                   odepath='../ode/', scpath="../data/steadycycles/"):
    """
    Calculate a restitution curve using dynamic pacing.
    The ODE model is paced for 50 beats at every BCL value,
    and the APD and DI are measured for the final beat.
    """

    # Compile the ODE solver module
    if isinstance(ode, str):
        module, forward = create_module(ode, path=odepath)
    else:
        module, forward, ode = ode

    # Get model parameters and initial conditions
    model_params = module.init_parameter_values()
    init_states = module.init_state_values()

    # Get state and parameter indices
    index = {}
    index['V'] = module.state_indices('V')
    index['BCL'] = module.parameter_indices('stim_period')
    index['offset'] = module.parameter_indices('stim_offset')

    model_params[index['offset']] = offset

    # For storing the results
    results = np.zeros((3, len(BCL_range)))

    for i, BCL in enumerate(BCL_range):
        # Set BCL
        model_params[index['BCL']] = BCL

        # Read in steady cycle from file 
        try:
            states = np.load(scpath+"%s_BCL%d.npy" % (ode, BCL))
        except:
            print "Steady cycle at BCL=%d for ODE model: %s not found." % (BCL, ode)
            print "Pacing 0D cell model to find it, this may take a minute."
            states = find_steadycycle([module, forward, ode], BCL, dt, odepath=odepath, scpath=scpath)
            print "Steady cycle found, proceeding to do dynamic pacing."

        # Measure when potential crosses threshold
        t = 0; tstop = BCL+offset
        V = [states[index['V']]]

        # First beat
        while t < tstop:
            forward(states, t, dt, model_params)
            t += dt
            V.append(states[index['V']])

        # Extract times from results
        V = np.array(V)
        APD = len(V[V>threshold])*dt
        DI = BCL - APD

        print "BCL: %g,  APD: %g,   DI: %g" % (BCL, APD, DI)

        if plot:
            # Plot action potential
            tarray = np.linspace(0, BCL, len(V))
            plt.plot(tarray, V, linewidth=1.5)

            # Find intersections and plot them
            above = tarray[V>threshold]
            lt, ht = above[0], above[-1]

            plt.plot([lt, ht], [threshold, threshold], 'o-', linewidth=1.5)
            plt.axis([0, BCL+offset, -0.05, 1.05])
            plt.grid()
            plt.xlabel('Time [ms]')
            plt.ylabel('V [rel.]')
            plt.show()

if __name__ == '__main__':
    ### Example of use
    ode = 'FK_cAF'
    ode = 'hAM_KSMT_nSR'
    ode = 'hAM_KSMT_cAF'
    ode = 'FK_nSR'

    BCL_range = range(1000, 295, -5)
    dt = 0.01

    pacing_dynamic(ode, BCL_range, dt)