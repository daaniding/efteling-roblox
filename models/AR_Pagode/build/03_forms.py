"""
BUILD PHASE TEMPLATE
Copy this file to <asset>/build/NN_<phase>.py, fill in build(), run:

  blender --background --python build/02_blockout.py -- --master <asset>_master.blend

Every phase script is re-runnable: it opens the master, deletes what it owns
(objects whose names carry OWNER_TAG in a custom property), rebuilds them, saves.
Nothing else in the file is touched, so earlier phases and manual edits survive.

Coordinate convention: metres, Z up, subject faces -Y, origin at the ground
contact point (characters, props, architecture) or the ground centre (vehicles).
"""
import bpy, bmesh, sys, os, math, argparse
from mathutils import Vector, Matrix, Euler

PHASE = "03_forms"
OWNER_TAG = "phase:" + PHASE   # objects created here get ob["owner"] = OWNER_TAG


# ARGS AND FILE HANDLING

def argv_after_dashes():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def open_master(path):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path))
    return bpy.context.scene


def save_master(path):
    bpy.context.preferences.filepaths.save_version = 0   # no .blend1 backups
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))


def col(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def clear_owned(tag=None):
    """Delete every object this phase created last time, so the script is idempotent."""
    tag = tag or OWNER_TAG
    for ob in [o for o in bpy.data.objects if o.get("owner") == tag]:
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Armature):
                bpy.data.armatures.remove(data)


def own(ob):
    ob["owner"] = OWNER_TAG
    return ob


def log(*a):
    print("[" + PHASE + "]", *a)


# MESH PRIMITIVES (bmesh based, no operators, safe in background mode)

def new_mesh_object(name, bm, collection, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.rotation_euler = rotation
    ob.scale = scale
    col(collection).objects.link(ob)
    return own(ob)


def box(name, size, collection="LOW", location=(0, 0, 0), rotation=(0, 0, 0), base_at_origin=False):
    """size = (x, y, z). base_at_origin puts the bottom face on z=0."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if base_at_origin:
        bmesh.ops.translate(bm, vec=(0, 0, size[2] / 2), verts=bm.verts)
    return new_mesh_object(name, bm, collection, location, rotation)


def cylinder(name, radius, height, collection="LOW", segments=32, axis="Z", location=(0, 0, 0),
             radius_top=None, base_at_origin=False):
    """Cylinder or truncated cone along axis. radius_top defaults to radius."""
    bm = bmesh.new()
    r2 = radius if radius_top is None else radius_top
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=r2, depth=height)
    if base_at_origin:
        bmesh.ops.translate(bm, vec=(0, 0, height / 2), verts=bm.verts)
    if axis == "X":
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"), verts=bm.verts)
    elif axis == "Y":
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, "X"), verts=bm.verts)
    return new_mesh_object(name, bm, collection, location)


def sphere(name, radius, collection="LOW", location=(0, 0, 0), u=24, v=12, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    return new_mesh_object(name, bm, collection, location)


def grid(name, size_x, size_y, cuts_x, cuts_y, collection="LOW", location=(0, 0, 0), rotation=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=cuts_x, y_segments=cuts_y, size=0.5)
    bmesh.ops.scale(bm, vec=(size_x, size_y, 1), verts=bm.verts)
    return new_mesh_object(name, bm, collection, location, rotation)


def loft(name, sections, collection="LOW", close_sections=True, cap_ends=True, smooth=True):
    """Bridge a list of cross sections (each a list of Vector/tuple, same point count) into a hull.
    Use it for vehicle bodies, boat hulls, torsos: read section widths/heights off the top and side
    reference views at fixed stations along the length."""
    bm = bmesh.new()
    rings = []
    for sec in sections:
        vs = [bm.verts.new(Vector(p)) for p in sec]
        ring = []
        for i in range(len(vs)):
            if i == len(vs) - 1 and not close_sections:
                break
            ring.append(bm.edges.new((vs[i], vs[(i + 1) % len(vs)])))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        bmesh.ops.bridge_loops(bm, edges=a + b)
    if cap_ends and close_sections:
        bmesh.ops.contextual_create(bm, geom=rings[0])
        bmesh.ops.contextual_create(bm, geom=rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_object(name, bm, collection)
    if smooth:
        shade_smooth(ob, math.radians(35))
    return ob


def profile_spin(name, profile_xz, collection="LOW", steps=32, location=(0, 0, 0), angle=360):
    """Lathe a 2D profile (list of (radius, z)) around Z: vases, columns, wheel rims, bolts."""
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0, z)) for r, z in profile_xz]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.radians(angle), steps=steps, use_merge=(angle >= 360))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object(name, bm, collection, location)


def profile_extrude(name, profile_xy, length, collection="LOW", location=(0, 0, 0), rotation=(0, 0, 0)):
    """Extrude a closed 2D outline (list of (x, y)) along Z: arches, mouldings, I-beams, tracks, trims."""
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, 0)) for x, y in profile_xy]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, length), verts=top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object(name, bm, collection, location, rotation)


def curve_tube(name, points, radius, collection="LOW", resolution=12, taper_to=None, bevel_res=6):
    """Poly/bezier tube through points: cables, horns, tails, pipes, tentacles, railings, roots."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("NURBS")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
        if taper_to is not None:
            t = i / max(1, len(points) - 1)
            sp.points[i].radius = 1.0 + (taper_to - 1.0) * t
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(points))
    cu.resolution_u = resolution
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    ob = bpy.data.objects.new(name, cu)
    col(collection).objects.link(ob)
    return own(ob)


