# Python built-in modules
import os  # os function, i.e. checking file status
import glfw
import assimpcy
import numpy as np  # all matrix manipulations & OpenGL args
import random
import math

# External, non built-in modules
from mesh import TexturedPhongMesh, TexturedPhongMeshSkinned
from skinning import SkinningControlNode, MAX_VERTEX_BONES, MAX_BONES
from texture import Texture
from node import Node
from texturedplane import TexturedPlane
from keyframe import KeyFrameControlNode
from procedural_anime import ProceduralAnimation
from transform import quaternion, rotate, translate, scale, vec, quaternion_from_axis_angle


# --------------------------------------------------------
# Loader functions for loading different types of 3D objects
# (multi-textured, single textured, and skeletal-based)
# --------------------------------------------------------

def multi_load_textured(file, shader, tex_file, k_a, k_d, k_s, s):
    """ load resources from file using assimp, return list of TexturedMesh """
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_FlipUVs
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []
    # print("materials: ", scene.mNumMaterials)
    # Note: embedded textures not supported at the moment
    path = os.path.dirname(file) if os.path.dirname(file) != '' else './'
    for index, mat in enumerate(scene.mMaterials):
        if not tex_file and 'TEXTURE_BASE' in mat.properties:  # texture token
            name = os.path.basename(mat.properties['TEXTURE_BASE'])
            # search texture in file's whole subdir since path often screwed up
            paths = os.walk(path, followlinks=True)
            found = [os.path.join(d, f) for d, _, n in paths for f in n
                     if name.startswith(f) or f.startswith(name)]
            assert found, 'Cannot find texture %s in %s subtree' % (name, path)
            tex_file = found[0]
        if tex_file:
            # print("Index: ", index)
            mat.properties['diffuse_map'] = Texture(tex_file=tex_file[index])

    # prepare textured mesh
    meshes = []
    for mesh in scene.mMeshes:
        mat = scene.mMaterials[mesh.mMaterialIndex].properties
        assert mat['diffuse_map'], "Trying to map using a textureless material"
        attributes = [mesh.mVertices, mesh.mTextureCoords[0], mesh.mNormals]
        mesh = TexturedPhongMesh(shader, mat['diffuse_map'], attributes, mesh.mFaces,
                                 k_d=k_d, k_a=k_a, k_s=k_s, s=s)
        meshes.append(mesh)

    size = sum((mesh.mNumFaces for mesh in scene.mMeshes))
    # print('Loaded %s\t(%d meshes, %d faces)' % (file, len(meshes), size))
    return meshes


def load_textured_phong_mesh(file, shader, tex_file, k_a, k_d, k_s, s):
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_FlipUVs
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []

    # Note: embedded textures not supported at the moment
    path = os.path.dirname(file) if os.path.dirname(file) != '' else './'
    for mat in scene.mMaterials:
        if not tex_file and 'TEXTURE_BASE' in mat.properties:  # texture token
            name = os.path.basename(mat.properties['TEXTURE_BASE'])
            # search texture in file's whole subdir since path often screwed up
            paths = os.walk(path, followlinks=True)
            found = [os.path.join(d, f) for d, _, n in paths for f in n
                     if name.startswith(f) or f.startswith(name)]
            assert found, 'Cannot find texture %s in %s subtree' % (name, path)
            tex_file = found[0]
        if tex_file:
            mat.properties['diffuse_map'] = Texture(tex_file=tex_file)

    meshes = []
    for mesh in scene.mMeshes:
        mat = scene.mMaterials[mesh.mMaterialIndex].properties
        assert mat['diffuse_map'], "Trying to map using a textureless material"
        attributes = [mesh.mVertices, mesh.mTextureCoords[0], mesh.mNormals]
        mesh = TexturedPhongMesh(shader=shader, tex=mat['diffuse_map'], attributes=attributes,
                                 faces=mesh.mFaces,
                                 k_d=k_d, k_a=k_a, k_s=k_s, s=s)
        meshes.append(mesh)

        size = sum((mesh.mNumFaces for mesh in scene.mMeshes))
        # print('Loaded %s\t(%d meshes, %d faces)' % (file, len(meshes), size))
    return meshes


