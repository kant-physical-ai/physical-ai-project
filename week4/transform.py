import week3.transform
def rotation_matrix_2d(theta_deg):
    return week3.transform.rotation_matrix_2d(theta_deg)
def scale_matrix_2d(sx, sy):
    return week3.transform.scale_matrix_2d(sx, sy)
def translate_2d(point: tuple[float, float], tx: float, ty: float):
    return week3.transform.translate_2d(point, tx, ty)