def skin_chain(name, joints, collection="HIGH", subdiv=2, root_index=0):
    """Organic blockout in one call. joints = [(x, y, z, radius), ...] connected in order, or a dict
    {"name": [(x, y, z, r), ...], ...} of chains sharing their first point with another chain by position.
    Skin modifier + Subdivision gives a smooth mass with quad loops at every joint, which is a usable
    LOW base for stylized characters after shrinkwrapping to the sculpt."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    chains = joints if isinstance(joints, dict) else {"main": joints}
    vert_by_pos = {}
    order = []
    for cname, pts in chains.items():
        prev = None
        for (x, y, z, r) in pts:
            key = (round(x, 5), round(y, 5), round(z, 5))
            v = vert_by_pos.get(key)
            if v is None:
                v = bm.verts.new((x, y, z))
                vert_by_pos[key] = v
                order.append((v, r))
            if prev is not None and prev is not v:
                if not bm.edges.get((prev, v)):
                    bm.edges.new((prev, v))
            prev = v
    bm.verts.index_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col(collection).objects.link(ob)
    skin = ob.modifiers.new("Skin", "SKIN")
    skin.use_smooth_shade = True
    # skin_vertices layer exists once the modifier is present
    layer = me.skin_vertices[0].data
    for i, (v, r) in enumerate(order):
        layer[i].radius = (r, r)
        layer[i].use_root = (i == root_index)
    sub = ob.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = subdiv
    sub.render_levels = subdiv
    return own(ob)


# MODIFIERS AND EDITS

def mirror_origin():
    """Shared empty at the world origin so mirrors work across the asset's centre line,
    not across each object's own origin (the classic Blender mirror mistake)."""
    ob = bpy.data.objects.get("REF_mirror_origin")
    if ob is None:
        ob = bpy.data.objects.new("REF_mirror_origin", None)
        ob.empty_display_type = "PLAIN_AXES"
        ob.empty_display_size = 0.05
        col("REF").objects.link(ob)
    return ob


def mirror(ob, axis="X", merge=0.001, clip=True, about_world=True):
    """Mirror across the world centre plane by default. Pass about_world=False to mirror
    across the object's own origin (only right when the origin sits on the symmetry plane)."""
    m = ob.modifiers.new("Mirror", "MIRROR")
    m.use_axis = (axis == "X", axis == "Y", axis == "Z")
    m.use_mirror_merge = merge > 0
    m.merge_threshold = merge
    m.use_clip = clip
    if about_world:
        m.mirror_object = mirror_origin()
    return m


def bevel(ob, width=0.01, segments=3, angle_limit=30, harden=True):
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width = width
    b.segments = segments
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle_limit)
    b.harden_normals = harden
    return b


def subsurf(ob, levels=2):
    s = ob.modifiers.new("Subdivision", "SUBSURF")
    s.levels = levels
    s.render_levels = levels
    return s


def solidify(ob, thickness=0.01, offset=-1.0, rim=True):
    s = ob.modifiers.new("Solidify", "SOLIDIFY")
    s.thickness = thickness
    s.offset = offset
    s.use_rim = rim
    return s


