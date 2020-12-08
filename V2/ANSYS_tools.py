# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 16:02:15 2020

@author: Rastko
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R


class ansys_accelerometer:
    """
    Converts the global positioning data provided by ANSYS into what an
    accelerometer would measure at the COG. The accelerations can then be
    translated to any point.
    """

    def __init__(self, df, ship_rot, person_rot, inc_gravity=False, position=[0,0,0]):
        """
        Initialises an ansys_accelerometer, which converts the global movement
        data of an ANSYS file to what an accelerometer would measure.

        df:             Motion data df.

        ship_rot:       The rotation of the ship origin in the global reference
                        frame.
        
        person_rot:     The rotation of the person on the ship.

        inc_gravity:    An option to add in the affect of gravity to the
                        acceleration in the global z axis.
        
        CoG:            The position of the accelerometer, relative to a fixed
                        point on the body.
        """
        self.person_rot = person_rot
        self.rot_z = ship_rot[2] + self.person_rot
        self.rot_y = ship_rot[1]
        self.rot_x = ship_rot[0]
        self.t, self.loc, self.rotation, self.acceleration = self.load_data(df, inc_gravity=inc_gravity)

        #define the local reference frame
        self.acc_directions = self.accelerometer_directions(rot_z=self.rot_z,
                                                            rot_y=self.rot_y,
                                                            rot_x=self.rot_x)

        # Rotate the local reference frame at each time step
        self.rotated_acc_directions = self.rotated_accelerometer_directions(self.acc_directions,
                                                                            self.rotation)

        # Calculate the component of acceleration in the direction of the 
        # rotated reference frame at each time step
        self.rotated_acc_vectors = self.rotated_accelerometer_vectors(self.rotated_acc_directions,
                                                                      self.acceleration)

        self.num_frames = len(self.t)
        self.max_acc = np.nanmax(np.linalg.norm(self.acceleration, axis=1))

        # Calculate the roll, pitch and yaw in the new reference frame
        self.new_rotations = self.calc_rotation(self.acc_directions,
                                                self.rotated_acc_directions)

        # Calculate the rotational acceleration in the new reference frame
        self.rotational_acc = self.calc_rot_acceleration(self.new_rotations, self.t)
        
        self.motion_data = {'Ax': self.rotated_acc_vectors[:,0],
                            'Ay': self.rotated_acc_vectors[:,1],
                            'Az': self.rotated_acc_vectors[:,2],
                            'Roll': self.new_rotations[0],
                            'Pitch': self.new_rotations[1],
                            'Yaw': self.new_rotations[2],
                            'Roll acc': self.rotational_acc[0],
                            'Pitch acc': self.rotational_acc[1],
                            'Yaw acc': self.rotational_acc[2],
                            'Time': self.t,
                            'Position': position}

    def load_data(self, df, inc_gravity=True):
        """
        Read the motion data from an ansys aqwa file.
        """
        t = df["Time"]
        self.frame_rate = t.diff()[1]
        loc = np.array(df[["X", "Y", "Z"]])
        rotation = np.array(df[["Rot x", "Rot y", "Rot z"]])
        acceleration = self.calc_acceleration(self.calc_acceleration(loc, t),
                                              t)
        if inc_gravity:
            acceleration[:, 2] -= 9.81
        return t, loc, rotation, acceleration

    def calc_acceleration(self, position, t):
        """
        Calculate the global acceleration acceleration from the global
        positioion
        """
        dloc = np.diff(position, axis=0, prepend=0)
        acc = dloc/self.frame_rate
        return acc

    def calc_rot_acceleration(self, rotation, t):
        """
        Calculate the global acceleration acceleration from the global
        positioion
        """
        drot = np.diff(rotation, prepend=0)/self.frame_rate
        d2rot = np.diff(drot, prepend =0)/self.frame_rate
        return d2rot

    def accelerometer_directions(self, origin_directions=np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]]), rot_z=0, rot_y=0, rot_x=0):
        """
        Calculate the local orientation of X, Y and Z
        """
        r = R.from_euler('XYZ', [rot_x, rot_y, rot_z], degrees=True)
        acc_directions = r.apply(origin_directions)
        return acc_directions

    def rotated_accelerometer_directions(self, directions, rotation):
        """
        Rotate the local origin axis' by the global rotation at each frame in
        the results.
        """
        r = R.from_euler("XYZ", rotation, degrees=True)
        rotated_x = r.apply(directions[0])
        rotated_y = r.apply(directions[1])
        rotated_z = r.apply(directions[2])
