#version 430

layout(local_size_x = 16, local_size_y = 16) in;

layout(rgba32i, binding = 0) uniform iimage2D world_texture;
layout(rgba32i, binding = 1) writeonly iimage2D new_world_texture;

void main() {
    ivec2 gid = ivec2(gl_GlobalInvocationID.xy);
    
    int cellValue = imageLoad(world_texture, gid).r;
    
    if (cellValue == ANT) {
        // Check surrounding cells in a cone in front of the ant.
        // This is a very simple forward check for simplicity.
        ivec2 forwardDir = ivec2(0, -1); // Example direction (upwards)
        
        bool foundAnt = false;
        ivec2 moveDir = ivec2(0, 0);
        
        // Simple check in the forward direction for other ants.
        for (int i = 1; i <= 3; i++) {
            ivec2 checkPos = gid + i * forwardDir;
            if (imageLoad(world_texture, checkPos).r == ANT) {
                foundAnt = true;
                moveDir = forwardDir;
                break;
            }
        }
        
        // If we found an ant, move towards it. Otherwise, move randomly.
        if (!foundAnt) {
            int randDir = int(mod(float(gl_GlobalInvocationID.x * gl_GlobalInvocationID.y), 4.0));
            if (randDir == 0) moveDir = ivec2(0, -1);
            else if (randDir == 1) moveDir = ivec2(1, 0);
            else if (randDir == 2) moveDir = ivec2(0, 1);
            else if (randDir == 3) moveDir = ivec2(-1, 0);
        }

        ivec2 newGid = gid + moveDir;
        
        // Move the ant to the new position in the new world texture.
        imageStore(new_world_texture, newGid, ivec4(ANT, 0, 0, 0));
    } else {
        // Copy the cell to the new world texture.
        imageStore(new_world_texture, gid, ivec4(cellValue, 0, 0, 0));
    }
}