def boolean(ob, cutter, op="DIFFERENCE", hide_cutter=True, solver="EXACT"):
    b = ob.modifiers.new("Bool_" + cutter.name, "BOOLEAN")
    b.operation = op
    b.object = cutter
    b.solver = solver
    if hide_cutter:
        cutter.hide_render = True
        cutter.hide_viewport = True
        cutter.display_type = "WIRE"
    return b


def array(ob, count, offset=(1, 0, 0), relative=True, curve=None):
    a = ob.modifiers.new("Array", "ARRAY")
    a.count = count
    if relative:
        a.relative_offset_displace = offset
    else:
        a.use_relative_offset = False
        a.use_constant_offset = True
        a.constant_offset_displace = offset
    if curve is not None:
        a.fit_type = "FIT_CURVE"
        a.curve = curve
        c = ob.modifiers.new("Curve", "CURVE")
        c.object = curve
    return a


def shrinkwrap(ob, target, offset=0.0, mode="NEAREST_SURFACEPOINT"):
    s = ob.modifiers.new("Shrinkwrap", "SHRINKWRAP")
    s.target = target
    s.offset = offset
    s.wrap_method = mode
    return s


def remesh_voxel(ob, voxel_size=0.02, smooth_normals=True):
    r = ob.modifiers.new("Remesh", "REMESH")
    r.mode = "VOXEL"
    r.voxel_size = voxel_size
    r.use_smooth_shade = smooth_normals
    return r


def decimate(ob, ratio):
    d = ob.modifiers.new("Decimate", "DECIMATE")
    d.ratio = ratio
    return d


def apply_all_modifiers(ob):
    """Bake the modifier stack into the mesh without operators (safe in background)."""
    dg = bpy.context.evaluated_depsgraph_get()
    eo = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(eo)
    old = ob.data
    name = old.name
    ob.data = me
    ob.modifiers.clear()
    if old.users == 0:
        bpy.data.meshes.remove(old)
    me.name = name                      # keep the mesh name free of .001
    return ob


def apply_transform(ob):
    """Freeze location/rotation/scale into the mesh. Only for unparented objects."""
    if ob.parent is not None or ob.type != "MESH":
        return ob
    ob.data.transform(ob.matrix_basis)
    ob.matrix_basis = Matrix.Identity(4)
    return ob


def set_origin(ob, world_point):
    """Move the object origin to world_point without moving the geometry."""
    p = Vector(world_point)
    local = ob.matrix_world.inverted() @ p
    ob.data.transform(Matrix.Translation(-local))
    ob.matrix_world = ob.matrix_world @ Matrix.Translation(local)
    return ob


def join_meshes(name, objects, collection="LOW"):
    """Merge several mesh objects into one new object in world space. Sources are left alone."""
    bm = bmesh.new()
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objects:
        eo = ob.evaluated_get(dg)
        me = eo.to_mesh()
        tmp = bmesh.new()
        tmp.from_mesh(me)
        bmesh.ops.transform(tmp, matrix=eo.matrix_world, verts=tmp.verts)
        tmp_me = bpy.data.meshes.new("_tmp_join")
        tmp.to_mesh(tmp_me)
        tmp.free()
        bm.from_mesh(tmp_me)
        bpy.data.meshes.remove(tmp_me)
        eo.to_mesh_clear()
    return new_mesh_object(name, bm, collection)


def duplicate(ob, name, collection=None):
    new = ob.copy()
    new.data = ob.data.copy()
    new.name = name
    new.data.name = name
    col(collection or ob.users_collection[0].name).objects.link(new)
    return own(new)


