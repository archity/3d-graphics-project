# 3D Graphics Project
Medieval scene based project for the 3D Graphics course of M1 MoSIG

## Camera

We defined a camera class which would help us with managing all the variables and functions associated with moving around the camera POV in our scene.

The following variables define the camera related data:

* `camera_pos` - defines the initial starting position of the camera in 3 dimensions (x, y, z).
* `up` - defines the up direction (the positive y axis as per convention), so we define it as (0, 1, 0)
* `camera_front` - defines the vector of direction the camera POV would be pointing at in the scene. We initialized it to (0, 0, 1) to point it along the z axis.

We define a `function process_keyboard_input()`, which would take action based on the key pressed by the user. For the physical displacement-based movement, we make use of WASD keys. For rotating the camera view along the sides, we use left and right arrow keys.

### Moving the camera (Translation)

For the forward and backwards motion, we essentially modify the camera's position, `camera_pos` variable by a factor which incorporates speed of camera movement, `camera_speed `(calculated by `factor * delta_time`, where delta_time is calculated in order to make the calculation system independent), and the front facing vector direction of camera, `camera_front`. The resultant is either added or subtracted, depending upon forward or backward movement.

For the left and right movement, we have to perform a cross product (between forward direction vector and the up vector) in order to first create the right vector, and then incorporate the same `camera_speed` factor. The resultant is either added or subtracted, depending upon left or right movement.

### Moving the camera around (Rotation)

In order to look left or right from camera POV (rotate the camera POV in a 2D plane CW or ACW), we make use of following diagram to understand the vectors involved:

| <img width="400" alt="rotation1" src="./img/rotation_vector.png"> | <img width="400" alt="rotation2" src="./img/rotation_vector2.png"> |
|:-:|:-:|

Any vector will be made up by its two constituent components, x and z. If both the components are equal, the vector will point exactly in between them (left figure). In order for the vector to point closer to x axis, the x component will have to increased, AND the z component will have to decreased at the same time (right figure).

So the idea is to increase/decrease the x and z components in unison, depending upon which direction we want the camera POV to rotate, and also in which quadrant the vector currently is in. If let's say, we are rotating along left side (anti-clockwise), a visual representation of all the cases for updating the front facing camera (`camera_front`)'s components is presented as follows:

<p align="center">
<img width="400" alt="rotation-sign-update" src="./img/rotation_sign_update.png" align=center>
</p>

For right side rotation (clockwise), all the signs will be just reversed.

## Skybox
TODO: Write about skybox

## Terrain

We made use of `TexturedPlane` class in order to render grass of sufficient area in our scene. The grass would repeat itself, giving the illusion of a large available area.

## 3D Objects

3D models of type `.obj` and `.fbx` both are supported by the object loader. Both require the texture images also to be placed along with object file in the same directory.

`Node` class was made use of in order to define the properties of our objects. We can `scale`, `translate` and `rotate` the object however we want, meaning we can place our object anywhere in our skybox

TODO: Write about multi-texture vs single texture based objects, as well as animated objects.

## Audio

Simpleaudio library,
Found from this link: https://stackoverflow.com/a/36284043/6475377

In case of the following missing file error:

`fatal error: alsa/asoundlib.h: No such file or directory`

* install `libasound2`

    * `sudo apt-get install libasound2-dev`

### Usage

```py
import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file("path/to/file.wav")
play_obj = wave_obj.play()
# play_obj.wait_done()
```
`play_obj.wait_done()` is removed so that audio plays in non-blocking manner.


