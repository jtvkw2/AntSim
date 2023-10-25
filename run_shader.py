import pygame
from pygame.locals import *
import numpy as np
import random
from OpenGL.GL import *
from OpenGL.GLU import  *

# Constants
WORLD_SIZE = 512
NUM_HILLS = 10
NUM_ANTS = 100
EMPTY = 0
ANT = 1
HILL = 2

# Initialize world
world = np.zeros((WORLD_SIZE, WORLD_SIZE), dtype=np.int32)

def spawn_hills(world, num_hills):
    for _ in range(num_hills):
        x, y = random.randint(0, WORLD_SIZE-1), random.randint(0, WORLD_SIZE-1)
        while world[y, x] != EMPTY:
            x, y = random.randint(0, WORLD_SIZE-1), random.randint(0, WORLD_SIZE-1)
        world[y, x] = HILL

def spawn_ants(world, num_ants):
    for _ in range(num_ants):
        x, y = random.randint(0, WORLD_SIZE-1), random.randint(0, WORLD_SIZE-1)
        while world[y, x] != EMPTY:
            x, y = random.randint(0, WORLD_SIZE-1), random.randint(0, WORLD_SIZE-1)
        world[y, x] = ANT

spawn_hills(world, NUM_HILLS)
spawn_ants(world, NUM_ANTS)

def setup_textures():
    world_texture = glGenTextures(1)
    new_world_texture = glGenTextures(1)

    # Setup for world_texture and new_world_texture
    for texture in [world_texture, new_world_texture]:
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32I, WORLD_SIZE, WORLD_SIZE, 0, GL_RGBA_INTEGER, GL_INT, world)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    return world_texture, new_world_texture

def draw_world():
    glClear(GL_COLOR_BUFFER_BIT)

    # Use our shader
    glUseProgram(program)

    # Bind textures to compute shader
    glBindImageTexture(0, world_texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32I)
    glBindImageTexture(1, new_world_texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32I)

    # Dispatch compute shader
    glDispatchCompute(WORLD_SIZE // 16, WORLD_SIZE // 16, 1)

    # Ensure all operations are finished before drawing
    glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

    # Swap the textures
    world_texture, new_world_texture = new_world_texture, world_texture

    # Visualization logic
    glBindTexture(GL_TEXTURE_2D, world_texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(-1, -1)
    glTexCoord2f(1, 0); glVertex2f( 1, -1)
    glTexCoord2f(1, 1); glVertex2f( 1,  1)
    glTexCoord2f(0, 1); glVertex2f(-1,  1)
    glEnd()

    pygame.display.flip()

if __name__ == "__main__":
    # Pygame setup
    pygame.init()
    display = (512, 512)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluOrtho2D(-1, 1, -1, 1)
    
    # Create textures and get handles
    global world_texture, new_world_texture
    world_texture, new_world_texture = setup_textures()

    # Load the compute shader
    print(glGetString(GL_VERSION))
    compute_shader = glCreateShader(GL_COMPUTE_SHADER)
    with open("shaders/compute_shader.glsl", "r") as f:
        glShaderSource(compute_shader, f.read())
    glCompileShader(compute_shader)

    # Check for errors
    if not glGetShaderiv(compute_shader, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(compute_shader))
        exit()

    # Link shaders into a program
    program = glCreateProgram()
    glAttachShader(program, compute_shader)
    glLinkProgram(program)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        draw_world()
        pygame.time.wait(10)
