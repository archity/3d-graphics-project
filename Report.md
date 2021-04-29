# Empire Earth - European Edition

Medieval scene based project for the course 3D Graphics at MoSIG.

## 1. Authors

* Archit YADAV
* Jit CHATTERJEE
* Nairit BANDYOPADHYAY

## 2. Installation

### 2.1 Minimum requirements

We have provided with a requirements.txt file in order to install all required libraries.

### 2.2 Extra libraries

In case OpenGL and other bare minimum is already installed, simply install simpleaudio library as follows:

`pip3 install simpleaudio`

In case of the following missing file error:

```
fatal error: alsa/asoundlib.h: No such file or directory
```
* install `libasound2`
    * `sudo apt-get install libasound2-dev`

__NOTE:__ For WSL + x11 case, there *might* be an issue during runtime even after correctly installing the sound libraries, because of x11 sound forwarding issues, for which we currently do not have a concrete solution.

As a solution to disable all the game sound components, simple navigate to `src/config.py` and change the value of `sound` variable to `False`. This will disable all the calls to `simpleaudio` objects as well as the import statement itself.

## 3. How to run

In the 3d-graphics-project/src folder, execute the `main.py` file:

```
python3 main.py
```

## 4. List of features

* Modelling
    * Hierarchical modelling
    * Mesh based objects
    * Non-flat ground

* Rendering
    * Light and materials
    * Texture based objects
    * Novel rendering effects:
        * Fog
        * Blendmap
        * Terrain collision detection
        * Day-night transition, with change in fog colour
    * Skybox
        * Multi-skybox support (day/night)

* Animation
    * Keyframe-only animation
    * Procedural animation
        * Birds circling over the sky in random fashion
    * Skinning + keyframe
        * Farmer/templar walking on a defined path
    * Keyboard control element
        * Cannon firing using F key
        * Day-night cycle control using F6/F7/F8

## 5. Who did what
All of us were involved in a mix of features.


## 6. Difficulties/Improvements

* Normal mapping - We attempted to implement normal mapping. We even had done an implementation which would calculate the tangents and bitangents, but the object wouldn't display at all at runtime. This is a feature which we would like to have it implemented sometime in future, when we'd have more time to properly work on it.

* Real-time based Point light effects - It took a lot of time to properly understand how to create 4 different sources of light, and how all the objects would be affected by these, that too in accordance with the time of the day.