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

from core import Shader, Viewer, load_textured, Node, multi_load_textured, TexturedPlane
from skybox import Skybox
import simpleaudio as sa

from transform import rotate, translate, scale


def main():
    """ create a window, add scene objects, then run rendering loop """

    viewer = Viewer(width=1920, height=1080)

    cube_shader = Shader("texture.vert", "texture.frag")
    terrain_shader = Shader("terrain.vert", "terrain.frag")
    # Simple cube
    # cube_node = Node(transform=scale(2, 2, 2) @ translate(1, 0, 0) @ rotate((0, 1, 0), 90))
    # mesh_list = load_textured("./../resources/cube/cube.obj", shader=cube_shader)
    # for mesh in mesh_list:
    #     cube_node.add(mesh)
    # viewer.add(cube_node)

    # Grass
    grass_node = Node(transform=translate(0, -1, 0) @ rotate((1, 0, 0), -90))
    plane = TexturedPlane("./../resources/grass.png", terrain_shader)
    grass_node.add(plane)
    viewer.add(grass_node)

    # House - 1
    house_node = Node(
        transform=translate(50, -1, 0) @ scale(0.3, 0.3, 0.3) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured("./../resources/house/big_house.FBX", shader=cube_shader,
                              tex_file="./../resources/house/big_house.jpg")
    for mesh in mesh_list:
        house_node.add(mesh)
    viewer.add(house_node)

    # Farm empty
    farm_node = Node(
        transform=translate(50, -1, 0) @ scale(0.5, 0.5, 0.5) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured("./../resources/farm/farm_empty.FBX", shader=cube_shader,
                              tex_file="./../resources/farm/farm_empty.jpg")
    for mesh in mesh_list:
        farm_node.add(mesh)
    viewer.add(farm_node)

    # Common tree
    farm_node = Node(
        transform=translate(50, -1, 10) @ scale(0.5, 0.5, 0.5) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured("./../resources/farm/farm_empty.FBX", shader=cube_shader,
                              tex_file="./../resources/farm/farm_empty.jpg")
    for mesh in mesh_list:
        farm_node.add(mesh)
    viewer.add(farm_node)

    # House - 2
    house_node = Node(
        transform=translate(50, -1, -35) @ scale(0.3, 0.3, 0.3) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 0))
    mesh_list = load_textured("./../resources/house/house_01.FBX", shader=cube_shader,
                              tex_file="./../resources/house/house_01.jpg")
    for mesh in mesh_list:
        house_node.add(mesh)
    viewer.add(house_node)

    # Farm empty
    farm_node = Node(
        transform=translate(50, -1, -35) @ scale(0.5, 0.5, 0.5) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured("./../resources/farm/farm_empty.FBX", shader=cube_shader,
                              tex_file="./../resources/farm/farm_empty.jpg")
    for mesh in mesh_list:
        farm_node.add(mesh)
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
    # Rocks
    rock_node = Node(
        transform=translate(30, -1, -20) @ scale(0.1, 0.1, 0.1) @ rotate((1, 0, 0), -90) @ rotate((0, 0, 1), 270))
    mesh_list = load_textured("./../resources/rock/rock_02.FBX", shader=cube_shader,
                              tex_file="./../resources/rock/mountain_rock.jpg")
    for mesh in mesh_list:
        rock_node.add(mesh)
    viewer.add(rock_node)
    # -------------------------------------------------

    # Castle
    # Load castle's multiple textures one by one
    tex_list = ["./../resources/castle/Texture/Castle Exterior Texture.jpg",
                "./../resources/castle/Texture/Towers Doors and Windows Texture.jpg",
                "./../resources/castle/Texture/Ground and Fountain Texture.jpg",
                "./../resources/castle/Texture/Castle Interior Texture.jpg"]
    castle_node = Node(transform=translate(0, -1, 200) @ scale(2.0, 2.0, 2.0) @ rotate((0, 1, 0), 180))
    castle_mesh_list = multi_load_textured(file="./../resources/castle/CastleFBX.fbx", shader=cube_shader,
                                           tex_file=tex_list)
    for mesh in castle_mesh_list:
        castle_node.add(mesh)
    viewer.add(castle_node)

    # Skybox
    shader_skybox = Shader(vertex_source="./skybox.vert", fragment_source="./skybox.frag")
    viewer.add(Skybox(shader_skybox=shader_skybox))

    # Start playing ambient audio in background
    wave_obj = sa.WaveObject.from_wave_file("./../resources/audio/amb_we_2.wav")
    wave_obj.play()

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()  # initialize window system glfw
    main()  # main function keeps variables locally scoped
    glfw.terminate()  # destroy all glfw windows and GL contexts
