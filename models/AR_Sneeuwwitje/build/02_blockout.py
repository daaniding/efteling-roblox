"""02_blockout Sneeuwwitje: kasteeltje + grot. Meters, Z op, gevel kijkt naar -Y (oost), +X = noord, z=0 = maaiveld plein.
Maten: asset-brief.md (OSM 60095998 / 60095997 + ref/front.jpg op 84 px/m display)."""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
PHASE = "02_blockout"; OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns); globals().update({k: v for k, v in _ns.items() if callable(v)})

def bx(name, x0, x1, y0, y1, z0, z1, L="LOW"):
    return box(name, (x1 - x0, y1 - y0, z1 - z0), L, ((x0 + x1) / 2, (y0 + y1) / 2, z0), base_at_origin=True)

def cone(name, cx, cy, r, z0, z1, segs=24, L="LOW"):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=0.0, depth=z1 - z0)
    bmesh.ops.translate(bm, vec=(cx, cy, (z0 + z1) / 2), verts=bm.verts); return new_mesh_object(name, bm, L)

def cyl(name, cx, cy, r, z0, z1, segs=24, L="LOW"):
    return cylinder(name, r, z1 - z0, L, segments=segs, location=(cx, cy, (z0 + z1) / 2))

def prism(name, pts, z0, z1, L="LOW"):
    bm = bmesh.new(); vs = [bm.verts.new((x, y, z0)) for x, y in pts]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, 0, z1 - z0), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return new_mesh_object(name, bm, L)

def gable_roof(name, x0, x1, y0, y1, z0, z1, L="LOW"):   # zadeldak, nok langs x
    bm = bmesh.new(); ym = (y0 + y1) / 2
    v = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, ym, z1), (x1, ym, z1))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return new_mesh_object(name, bm, L)

def build(master):
    open_master(master); clear_owned(); L = "LOW"
    # ---- linkertoren met trapgevel (front.jpg 175..572 px)
    bx("BLK_linkertoren", -7.19, -2.46, 0.51, 5.77, 0, 3.8)            # voet tot de hoektorentjes (front.jpg 175..600 px)
    bx("BLK_toren_romp", -6.54, -2.79, 0.51, 5.77, 3.8, 6.73)           # romp 3.75 breed (230..545 px)
    bx("BLK_trap1", -5.76, -3.44, 0.51, 1.3, 6.73, 7.74)                # trede 2.3 breed (295..490 px)
    bx("BLK_trap2", -5.25, -4.24, 0.51, 1.3, 7.74, 8.75)                # top 1.0 breed (355..440 px)
    gable_roof("BLK_toren_dak", -6.54, -2.79, 1.3, 5.77, 6.73, 8.0)     # dak achter de trapgevel (inferred)
    cyl("BLK_kroon", -4.75, 0.9, 0.25, 8.75, 9.8, 8)
    bx("BLK_ingang", -4.79 - 0.83, -4.79 + 0.83, 0.45, 0.53, 0, 2.68)
    bx("BLK_gevelraam", -4.69 - 0.3, -4.69 + 0.3, 0.45, 0.53, 4.4, 5.7)
    bx("BLK_schild", -4.69 - 0.45, -4.69 + 0.45, 0.42, 0.51, 3.3, 4.2)
    for x in (-7.25, -2.13):   # uitgekraagde hoektorentjes
        cyl("BLK_hoektoren", x, 0.6, 0.57, 3.8, 5.65, 12)
        cone("BLK_hoektoren_kegel", x, 0.6, 0.64, 5.65, 7.25, 12)
        cyl("BLK_makelaar", x, 0.6, 0.04, 7.25, 7.9, 6)
    # ---- weergang met kantelen, dak met dakkapellen en daktorentje
    bx("BLK_weergang", -2.46, 3.39, 1.31, 4.14, 0, 4.17)
    for i in range(7):
        x0 = -2.46 + i * 0.86
        bx("BLK_merlon", x0, x0 + 0.62, 1.31, 1.71, 4.17, 4.58)
    for xa in (-0.4, 2.27):
        bx("BLK_blindboog", xa - 0.85, xa + 0.85, 1.25, 1.33, 0, 2.9)
    gable_roof("BLK_dak_weergang", -2.46, 3.39, 1.9, 6.0, 4.17, 5.7)
    for xd in (-0.52, 0.97, 2.39):
        bx("BLK_dakkapel", xd - 0.3, xd + 0.3, 1.85, 2.6, 4.3, 5.4)
        cone("BLK_dakkapel_spits", xd, 2.0, 0.42, 5.4, 6.0, 4)
    cyl("BLK_daktoren", 1.32, 3.6, 0.7, 4.5, 6.3, 12)
    cone("BLK_daktoren_kegel", 1.32, 3.6, 0.8, 6.3, 7.85, 12)
    # ---- achterbouw (hal) en ronde toren
    bx("BLK_hal", -1.06, 3.25, 4.14, 9.28, 0, 4.4)
    gable_roof("BLK_dak_hal", -1.16, 3.35, 4.14, 9.38, 4.4, 5.7)
    bx("BLK_achter_links", -7.19, -1.06, 5.77, 9.28, 0, 4.4)
    cyl("BLK_rondetoren", 5.45, 2.2, 2.05, 0, 5.35, 32)
    cyl("BLK_rondetoren_fries", 5.45, 2.2, 2.15, 4.8, 5.65, 32)
    cone("BLK_rondetoren_kegel", 5.45, 2.2, 2.25, 5.65, 8.65, 32)
    cyl("BLK_makelaar_rond", 5.45, 2.2, 0.05, 8.65, 9.5, 6)
    # ---- grot: kunstrots langs de OSM-vorm, ruinemuur bij de ingang, ruinetorentje
    grot = [(15.28, 2.26), (18.64, 1.76), (21.95, -1.88), (21.34, -2.42), (23.69, -6.61), (22.53, -7.16), (21.46, -7.62), (19.6, -6.57), (18.58, -6.61),
            (17.7, -6.55), (16.88, -6.4), (16.08, -6.16), (15.25, -5.83), (14.63, -5.5), (13.88, -5.0), (13.4, -4.59), (13.06, -4.28), (12.46, -3.62),
            (10.18, -2.96), (10.42, -1.63), (10.68, -0.31), (12.49, -0.51)]
    prism("BLK_grot", grot, 0, 3.8)
    bx("BLK_ruinemuur", 9.6, 10.6, -3.6, 0.6, 0, 4.4)
    cyl("BLK_ruinetoren", 15.5, -1.0, 1.1, 3.8, 7.0, 12)
    bx("BLK_maaiveld", -10, 26, -12, 12, -0.05, 0)
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]))

if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
