# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 14:35:39 2020

@author: Rastko
"""
import numpy as np


def mesh_grid_points(acc_pos, height, length, beam, nh=10, nl=10, nb=10):
    """
    Creates a meshgrid of 3D coordinates from   x=0 to x=length,
                                                y=-beam/2 to y=beam/2,
                                                z=0 to z=height.

    The positions are defined relative to the accelerometer position [x, y, z].
    """
    x = np.linspace(0, length, nl)
    y = np.linspace(-beam/2, beam/2, nb)
    z = np.linspace(0, height, nh)

    x -= acc_pos[0]
    y -= acc_pos[1]
    z -= acc_pos[2]

    XX, YY, ZZ = np.meshgrid(x, y, z)

    return XX, YY, ZZ


def deck_slice(acc_pos, slice_height, beam, length, nl=10, nb=10):
    """
    Returns 3D coordinates of a deck slice at slice_height. The slice height
    is relative to the ship origin but the returned positions are relative to
    the accelerometer. To convert back into ship coordinates use [X]
    """
    x = np.linspace(0, length, nl)
    y = np.linspace(-beam/2, beam/2, nb)
    z = np.linspace(slice_height, slice_height, 1)

    x -= acc_pos[0]
    y -= acc_pos[1]
    z -= acc_pos[2]

    XX, YY, ZZ = np.meshgrid(x, y, z)

    return XX, YY, ZZ


def transverse_slice(acc_pos, slice_length, beam, height, nb=10, nh=10):
    """
    Returns 3D coordinates of a transverse slice at slice_height. The slice
    height is relative to the ship origin but the returned positions are
    relative to the accelerometer. To convert back into ship coordinates use
    [X]
    """
    x = np.linspace(slice_length, slice_length, 1)
    y = np.linsapce(-beam/2, beam/2, nb)
    z = np.linspace(0, height, nh)

    x -= acc_pos[0]
    y -= acc_pos[1]
    z -= acc_pos[2]

    XX, YY, ZZ = np.meshgrid(x, y, z)

    return XX, YY, ZZ


def longitudinal_slice(acc_pos, slice_transverse_pos, length, height, nl=10, nh=10):
    """
    Returns 3D coordinates of a longitudinal slice at slice_height. The slice
    height is relative to the ship origin but the returned positions are
    relative to the accelerometer. To convert back into ship coordinates use
    [X]
    """
    x = np.linspace(0, length, nl)
    y = np.linsapce(slice_transverse_pos, slice_transverse_pos, 1)
    z = np.linspace(0, height, nh)

    x -= acc_pos[0]
    y -= acc_pos[1]
    z -= acc_pos[2]

    XX, YY, ZZ = np.meshgrid(x, y, z)

    return XX, YY, ZZ


def points(acc_pos, X, Y, Z):
    """
    Returns 3D coordinates relative the accelerometer position.
    acc_pos:    The accelerometer position relative to the ship origin
    X:          A list of points in the X direction
    Y:          A list of points in the Y direction
    Z:          A list of points in the Z direction
    """
    XX = np.array([[X-acc_pos[0]]])
    YY = np.array([[Y-acc_pos[1]]])
    ZZ = np.array([[Z-acc_pos[2]]])
    return XX, YY, ZZ


def stl_points(acc_pos, STL_loader_object):
    """
    Returns the centre of panels of an STL object.
    
    acc_pos:            The accelerometer position relative to the ship origin
    STL_loader_object:  A STL_loader.create_object object.
    """
    XX, YY, ZZ = points(acc_pos,
                        STL_loader_object.panel_centre[:,0],
                        STL_loader_object.panel_centre[:,1],
                        STL_loader_object.panel_centre[:,2])
    return XX, YY, ZZ


def calc_tip_ratio(h, n4_acc, D2_acc, g, n4, D3_acc):
    top = np.abs((-1/3)*h*n4_acc + D2_acc + g*n4)
    bottom = D3_acc+g
    return top/bottom


def calc_trips(Rt, t_coeff):
    trips = Rt > t_coeff
    return trips


def count_trips(trips):
    return int(np.count_nonzero(trips != np.roll(trips, -1))/2)


def translate_accelerations(XX, YY, ZZ, accelerometer, degrees=True):
    """
    Translates accelerations in 3D coorindates XX, YY, ZZ, relative to the
    position of the accelerometer.

    XX, YY, ZZ -    Use mesh_grid_points to generate

    accelerometer - A class with a dictionary .motion_data which holds "Az",
                    "Ay", "Az", "Roll", "Pitch", "Yaw", "Time" time series data
    """
    Az = trans_vert(XX,
                    YY,
                    accelerometer.motion_data["Az"],
                    accelerometer.motion_data["Pitch"],
                    accelerometer.motion_data["Roll"],
                    accelerometer.motion_data["Time"],
                    degrees=degrees)

    Ay = trans_lat(XX,
                   ZZ,
                   accelerometer.motion_data["Ay"],
                   accelerometer.motion_data["Yaw"],
                   accelerometer.motion_data["Roll"],
                   accelerometer.motion_data["Time"],
                   degrees=degrees)

    Ax = trans_long(YY,
                    ZZ,
                    accelerometer.motion_data["Ax"],
                    accelerometer.motion_data["Yaw"],
                    accelerometer.motion_data["Pitch"],
                    accelerometer.motion_data["Time"],
                    degrees=degrees)

    A = np.linalg.norm([Ax, Ay, Az], axis=0)

    shape = np.append(XX.shape, len(accelerometer.motion_data["Az"]))
    Az = np.reshape(Az, shape)
    Ay = np.reshape(Ay, shape)
    Ax = np.reshape(Ax, shape)
    A = np.reshape(A, shape)

    return Ax, Ay, Az, A


def trans_vert(dx, dy, Az, Pitch, Roll, Time_step, degrees):
    """
    dx:         Relative distance in x from the accelerometer
    dy:         Relative distance in y from the accelerometer
    Az:         Accelerations in Z time series from th accelerometer
    Pitch:      Pitching motion time series from the accelerometer
    Roll:       Roll motion time series from the accelerometer
    Time_step:  The time series
    """
    if degrees:
        Pitch = np.deg2rad(Pitch)
        Roll = np.deg2rad(Roll)
    dx = np.vstack(dx.flatten())
    dy = np.vstack(dy.flatten())
    Time_step = np.average(np.diff(Time_step))
    dP = np.diff(Pitch, prepend=0)/Time_step
    dR = np.diff(Roll, prepend=0)/Time_step
    d2P = np.diff(dP, prepend=0)/Time_step
    d2R = np.diff(dR, prepend=0)/Time_step
    translated = Az + dx*d2P - dy*d2R
    return translated


def trans_lat(dx, dz, Ay, Yaw, Roll, Time_step, degrees):
    """
    dx:         Relative distance in x from the accelerometer
    dz:         Relative distance in y from the accelerometer
    Ay:         Accelerations in Z time series from the accelerometer
    Yaw:        Yaw motion time series from the accelerometer
    Roll:       Roll motion time series from the accelerometer
    Time_step:  The time series
    """
    if degrees:
        Yaw = np.deg2rad(Yaw)
        Roll = np.deg2rad(Roll)
    dx = np.vstack(dx.flatten())
    dz = np.vstack(dz.flatten())
    Time_step = np.average(np.diff(Time_step))
    d2Y = np.diff(np.diff(Yaw, prepend=0)/Time_step, prepend=0)/Time_step
    d2R = np.diff(np.diff(Roll, prepend=0)/Time_step, prepend=0)/Time_step
    translated = Ay + dz*d2R + dx*d2Y
    return translated


def trans_long(dy, dz, Ax, Yaw, Pitch, Time_step, degrees):
    """
    dx:         Relative distance in x from the accelerometer
    dy:         Relative distance in y from the accelerometer
    Az:         Accelerations in Z time series from the accelerometer
    Pitch:      Pitching motion time series from the accelerometer
    Roll:       Roll motion time series from the accelerometer
    Time_step:  The time series
    """
    if degrees:
        Yaw = np.deg2rad(Yaw)
        Pitch = np.deg2rad(Pitch)
    dy = np.vstack(dy.flatten())
    dz = np.vstack(dz.flatten())
    Time_step = np.average(np.diff(Time_step))
    d2Y = np.diff(np.diff(Yaw, prepend=0)/Time_step, prepend=0)/Time_step
    d2P = np.diff(np.diff(Pitch, prepend=0)/Time_step, prepend=0)/Time_step
    translated = Ax - dz*d2P + dy*d2Y
    return translated


def octave(Az, TIMES, Scale_factor):
    from scipy import fftpack
    sf = np.sqrt(Scale_factor)
    bd10 = [0.089*sf, 0.112*sf]
    bd9 = [0.112*sf, 0.141*sf]
    bd8 = [0.141*sf, 0.178*sf]
    bd7 = [0.178*sf, 0.224*sf]
    bd6 = [0.224*sf, 0.282*sf]
    bd5 = [0.282*sf, 0.355*sf]
    bd4 = [0.355*sf, 0.447*sf]
    bd3 = [0.447*sf, 0.562*sf]
    bd2 = [0.562*sf, 0.708*sf]
    bd1 = [0.708*sf, 0.892*sf]
    bd0 = [0.892*sf, 1.108*sf]
    ldata = len(Az)
    loop = [0]
    for i in loop:
        if ldata % np.sqrt(ldata) == 0 and ldata % 2 and ldata % 3:
            pass
        else:
            ldata = ldata - 1
            loop.append(0)
    Az = Az[0:ldata]
    TIMES = TIMES[0:ldata]
    time_steps = np.diff(TIMES)

    # find average of timesteps, only a precaution to properly account for a
    # slightly varied sample rate
    time_step = np.average(time_steps)

    # performing fft of the wave elevations, makes it absolute
    freq_fft = fftpack.rfft(np.array(Az))

    # find frequency range
    xf = fftpack.rfftfreq(len(freq_fft), d=time_step)

    b10 = np.copy(freq_fft)
    b9 = np.copy(freq_fft)
    b8 = np.copy(freq_fft)
    b7 = np.copy(freq_fft)
    b6 = np.copy(freq_fft)
    b5 = np.copy(freq_fft)
    b4 = np.copy(freq_fft)
    b3 = np.copy(freq_fft)
    b2 = np.copy(freq_fft)
    b1 = np.copy(freq_fft)
    b0 = np.copy(freq_fft)

    b10[np.abs(xf) < bd10[0]] = 0
    b10[np.abs(xf) > bd10[1]] = 0
    b9[np.abs(xf) < bd9[0]] = 0
    b9[np.abs(xf) > bd9[1]] = 0
    b8[np.abs(xf) < bd8[0]] = 0
    b8[np.abs(xf) > bd8[1]] = 0
    b7[np.abs(xf) < bd7[0]] = 0
    b7[np.abs(xf) > bd7[1]] = 0
    b6[np.abs(xf) < bd6[0]] = 0
    b6[np.abs(xf) > bd6[1]] = 0
    b5[np.abs(xf) < bd5[0]] = 0
    b5[np.abs(xf) > bd5[1]] = 0
    b4[np.abs(xf) < bd4[0]] = 0
    b4[np.abs(xf) > bd4[1]] = 0
    b3[np.abs(xf) < bd3[0]] = 0
    b3[np.abs(xf) > bd3[1]] = 0
    b2[np.abs(xf) < bd2[0]] = 0
    b2[np.abs(xf) > bd2[1]] = 0
    b1[np.abs(xf) < bd1[0]] = 0
    b1[np.abs(xf) > bd1[1]] = 0
    b0[np.abs(xf) < bd0[0]] = 0
    b0[np.abs(xf) > bd0[1]] = 0

    b10, b9, b8, b7, b6 = fftpack.irfft(b10), fftpack.irfft(b9), fftpack.irfft(b8), fftpack.irfft(b7), fftpack.irfft(b6)
    b5, b4, b3, b2, b1, b0 = fftpack.irfft(b5), fftpack.irfft(b4), fftpack.irfft(b3), fftpack.irfft(b2), fftpack.irfft(b1), fftpack.irfft(b0)

    RMSF = [RMS(b10), RMS(b9), RMS(b8), RMS(b7), RMS(b6), RMS(b5), RMS(b4),
            RMS(b3), RMS(b2), RMS(b1), RMS(b0)]

    return RMSF


def MSI(Azs, Times, Scale_factor, Exposure_Time, k=1/3):
    RMS = octave(Azs, Times, Scale_factor)
    RMS = np.array(RMS)
    RMSms = RMS
    Weights = np.array([0.695, 0.895, 1.006, 0.992, 0.854, 0.619, 0.384, 0.224,
                        0.116, 0.053, 0.0235])
    RMSW = RMSms * Weights
    RMSW2 = RMSW**2
    aw = np.sqrt(np.sum(RMSW2))
    MSDV = aw * np.sqrt(Exposure_Time * 60 * 60)
    MSI = MSDV * k
    return MSI


def RMS(DATA):
    DATA = np.array(DATA)
    return np.sqrt(np.mean(DATA**2))


def calc_RMS(series, axis=3):
    mean = np.mean(series**2, axis=axis)
    RMS = np.sqrt(mean)
    return RMS


def calc_MSI(Az, XX, accelerometer, exposure_time):
    """
    Calculates the MSI at a grid of points like XX.

    Inputs:
        Az -            Acceleration in z time series at each coordinate. Az
                        [SHOULD/SHOULD NOT] include acceleration due to gravity.

        XX -            The X coordinates, used to create an MSI grid of the
                        same shape.

        accelerometer - An object which holds a dictionary 'motion_data' which
                        holds the roll and roll acceleration time series'.

        exposure_time - The exposure time in the MII calculation.

    Returns:
        MSI -           A 3D vector of the MSI at each coordinate [x][y][z].
    """
    MSI_value = np.empty_like(XX, dtype=np.float32)
    count = 0
    for i in range(XX.shape[0]):
        for j in range(XX.shape[1]):
            for k in range(XX.shape[2]):
                MSI_value[i][j][k] = MSI(Az[i][j][k],accelerometer.motion_data["Time"], 1, exposure_time[count])
                count += 1
    return MSI_value


def calc_MII_rate(A_lat, Az, XX, accelerometer, Ct, h=0.91, g=9.81):
    """
    Calculates the MII at a grid of points like XX

    Inputs:
        Ax -            Acceleration in x time series at each coordinate

        Ay -            Acceleration in y time series at each cooridnate

        Az -            Acceleration in z time series at each coordinate.
                        Acceleration due to gravity [SHOULD/SHOULD NOT] be
                        included.

        XX -            The X coordinates, used to create an array of the same
                        shape

        accelerometer - An object which holds a dictionary 'motion_data' which
                        holds the roll and roll acceleration time series'

        Ct -            The tipping coefficient where a trip occurs.

        h -             The height of the centre of gravity

        g -             The acceleration due to gravity

    Returns:
        MII_rate -      A 3D vector of the MII rate per second at each coordinate
                        [x][y][z]
    """
    MII_rate = np.empty_like(XX, dtype=np.float32).flatten()
    for i in range(len(MII_rate)):
        Rt = calc_tip_ratio(h[i],
                            accelerometer.motion_data["Roll acc"],
                            A_lat[0,0,i],
                            g,
                            accelerometer.motion_data["Roll"],
                            Az[0,0,i])
        trips = calc_trips(Rt, Ct[i])
        MII_rate[i] = count_trips(trips)/accelerometer.motion_data["Time"].iloc[-1]
    return MII_rate


def calc_T_waves(T_calm, MII_rate, D_MII):
    """
    Calculates the time to complete a task in waves.

    Inputs:
        T_calm -    The time to complete the task in calm weather.

        MII_rate -  The number of MIIs per second

        D_MII -     The time taken to recover from an MII (seconds per trip)

    Returns:
        T_waves -   The time to complete the task in waves
    """
    T_waves = T_calm(1/(1-((MII_rate*D_MII))))
    return T_waves


def calc_E_task(MII_rate, D_MII):
    """
    Calculates the time to complete a task in waves.

    Inputs:
        MII_rate -  The number of MIIs per second.

        D_MII -     The time taken to recover from an MII (seconds per trip).

    Returns:
        E_task -   The efficiency in performing the task at each location.
    """
    E_task = 1 - ((MII_rate*D_MII)/60)
    return E_task