def shade_smooth(ob, sharp_angle=math.radians(30)):
    """Smooth shading with sharp edges marked by angle. Marked sharp edges always split normals in 4.1+."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0.0) <= sharp_angle
    bm.to_mesh(me)
    bm.free()
    if hasattr(me, "use_auto_smooth"):      # 4.0 only; removed in 4.1
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.pi
    return ob


def push(ob, center, radius, strength, direction=None, falloff="smooth"):
    """Code sculpting: move vertices within radius of center along their normal (or direction)."""
    me = ob.data
    c = ob.matrix_world.inverted() @ Vector(center)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    d = None if direction is None else (ob.matrix_world.to_3x3().inverted() @ Vector(direction)).normalized()
    for v in bm.verts:
        t = (v.co - c).length / radius
        if t >= 1.0:
            continue
        w = (1 - t * t) ** 2 if falloff == "smooth" else (1 - t)
        v.co += (d if d is not None else v.normal) * strength * w
    bm.to_mesh(me)
    bm.free()
    return ob


def taper(ob, axis="Z", top_scale=0.5, bottom=None, top=None):
    """Scale cross sections linearly along an axis (limb tapering, spires, hulls)."""
    me = ob.data
    idx = "XYZ".index(axis)
    cos = [v.co[idx] for v in me.vertices]
    lo = min(cos) if bottom is None else bottom
    hi = max(cos) if top is None else top
    for v in me.vertices:
        t = 0 if hi == lo else max(0.0, min(1.0, (v.co[idx] - lo) / (hi - lo)))
        s = 1 + (top_scale - 1) * t
        for j in range(3):
            if j != idx:
                v.co[j] *= s
    return ob


# UV

def smart_uv(ob, angle=66.0, margin=0.02, seams_from_sharp=True):
    """Quick unwrap for blockouts, props and hard surface: Smart UV Project through the operator,
    with seams taken from marked sharp edges when asked. Hero deforming parts get seams placed
    by hand in the phase script (mark_seams) and unwrap_by_seams instead."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    if seams_from_sharp:
        bpy.ops.mesh.edges_select_sharp(sharpness=math.radians(angle))
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def mark_seams(ob, edge_filter):
    """edge_filter(bmesh_edge) -> bool. Marks seams by rule, e.g. lambda e: abs(e.verts[0].co.x) < 1e-4."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    n = 0
    for e in bm.edges:
        if edge_filter(e):
            e.seam = True
            n += 1
    bm.to_mesh(me)
    bm.free()
    log("seams marked on", ob.name, n)
    return ob


def unwrap_by_seams(ob, margin=0.02, method="ANGLE_BASED"):
    """Unwrap along marked seams, then pack islands."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method=method, margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


# MATERIALS

def material(name, color=(0.5, 0.5, 0.5, 1), roughness=0.5, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0) and not m.use_nodes:   # 5.0+ materials always use nodes
        m.use_nodes = True
    # look nodes up by type: display names are translated in non-English Blender UIs
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m


def assign(ob, mat):
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)
    return ob


# RIG HELPERS

