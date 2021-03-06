from itertools import cycle

import glfw
import numpy as np
import OpenGL.GL as GL
from PIL import Image

from mesh import Mesh
from texture import Texture
from transform import normalized
from node import Node
import config


# -------------- Example texture plane class ----------------------------------
class TexturedPlane(Mesh, Node):
    """ Simple first textured object """

    def __init__(self, background_texture_file, road_texture_file, road2_texture_file,  blendmap_file, shader, size, hmap_file):

        # Load heightmap file
        hmap_tex = np.asarray(Image.open(hmap_file).convert('RGB'))

        self.MAX_HEIGHT = 30
        self.MIN_HEIGHT = 0
        self.MAX_PIXEL_COLOR = 256
        self.HMAP_SIZE = hmap_tex.shape[0]  # 256
        self.background_texture_file = background_texture_file
        self.road_texture_file = road_texture_file
        self.road2_texture_file = road2_texture_file
        self.blendmap_file = blendmap_file
        # self.fog_colour = FogColour()

        vertices, texture_coords, normals, indices = self.create_attributes(self.HMAP_SIZE, hmap_tex=hmap_tex)

        super().__init__(shader, [vertices, texture_coords, normals], indices)

        self.names = ['diffuse_map', 'blue_texture', 'red_texture', 'blendmap', 'fog_colour']
        self.loc1 = {n: GL.glGetUniformLocation(shader.glid, n) for n in self.names}

        # interactive toggles
        self.wrap = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                           GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filter = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                             (GL.GL_LINEAR, GL.GL_LINEAR),
                             (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap_mode, self.filter_mode = next(self.wrap), next(self.filter)

        # setup texture and upload it to GPU
        self.background_texture = Texture(self.background_texture_file, self.wrap_mode, *self.filter_mode)
        self.road_texture = Texture(self.road_texture_file, self.wrap_mode, *self.filter_mode)
        self.road2_texture = Texture(self.road2_texture_file, self.wrap_mode, *self.filter_mode)
        self.blendmap_texture = Texture(self.blendmap_file, self.wrap_mode, *self.filter_mode)

    def create_attributes(self, size, hmap_tex):
        vertices = []
        normals = []
        texture_coords = []

        # Create vertices, normals, and texture coordinates
        for i in range(0, size):
            for j in range(0, size):
                # Vertices - (x, y, z)
                vertices.append([(j / (size - 1)) * 1000,
                                 self.get_height(i, j, image=hmap_tex),
                                 (i / (size - 1)) * 1000])
                normals.append(self.calculate_normal(x=j, z=i, hmap_image=hmap_tex))
                # normals.append([0, 1, 0])
                texture_coords.append([j / (size - 1), i / (size - 1)])

        # Convert to numpy array list
        vertices = np.array(vertices)
        normals = np.array(normals)
        texture_coords = np.array(texture_coords)

        indices = []
        for gz in range(0, size - 1):
            for gx in range(0, size - 1):
                top_left = (gz * size) + gx
                top_right = top_left + 1
                bottom_left = ((gz + 1) * size) + gx
                bottom_right = bottom_left + 1
                indices.append([top_left, bottom_left, top_right, top_right, bottom_left, bottom_right])

        indices = np.array(indices)

        return vertices, texture_coords, normals, indices

    def calculate_normal(self, x, z, hmap_image):
        """
        Calculate normals based on current point's neightbours.
        :param x: x coordinate
        :param z: z coordinate
        :param hmap_image: the heightmap image
        :return: normalized calculated normals
        """
        height_l = self.get_height(x-1, z, image=hmap_image)
        height_r = self.get_height(x+1, z, hmap_image)
        height_d = self.get_height(x, z-1, hmap_image)
        height_u = self.get_height(x, z+1, hmap_image)
        return normalized(np.array([height_l-height_r, 2.0, height_d-height_u]))

    def get_height(self, x, z, image):
        if x < 0 or x >= image.shape[0] or z < 0 or z >= image.shape[0]:
            return 0
        height = image[x, z, 0]
        # [0 to 1] range
        height /= self.MAX_PIXEL_COLOR
        # [0 to MAX_HEIGHT] range
        height *= self.MAX_HEIGHT

        return height

    def key_handler(self, key):
        # some day-night interactive elements
        if key == glfw.KEY_F6:
            config.fog_colour.toggle_value = 6
        if key == glfw.KEY_F7:
            config.fog_colour.toggle_value = 7
        if key == glfw.KEY_F8:
            config.fog_colour.toggle_value = 8

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # texture access setups
        self.bind_textures()
        self.connect_texture_units()
        super().draw(projection, view, model, primitives)

    def connect_texture_units(self):
        GL.glUniform1i(self.loc1['diffuse_map'], 0)
        GL.glUniform1i(self.loc1['blue_texture'], 1)
        GL.glUniform1i(self.loc1['red_texture'], 2)
        GL.glUniform1i(self.loc1['blendmap'], 3)
        GL.glUniform3fv(self.loc1['fog_colour'], 1, config.fog_colour.get_colour())

        # print(self.fog_colour.get_atten()[0])
        # atten_var = self.fog_colour.get_atten()
        for i in range(0, config.fog_colour.num_light_src):
            light_pos_loc = GL.glGetUniformLocation(self.shader.glid, 'light_position[%d]' % i)
            GL.glUniform3fv(light_pos_loc, 1, config.fog_colour.light_pos[i])

            atten_loc = GL.glGetUniformLocation(self.shader.glid, 'atten_factor[%d]' % i)
            GL.glUniform3fv(atten_loc, 1, config.fog_colour.get_atten()[i])

    def bind_textures(self):
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.background_texture.glid)
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.road_texture.glid)
        GL.glActiveTexture(GL.GL_TEXTURE2)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.road2_texture.glid)
        GL.glActiveTexture(GL.GL_TEXTURE3)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.blendmap_texture.glid)
