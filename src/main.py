#!/usr/bin/env python3
"""
Python OpenGL Medieval Project.
"""
# Python built-in modules
import os  # os function, i.e. checking file status
from itertools import cycle
import sys
from PIL import Image  # load images for textures

# External, non built-in modules
import OpenGL.GL as GL  # standard Python OpenGL wrapper
import glfw  # lean window system wrapper for OpenGL
import numpy as np  # all matrix manipulations & OpenGL args
import assimpcy  # 3D resource loader

from core import Shader, Viewer, Texture, Node, multi_load_textured, TexturedPlane, load_textured_phong_mesh, \
    TexturedPlaneFlat
from skybox import Skybox
import simpleaudio as sa

from transform import rotate, translate, scale

from transform import lerp, vec
from bisect import bisect_left  # search sorted keyframe lists

from transform import (quaternion_slerp, quaternion_matrix, quaternion,
                       quaternion_from_euler)


def build_houses(viewer, shader):
    # Farm empty - 1
    farm_node = Node(
        transform=translate(50, -1, 0) @ scale(0.5, 0.5, 0.5) @ rotate((1, 0, 0), -90))
    mesh_list = load_textured_phong_mesh("./../resources/farm/farm_empty.FBX", shader=shader,
                                         tex_file="./../resources/farm/farm_empty.jpg",
                                         k_a=(.7, .7, .7),
                                         k_d=(.6, .6, .6),
                                         k_s=(.1, .1, .1),
                                         s=4
                                         )
    for mesh in mesh_list:
        farm_node.add(mesh)

    # House - 1
    house_node = Node(
        transform=scale(0.5, 0.5, 0.5) @ rotate((0, 0, 1), -90))
    mesh_list = load_textured_phong_mesh("./../resources/house/big_house.FBX", shader=shader,
                                         tex_file="./../resources/house/big_house.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    # Add the house on top of empty farm (hierarchically)
    farm_node.add(house_node)
    viewer.add(farm_node)

    # Farm empty - 2
    farm_node = Node(
        transform=translate(50, -1, -35) @ scale(0.5, 0.5, 0.5) @ rotate((1, 0, 0), -90))
    mesh_list = load_textured_phong_mesh(file="./../resources/farm/farm_empty.FBX", shader=shader,
                                         tex_file="./../resources/farm/farm_empty.jpg",
                                         k_a=(.7, .7, .7),
                                         k_d=(.6, .6, .6),
                                         k_s=(.1, .1, .1),
                                         s=4
                                         )
    for mesh in mesh_list:
        farm_node.add(mesh)

    # House - 2
    house_node = Node(
        transform=scale(0.5, 0.5, 0.5) @ rotate((0, 0, 1), 0))
    mesh_list = load_textured_phong_mesh(file="./../resources/house/house_01.FBX", shader=shader,
                                         tex_file="./../resources/house/house_01.jpg",
                                         k_a=(.5, .5, .5),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        house_node.add(mesh)

    # Add the house on top of empty farm (hierarchically)
    farm_node.add(house_node)
    viewer.add(farm_node)

    # -------------------------------------------------
    # Farm - full
    # for i in range(0, 14, 7):
    #     for j in range(0, 14, 7):
    #         farm_node = Node(
    #             transform=translate(22 + i, -1, -14 + j) @ scale(0.1, 0.1, 0.1) @ rotate((1, 0, 0), -90) @ rotate(
    #                 (0, 0, 1),
    #                 270))
    #         mesh_list = load_textured("./../resources/farm/farm_full.FBX", shader=cube_shader,
    #                                   tex_file="./../resources/farm/farm_full.jpg")
    #         for mesh in mesh_list:
    #             farm_node.add(mesh)
    #         viewer.add(farm_node)

    # -------------------------------------------------


def build_nature(viewer, shader):
    # Rocks
    rock_node = Node(
        transform=translate(30, -1, -20) @ scale(0.1, 0.1, 0.1) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured_phong_mesh(file="./../resources/rock/rock_02.FBX", shader=shader,
                                         tex_file="./../resources/rock/mountain_rock.jpg",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        rock_node.add(mesh)
    viewer.add(rock_node)

    # Graveyard Grass
    graveyard_grass_node = Node(
        transform=translate(-60, -1, -20) @ scale(0.1, 0.1, 0.1))
    mesh_list = load_textured_phong_mesh(file="./../resources/graveyard/1/2/Demo_Scene.obj", shader=shader,
                                         tex_file="./../resources/graveyard/1/2/tex.png",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        graveyard_grass_node.add(mesh)
    viewer.add(graveyard_grass_node)

    # Graveyard Cross 1
    graveyard_cross1_node = Node(
        transform=translate(-60, -1, -20) @ scale(0.15, 0.15, 0.15) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured_phong_mesh(file="./../resources/graveyard/grave3.fbx", shader=shader,
                                         tex_file="./../resources/graveyard/pattern/Material_roughness.jpg",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        graveyard_cross1_node.add(mesh)
    viewer.add(graveyard_cross1_node)

    # Graveyard Cross 2
    graveyard_cross2_node = Node(
        transform=translate(-50, -1, -10) @ scale(0.2, 0.2, 0.2) @ rotate((0, 1, 0), -90))
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

    # House Tree 1
    # size = 0.3
    # tree_node = Node(
    #     transform=translate(30, -1, -14) @ scale(size, size, size) @ rotate((1, 0, 0), 0))
    # mesh_list = load_textured_phong_mesh(file="./../resources/tree/lowPolyTree.obj", shader=shader,
    #                             tex_file="./../resources/tree/lowPolyTree.png")
    # for mesh in mesh_list:
    #     tree_node.add(mesh)
    # viewer.add(tree_node)
    #
    # # House Tree 2
    # tree_node = Node(
    #     transform=translate(30, -1, -8) @ scale(size, size, size) @ rotate((0, 1, 0), 45))
    # mesh_list = load_textured_phong_mesh(file="./../resources/tree/lowPolyTree.obj", shader=shader,
    #                            tex_file="./../resources/tree/lowPolyTree.png")
    # for mesh in mesh_list:
    #     tree_node.add(mesh)
    # viewer.add(tree_node)

    # -------------------------------------------------
    # Very high poly tree
    # tex_list = ["./../resources/tree/nice_tree/leaf.png",
    #             "./../resources/tree/nice_tree/bark.jpg",
    #             "./../resources/tree/nice_tree/leaf.png",
    #             "./../resources/tree/nice_tree/leaf.png",
    #             ]
    # size_conetree = 0.02
    # tree_node = Node(
    #     transform=translate(-5, -1, -8) @ scale(size_conetree, size_conetree, size_conetree) @ rotate((0, 1, 0), 45))
    # mesh_list = multi_load_textured(file="./../resources/tree/nice_tree/nice_tree.obj", shader=shader,
    #                                      tex_file=tex_list)
    # for mesh in mesh_list:
    #     tree_node.add(mesh)
    # viewer.add(tree_node)
    # -------------------------------------------------
    # Pathway trees
    for i in range(-70, 100, 40):
        tree_node = Node(
            transform=translate(5, -1.5, i) @ scale(0.3, 0.3, 0.3) @ rotate((0, 1, 0), 45))
        mesh_list = load_textured_phong_mesh(file="./../resources/tree/lowPolyTree.obj", shader=shader,
                                             tex_file="./../resources/tree/lowPolyTree.png",
                                             k_a=(.5, .5, .5),
                                             k_d=(1, 1, 1),
                                             k_s=(.1, .1, .1),
                                             s=64
                                             )
        for mesh in mesh_list:
            tree_node.add(mesh)
        viewer.add(tree_node)

        tree_node = Node(
            transform=translate(-5, -1.5, i) @ scale(0.3, 0.3, 0.3) @ rotate((0, 1, 0), 45))
        mesh_list = load_textured_phong_mesh(file="./../resources/tree/lowPolyTree.obj", shader=shader,
                                             tex_file="./../resources/tree/lowPolyTree.png",
                                             k_a=(.4, .4, .4),
                                             k_d=(1.2, 1.2, 1.2),
                                             k_s=(.2, .2, .2),
                                             s=4
                                             )
        for mesh in mesh_list:
            tree_node.add(mesh)
        viewer.add(tree_node)


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
        mesh_list = load_textured_phong_mesh(file="./../resources/Cannon_3/low-poly-cannon.fbx", shader=shader,
                                             tex_file="./../resources/Cannon_3/Textures/plate.jpg",
                                             k_a=(.5, .5, .5),
                                             k_d=(1, 1, 1),
                                             k_s=(.1, .1, .1),
                                             s=64
                                             )

        for mesh in mesh_list:
            cannon_3_node.add(mesh)
        viewer.add(cannon_3_node)

    # Ground cannon (Cannon_3)
    tex_list2 = ["./../resources/Cannon_3/Textures/body_wood.jpg",
                 "./../resources/Cannon_3/Textures/body_wood.jpg",
                 "./../resources/Cannon_3/Textures/gun.jpg",
                 "./../resources/Cannon_3/Textures/metal.jpg",
                 "./../resources/Cannon_3/Textures/body_wood.jpg",
                 "./../resources/Cannon_3/Textures/body_wood.jpg"
                 ]
    for x_pos in [30, 15, -15, -30]:
        cannon_3_node = Node(
            transform=translate(x_pos, -1, 145) @ scale(3, 3, 3) @ rotate((0, 1, 0), 90))
        mesh_list = multi_load_textured(file="./../resources/Cannon_3/cannon_3.obj", shader=shader,
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
        mesh_list = load_textured_phong_mesh(file="./../resources/Cannon_1/cannon_2.obj", shader=shader,
                                             tex_file="./../resources/Cannon_1/cannon_1_texture.jpg",
                                             k_a=(.4, .4, .4),
                                             k_d=(1.2, 1.2, 1.2),
                                             k_s=(.2, .2, .2),
                                             s=4
                                             )
        for mesh in mesh_list:
            cannon_1_node.add(mesh)
        viewer.add(cannon_1_node)


def build_terrain(viewer, shader):
    # Grass
    grass_node = Node(transform=translate(-500, -1, -500) @ rotate((1, 0, 0), 0))
    plane = TexturedPlane("./../resources/grass.png", shader, size=1000,
                          hmap_file="./../resources/hmap_2_mounds_256px.png")
    grass_node.add(plane)
    viewer.add(grass_node)

    # TODO: Build road
    # width = 10
    # vertices = (
    #     np.array(((-width / 2, -160, 0), (width / 2, -160, 0), (width / 2, 80, 0), (-width / 2, 80, 0)), np.float32))
    # pavement_node = Node(transform=translate(0, -0.9, 0) @ rotate((1, 0, 0), -90))
    # plane = TexturedPlane("./../resources/stone_road.jpg", shader, size=2, vertices=vertices)
    # pavement_node.add(plane)
    # viewer.add(pavement_node)


def build_church(viewer, shader):
    # Church
    # light_dir = (-1, -1, -1)
    church_node = Node(
        transform=translate(-108.2, -1, -100) @ scale(0.3, 0.3, 0.3) @ rotate((0, 1, 0), 90) @ rotate((1, 0, 0), 270))
    church_mesh_list = load_textured_phong_mesh(file="./../resources/church/church.FBX", shader=shader,
                                                tex_file="./../resources/church/church_D.jpg",
                                                k_a=(1, 1, 1),
                                                k_d=(.6, .6, .6),
                                                k_s=(.1, .1, .1),
                                                s=4
                                                )
    for mesh in church_mesh_list:
        church_node.add(mesh)
    viewer.add(church_node)


class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""

    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
        keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # 1. ensure time is within bounds else return boundary keyframe
        if time <= self.times[0]:
            return self.values[0]
        elif time >= self.times[len(self.times) - 1]:
            return self.values[len(self.times) - 1]

        # 2. search for closest index entry in self.times, using bisect_left function
        index_closest = bisect_left(self.times, time)

        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        f = (time - self.times[index_closest - 1]) / (self.times[index_closest] - self.times[index_closest - 1])

        interpolated_val = self.interpolate(self.values[index_closest], self.values[index_closest - 1], f)
        return interpolated_val


class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """

    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.translate_keys = KeyFrames(translate_keys)
        self.rotate_keys = KeyFrames(rotate_keys, interpolation_function=quaternion_slerp)
        self.scale_keys = KeyFrames(scale_keys)

    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """
        T = translate(self.translate_keys.value(time=time))
        R = quaternion_matrix(self.rotate_keys.value(time=time))
        S = scale(self.scale_keys.value(time=time))
        return T @ R @ S


class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """

    def __init__(self, translate_keys, rotate_keys, scale_keys):
        super().__init__()
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform = self.keyframes.value(glfw.get_time())
        super().draw(projection, view, model)


def main():
    """ create a window, add scene objects, then run rendering loop """

    viewer = Viewer(width=1920, height=1080)
    terrain_shader = Shader("terrain.vert", "terrain.frag")
    cube_shader = Shader("texture.vert", "texture.frag")
    phong_shader = Shader("phong.vert", "phong.frag")
    # phong_shader2 = Shader("phong.vert", "phong.frag")
    # Simple cube
    # cube_node = Node(transform=scale(4, 4, 4) @ translate(0, 0.25, 0) @ rotate((0, 1, 0), 90))
    # mesh_list = load_textured("./../resources/cube/cube.obj", shader=cube_shader)
    # for mesh in mesh_list:
    #     cube_node.add(mesh)
    # viewer.add(cube_node)

    build_terrain(viewer, shader=terrain_shader)
    build_nature(viewer, shader=phong_shader)
    build_houses(viewer, shader=phong_shader)
    build_castle(viewer, shader=phong_shader)
    build_church(viewer, shader=phong_shader)

    # -------------------------------------------------
    # Archer
    # archer_node = Node(
    #     transform=translate(35, 0, 0) @ scale(0.02, 0.02, 0.02) @ rotate((0, 1, 0), -90) @ rotate((0, 0, 1), 0))
    # mesh_list = load_textured("./../resources/archer/archer_female.fbx", shader=cube_shader,
    #                           tex_file="./../resources/archer/archer_female.png")
    # for mesh in mesh_list:
    #     archer_node.add(mesh)
    # viewer.add(archer_node)

    # -------------------------------------------------

    # Skybox
    shader_skybox = Shader(vertex_source="./skybox.vert", fragment_source="./skybox.frag")
    viewer.add(Skybox(shader_skybox=shader_skybox))

    # Start playing ambient audio in background
    # wave_obj = sa.WaveObject.from_wave_file("./../resources/audio/amb_we_2.wav")
    # wave_obj.play()

    # Key Frame animation for Tower Cannon Ball (Cannon_1)
    translate_keys = {0: vec(0, 0, 1), 5: vec(0, 0, 1), 10: vec(0, 10, 1), 15: vec(0, 0, 1)}
    rotate_keys = {0: quaternion(), 2: quaternion_from_euler(180, 45, 90),
                   3: quaternion_from_euler(180, 0, 180), 4: quaternion()}
    scale_keys = {0: 2, 2: 2, 4: 2}
    cannon_ball_node = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    mesh_list = load_textured_phong_mesh(file="./../resources/Cannon_3/cannon_ball.obj", shader=phong_shader,
                                         tex_file="./../resources/Cannon_3/Textures/cannon.jpg",
                                         k_a=(.4, .4, .4),
                                         k_d=(1.2, 1.2, 1.2),
                                         k_s=(.2, .2, .2),
                                         s=4
                                         )
    for mesh in mesh_list:
        cannon_ball_node.add(mesh)
    viewer.add(cannon_ball_node)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()  # initialize window system glfw
    main()  # main function keeps variables locally scoped
    glfw.terminate()  # destroy all glfw windows and GL contexts