def armature(name, bones, collection="RIG_DEF"):
    """bones = [(name, head, tail, parent_name_or_None, roll_deg, deform_bool), ...]"""
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    col(collection).objects.link(ob)
    own(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    for bname, head, tail, parent, roll, deform in bones:
        eb = arm.edit_bones.new(bname)
        eb.head, eb.tail = Vector(head), Vector(tail)
        eb.roll = math.radians(roll)
        eb.use_deform = deform
        if parent:
            eb.parent = arm.edit_bones[parent]
            eb.use_connect = (Vector(head) - arm.edit_bones[parent].tail).length < 1e-5
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def bind(mesh_ob, arm_ob, method="ARMATURE_AUTO"):
    """Parent with automatic weights. Weight painting corrections come after, in a later phase."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    mesh_ob.select_set(True)
    arm_ob.select_set(True)
    bpy.context.view_layer.objects.active = arm_ob
    bpy.ops.object.parent_set(type=method)
    return mesh_ob


def socket(name, location, parent=None, parent_bone=None, rotation=(0, 0, 0), size=0.1, **props):
    """Semantic attachment point. Local +Y = forward of whatever attaches, +Z = its up."""
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "ARROWS"
    ob.empty_display_size = size
    col("SOCKETS").objects.link(ob)
    own(ob)
    if parent is not None:
        ob.parent = parent
        if parent_bone:
            ob.parent_type = "BONE"
            ob.parent_bone = parent_bone
    ob.matrix_world = Matrix.Translation(Vector(location)) @ Euler(rotation).to_matrix().to_4x4()
    for k, v in props.items():
        ob[k] = v
    return ob


def lod_copy(ob, level, ratio):
    """Make <name>_LOD<level> from a LOD0 object with a Decimate at ratio. Rework silhouettes by hand after."""
    base = ob.name.replace("_LOD0", "")
    new = duplicate(ob, base + "_LOD" + str(level))
    decimate(new, ratio)
    return new


# BUILD

# ---------- maten (asset-brief.md; video 6:40-6:50; Pagode2012.jpg; zijkant_onder.jpg) ----------
RAND = 1.5                     # schotelrand boven onderkant
DEK = RAND + 0.7               # dek
N = 22                         # puntgevels
R_GEVEL = 8.4                  # voorvlak gevels
Z_GOOT = DEK + 2.6             # voet gevels (video)
Z_PUNT = DEK + 4.6             # gevelpunt (video)
D_KAP = 2.6                    # diepte dakkapel naar binnen (luchtfoto: tot ~r 5.8)
Zr = lambda h: RAND + h        # hoogte boven de schotelrand (zijfoto-maten)

VERVANGT = ("AR_Pagode_gevel_", "AR_Pagode_vlam_", "AR_Pagode_dak1", "AR_Pagode_dak2", "AR_Pagode_dak3",
            "AR_Pagode_kroondak", "AR_Pagode_binnenwand", "AR_Pagode_binnendak", "AR_Pagode_trommel",
            "AR_Pagode_trommel2", "AR_Pagode_trommel3")


def wis_blokkering():
    for ob in list(bpy.data.objects):
        if ob.name.startswith(VERVANGT) and ob.get("owner") != OWNER_TAG:
            bpy.data.objects.remove(ob, do_unlink=True)


def mesh_uit(name, verts, faces, collection="LOW", mat=None):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        try: bm.faces.new([vs[i] for i in f])
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_object(name, bm, collection)
    if mat: ob["rol"] = mat
    return ob


def strook(p0, p1, breed, diep, y0=0.0):
    """Balk langs de lijn p0->p1 in het xz-vlak (y = diepte): windveer."""
    p0, p1 = Vector(p0), Vector(p1)
    t = (p1 - p0).normalized(); n = Vector((-t.z, 0, t.x))   # normaal in het vlak (naar binnen van de driehoek)
    a, b = p0, p1
    c, d = p1 + n * breed, p0 + n * breed
    vs = []
    for y in (y0, y0 + diep):
        vs += [(v.x, y, v.z) for v in (a, b, c, d)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return vs, faces


def plaats(ob, hoek, r, z=0.0):
    """Lokaal frame (x = raaklijn, -y = naar buiten) naar de ring."""
    ob.rotation_euler = (0, 0, hoek + math.pi / 2)
    ob.location = (r * math.cos(hoek), r * math.sin(hoek), z)


def krul(name, pts, r, taper, rol, collection="LOW"):
    ob = curve_tube(name, pts, r, collection=collection, resolution=10, taper_to=taper, bevel_res=3)
    ob["rol"] = rol
    return ob


def dakkapel(i):
    hoek = i / N * 2 * math.pi
    hw = math.pi * R_GEVEL / N           # halve basisbreedte
    z0, z1 = Z_GOOT, Z_PUNT
    obs = []
    # 1 sierveld (timpaan): ingezet driehoekig paneel
    ins = 0.34
    tv = [(-hw + ins * 1.4, 0.16, z0 + 0.12), (hw - ins * 1.4, 0.16, z0 + 0.12), (0, 0.16, z1 - ins * 1.6)]
    vs = tv + [(x, y + 0.06, z) for x, y, z in tv]
    obs.append(mesh_uit(f"AR_Pagode_F_sierveld_{i:02d}", vs, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], mat="sierveld"))
    # 2 windveren (rood met witte schubben): twee balken langs de schuine randen, iets voorbij de punt
    for k, (pa, pb) in enumerate([((-hw - 0.08, 0, z0 - 0.05), (0.04, 0, z1 + 0.12)), ((hw + 0.08, 0, z0 - 0.05), (-0.04, 0, z1 + 0.12))]):
        vs, fs = strook(pa, pb, 0.40 if k == 0 else -0.40, 0.24, y0=-0.07)   # video: brede rode windveer
        obs.append(mesh_uit(f"AR_Pagode_F_windveer_{i:02d}_{k}", vs, fs, mat="windveer"))
    # 3 groene binnenlijst langs de windveren
    for k, (pa, pb) in enumerate([((-hw + 0.25, 0.05, z0 + 0.05), (0, 0.05, z1 - 0.32)), ((hw - 0.25, 0.05, z0 + 0.05), (0, 0.05, z1 - 0.32))]):
        vs, fs = strook(pa, pb, 0.09 if k == 0 else -0.09, 0.12, y0=0.05)
        obs.append(mesh_uit(f"AR_Pagode_F_lijst_{i:02d}_{k}", vs, fs, mat="groen"))
    # 4 pannendak van de kapel: twee holle vlakken van de windveer naar de nok achter (luchtfoto: oranje, groene randen)
    nok_v, nok_a = (0, 0.15, z1), (0, D_KAP, z1 - 0.35)
    for k, s in enumerate((-1, 1)):
        hoek_v = (s * hw, 0.15, z0)
        hoek_a = (s * hw * 0.55, D_KAP, z0 + 1.15)
        rows = []
        for u in range(5):           # 5 x 5 raster, licht hol (Thaise dakzwaai)
            row = []
            for w in range(5):
                a_, b_ = u / 4, w / 4
                p = (Vector(hoek_v) * (1 - a_) + Vector(nok_v) * a_) * (1 - b_) + (Vector(hoek_a) * (1 - a_) + Vector(nok_a) * a_) * b_
                p.z -= 0.10 * math.sin(math.pi * a_) * (1 - 0.5 * b_)
                row.append(tuple(p))
            rows.append(row)
        vs = [p for row in rows for p in row]
        fs = [(u * 5 + w, u * 5 + w + 1, (u + 1) * 5 + w + 1, (u + 1) * 5 + w) for u in range(4) for w in range(4)]
        ob = mesh_uit(f"AR_Pagode_F_pannen_{i:02d}_{k}", vs, fs, mat="pannen")
        solidify(ob, 0.06)
        obs.append(ob)
        # groene randlat op de nok
    vs, fs = strook((0, 0.15, z1 + 0.02), (0, D_KAP, z1 - 0.33), 0.06, 0.18, y0=-0.09)
    # (nok loopt in y: bouw als buis)
    obs.append(krul(f"AR_Pagode_F_nok_{i:02d}", [(0, 0.15, z1 + 0.03), (0, D_KAP * 0.5, z1 - 0.12), (0, D_KAP, z1 - 0.33)], 0.07, 1.0, "groen"))
    # 5 witte vlam (chofa) op de punt: naar buiten en omhoog, punt krult terug
    # foto's: vlam schiet omhoog en de punt zwiept naar BUITEN
    obs.append(krul(f"AR_Pagode_F_vlam_{i:02d}", [(0, -0.02, z1 + 0.05), (0, -0.10, z1 + 0.45), (0, -0.06, z1 + 0.85),
                                                   (0, -0.25, z1 + 1.15), (0, -0.55, z1 + 1.28)], 0.12, 0.15, "vlam"))
    # 6 witte krullen (hang hong) onderaan de windveren + gouden hanger in de kiel
    for k, s in enumerate((-1, 1)):
        x = s * (hw - 0.16)     # naast elkaar in de kiel, niet op de krul van de buurgevel (z-fighting)
        obs.append(krul(f"AR_Pagode_F_haak_{i:02d}_{k}", [(x, -0.05, z0 + 0.1), (x * 1.04, -0.28, z0 + 0.02), (x * 1.06, -0.42, z0 + 0.22),
                                                          (x * 1.03, -0.32, z0 + 0.42)], 0.07, 0.35, "vlam"))
    obs.append(mesh_uit(f"AR_Pagode_F_hanger_{i:02d}", [(hw - 0.07, -0.02, z0 - 0.02), (hw + 0.07, -0.02, z0 - 0.02), (hw, 0.1, z0 - 0.02),
                                                         (hw, 0.02, z0 - 0.42)], [(0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0)], mat="goud"))
    for ob in obs:
        if ob.type == "MESH" or ob.type == "CURVE":
            plaats(ob, hoek, R_GEVEL, 0)


def klokdak(name, r_goot, z_goot, r_top, z_top, n_hoek=8, horen=0.6, rib=True):
    """Klokvormig (gezwaaid) dak met groene goot, ribben en witte hoorns op de hoeken."""
    prof = []
    for k in range(9):
        t = k / 8
        r = r_goot + (r_top - r_goot) * (1 - (1 - t) ** 1.8)       # holle zwaai
        z = z_goot + (z_top - z_goot) * t ** 1.35
        prof.append((r, z))
    prof = [(r_goot + 0.05, z_goot - 0.18)] + prof + [(0.0, z_top)]
    ob = profile_spin(name, prof, steps=n_hoek * 4)
    ob["rol"] = "pannen"
    goot = profile_spin(name + "_goot", [(r_goot + 0.08, z_goot - 0.22), (r_goot + 0.08, z_goot - 0.02), (r_goot - 0.25, z_goot - 0.02),
                                         (r_goot - 0.25, z_goot - 0.22)], steps=n_hoek * 4)
    goot["rol"] = "groen"
    for k in range(n_hoek):
        a = (k + 0.5) / n_hoek * 2 * math.pi
        ca, sa = math.cos(a), math.sin(a)
        if rib:
            pts = []
            for j in range(0, 9, 2):
                t = j / 8
                r = r_goot + (r_top - r_goot) * (1 - (1 - t) ** 1.8) + 0.015   # rib zakt iets in het dak
                z = z_goot + (z_top - z_goot) * t ** 1.35 + 0.02
                pts.append((r * ca, r * sa, z))
            krul(f"{name}_rib_{k}", pts, 0.06 * (r_goot / 3.0) + 0.025, 0.6, "rib")
        h = horen * (r_goot / 3.0) + 0.25
        krul(f"{name}_hoorn_{k}", [((r_goot + 0.0) * ca, (r_goot + 0.0) * sa, z_goot - 0.05),
                                   ((r_goot + 0.35 * h) * ca, (r_goot + 0.35 * h) * sa, z_goot + 0.05),
                                   ((r_goot + 0.6 * h) * ca, (r_goot + 0.6 * h) * sa, z_goot + 0.45 * h),
                                   ((r_goot + 0.45 * h) * ca, (r_goot + 0.45 * h) * sa, z_goot + 0.85 * h)],
             0.07 * (r_goot / 3.0) + 0.03, 0.2, "vlam")
    return ob


def build(scene, args):
    wis_blokkering()
    for i in range(N):
        dakkapel(i)
    # groene goot onder de kapellen
    g = profile_spin("AR_Pagode_F_goot", [(R_GEVEL + 0.1, Z_GOOT - 0.3), (R_GEVEL + 0.1, Z_GOOT), (R_GEVEL - 0.2, Z_GOOT), (R_GEVEL - 0.2, Z_GOOT - 0.3)], steps=N * 4)
    g["rol"] = "groen"
    # dakvlak tussen de kapellen en de groene schutting (luchtfoto: groene band)
    d = profile_spin("AR_Pagode_F_ringdak", [(R_GEVEL - 0.1, Z_GOOT), (5.6, Z_GOOT + 1.2), (5.6, Z_GOOT + 1.0), (R_GEVEL - 0.1, Z_GOOT - 0.15)], steps=N * 4)
    d["rol"] = "groen"
    # groene schutting rond het open midden (luchtfoto: steekt ~2 m boven het ringdak uit)
    w = profile_spin("AR_Pagode_F_schutting", [(5.55, Z_GOOT), (5.55, Z_GOOT + 1.6), (5.40, Z_GOOT + 1.6), (5.40, Z_GOOT)], steps=96)   # onder de gevelpunten (video: van opzij niet zichtbaar)
    w["rol"] = "groen"
    # rood ribbendak binnen de schutting, van de schutting naar de trommel
    b = profile_spin("AR_Pagode_F_binnendak", [(5.40, Z_GOOT + 1.0), (2.2, Zr(4.6)), (2.2, Zr(4.5)), (5.40, Z_GOOT + 0.9)], steps=96)
    b["rol"] = "rood"
    for k in range(24):
        a = k / 24 * 2 * math.pi
        krul(f"AR_Pagode_F_binnenrib_{k:02d}", [(5.35 * math.cos(a), 5.35 * math.sin(a), Z_GOOT + 1.05),
                                               (2.25 * math.cos(a), 2.25 * math.sin(a), Zr(4.62))], 0.07, 1.0, "rood")
    # middentrommel: ACHThoek, onder iets wijder (Pagode-toren-close.jpg), gouden pilasters op de hoeken
    t = cylinder("AR_Pagode_F_trommel", 2.30, 2.6, segments=8, radius_top=2.05, location=(0, 0, Zr(4.5 + 1.3)))
    t.rotation_euler = (0, 0, math.pi / 8)
    t["rol"] = "trommel"
    for k in range(8):
        a = (k + 0.5) / 8 * 2 * math.pi          # op de hoeken (trommel 22.5 graden gedraaid)
        p = cylinder(f"AR_Pagode_F_pilaster_{k:02d}", 0.07, 2.54, segments=6, location=(2.20 * math.cos(a), 2.20 * math.sin(a), Zr(5.8)))
        p["rol"] = "goud"
    band = profile_spin("AR_Pagode_F_trommelband", [(2.25, Zr(6.85)), (2.25, Zr(7.1)), (2.0, Zr(7.1)), (2.0, Zr(6.85))], steps=64)
    band["rol"] = "groen"
    # klokdaken (zijfoto: 7.1-8.3, 8.3-9.4, 9.4-10.4 boven de rand)
    klokdak("AR_Pagode_F_dak1", 3.1, Zr(7.1), 1.25, Zr(8.3), n_hoek=8, horen=0.9)
    cylinder("AR_Pagode_F_trommel2", 1.15, 0.37, segments=16, location=(0, 0, Zr(8.435)))["rol"] = "trommel"   # overlapt dak1 en dak2
    klokdak("AR_Pagode_F_dak2", 1.95, Zr(8.6), 0.75, Zr(9.4), n_hoek=8, horen=0.6)
    cylinder("AR_Pagode_F_trommel3", 0.7, 0.27, segments=16, location=(0, 0, Zr(9.485)))["rol"] = "trommel"   # overlapt dak2 en dak3
    klokdak("AR_Pagode_F_dak3", 1.25, Zr(9.6), 0.45, Zr(10.4), n_hoek=8, horen=0.45)
    # balustrade als open hek (video 6:45: groene spijlen, bovenregel, onderregel, rode palen op de kielen)
    for ob in list(bpy.data.objects):
        if ob.name == "AR_Pagode_balustrade":
            bpy.data.objects.remove(ob, do_unlink=True)
    rb = 8.3
    for nm, z0_, z1_ in (("boven", DEK + 1.22, DEK + 1.32), ("onder", DEK + 0.12, DEK + 0.20), ("midden", DEK + 1.02, DEK + 1.08)):
        o = profile_spin(f"AR_Pagode_F_hek_{nm}", [(rb - 0.05, z0_), (rb + 0.05, z0_), (rb + 0.05, z1_), (rb - 0.05, z1_)], steps=N * 8)
        o["rol"] = "groen"
    n_sp = int(2 * math.pi * rb / 0.13)
    bm = bmesh.new()
    palen = [(i + 0.5) / N * 2 * math.pi for i in range(N)]
    for k in range(n_sp):
        a = k / n_sp * 2 * math.pi
        if min(abs((a - pa + math.pi) % (2 * math.pi) - math.pi) for pa in palen) * rb < 0.16:
            continue     # geen spijl in een paal (z-fighting)
        m = Matrix.Translation((rb * math.cos(a), rb * math.sin(a), DEK + 0.66)) @ Matrix.Rotation(a, 4, "Z")
        r = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.025, 0.025, 0.95), verts=r["verts"])
        bmesh.ops.transform(bm, matrix=m, verts=r["verts"])
    o = new_mesh_object("AR_Pagode_F_hek_spijlen", bm, "LOW"); o["rol"] = "groen"
    # radiale ribben onder de schotel (zijkant_onder.jpg: ~24 lichte ribben)
    for k in range(24):
        a = k / 24 * 2 * math.pi
        c, s_ = math.cos(a), math.sin(a)     # ribben volgen de holle paraplu (02: rand RAND, r 5.4 +0.55, naaf r 1.0 +2.5), 6 cm eronder
        krul(f"AR_Pagode_F_schotelrib_{k:02d}", [(1.3 * c, 1.3 * s_, RAND + 2.30), (5.4 * c, 5.4 * s_, RAND + 0.50), (8.15 * c, 8.15 * s_, RAND + 0.02)],
             0.08, 1.0, "onderkant")
    # rollen naar blokkering-objecten die blijven
    for ob in bpy.data.objects:
        if ob.name.startswith("AR_Pagode_") and "rol" not in ob:
            n = ob.name
            ob["rol"] = ("onderkant" if "schotel" in n else "sierrand" if "sierrand" in n else "dek" if "dek" in n else
                         "groen" if "balustrade" in n else "kernwand" if "kernwand" in n else "rood" if ("paal" in n or "plafond" in n) else
                         "wit" if "bank" in n else "goud" if "spits" in n else "rood")
    log("vormen klaar:", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objecten")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--master", required=True)
    a = p.parse_args(argv_after_dashes())
    scene = open_master(a.master)
    clear_owned()
    build(scene, a)
    save_master(a.master)
    log("saved", a.master)
