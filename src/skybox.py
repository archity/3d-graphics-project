#!/usr/bin/env python3
"""
Skybox
"""

import OpenGL.GL as GL
import numpy as np
from PIL import Image
from core import VertexArray, FogColour
import glfw
from transform import translate, perspective, rotate, lookat

# Skybox vertices
skyboxVertices = np.array((
    # positions
    (-1.0, 1.0, -1.0),
    (-1.0, -1.0, -1.0),
    (1.0, -1.0, -1.0),
    (1.0, -1.0, -1.0),
    (1.0, 1.0, -1.0),
    (-1.0, 1.0, -1.0),

    (-1.0, -1.0, 1.0),
    (-1.0, -1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (-1.0, 1.0, 1.0),
    (-1.0, -1.0, 1.0),

    (1.0, -1.0, -1.0),
    (1.0, -1.0, 1.0),
    (1.0, 1.0, 1.0),
    (1.0, 1.0, 1.0),
    (1.0, 1.0, -1.0),
    (1.0, -1.0, -1.0),

    (-1.0, -1.0, 1.0),
    (-1.0, 1.0, 1.0),
    (1.0, 1.0, 1.0),
    (1.0, 1.0, 1.0),
    (1.0, -1.0, 1.0),
    (-1.0, -1.0, 1.0),

    (-1.0, 1.0, -1.0),
    (1.0, 1.0, -1.0),
    (1.0, 1.0, 1.0),
    (1.0, 1.0, 1.0),
    (-1.0, 1.0, 1.0),
    (-1.0, 1.0, -1.0),

    (-1.0, -1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (1.0, -1.0, -1.0),
    (1.0, -1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (1.0, -1.0, 1.0)), 'f')

face_list = [
    "left.jpg", "right.jpg",
    "top.jpg", "bottom.jpg",
    "front.jpg", "back.jpg"
]


class Skybox:
    def __init__(self, shader_skybox):
        self.rotation = 0

        self.ROTATION_SPEED = 1
        self.shader_skybox = shader_skybox
        self.time = 0
        self.fog_colour = FogColour()

        day_skybox = "./../resources/skybox2/"
        night_skybox = "./../resources/skybox3/"

        self.day_skybox_texture = self.load_cubemap(texture_file=day_skybox, tex_num=GL.GL_TEXTURE0)
        self.night_skybox_texture = self.load_cubemap(texture_file=night_skybox, tex_num=GL.GL_TEXTURE1)

        # create vertex array object, bind it
        # Create VBO, bind the new VBO, upload its data to GPU, declare size and type
        # (using the VertexArray class)
        self.vertex_array = VertexArray([skyboxVertices])

        # Get Uniform location of shader program
        names = ['view', 'projection', 'model', 'blend_factor', 'skybox', 'skybox2', 'sky_color']
        self.loc = {n: GL.glGetUniformLocation(self.shader_skybox.glid, n) for n in names}

    def load_cubemap(self, texture_file, tex_num):
        # Create a cubemap texture, and bind it to proper texture target
        # (bind to GL_TEXTURE_CUBE_MAP)
        texture_cubemap = GL.glGenTextures(1)
        GL.glActiveTexture(tex_num)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, texture_cubemap)

        # Read all the faces one by one
        # Specify a 2D texture image for each
        face_list_urls = [texture_file + s for s in face_list]
        for index, face_url in enumerate(face_list_urls):
            face = np.array(Image.open(face_url))
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + index, 0, GL.GL_RGB, face.shape[1],
                            face.shape[0], 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, face)
            print("Loaded: ", face_url)

        # Cubemap's wrapping and filtering methods
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

        return texture_cubemap
        # --------------------------------------------------------------------------------

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader_skybox.glid)

        # change depth function so depth test passes when values are equal to depth buffer's content
        GL.glDepthFunc(GL.GL_LEQUAL)

        # Disable depth writing
        GL.glDepthMask(GL.GL_FALSE)

        # Remove translation from view matrix
        # (last coloumn's top 3 values)
        # for i in range(3):
        #     view[i, 3] = 0
        # model = rotate(axis=(1.0, 0.0, 0.0), radians=-55.0)
        # view = translate(z=-3.0)
        # projection = perspective(45.0, 800.0/600.0, 0.1, 100.0)

        self.rotation = self.ROTATION_SPEED * glfw.get_time()
        self.rotation = self.rotation % 360

        model = rotate(axis=(0, 1, 0), angle=self.rotation)

        GL.glUniformMatrix4fv(self.loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(self.loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(self.loc['model'], 1, True, model)

        # Bind the skybox's VAO
        GL.glBindVertexArray(self.vertex_array.glid)

        # Enable vertex attribute array
        GL.glEnableVertexAttribArray(0)

        # Bind cubemap textures and upload to GPU
        self.bind_textures()
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)

        # Disable vertex attribute array
        GL.glDisableVertexAttribArray(0)

        # Set depth function back to default
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LESS)

    def bind_textures(self):
        # color = (0.2, 0.20, 0.20)
        self.time = glfw.get_time() * 1000
        self.time %= 24000
        if 0 <= self.time < 5000:
            blend_factor = (self.time - 0) / (5000 - 0)
            texture1 = self.night_skybox_texture
            texture2 = self.night_skybox_texture
            # color = (0.2, 0.20, 0.20)
        elif 5000 <= self.time < 8000:
            blend_factor = (self.time - 5000) / (8000 - 5000)
            texture1 = self.night_skybox_texture
            texture2 = self.day_skybox_texture
            # color = (0.4, 0.45, 0.45)
        elif 8000 <= self.time < 21000:
            blend_factor = (self.time - 8000) / (21000 - 8000)
            texture1 = self.day_skybox_texture
            texture2 = self.day_skybox_texture
            # color = (0.6, 0.70, 0.70)
        else:
            blend_factor = (self.time - 21000) / (24000 - 21000)
            texture1 = self.day_skybox_texture
            texture2 = self.night_skybox_texture
            # color = (0.4, 0.45, 0.45)

        # Bind the cubemaps' texture
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, texture1)
        GL.glUniform1i(self.loc['skybox'], 0)
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, texture2)
        GL.glUniform1i(self.loc['skybox2'], 1)
        GL.glUniform1f(self.loc['blend_factor'], blend_factor)
        GL.glUniform3fv(self.loc['sky_color'], 1, self.fog_colour.get_colour())
