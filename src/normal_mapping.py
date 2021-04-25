from math import fabs

import numpy as np
import glfw
import OpenGL.GL as GL
import assimpcy
import glm

from texture import Texture
from vertexarray import VertexArray

from objLoader import objLoader


class NormalMapping:
    def __init__(self, shader, attributes, faces, k_a, k_d, k_s, s, tex_file, normal_tex_file):
        self.diffuse_texture = tex_file
        self.normal_texture = normal_tex_file
        self.shader = shader

        self.vertex_array = VertexArray(attributes=attributes, index=faces)

        self.k_a = k_a
        self.k_d = k_d
        self.k_s = k_s
        self.s = s
        # ----------------

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        names = ['MVP', 'V', 'M', 'MV3x3', 'P',
                 'DiffuseTextureSampler', 'NormalTextureSampler', 'LightPosition_worldspace',
                 'k_a', 'k_d', 'k_s', 's']
        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}

        ProjectionMatrix = projection
        ViewMatrix = view
        # ModelMatrix = np.identity(4)
        ModelMatrix = model
        ModelViewMatrix = ViewMatrix * ModelMatrix
        ModelView3x3Matrix = ModelViewMatrix[0:3, 0:3]
        # print(ModelView3x3Matrix)
        MVP = ProjectionMatrix * ViewMatrix * ModelMatrix
        light_dir = (-1, -1, -1)

        GL.glUniformMatrix4fv(loc['MVP'], 1, GL.GL_FALSE, MVP)
        GL.glUniformMatrix4fv(loc['M'], 1, GL.GL_FALSE, ModelMatrix)
        GL.glUniformMatrix4fv(loc['V'], 1, GL.GL_FALSE, ViewMatrix)
        GL.glUniformMatrix4fv(loc['P'], 1, GL.GL_FALSE, ProjectionMatrix)
        GL.glUniformMatrix3fv(loc['MV3x3'], 1, GL.GL_FALSE, ModelView3x3Matrix)

        GL.glUniform3fv(loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(loc['k_s'], 1, self.k_s)
        GL.glUniform1f(loc['s'], max(self.s, 0.001))
        GL.glUniform3fv(loc['LightPosition_worldspace'], 1, light_dir)
        # GL.glUniform3fv(loc['fog_colour'], 1, self.fog_colour.get_colour())

        # ----------------
        # texture access setups
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.diffuse_texture.glid)
        GL.glUniform1i(loc['DiffuseTextureSampler'], 0)

        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.normal_texture.glid)
        GL.glUniform1i(loc['NormalTextureSampler'], 1)

        self.vertex_array.execute(primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)


# --------------------------------------------------------------------------------


