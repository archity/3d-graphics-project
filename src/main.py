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

from core import Shader, Viewer, Texture, Node, multi_load_textured, TexturedPlane, load_textured_phong_mesh
from skybox import Skybox
import simpleaudio as sa

from transform import rotate, translate, scale


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
    for i in range(-70, 160, 40):
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
                                             k_a=(.5, .5, .5),
                                             k_d=(1, 1, 1),
                                             k_s=(.1, .1, .1),
                                             s=64
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

    # Pond
    # Load pond's multiple textures one by one
    # tex_list2 = ["./../resources/Test/pond/aea4776c-07fb-4104-b781-cdd4792fbaee.jpg",
    #              "./../resources/Test/pond/abb783e6-3e93-26c0-248a-247666855da3.jpg",
    #              "./../resources/Test/pond/b8d3965a-ad78-bf43-699b-bff8eca6c975.jpg",
    #              "./../resources/Test/pond/00000000-0000-2222-3333-100000001042.jpg",
    #              "./../resources/Test/pond/00000000-0000-2222-3333-100000001027.jpg",
    #              "./../resources/Test/pond/00000000-0000-2222-3333-100000001027.jpg"
    #              ]
    # pond_node = Node(
    #     transform=translate(-50, 2, 40) @ scale(4.2, 4.2, 4.2))
    # mesh_list = multi_load_textured(file="./../resources/Test/pond/pond_wo-cube-base.fbx", shader=shader,
    #                                 tex_file=tex_list2)
    #
    # for mesh in mesh_list:
    #     pond_node.add(mesh)
    # viewer.add(pond_node)

    # Castle 2
    # tex_list = 30*["./../resources/castle/Brick1.jpg"]
    # castle_node = Node(transform=translate(100, 10, 100) @ scale(1.0, 1.0, 1.0) @ rotate((0, 1, 0), 0))
    # castle_mesh_list = multi_load_textured(file="./../resources/castle/castle_only.fbx", shader=shader,
    #                                        tex_file=tex_list,
    #                                        k_a=(1, 1, 1),
    #                                        k_d=(.6, .6, .6),
    #                                        k_s=(.1, .1, .1),
    #                                        s=4
    #                                        )
    # for mesh in castle_mesh_list:
    #     castle_node.add(mesh)
    # viewer.add(castle_node)


def build_terrain(viewer, shader):
    # Grass
    grass_node = Node(transform=translate(-500, -1, -500) @ rotate((1, 0, 0), 0))
    plane = TexturedPlane("./../resources/grass.png", shader, size=1000, hmap_file="./../resources/hmap_2_mounds_256px.png")
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

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()  # initialize window system glfw
    main()  # main function keeps variables locally scoped
    glfw.terminate()  # destroy all glfw windows and GL contexts