def load_textured_phong_mesh_skinned(file, shader, tex_file, k_a, k_d, k_s, s, delay=None):
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []
    # print("Materials: ", scene.mNumMaterials)
    # Note: embedded textures not supported at the moment
    path = os.path.dirname(file) if os.path.dirname(file) != '' else './'
    for mat in scene.mMaterials:
        if not tex_file and 'TEXTURE_BASE' in mat.properties:  # texture token
            name = os.path.basename(mat.properties['TEXTURE_BASE'])
            # search texture in file's whole subdir since path often screwed up
            paths = os.walk(path, followlinks=True)
            found = [os.path.join(d, f) for d, _, n in paths for f in n
                     if name.startswith(f) or f.startswith(name)]
            assert found, 'Cannot find texture %s in %s subtree' % (name, path)
            tex_file = found[0]
        if tex_file:
            mat.properties['diffuse_map'] = Texture(tex_file=tex_file)

    # ----- load animations
    def conv(assimp_keys, ticks_per_second):
        """ Conversion from assimp key struct to our dict representation """
        return {key.mTime / ticks_per_second: key.mValue for key in assimp_keys}

    # load first animation in scene file (could be a loop over all animations)
    transform_keyframes = {}
    if scene.mAnimations:
        anim = scene.mAnimations[0]
        for channel in anim.mChannels:
            # for each animation bone, store TRS dict with {times: transforms}
            transform_keyframes[channel.mNodeName] = (
                conv(channel.mPositionKeys, anim.mTicksPerSecond),
                conv(channel.mRotationKeys, anim.mTicksPerSecond),
                conv(channel.mScalingKeys, anim.mTicksPerSecond)
            )

    # ---- prepare scene graph nodes
    # create SkinningControlNode for each assimp node.
    # node creation needs to happen first as SkinnedMeshes store an array of
    # these nodes that represent their bone transforms
    nodes = {}  # nodes name -> node lookup
    nodes_per_mesh_id = [[] for _ in scene.mMeshes]  # nodes holding a mesh_id

    def make_nodes(assimp_node):
        """ Recursively builds nodes for our graph, matching assimp nodes """
        trs_keyframes = transform_keyframes.get(assimp_node.mName, (None,))
        skin_node = SkinningControlNode(*trs_keyframes,
                                        transform=assimp_node.mTransformation, delay=delay)
        nodes[assimp_node.mName] = skin_node
        for mesh_index in assimp_node.mMeshes:
            nodes_per_mesh_id[mesh_index].append(skin_node)
        skin_node.add(*(make_nodes(child) for child in assimp_node.mChildren))
        return skin_node

    root_node = make_nodes(scene.mRootNode)

    # ---- create SkinnedMesh objects
    for mesh_id, mesh in enumerate(scene.mMeshes):
        # -- skinned mesh: weights given per bone => convert per vertex for GPU
        # first, populate an array with MAX_BONES entries per vertex
        v_bone = np.array([[(0, 0)] * MAX_BONES] * mesh.mNumVertices,
                          dtype=[('weight', 'f4'), ('id', 'u4')])
        for bone_id, bone in enumerate(mesh.mBones[:MAX_BONES]):
            for entry in bone.mWeights:  # weight,id pairs necessary for sorting
                v_bone[entry.mVertexId][bone_id] = (entry.mWeight, bone_id)

        v_bone.sort(order='weight')  # sort rows, high weights last
        v_bone = v_bone[:, -MAX_VERTEX_BONES:]  # limit bone size, keep highest

        # prepare bone lookup array & offset matrix, indexed by bone index (id)
        bone_nodes = [nodes[bone.mName] for bone in mesh.mBones]
        bone_offsets = [bone.mOffsetMatrix for bone in mesh.mBones]

        # Initialize mat for phong and texture
        # mat = scene.mMaterials[mesh.mMaterialIndex].properties
        # assert mat['diffuse_map'], "Trying to map using a textureless material"

    # meshes = []
    for mesh in scene.mMeshes:
        mat = scene.mMaterials[mesh.mMaterialIndex].properties
        assert mat['diffuse_map'], "Trying to map using a textureless material"
        attributes = [mesh.mVertices, mesh.mTextureCoords[0], mesh.mNormals, v_bone['id'], v_bone['weight']]
        mesh = TexturedPhongMeshSkinned(shader=shader, tex=mat['diffuse_map'], attributes=attributes,
                                        faces=mesh.mFaces, bone_nodes=bone_nodes, bone_offsets=bone_offsets,
                                        k_d=k_d, k_a=k_a, k_s=k_s, s=s)
        # meshes.append(mesh)

        for node in nodes_per_mesh_id[mesh_id]:
            node.add(mesh)

        nb_triangles = sum((mesh.mNumFaces for mesh in scene.mMeshes))
        # print('Loaded', file, '\t(%d meshes, %d faces, %d nodes, %d animations)' % (
        #     scene.mNumMeshes, nb_triangles, len(nodes), scene.mNumAnimations))

    return [root_node]