#        print(rotated_x, rotated_y, rotated_z)
        rotated_acc_directions = np.stack((rotated_x, rotated_y, rotated_z),
                                          axis=1)
        return rotated_acc_directions

    def rotated_accelerometer_vectors(self, rotated_acc_directions, acceleration):
        """
        Calculate the component of the global acceleration in the direction of
        the local orientation at each time frame to get the local acceleration
        independant of rotation, yaw and pitch.
        Einsum is used instead of dot product as it is easier to implement
        on 3D vectors, instead of using a for loop.
        """
        rotated_acc_x = np.einsum('ij, ij->i',
                                  acceleration,
                                  rotated_acc_directions[:, 0])
        rotated_acc_y = np.einsum('ij, ij->i',
                                  acceleration,
                                  rotated_acc_directions[:, 1])
        rotated_acc_z = np.einsum('ij, ij->i',
                                  acceleration,
                                  rotated_acc_directions[:, 2])
        rotated_acc = np.stack([rotated_acc_x,
                                rotated_acc_y,
                                rotated_acc_z], axis=1)
        return rotated_acc

    def get_position_vectors_at_frame(self, i):
        """
        At frame i, return the location [x, y, z] and the vectors of the three
        basis vectors [X, Y, Z]
        """
        loc_ = self.loc[i]
        vector_ = self.rotated_acc_directions[i]
        return loc_, vector_

    def position_vectors_to_segs(self, fr, to):
        """
        Converts positions 'fr' (from) and vectors 'to' to quiver segments
        """
        fr = np.array(fr)
        to = np.array(to)
        x = fr[:, 0]
        y = fr[:, 1]
        z = fr[:, 2]
        u = to[:, 0]+x
        v = to[:, 1]+y
        w = to[:, 2]+z
        return x, y, z, u, v, w

    def animate_plot(self):
        """
        Makes an animation of the motion data
        """
        self.fig = plt.figure()
        self.ax = self.fig.gca(projection='3d')
        # Create a quiver of the three vectors at the start of the animation
        fr = [self.loc[0]]*4
        to = self.rotated_acc_directions[0]
        to = np.append(to, [[1, 1, 1]], axis=0)
        self.cols = ['r', 'g', 'b',  'k', 'r', 'r', 'g', 'g', 'b', 'b', 'k', 'k']
        segs = self.position_vectors_to_segs(fr, to)
        self.quivers = self.ax.quiver(*segs, colors=self.cols)

        # Set the limits of the 3d plot
        self.ax.set_xlim([-2, 2])
        self.ax.set_ylim([-2, 2])
        self.ax.set_zlim([-2, 2])
        self.ax.set_xlim3d([-2.0, 2.0])
        self.ax.set_xlabel('X')
        self.ax.set_ylim3d([-2.0, 2.0])
        self.ax.set_ylabel('Y')
        self.ax.set_zlim3d([-2, 2])
        self.ax.set_zlabel('Z')

        # Create an animation, use animate_frame to set the new positions of
        # the quivers at each frame.
        self.ani = FuncAnimation(self.fig,
                                 self.animate_frame,
                                 frames=self.num_frames,
                                 interval=self.frame_rate*1e3,
                                 blit=False)
        plt.show()

    def animate_frame(self, i):
        """
        Update the line segments of quiver in the animation.
        """
        loc_, vector_ = self.get_position_vectors_at_frame(i)
        vector_ = np.append(vector_,
                            [self.acceleration[i]/(self.max_acc/2)],
                            axis=0)
        fr = [loc_]*len(vector_)
        to = vector_
        segs = np.array(self.position_vectors_to_segs(fr, to)).reshape(6, -1)
        new_segs = [[[x, y, z], [u, v, w]] for x, y, z, u, v, w in zip(*segs.tolist())]
        self.quivers.set_segments(new_segs)
        self.ax.set_title('%03d'%(i))
        return self.quivers

    def save_data(self, file_name):
        """
        Save the acceleration data to an excel file
        """
        df = pd.DataFrame(self.t)
        df["Acc X (m/s^2)"] = self.rotated_acc_vectors[:, 0]
        df["Acc Y (m/s^2)"] = self.rotated_acc_vectors[:, 1]
        df["Acc Z (m/s^2)"] = self.rotated_acc_vectors[:, 2]
        df["Rot about X (rad)"] = self.new_rotations[0]
        df["Rot about Y (rad)"] = self.new_rotations[1]
        df["Rot about Z (rad)"] = self.new_rotations[2]
        df["Rot acc about X (rad/s^2)"] = self.rotational_acc[0]
        df["Rot acc about Y (rad/s^2)"] = self.rotational_acc[1]
        df["Rot acc about Z (rad/s^2)"] = self.rotational_acc[2]
        df.to_excel(file_name+".xlsx")

    def calc_rotation(self, original_vectors, rotated_vectors, rotation_axis=[0, 1, 2], return_deg=True):
        """
        Calculates the rotation about a direction, given by rot_about.
        Vectors must be in the format XYZ.
        Roll is rotation about the X axis.
        Pitch is rotation about the Y axis.
        Yaw is rotation about the Z axis.
        """
        rotation = []
        for rot_about in [0, 1, 2]:
            if rot_about == 0:
                rotated_vector_number = 1
            elif rot_about == 1:
                rotated_vector_number = 2
            else:
                rotated_vector_number = 0
            rotation_vector = rotated_vectors[:, rot_about]
            original_rotated_vector = original_vectors[rotated_vector_number]
            rotated_vector = rotated_vectors[:, rotated_vector_number]
        #    print(rotation_vector)
        #    print(original_rotated_vector)
        #    print(rotated_vector)
            n1 = self.calc_norm_vector(rotation_vector,
                                       original_rotated_vector)
            n2 = self.calc_norm_vector(rotation_vector,
                                       rotated_vector)
        #    return n1, n2
        #    print(n1)
            angle = self.calc_angle2(n1, n2, rotation_vector)
            rotation.append(angle)

        if return_deg:
            rotation = np.rad2deg(rotation)

        return rotation

    def calc_deck_angle(self):
        """
        Calculates the deck angle at each time step
        """
        deck_normal = self.calc_norm_vector(self.rotated_acc_directions[:,0],
                                            self.rotated_acc_directions[:,1])
        deck_angle = self.calc_angle(deck_normal,
                                     self.acc_directions[:,2],
                                     returnDeg=True)
        return deck_angle

    def calc_norm_vector(self, v1, v2):
        """
        Calculates the normal vector between two vectors
        """
        return np.cross(v1, v2)

    def calc_angle(self, n1, n2, returnDeg=False):
        """
        Calculates angle between two planes with normal vectors n1 and n2.
        """
        top = np.dot(n1, n2)
        bottom = np.dot(np.linalg.norm(n1, axis=1),
                        np.linalg.norm(n2))
        cos = np.abs(top/bottom)
        theta = np.arccos(cos)
        if returnDeg:
            theta = np.rad2deg(theta)
        return theta

    def calc_angle2(self, a, b, n, returnDeg=False):
        """
        Calculates the angle between two vectors a, b, with the right hand rule
        with vector n which is perpendicular to both a and b.
        """
        A = np.einsum('ij,ij->i', np.cross(a, b), n)
        B = np.einsum('ij,ij->i', a, b)
        beta = np.arctan2(A, B)
        if returnDeg == True:
            beta = np.rad2deg(beta)
        return beta

    def get_MII_data(self):
        """
        Outputs the required motion data for calculation of MII
        """
        n4 = self.new_rotations[0]
        n4_acc = self.rotational_acc[0]
        D3_acc = self.rotated_acc_vectors[:,2]
        D2_acc = self.rotated_acc_vectors[:,1]
        return n4, n4_acc, D3_acc, D2_acc

    def coordinates_in_person_rf(self, XX, YY, ZZ):
        r = R.from_euler('Z', [self.person_rot], degrees=True)
        ship_coords = np.stack((XX.flatten(), YY.flatten(), ZZ.flatten()),
                               axis=1)
        print(ship_coords)
        person_coords = r.apply(ship_coords)
        print(person_coords)
        XX_person = np.reshape(person_coords[:,0], XX.shape)
        YY_person = np.reshape(person_coords[:,1], YY.shape)
        ZZ_person = np.reshape(person_coords[:,2], ZZ.shape)
        return XX_person, YY_person, ZZ_person
#accelerometer = ansys_accelerometer('sample data.xlsx', rot_x=180)
#accelerometer.animate_plot()
#accelerometer.save_data("results3")