#!/usr/bin/env python3
"""
Skybox
"""

import OpenGL.GL as GL
import numpy as np
from PIL import Image
from core import VertexArray
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
        self.ROTATION_SPEED = 0.005

        self.shader_skybox = shader_skybox
        # -------------------------------Cubemap stuff------------------------------------
        # Create a cubemap texture, and bind it to proper texture target
        # (bind to GL_TEXTURE_CUBE_MAP)
        self.texture_cubemap = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.texture_cubemap)

        # Read all the faces one by one
        # Specify a 2D texture image for each
        face_list_urls = ["./../resources/skybox2/" + s for s in face_list]
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

        # --------------------------------------------------------------------------------

        # create vertex array object, bind it
        # Create VBO, bind the new VBO, upload its data to GPU, declare size and type
        # (using the VertexArray class)
        self.vertex_array = VertexArray([skyboxVertices])

        # Get Uniform location of shader program
        names = ['view', 'projection', 'model']
        self.loc = {n: GL.glGetUniformLocation(self.shader_skybox.glid, n) for n in names}

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

        self.rotation += (self.ROTATION_SPEED * glfw.get_time())
        model = rotate(axis=(0, 1, 0), angle=self.rotation)

        GL.glUniformMatrix4fv(self.loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(self.loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(self.loc['model'], 1, True, model)

        # Bind the skybox's VAO
        GL.glBindVertexArray(self.vertex_array.glid)
        # ??? (making no difference)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        # Bind the cubemap texture
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.texture_cubemap)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)

        # Set depth function back to default
        GL.glDepthMask(GL.GL_TRUE)

        GL.glDepthFunc(GL.GL_LESS)

    # def bind_textures(self):
    #     GL.glActiveTexture(GL.GL_TEXTURE0)
    #     GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.texture_cubemap)
    #     GL.glActiveTexture(GL.GL_TEXTURE1)
    #     GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.night_texture)
    #     GL.glUniform1f()