def load_textured_phong_mesh_normal_mapped(file, tex_file, normal_tex_file, shader, k_a, k_d, k_s, s):
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_FlipUVs
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []

    # Note: embedded textures not supported at the moment
    # for mat in scene.mMaterials:
    #     if tex_file:
    diffuse_texture = Texture(tex_file=tex_file)
    normal_texture = Texture(tex_file=normal_tex_file)

    # Extract vertices, texture coordinates, and normals from the meshes
    vertices_list = []
    tex_coords_list = []
    normals_list = []
    face_list = []
    for mesh in scene.mMeshes:
        vertices_list.append(mesh.mVertices)
        tex_coords_list.append(mesh.mTextureCoords[0])
        normals_list.append(mesh.mNormals)
        face_list.append(mesh.mFaces)

    # Compute the tangent and bitangents
    # vertex = vertices_list
    # uv = tex_coords_list
    # normal = normals_list
    # print(vertices_list)
    tangents_o = []
    bitangents_o = []
    # print(len(vertex))

    model = objLoader(file).to_array_style()
    vertex = model.vertexs
    uv = model.texcoords
    normal = model.normals

    for idx in range(0, int(len(vertex) / 9)):
        offset = idx * 9
        v0 = vertex[offset:offset + 3]
        v1 = vertex[offset + 3:offset + 6]
        v2 = vertex[offset + 6:offset + 9]

        offset = idx * 6
        uv0 = uv[offset:offset + 2]
        uv1 = uv[offset + 2:offset + 4]
        uv2 = uv[offset + 4:offset + 6]
        # print v0,v1,v2
        deltaPos1 = np.array([v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]])
        deltaPos2 = np.array([v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]])

        deltaUV1 = np.array([uv1[0] - uv0[0], uv1[1] - uv0[1]])
        deltaUV2 = np.array([uv2[0] - uv0[0], uv2[1] - uv0[1]])

        r = 1.0 / (deltaUV1[0] * deltaUV2[1] - deltaUV1[1] * deltaUV2[0])
        tangent = (deltaPos1 * deltaUV2[1] - deltaPos2 * deltaUV1[1]) * r
        bitangent = (deltaPos2 * deltaUV1[0] - deltaPos1 * deltaUV2[0]) * r

        tangents_o.append([tangent[0], tangent[1], tangent[2]])
        tangents_o.append([tangent[0], tangent[1], tangent[2]])
        tangents_o.append([tangent[0], tangent[1], tangent[2]])
        # tangents_o.extend([tangent.x, tangent.y, tangent.z])
        # tangents_o.extend([tangent.x, tangent.y, tangent.z])

        bitangents_o.append([bitangent[0], bitangent[1], bitangent[2]])
        bitangents_o.append([bitangent[0], bitangent[1], bitangent[2]])
        bitangents_o.append([bitangent[0], bitangent[1], bitangent[2]])
        # bitangents_o.extend([bitangent.x, bitangent.y, bitangent.z])
        # bitangents_o.extend([bitangent.x, bitangent.y, bitangent.z])

    # Index VBO, so as to find similar vertices and not use its tangent and bitangent
    indices, vertexs, texcoords, normals, tangents, bitangents = \
        indexVBO_TBN(vertex=vertex, uv=uv, normal=normal,
                     tangents=tangents_o, bitangents=bitangents_o)

    # print(len(vertexs))
    # print(len(texcoords))
    # print(len(normals))
    # print(len(tangents))
    # print(len(bitangents))
    vertexs = np.array(vertexs).reshape(-1, 3)
    texcoords = np.array(texcoords).reshape(-1, 2)
    normals = np.array(normals).reshape(-1, 3)
    tangents = np.array(tangents).reshape(-1, 3)
    bitangents = np.array(bitangents).reshape(-1, 3)

    print(vertexs.shape)
    print(texcoords.shape)
    print(normals.shape)
    print(tangents.shape)
    print(bitangents.shape)

    # exit(-1)
    # Prepare list of attributes to be sent to the class' constructor
    for mesh in scene.mMeshes:
        faces = mesh.mFaces
    meshes = []
    attributes = [vertexs, texcoords, normals, tangents, bitangents]
    mesh = NormalMapping(shader=shader, attributes=attributes,
                         k_a=k_a, k_d=k_d, k_s=k_s, s=s,
                         tex_file=diffuse_texture, normal_tex_file=normal_texture,
                         faces=faces)
    meshes.append(mesh)
    size = sum((mesh.mNumFaces for mesh in scene.mMeshes))
    print('Loaded %s\t(%d meshes, %d faces)' % (file, len(meshes), size))
    return meshes


def indexVBO_TBN(vertex, uv, normal, tangents, bitangents):

    indices = []
    out_vertexs = []
    out_uvs = []
    out_normals = []
    out_tangents = []
    out_bitangents = []
    newindex = 0

    def getSimilarVertexIndex(in_vertex, in_uv, in_normal, vertex_list, uv_list, normal_list):

        def is_near(v1, v2):
            return fabs(v1 - v2) < 0.01

        for idx in range(0, int(len(vertex_list) / 3)):
            vertex_in_list = vertex_list[idx * 3:idx * 3 + 3]
            uv_in_list = uv_list[idx * 2:idx * 2 + 2]
            normal_in_list = normal_list[idx * 3:idx * 3 + 3]

            if (is_near(in_vertex[0], vertex_in_list[0]) &
                    is_near(in_vertex[1], vertex_in_list[1]) &
                    is_near(in_vertex[2], vertex_in_list[2]) &
                    is_near(in_uv[0], uv_in_list[0]) &
                    is_near(in_uv[1], uv_in_list[1]) &
                    is_near(in_normal[0], normal_in_list[0]) &
                    is_near(in_normal[1], normal_in_list[1]) &
                    is_near(in_normal[2], normal_in_list[2])):
                return True, idx

        return False, 0

    for idx in range(0, int(len(vertex) / 3)):
        current_v = vertex[idx * 3:idx * 3 + 3]
        current_uv = uv[idx * 2:idx * 2 + 2]
        current_normal = normal[idx * 3:idx * 3 + 3]

        found, idx_found = getSimilarVertexIndex(current_v, current_uv, current_normal, out_vertexs, out_uvs,
                                                 out_normals)
        if found:
            indices.append(idx_found)
        else:
            indices.append(newindex)
            out_vertexs = out_vertexs + current_v
            out_uvs = out_uvs + current_uv
            out_normals = normal + current_normal
            out_tangents = out_tangents + tangents[idx * 3:idx * 3 + 3]
            out_bitangents = out_bitangents + bitangents[idx * 3:idx * 3 + 3]
            newindex += 1

    indices = indices
    vertexs = out_vertexs
    texcoords = out_uvs
    normals = out_normals
    tangents = out_tangents
    bitangents = out_bitangents

    return indices, vertexs, texcoords, normals, tangents, bitangents
