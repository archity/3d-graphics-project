#!/usr/bin/env python3
"""
Python OpenGL Medieval Project.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
from itertools import cycle
import sys
from PIL import Image               # load images for textures

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy                     # 3D resource loader

from core import Shader, Viewer
from skybox import Skybox


def main():
    """ create a window, add scene objects, then run rendering loop """

    viewer = Viewer(width=1920, height=1080)

    shader_skybox = Shader(vertex_source="./skybox.vert", fragment_source="./skybox.frag")

    viewer.add(Skybox(shader_skybox=shader_skybox))

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
