#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec2 in_texcoord_0;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

out vec2 uv0;

void main() {
    mat4 mv = m_view * m_model;
 
    vec3 position = vec3(m_model[3]);
    float scale = length(vec3(m_model[0]));
    
    vec3 right = vec3(m_view[0][0], m_view[1][0], m_view[2][0]);
    vec3 up = vec3(m_view[0][1], m_view[1][1], m_view[2][1]);
    vec3 billboard_pos = position + scale * (right * in_position.x + up * in_position.y);
    
    gl_Position = m_proj * m_view * vec4(billboard_pos, 1.0);
    
    uv0 = in_texcoord_0;
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

uniform sampler2D texture0;
uniform vec4 color = vec4(1.0,1.0,1.0,1.0);

in vec2 uv0;

void main() {
    fragColor = vec4(color.rgb, color.a * texture(texture0, uv0).r);
}
#endif