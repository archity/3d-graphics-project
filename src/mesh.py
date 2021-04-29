import OpenGL.GL as GL
import numpy as np
import glfw

from vertexarray import VertexArray
from node import Node
import config


# ------------  Mesh is a core drawable, can be basis for most objects --------
class Mesh:
    """ Basic mesh class with attributes passed as constructor arguments """

    def __init__(self, shader, attributes, index=None):
        self.shader = shader
        self.names = ['view', 'projection', 'model']
        self.loc = {n: GL.glGetUniformLocation(shader.glid, n) for n in self.names}
        self.vertex_array = VertexArray(attributes, index)

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        GL.glUniformMatrix4fv(self.loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(self.loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(self.loc['model'], 1, True, model)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertex_array.execute(primitives)


# -------------- Texture based Phong rendered Mesh class -------------------------

class TexturedPhongMesh(Node):
    def __init__(self, shader, tex, attributes, faces,
                 light_dir=None, k_a=(1, 1, 1), k_d=(1, 1, 0), k_s=(1, 1, 0),
                 s=64.):
        # super().__init__(shader, tex, attributes, faces)
        super().__init__()
        # setup texture and upload it to GPU
        self.texture = tex
        self.vertex_array = VertexArray(attributes=attributes, index=faces)
        self.shader = shader

        self.k_a = k_a
        self.k_d = k_d
        self.k_s = k_s
        self.s = s
        # ----------------

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # projection geometry
        names = ['view', 'projection', 'model',
                 'diffuseMap', 'k_a', 'k_d', 'k_s', 's',
                 'fog_colour', 'w_camera_position']
        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}

        # Iterate over all the light sources and send (to shader) their properties.
        for i in range(0, config.fog_colour.num_light_src):
            light_pos_loc = GL.glGetUniformLocation(self.shader.glid, 'light_position[%d]' % i)
            GL.glUniform3fv(light_pos_loc, 1, config.fog_colour.light_pos[i])

            atten_loc = GL.glGetUniformLocation(self.shader.glid, 'atten_factor[%d]' % i)
            GL.glUniform3fv(atten_loc, 1, config.fog_colour.get_atten()[i])

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)

        GL.glUniform3fv(loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(loc['k_s'], 1, self.k_s)
        GL.glUniform1f(loc['s'], max(self.s, 0.001))
        GL.glUniform3fv(loc['fog_colour'], 1, config.fog_colour.get_colour())

        # world camera position for Phong illumination specular component
        w_camera_position = np.linalg.inv(view)[:, 3]
        GL.glUniform3fv(loc['w_camera_position'], 1, w_camera_position)

        # ----------------
        # texture access setups
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc['diffuseMap'], 0)
        self.vertex_array.execute(primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)

    def key_handler(self, key):
        # Some day-night toggling functions
        # fog_colour is globally defined in config.py file,
        # hence changes here will be reflected and available for all classes/functions
        if key == glfw.KEY_F6:
            config.fog_colour.toggle_value = 6
        if key == glfw.KEY_F7:
            config.fog_colour.toggle_value = 7
        if key == glfw.KEY_F8:
            config.fog_colour.toggle_value = 8


class TexturedPhongMeshSkinned(Node):
    def __init__(self, shader, tex, attributes, faces, bone_nodes, bone_offsets,
                 k_a=(1, 1, 1), k_d=(1, 1, 0), k_s=(1, 1, 0), s=64.):
        super().__init__()

        # setup texture and upload it to GPU
        self.texture = tex
        self.vertex_array = VertexArray(attributes=attributes, index=faces)
        self.shader = shader
        # self.fog_colour = FogColour()

        self.k_a = k_a
        self.k_d = k_d
        self.k_s = k_s
        self.s = s
        # ----------------
        self.bone_nodes = bone_nodes
        self.bone_offsets = np.array(bone_offsets, np.float32)

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # projection geometry
        names = ['view', 'projection', 'model', 'diffuseMap', 'k_a', 'k_d', 'k_s', 's',
                 'fog_colour', 'w_camera_position']
        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)

        GL.glUniform3fv(loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(loc['k_s'], 1, self.k_s)
        GL.glUniform1f(loc['s'], max(self.s, 0.001))
        GL.glUniform3fv(loc['fog_colour'], 1, config.fog_colour.get_colour())

        # bone world transform matrices need to be passed for skinning
        for bone_id, node in enumerate(self.bone_nodes):
            bone_matrix = node.world_transform @ self.bone_offsets[bone_id]

            bone_loc = GL.glGetUniformLocation(self.shader.glid, 'bone_matrix[%d]' % bone_id)
            GL.glUniformMatrix4fv(bone_loc, len(self.bone_nodes), True, bone_matrix)

        # Iterate over all the light sources and send (to shader) their properties.
        for i in range(0, config.fog_colour.num_light_src):
            light_pos_loc = GL.glGetUniformLocation(self.shader.glid, 'light_position[%d]' % i)
            GL.glUniform3fv(light_pos_loc, 1, config.fog_colour.light_pos[i])

            atten_loc = GL.glGetUniformLocation(self.shader.glid, 'atten_factor[%d]' % i)
            GL.glUniform3fv(atten_loc, 1, config.fog_colour.get_atten()[i])

        # world camera position for Phong illumination specular component
        w_camera_position = np.linalg.inv(view)[:, 3]
        GL.glUniform3fv(loc['w_camera_position'], 1, w_camera_position)

        # ----------------
        # texture access setups
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc['diffuseMap'], 0)
        self.vertex_array.execute(primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)
