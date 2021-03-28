#!/usr/bin/env python3
"""
Skybox
"""
import copy
import OpenGL.GL as GL
import numpy as np
from PIL import Image

# Skybox vertices
from core import VertexArray

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
        self.shader_skybox = shader_skybox
        # -------------------------------Cubemap stuff------------------------------------
        # Create a Skybox texture, and bind it to proper texture target
        # (bind to GL_TEXTURE_CUBE_MAP)
        self.skybox_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.skybox_texture)

        face_list_urls = ["./../resources/skybox/" + s for s in face_list]
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

    def draw(self, projection, view,  model):
        # change depth functions
        GL.glDepthMask(GL.GL_FALSE)
        GL.glDepthFunc(GL.GL_LEQUAL)

        GL.glUseProgram(self.shader_skybox.glid)
        view_copy = copy.deepcopy(view)
        for i in range(3):
            view_copy[i, 3] = 0

        GL.glUniformMatrix4fv(self.loc['view'], 1, True, view_copy)
        GL.glUniformMatrix4fv(self.loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(self.loc['model'], 1, True, model)

        # skybox cube
        # GL.glBindVertexArray(self.glid)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        loc = GL.glGetUniformLocation(self.shader_skybox.glid, 'skybox')
        GL.glUniform1i(loc, 0)
        self.vertex_array.execute(GL.GL_TRIANGLES)

        GL.glDepthMask(GL.GL_FALSE)

        GL.glBindVertexArray(self.vertex_array.glid)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.skybox_texture)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)

        GL.glDepthFunc(GL.GL_LESS)

        GL.glDepthMask(GL.GL_TRUE)

        # bind the cubemap texture before rendering the container


        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, 0)
        GL.glUseProgram(0)
