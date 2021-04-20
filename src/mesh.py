import OpenGL.GL as GL
import numpy as np

from vertexarray import VertexArray
from fog import FogColour


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


class TexturedMesh(Mesh):

    def __init__(self, shader, tex, attributes, faces):
        super().__init__(shader, attributes, faces)

        loc = GL.glGetUniformLocation(shader.glid, 'diffuse_map')
        self.loc['diffuse_map'] = loc

        # setup texture and upload it to GPU
        self.texture = tex

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # texture access setups
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(self.loc['diffuse_map'], 0)
        super().draw(projection, view, model, primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)


# -------------- Phong rendered Mesh class -----------------------------------
class PhongMesh(Mesh):
    """ Mesh with Phong illumination """

    def __init__(self, shader, attributes, index=None,
                 light_dir=(1, -1, 1),  # directional light (in world coords)
                 k_a=(0, 0, 0), k_d=(1, 1, 0), k_s=(1, 1, 1), s=16.):
        super().__init__(shader, attributes, index)

        print(light_dir)
        self.light_dir = light_dir
        self.k_a, self.k_d, self.k_s, self.s = k_a, k_d, k_s, s

        # retrieve OpenGL locations of shader variables at initialization
        names = ['light_dir', 'k_a', 's', 'k_s', 'k_d', 'w_camera_position']

        loc = {n: GL.glGetUniformLocation(shader.glid, n) for n in names}
        self.loc.update(loc)

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # setup light parameters
        GL.glUniform3fv(self.loc['light_dir'], 1, self.light_dir)

        # setup material parameters
        GL.glUniform3fv(self.loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(self.loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(self.loc['k_s'], 1, self.k_s)
        GL.glUniform1f(self.loc['s'], max(self.s, 0.001))

        # world camera position for Phong illumination specular component
        w_camera_position = np.linalg.inv(view)[:, 3]
        GL.glUniform3fv(self.loc['w_camera_position'], 1, w_camera_position)

        super().draw(projection, view, model, primitives)


class TexturedPhongMesh:
    def __init__(self, shader, tex, attributes, faces,
                 light_dir=None,  # directional light (in world coords)
                 k_a=(1, 1, 1), k_d=(1, 1, 0), k_s=(1, 1, 0), s=64.
                 ):
        # super().__init__(shader, tex, attributes, faces)

        # setup texture and upload it to GPU
        self.texture = tex
        self.vertex_array = VertexArray(attributes=attributes, index=faces)
        self.shader = shader
        self.fog_colour = FogColour()

        self.k_a = k_a
        self.k_d = k_d
        self.k_s = k_s
        self.s = s
        # ----------------

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # projection geometry
        names = ['view', 'projection', 'model', 'nit_matrix', 'diffuseMap', 'k_a', 'k_d', 'k_s', 's', 'fog_colour']
        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}

        # model3x3 = model[0:3, 0:3]
        # nit_matrix = np.linalg.inv(model3x3).T

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)

        GL.glUniform3fv(loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(loc['k_s'], 1, self.k_s)
        GL.glUniform1f(loc['s'], max(self.s, 0.001))
        GL.glUniform3fv(loc['fog_colour'], 1, self.fog_colour.get_colour())
        # GL.glUniformMatrix4fv(loc['nit_matrix'], 1, True, nit_matrix)

        # ----------------
        # texture access setups
        # loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc['diffuseMap'], 0)
        self.vertex_array.execute(primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)


class TexturedPhongMeshSkinned:
    def __init__(self, shader, tex, attributes, faces,
                 bone_nodes, bone_offsets,
                 light_dir=None,  # directional light (in world coords)
                 k_a=(1, 1, 1), k_d=(1, 1, 0), k_s=(1, 1, 0), s=64.
                 ):
        # super().__init__(shader, tex, attributes, faces)

        # setup texture and upload it to GPU
        self.texture = tex
        self.vertex_array = VertexArray(attributes=attributes, index=faces)
        self.shader = shader
        self.fog_colour = FogColour()

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
        names = ['view', 'projection', 'model', 'nit_matrix', 'diffuseMap', 'k_a', 'k_d', 'k_s', 's',
                 'fog_colour', 'w_camera_position']
        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}

        # model3x3 = model[0:3, 0:3]
        # nit_matrix = np.linalg.inv(model3x3).T

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)

        GL.glUniform3fv(loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(loc['k_s'], 1, self.k_s)
        GL.glUniform1f(loc['s'], max(self.s, 0.001))
        GL.glUniform3fv(loc['fog_colour'], 1, self.fog_colour.get_colour())
        # GL.glUniformMatrix4fv(loc['nit_matrix'], 1, True, nit_matrix)

        # bone world transform matrices need to be passed for skinning
        for bone_id, node in enumerate(self.bone_nodes):
            bone_matrix = node.world_transform @ self.bone_offsets[bone_id]

            bone_loc = GL.glGetUniformLocation(self.shader.glid, 'bone_matrix[%d]' % bone_id)
            GL.glUniformMatrix4fv(bone_loc, len(self.bone_nodes), True, bone_matrix)

        # world camera position for Phong illumination specular component
        w_camera_position = np.linalg.inv(view)[:, 3]
        GL.glUniform3fv(loc['w_camera_position'], 1, w_camera_position)

        # ----------------
        # texture access setups
        # loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc['diffuseMap'], 0)
        self.vertex_array.execute(primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)