import copy
import numpy as np
import glfw
from PIL import Image

from transform import normalized


class Camera:
    def __init__(self):
        # Define camera specific variables
        self.camera_pos = np.array((0.0, 4.0, 0.0))
        # self.camera_target = np.array((1.0, 0.0, 0.0))
        # self.camera_direction = normalized((self.camera_pos - self.camera_target))
        self.up = np.array((0.0, 1.0, 0.0))

        self.camera_front = np.array((0.0, 0.0, 1.0))
        # self.camera_right = normalized(np.cross(self.up, self.camera_direction))

        # Define mouse specific variables
        self.first_mouse = True
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 45.0
        self.last_x = 800.0 / 2.0
        self.last_y = 600.0 / 2.0
        self.sensitivity = 0.04
        # self.update_camera_vectors()

        # High resolution heightmap image for smoother collision detection
        self.hmap_file = "./../resources/map/hmap_2_mounds_4096px.png"
        self.hmap_tex = np.asarray(Image.open(self.hmap_file).convert('RGB'))

    def process_keyboard_input(self, window, delta_time):
        camera_speed = 30 * delta_time
        self.camera_pos[1] = self.scale_xz_to_hmap() + 3
        # print(self.camera_pos[0], ", ", self.camera_pos[1], ", ", self.camera_pos[2])
        if glfw.get_key(window=window, key=glfw.KEY_W):
            temp = copy.deepcopy(self.camera_front)
            temp[1] = 0
            self.camera_pos += camera_speed * temp
        if glfw.get_key(window=window, key=glfw.KEY_S):
            temp = copy.deepcopy(self.camera_front)
            temp[1] = 0
            self.camera_pos -= camera_speed * temp
        if glfw.get_key(window=window, key=glfw.KEY_A):
            temp = copy.deepcopy(self.camera_front)
            temp[1] = 0
            self.camera_pos -= normalized(np.cross(temp, self.up)) * camera_speed
        if glfw.get_key(window=window, key=glfw.KEY_D):
            temp = copy.deepcopy(self.camera_front)
            temp[1] = 0
            self.camera_pos += normalized(np.cross(temp, self.up)) * camera_speed
        # print("Position: ", self.camera_pos, "Direction: ", self.camera_front)
        if glfw.get_key(window=window, key=glfw.KEY_LEFT):
            if self.camera_front[2] >= 0 and self.camera_front[0] >= 0:
                self.camera_front[2] -= self.sensitivity
                self.camera_front[0] += self.sensitivity
                self.camera_front = normalized(self.camera_front)
            if self.camera_front[2] < 0 and self.camera_front[0] >= 0:
                self.camera_front[2] -= self.sensitivity
                self.camera_front[0] -= self.sensitivity
                self.camera_front = normalized(self.camera_front)
            if self.camera_front[2] < 0 and self.camera_front[0] < 0:
                self.camera_front[2] += self.sensitivity
                self.camera_front[0] -= self.sensitivity
                self.camera_front = normalized(self.camera_front)
            if self.camera_front[2] >= 0 and self.camera_front[0] < 0:
                self.camera_front[2] += self.sensitivity
                self.camera_front[0] += self.sensitivity
                self.camera_front = normalized(self.camera_front)
        if glfw.get_key(window=window, key=glfw.KEY_RIGHT):
            if self.camera_front[2] >= 0 and self.camera_front[0] >= 0:
                self.camera_front[2] += self.sensitivity
                self.camera_front[0] -= self.sensitivity
                self.camera_front = normalized(self.camera_front)
            if self.camera_front[2] < 0 and self.camera_front[0] >= 0:
                self.camera_front[2] += self.sensitivity
                self.camera_front[0] += self.sensitivity
                self.camera_front = normalized(self.camera_front)
            if self.camera_front[2] < 0 and self.camera_front[0] < 0:
                self.camera_front[2] -= self.sensitivity
                self.camera_front[0] += self.sensitivity
                self.camera_front = normalized(self.camera_front)
            if self.camera_front[2] >= 0 and self.camera_front[0] < 0:
                self.camera_front[2] -= self.sensitivity
                self.camera_front[0] -= self.sensitivity
                self.camera_front = normalized(self.camera_front)
        if glfw.get_key(window=window, key=glfw.KEY_UP):
            if self.camera_front[1] < 1:
                self.camera_front[1] += self.sensitivity
                # self.camera_front = normalized(self.camera_front)
        if glfw.get_key(window=window, key=glfw.KEY_DOWN):
            if self.camera_front[1] > 0:
                self.camera_front[1] -= self.sensitivity
                # self.camera_front = normalized(self.camera_front)

    def scale_xz_to_hmap(self):
        # Scale the current coordinates to the high resolution (4096px)
        # heightmap's range.
        # +500 offset because because our world (grass area) is from [-500 to +500]
        x_coord = int(((self.camera_pos[2] + 500) / 1000) * self.hmap_tex.shape[0])
        z_coord = int(((self.camera_pos[0] + 500) / 1000) * self.hmap_tex.shape[0])
        height = self.get_height(x_coord, z_coord, self.hmap_tex)
        return height

    def get_height(self, x, z, image):
        if x < 0 or x >= image.shape[0] or z < 0 or z >= image.shape[0]:
            return 0
        height = image[x, z, 0]
        # [0 to 1] range
        height /= 256
        # [0 to MAX_HEIGHT] range
        height *= 30

        return height

    def get_camera_pos(self):
        return self.camera_pos

    def get_camera_front(self):
        return self.camera_front

    def get_camera_up(self):
        return self.up

    def get_fov(self):
        return self.fov
