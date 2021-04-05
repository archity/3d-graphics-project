import numpy as np
import glfw  # lean window system wrapper for OpenGL
import OpenGL.GL as GL  # standard Python OpenGL wrapper

from transform import rotate, translate, scale, normalized


class Camera:
    def __init__(self):
        self.camera_pos = np.array((0.0, 0.0, 3.0))
        self.camera_target = np.array((0.0, 0.0, 0.0))
        self.camera_direction = normalized((self.camera_pos - self.camera_target))
        self.up = np.array((0.0, 1.0, 0.0))

        self.camera_front = np.array((0.0, 0.0, -1.0))
        self.camera_right = normalized(np.cross(self.up, self.camera_direction))

    def process_input(self, window, delta_time):
        camera_speed = 2.5 * delta_time
        if glfw.get_key(window=window, key=glfw.KEY_UP):
            self.camera_pos += camera_speed * self.camera_front
        if glfw.get_key(window=window, key=glfw.KEY_DOWN):
            self.camera_pos -= camera_speed * self.camera_front
        if glfw.get_key(window=window, key=glfw.KEY_LEFT):
            self.camera_pos -= normalized(np.cross(self.camera_front, self.up)) * camera_speed
        if glfw.get_key(window=window, key=glfw.KEY_RIGHT):
            self.camera_pos += normalized(np.cross(self.camera_front, self.up)) * camera_speed

    def get_camera_pos(self):
        return self.camera_pos

    def get_camera_front(self):
        return self.camera_front

    def get_camera_up(self):
        return self.up
