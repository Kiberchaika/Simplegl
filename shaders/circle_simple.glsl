#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec2 in_texcoord_0;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

out vec2 uv0;

void main() {
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);

    //gl_Position = vec4(in_position, 1.0);

    uv0 = in_texcoord_0;
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

uniform vec4 color = vec4(1.0,1.0,1.0,1.0);

in vec2 uv0;

void main() {
    if(distance(uv0, vec2(0.5,0.5)) < 0.5){
        fragColor = color;
    }
    else {
        discard;
    }
}

#endif
 