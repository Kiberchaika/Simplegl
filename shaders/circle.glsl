#version 330

#if defined VERTEX_SHADER

in vec3 in_position;

void main() {
    gl_Position = vec4(in_position, 1.0);
}

#elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;
uniform float radius;

out vec2 g_uv;

void main() {
    mat4 mvp = m_proj * m_view * m_model;
    mat4 mv = m_view * m_model;
 
    vec3 pos = gl_in[0].gl_Position.xyz;

    vec3 right = vec3(mv[0][0], mv[1][0], mv[2][0]);
    vec3 up = vec3(mv[0][1], mv[1][1], mv[2][1]);
     
    right *= radius;
    up *= radius;
    
    gl_Position = mvp * vec4(pos - right - up, 1.0);
    g_uv = vec2(0.0, 0.0);
    EmitVertex();
    
    gl_Position = mvp * vec4(pos + right - up, 1.0);
    g_uv = vec2(1.0, 0.0);
    EmitVertex();
    
    gl_Position = mvp * vec4(pos - right + up, 1.0);
    g_uv = vec2(0.0, 1.0);
    EmitVertex();
    
    gl_Position = mvp * vec4(pos + right + up, 1.0);
    g_uv = vec2(1.0, 1.0);
    EmitVertex();
    
    EndPrimitive();
}

#elif defined FRAGMENT_SHADER

in vec2 g_uv;

out vec4 fragColor;

uniform vec4 color = vec4(1.0,1.0,1.0,1.0);

void main() {
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(g_uv, center);
    if (dist <= 0.5) {
        fragColor = color;
    } else {
        discard;
    }
}

#endif