# --------------------------------------------------------
# Builder functions
# Utility functions calling the loader functions
# --------------------------------------------------------

def build_houses(viewer, shader, lamb_shader):
    # Hierarchical modelling for just the first house
    # Hierarchy contains house, a tree and 3 bushes as a single entity
    house_master_node = Node()
    # House - 1
    house_node = Node(
        transform=translate(28, -1, 30) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), -180))
    mesh_list = load_textured_phong_mesh("./../resources/house/big_house.FBX", shader=shader,
                                         tex_file="./../resources/house/big_house.jpg",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    house_master_node.add(house_node)

    bush_node = Node(transform=translate(14, -1, 0) @ scale(2.5, 2.5, 2.5))
    for bush_pos in [7, 10, 13]:
        bush = Node(
            transform=translate(0, 0, bush_pos) @ scale(1, 1, 1) @ rotate((1, 0, 0), -90))
        mesh_list = load_textured_phong_mesh("./../resources/nature/BushBerries_2.fbx", shader=shader,
                                             tex_file="./../resources/nature/leaves_256px.jpg",
                                             k_a=(.1, .5, .1),
                                             k_d=(3, 3, 3),
                                             k_s=(1, 1, 1),
                                             s=4
                                             )
        for mesh in mesh_list:
            bush.add(mesh)

        bush_node.add(bush)

    house_master_node.add(bush_node)

    tex_list = ["./../resources/nature/tree/CommonTree/bark_decidious.jpg",
                "./../resources/nature/tree/CommonTree/leaves_256px.jpg",
                "./../resources/nature/tree/CommonTree/leaves_256px.jpg"]

    tree_node = Node(
        transform=translate(35, -1, 15) @ scale(3, 3, 3) @ rotate((1, 0, 0), -90))
    mesh_list = multi_load_textured(file="./../resources/nature/tree/CommonTree/CommonTree_4.fbx", shader=lamb_shader,
                                    tex_file=tex_list,
                                    k_a=(.4, .4, .4),
                                    k_d=(1.2, 1.2, 1.2),
                                    k_s=(.2, .2, .2),
                                    s=4
                                    )
    for mesh in mesh_list:
        tree_node.add(mesh)

    house_master_node.add(tree_node)
    viewer.add(house_master_node)

    house_node = Node(
        transform=translate(65, -1, 32) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 0))
    mesh_list = load_textured_phong_mesh("./../resources/house/house_02.FBX", shader=shader,
                                         tex_file="./../resources/house/house_02_D.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)

    house_node = Node(
        transform=translate(72, -7, 35) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), -90))
    mesh_list = load_textured_phong_mesh("./../resources/house/ambar.FBX", shader=shader,
                                         tex_file="./../resources/house/ambar.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)

    # House - 2
    house_node = Node(
        transform=translate(28, -1, 48) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), -180))
    mesh_list = load_textured_phong_mesh("./../resources/house/house_01.FBX", shader=shader,
                                         tex_file="./../resources/house/house_01.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)

    house_node = Node(
        transform=translate(55, -1, 46) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 0))
    mesh_list = load_textured_phong_mesh("./../resources/house/big_house.FBX", shader=shader,
                                         tex_file="./../resources/house/big_house.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)

    house_node = Node(
        transform=translate(80, -1, 46) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 180))
    mesh_list = load_textured_phong_mesh("./../resources/house/house_02.FBX", shader=shader,
                                         tex_file="./../resources/house/house_02_D.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)

    # --------
    house_node = Node(
        transform=translate(28, -1, 80) @ scale(0.20, 0.20, 0.20) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), -90))
    mesh_list = load_textured_phong_mesh("./../resources/house/house_2.FBX", shader=shader,
                                         tex_file="./../resources/house/house_2.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)
    # -----------------------------------------------------------------------------
    # Buildings near church

    # House - 2
    house_node = Node(
        transform=translate(24, -1, -28) @ scale(0.25, 0.25, 0.25) @ rotate((1, 0, 0), -90))
    mesh_list = load_textured_phong_mesh(file="./../resources/house/house_01.FBX", shader=shader,
                                         tex_file="./../resources/house/house_01.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    viewer.add(house_node)


def build_graveyard(viewer, shader):
    # Graveyard Full scene
    graveyard_grass_node = Node(
        transform=translate(-60, -1, -60) @ scale(0.07, 0.07, 0.07) @ rotate((0, 1, 0), angle=-120))
    mesh_list = load_textured_phong_mesh(file="./../resources/graveyard/graveyardpack/Demo_Scene.obj", shader=shader,
                                         tex_file="./../resources/graveyard/graveyardpack/tex.png",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        graveyard_grass_node.add(mesh)
    viewer.add(graveyard_grass_node)

    # Graveyard Cross 2
    for grave_pos in [-25, -15, -5]:
        graveyard_cross2_node = Node(
            transform=translate(-60, -1, grave_pos) @ scale(0.2, 0.2, 0.2) @ rotate((0, 1, 0), -90))
        mesh_list = load_textured_phong_mesh(file="./../resources/graveyard/grave4.obj", shader=shader,
                                             tex_file="./../resources/graveyard/pattern/Material_roughness.jpg",
                                             k_a=(.4, .4, .4),
                                             k_d=(1.2, 1.2, 1.2),
                                             k_s=(.2, .2, .2),
                                             s=4
                                             )
        for mesh in mesh_list:
            graveyard_cross2_node.add(mesh)
        viewer.add(graveyard_cross2_node)

    # Angel of Death
    angelofdeath_node = Node(
        transform=translate(-90, -1, -10) @ scale(0.06, 0.06, 0.06) @ rotate((0, 1, 0), 90))
    mesh_list = load_textured_phong_mesh(
        file="./../resources/graveyard/Angel/Angelofdeath/angelofdeath_dec_reduced.obj", shader=shader,
        tex_file="./../resources/cannon/Cannon_3/Textures/metal.jpg",
        k_a=(.4, .4, .4),
        k_d=(1.2, 1.2, 1.2),
        k_s=(.2, .2, .2),
        s=4
    )

    for mesh in mesh_list:
        angelofdeath_node.add(mesh)
    viewer.add(angelofdeath_node)


def build_tree(viewer, shader):
    # Pathway trees
    tex_list = ["./../resources/nature/tree/CommonTree/bark_decidious.jpg",
                "./../resources/nature/tree/CommonTree/leaves_256px.jpg"]
    tree_size = 4.0
    for i in range(-70, 100, 40):
        tree_node = Node(
            transform=translate(10, -1, i) @ scale(tree_size, tree_size, tree_size) @ rotate((1, 0, 0), -90))
        mesh_list = multi_load_textured(file="./../resources/nature/tree/CommonTree/CommonTree_1.fbx", shader=shader,
                                        tex_file=tex_list,
                                        k_a=(.4, .4, .4),
                                        k_d=(1.2, 1.2, 1.2),
                                        k_s=(.2, .2, .2),
                                        s=4
                                        )
        for mesh in mesh_list:
            tree_node.add(mesh)
        viewer.add(tree_node)

        tree_node = Node(
            transform=translate(-10, -1, i) @ scale(tree_size, tree_size, tree_size) @ rotate((1, 0, 0), -90))
        mesh_list = multi_load_textured(file="./../resources/nature/tree/CommonTree/CommonTree_1.fbx", shader=shader,
                                        tex_file=tex_list,
                                        k_a=(.4, .4, .4),
                                        k_d=(1.2, 1.2, 1.2),
                                        k_s=(.2, .2, .2),
                                        s=4
                                        )
        for mesh in mesh_list:
            tree_node.add(mesh)
        viewer.add(tree_node)

    # Rocks
    rock_node = Node(
        transform=translate(20, -1, -15) @ scale(0.1, 0.1, 0.1) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured_phong_mesh(file="./../resources/nature/rock/rock_02.FBX", shader=shader,
                                         tex_file="./../resources/nature/rock/mountain_rock.jpg",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        rock_node.add(mesh)
    viewer.add(rock_node)


def build_castle(viewer, shader):
    # Castle
    # Load castle's multiple textures one by one
    tex_list = ["./../resources/castle/Texture/Castle Exterior Texture.jpg",
                "./../resources/castle/Texture/Towers Doors and Windows Texture.jpg",
                "./../resources/castle/Texture/Ground and Fountain Texture.jpg",
                "./../resources/castle/Texture/Castle Interior Texture.jpg"]
    castle_node = Node(transform=translate(0, -1.7, 200) @ scale(2.0, 2.0, 2.0) @ rotate((0, 1, 0), 180))
    castle_mesh_list = multi_load_textured(file="./../resources/castle/castle_cull_fixed.fbx", shader=shader,
                                           tex_file=tex_list,
                                           k_a=(.5, .5, .5),
                                           k_d=(1, 1, 1),
                                           k_s=(.1, .1, .1),
                                           s=64
                                           )
    for mesh in castle_mesh_list:
        castle_node.add(mesh)
    viewer.add(castle_node)

    # Wall cannon (low poly cannon)
    for x_pos in [29.4, 17.9, 6.7, -4.5, -15.6, -27]:
        cannon_3_node = Node(
            transform=translate(x_pos, 16, 158) @ scale(.03, .03, .03) @ rotate((0, 1, 0), 180))
        mesh_list = load_textured_phong_mesh(file="./../resources/cannon/Cannon_3/low-poly-cannon.fbx", shader=shader,
                                             tex_file="./../resources/cannon/Cannon_3/Textures/plate.jpg",
                                             k_a=(.5, .5, .5),
                                             k_d=(1, 1, 1),
                                             k_s=(.1, .1, .1),
                                             s=64
                                             )

        for mesh in mesh_list:
            cannon_3_node.add(mesh)
        viewer.add(cannon_3_node)

    # Ground cannon (Cannon_3)
    tex_list2 = ["./../resources/cannon/Cannon_3/Textures/body_wood.jpg",
                 "./../resources/cannon/Cannon_3/Textures/body_wood.jpg",
                 "./../resources/cannon/Cannon_3/Textures/gun.jpg",
                 "./../resources/cannon/Cannon_3/Textures/metal.jpg",
                 "./../resources/cannon/Cannon_3/Textures/body_wood.jpg",
                 "./../resources/cannon/Cannon_3/Textures/body_wood.jpg"
                 ]
    for x_pos in [30, 15, -15, -30]:
        cannon_3_node = Node(
            transform=translate(x_pos, -1, 145) @ scale(3, 3, 3) @ rotate((0, 1, 0), 90))
        mesh_list = multi_load_textured(file="./../resources/cannon/Cannon_3/cannon_3_reduced.obj", shader=shader,
                                        tex_file=tex_list2,
                                        k_a=(.5, .5, .5),
                                        k_d=(1, 1, 1),
                                        k_s=(.1, .1, .1),
                                        s=64
                                        )

        for mesh in mesh_list:
            cannon_3_node.add(mesh)
        viewer.add(cannon_3_node)

    # Tower Cannon (Cannon_1)
    for x_pos in [46, -45]:
        cannon_1_node = Node(
            transform=translate(x_pos, 17, 151) @ scale(1, 1, 1) @ rotate((0, 1, 0), 180))
        mesh_list = load_textured_phong_mesh(file="./../resources/cannon/Cannon_1/cannon_2.obj", shader=shader,
                                             tex_file="./../resources/cannon/Cannon_1/cannon_1_texture.jpg",
                                             k_a=(.4, .4, .4),
                                             k_d=(1.2, 1.2, 1.2),
                                             k_s=(.2, .2, .2),
                                             s=4
                                             )
        for mesh in mesh_list:
            cannon_1_node.add(mesh)
        viewer.add(cannon_1_node)


def build_terrain(viewer, shader):
    # Grass, pavement and soil

    background_texture_file = "./../resources/textures/grass.png"
    road_texture_file = "./../resources/textures/pavement-texture.jpg"
    road2_texture_file = "./../resources/textures/fertile-loam-soil.jpg"
    blendmap_file = "./../resources/map/blend_map_t_point_local_road.png"

    grass_node = Node(transform=translate(-500, -1, -500) @ rotate((1, 0, 0), 0))
    plane = TexturedPlane(background_texture_file, road_texture_file, road2_texture_file,
                          blendmap_file, shader, size=1000,
                          hmap_file="./../resources/map/hmap_2_mounds_256px.png")
    grass_node.add(plane)
    viewer.add(grass_node)


def build_church(viewer, shader):
    # Church
    church_node = Node(
        transform=translate(-108.2, -1, -100) @ scale(0.3, 0.3, 0.3) @ rotate((0, 1, 0), 90) @ rotate((1, 0, 0), 270))
    church_mesh_list = load_textured_phong_mesh(file="./../resources/church/church.FBX", shader=shader,
                                                tex_file="./../resources/church/church_D.jpg",
                                                k_a=(.5, .5, .5),
                                                k_d=(1.2, 1.2, 1.2),
                                                k_s=(.2, .2, .2),
                                                s=4
                                                )
    for mesh in church_mesh_list:
        church_node.add(mesh)
    viewer.add(church_node)


def add_characters(viewer, shader):
    # Archer
    # keyframe_archer_node = KeyFrameControlNode(
    #     translate_keys={0: vec(0, 0, 0), 1: vec(0, 0, 0)},
    #     rotate_keys={0: quaternion(), 1: quaternion()},
    #     scale_keys={0: 1, 1: 1},
    #     loop=True
    # )
    # size = 0.015
    # archer_node = Node(
    #     transform=translate(35, 0, 0) @ scale(size, size, size) @ rotate((0, 1, 0), -90))
    # mesh_list = load_textured_phong_mesh_skinned("./../resources/characters/archer/archer_standing.FBX", shader=shader,
    #                                              tex_file="./../resources/characters/archer/archer.tga",
    #                                              k_a=(1, 1, 1),
    #                                              k_d=(.6, .6, .6),
    #                                              k_s=(.1, .1, .1),
    #                                              s=4, delay=0.5
    #                                              )
    #
    # for mesh in mesh_list:
    #     archer_node.add(mesh)
    # keyframe_archer_node.add(archer_node)
    # viewer.add(keyframe_archer_node)

    # Farmer
    keyframe_farmer_node = KeyFrameControlNode(
        translate_keys={60: vec(0, -1, -5), 30: vec(100, -1, -5), 0: vec(0, -1, -5)},
        rotate_keys={60: quaternion_from_axis_angle(axis=(0, 1, 0), degrees=180),
                     30.001: quaternion_from_axis_angle(axis=(0, 1, 0), degrees=180),
                     30: quaternion(),
                     0: quaternion()},
        scale_keys={60: 1, 0: 1},
        loop=True
    )
    size = 0.05
    farmer_node = Node(
        transform=translate(0, 0, 0) @ scale(size, size, size) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), -90))
    mesh_list = load_textured_phong_mesh_skinned("./../resources/characters/farmer/farmer.FBX", shader=shader,
                                                 tex_file="./../resources/characters/farmer/texture_01.jpg",
                                                 k_a=(.4, .4, .4),
                                                 k_d=(.6, .6, .6),
                                                 k_s=(.1, .1, .1),
                                                 s=4, delay=1.0
                                                 )

    for mesh in mesh_list:
        farmer_node.add(mesh)
    keyframe_farmer_node.add(farmer_node)
    viewer.add(keyframe_farmer_node)

    # Templar
    keyframe_templar_node = KeyFrameControlNode(
        translate_keys={60: vec(0, -1, 30), 30: vec(0, -1, -70), 0: vec(0, -1, 30)},
        rotate_keys={60: quaternion_from_axis_angle(axis=(0, 1, 0), degrees=180),
                     30.001: quaternion_from_axis_angle(axis=(0, 1, 0), degrees=180),
                     30: quaternion(),
                     0: quaternion()},
        scale_keys={60: 1, 0: 1},
        loop=True
    )
    size = 0.05
    templar_node = Node(
        transform=translate(0, 0, 0) @ scale(size, size, size) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 0))
    mesh_list = load_textured_phong_mesh_skinned("./../resources/characters/farmer/farmer.FBX", shader=shader,
                                                 tex_file="./../resources/characters/farmer/cahracter_templar.jpg",
                                                 k_a=(.4, .4, .4),
                                                 k_d=(1.2, 1.2, 1.2),
                                                 k_s=(.2, .2, .2),
                                                 s=4, delay=1.0
                                                 )

    for mesh in mesh_list:
        templar_node.add(mesh)
    keyframe_templar_node.add(templar_node)
    viewer.add(keyframe_templar_node)


def add_animations(viewer, shader):
    # Key Frame animation for Tower Cannon Ball (Cannon_1)
    translate_keys = {0: vec(-48, 0, 30), 4: vec(-48, 19, 148)}
    rotate_keys = {0: quaternion(), 4: quaternion()}
    scale_keys = {0: 2, 4: 2}
    cannon_ball_node = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    mesh_list = load_textured_phong_mesh(file="./../resources/cannon/Cannon_3/cannon_ball.obj", shader=shader,
                                         tex_file="./../resources/cannon/Cannon_3/Textures/cannon.jpg",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        cannon_ball_node.add(mesh)
    viewer.add(cannon_ball_node)

    def circular_motion(r=30, x_offset=0, y_offset=0, z_offset=0, direction=0):
        speed = 10
        angle = (glfw.get_time() * speed) % 360

        # Reverse the direction of rotation
        if direction == 1:
            rev_angle = 360 - angle
            angle = rev_angle
        x = x_offset + (r * math.cos(math.radians(angle)))
        y = y_offset + (np.absolute(10 * math.sin(math.radians(angle))))
        z = z_offset + (r * math.sin(math.radians(angle)))
        transformation = translate(x, y, z) @ rotate((0, 1, 0), angle)
        return transformation

    # Bird
    for i in range(5):
        radius = int(random.randrange(start=10, stop=100, step=10))
        x_offset = int(random.randrange(start=10, stop=50, step=5))
        y_offset = int(random.randrange(start=0, stop=10, step=2))
        z_offset = int(random.randrange(start=10, stop=50, step=5))
        direction = int(random.randrange(start=0, stop=2, step=1))

        bird_node = ProceduralAnimation(circular_motion,
                                        radius=radius,
                                        x_offset=x_offset,
                                        y_offset=y_offset,
                                        z_offset=z_offset,
                                        direction=direction)
        mesh_list = load_textured_phong_mesh(file="./../resources/bird/Bird_2.obj", shader=shader,
                                             tex_file="./../resources/bird/black.jpg",
                                             k_a=(.4, .4, .4),
                                             k_d=(1.2, 1.2, 1.2),
                                             k_s=(.2, .2, .2),
                                             s=4
                                             )
        for mesh in mesh_list:
            bird_node.add(mesh)
        viewer.add(bird_node)


def add_lamps(viewer, shader):
    # Lamp 1
    lamp_node = Node(
        transform=translate(10, -1, -10) @ scale(0.7, 0.7, 0.7))
    lamp_mesh_list = load_textured_phong_mesh(file="./../resources/lamp/lamp_ThinMatrix.obj", shader=shader,
                                              tex_file="./../resources/lamp/lamp_ThinMatrix_bnw.jpeg",
                                              k_a=(.1, .1, .1),
                                              k_d=(5, 5, 5),
                                              k_s=(.1, .1, .1),
                                              s=2
                                              )
    for mesh in lamp_mesh_list:
        lamp_node.add(mesh)
    viewer.add(lamp_node)

    # Lamp 2
    lamp_node = Node(
        transform=translate(15, -1, 55) @ scale(0.7, 0.7, 0.7))
    lamp_mesh_list = load_textured_phong_mesh(file="./../resources/lamp/lamp_ThinMatrix.obj", shader=shader,
                                              tex_file="./../resources/lamp/lamp_ThinMatrix_bnw.jpeg",
                                              k_a=(.1, .1, .1),
                                              k_d=(5, 5, 5),
                                              k_s=(.1, .1, .1),
                                              s=2
                                              )
    for mesh in lamp_mesh_list:
        lamp_node.add(mesh)
    viewer.add(lamp_node)

    # Graveyard lamp
    lamp_node = Node(
        transform=translate(-60, -1, -30) @ scale(0.7, 0.7, 0.7))
    lamp_mesh_list = load_textured_phong_mesh(file="./../resources/lamp/lamp_ThinMatrix.obj", shader=shader,
                                              tex_file="./../resources/lamp/lamp_ThinMatrix_bnw.jpeg",
                                              k_a=(.1, .1, .1),
                                              k_d=(5, 5, 5),
                                              k_s=(.1, .1, .1),
                                              s=2
                                              )
    for mesh in lamp_mesh_list:
        lamp_node.add(mesh)
    viewer.add(lamp_node)
