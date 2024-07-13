#version 330

#if defined VERTEX_SHADER

in vec3 in_position;

void main() {
    gl_Position = vec4(in_position, 1.0);
}

#elif defined GEOMETRY_SHADER

layout (lines) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;
uniform float width;

out vec2 g_uv;

// Function to create a billboard direction that faces the camera
vec3 billboard(vec3 camRight, vec3 camUp, vec3 direction, float offset) {
    return camRight * direction.x * offset + camUp * direction.y * offset;
}

void main() {
    mat4 mvp = m_proj * m_view * m_model;
    mat4 mv = m_view * m_model;
    
    vec4 p1 = gl_in[0].gl_Position;
    vec4 p2 = gl_in[1].gl_Position;

    vec3 right = vec3(mv[0][0], mv[1][0], mv[2][0]);
    vec3 up = vec3(mv[0][1], mv[1][1], mv[2][1]);
    
    vec2 dir = normalize((mv*(p2 - p1)).xy);
    vec2 normal = vec2(-dir.y, dir.x);
    
    vec3 offset1 = billboard(right, up, vec3(normal, 0.0), width / 2.0);
    vec3 offset2 = billboard(right, up, vec3(-normal, 0.0), width / 2.0);
    
    gl_Position = mvp * (p1 + vec4(offset1, 0.0));
    g_uv = vec2(0.0, 0.0);
    EmitVertex();
    
    gl_Position = mvp * (p1 + vec4(offset2, 0.0));
    g_uv = vec2(0.0, 1.0);
    EmitVertex();
    
    gl_Position = mvp * (p2 + vec4(offset1, 0.0));
    g_uv = vec2(1.0, 0.0);
    EmitVertex();
    
    gl_Position = mvp * (p2 + vec4(offset2, 0.0));
    g_uv = vec2(1.0, 1.0);
    EmitVertex();
    
    EndPrimitive();
}


#elif defined FRAGMENT_SHADER

out vec4 fragColor;

uniform vec4 color = vec4(1.0,1.0,1.0,1.0);

void main() {
    fragColor = color;
}

#endif