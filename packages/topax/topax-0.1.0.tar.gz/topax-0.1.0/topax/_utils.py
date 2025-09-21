import numpy as np
import OpenGL.GL as gl

def norm(v, axis=-1, keepdims=False, eps=0.0):
    return np.sqrt((v*v).sum(axis, keepdims=keepdims).clip(eps))

def normalize(v, axis=-1, eps=1e-20):
    return v/norm(v, axis, keepdims=True, eps=eps)

def rotation_matrix(angle, axis):
    s, c = np.sin(angle), np.cos(angle)
    match axis:
        case 'x':
            return np.array([[1., 0., 0.], [0., c, -s], [0., s, c]])
        case 'y':
            return np.array([[c, 0., s], [0., 1., 0.], [-s, 0., c]])
        case 'z':
            return np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]])
        case _:
            raise ValueError(f"Axis must be 'x' 'y' or 'z', not {axis}")
        
def rotation_matrix_about_vector(angle, axis_vec):
    axis_vec = np.asarray(axis_vec, dtype=float)
    axis_vec = axis_vec / np.linalg.norm(axis_vec)
    x, y, z = axis_vec
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1 - c
    return np.array([
        [c + x*x*C,     x*y*C - z*s, x*z*C + y*s],
        [y*x*C + z*s,   c + y*y*C,   y*z*C - x*s],
        [z*x*C - y*s,   z*y*C + x*s, c + z*z*C]
    ])

def compile_shader(src, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, src)
    gl.glCompileShader(shader)
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(shader).decode())
    return shader
