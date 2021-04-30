#!/usr/bin/env python3
"""
Python OpenGL Medieval Project.
"""
# Python built-in modules
import glfw  # lean window system wrapper for OpenGL

# External, non built-in modules
from viewer import Viewer
from shader import Shader
from core import build_terrain, build_tree, build_houses,\
    add_characters, add_animations, add_lamps, build_graveyard,\
    build_castle, build_church
from skybox import Skybox

import config


def main():
    """ create a window, add scene objects, then run rendering loop """

    # Define all the shaders
    viewer = Viewer(width=1920, height=1080)
    terrain_shader = Shader("shaders/terrain.vert", "shaders/terrain.frag")
    # cube_shader = Shader("shaders/texture.vert", "shaders/texture.frag")
    phong_shader = Shader("shaders/phong.vert", "shaders/phong.frag")
    lambertian_shader = Shader("shaders/lambertian.vert", "shaders/lambertian.frag")
    skinning_shader = Shader("shaders/skinning.vert", "shaders/skinning.frag")

    # Add all the elements of the scene ony by one
    build_terrain(viewer, shader=terrain_shader)
    build_tree(viewer, shader=phong_shader)
    build_graveyard(viewer, shader=phong_shader)
    build_houses(viewer, shader=phong_shader, lamb_shader=lambertian_shader)
    build_castle(viewer, shader=phong_shader)
    build_church(viewer, shader=phong_shader)
    add_characters(viewer, shader=skinning_shader)
    add_animations(viewer, shader=phong_shader)
    add_lamps(viewer, shader=phong_shader)

    # -------------------------------------------------

    # Skybox
    shader_skybox = Shader(vertex_source="./shaders/skybox.vert", fragment_source="./shaders/skybox.frag")
    viewer.add(Skybox(shader_skybox=shader_skybox))

    # Start playing ambient audio in background
    if config.sound==True:
        wave_obj = config.sa.WaveObject.from_wave_file("./../resources/audio/amb_we_1-3.wav")
        wave_obj.play()

    message = """
    Empire Earth: European Edition
    Welcome to the EE first person RTS game!
    
    Use WASD keys to move around, and the ARROW keys to look around.
    Press F to fire a cannon ball form the tower turrent.
    Press F6/F7/F8 to toggle between day-night cycles
    (F8 for auto-toggle between day and night)
    
    Press SPACEBAR to reset all animations.
    
    And finally, press ESC or Q to exit the game.
    """
    print(message)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()  # initialize window system glfw
    main()  # main function keeps variables locally scoped
    glfw.terminate()  # destroy all glfw windows and GL contexts
