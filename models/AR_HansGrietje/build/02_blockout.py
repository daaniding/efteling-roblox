"""02_blockout Hans en Grietje (snoephuisje). Meters, Z op, gevel kijkt naar -Y (WNW), +X = rechts (ZZO), oorsprong = midden BAG-footprint, z=0 maaiveld.
Maten: asset-brief.md (BAG 50911615 in modelframe, deur 1.45 m als maatstok in Hghuis-vk, erker/kooi uit de schilderfoto's)."""
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
def roof_y(name, x0, x1, y0, y1, z0, z1, L="LOW"):   # zadeldak, nok langs y
    bm = bmesh.new(); xm = (x0 + x1) / 2
    v = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (xm, y0, z1), (xm, y1, z1))]
    for f in ((0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2), (0, 3, 2, 1)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return new_mesh_object(name, bm, L)
def lean(name, x0, x1, y0, y1, zlow, zhigh, L="LOW"):   # lessenaarsdak, laag aan y0
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((x0, y0, zlow - 0.05), (x1, y0, zlow - 0.05), (x1, y1, zhigh - 0.05), (x0, y1, zhigh - 0.05),
                                    (x0, y0, zlow), (x1, y0, zlow), (x1, y1, zhigh), (x0, y1, zhigh))]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return new_mesh_object(name, bm, L)

def build(master):
    open_master(master); clear_owned(); L = "LOW"
    # hoofdhuis (BAG: x -3.15..1.25, y -2.12..2.7); voorgevel staat 0.87 achter de BAG-voorlijn (erker + trap ervoor)
    bx("BLK_huis", -3.15, 1.25, -1.25, 2.7, 0, 2.6)
    roof_y("BLK_dak", -3.45, 1.55, -1.45, 2.95, 2.5, 5.6)
    bx("BLK_gevelschoorsteen", -1.27, -0.63, -1.45, -0.9, 4.6, 6.0)          # witte stapel op de gevelpunt met de witte vogel
    bx("BLK_vogel_wit", -1.07, -0.82, -1.3, -0.9, 6.0, 6.4)
    # erker links voor (gootlijst 1.15, dak tot 2.05 tegen de gevel)
    bx("BLK_erker", -2.6, 0.1, -2.12, -1.25, 0, 1.0)
    lean("BLK_erkerdak", -2.8, 0.3, -2.45, -1.2, 0.95, 2.05)
    # trap rechts van de erker naar de deur (drempel 1.15)
    for i in range(4):
        bx("BLK_trede", 0.1, 1.35 - i * 0.12, -2.3 + i * 0.27, -1.25, 0, 0.29 * (i + 1))
    bx("BLK_deur", -0.66, 0.02, -1.29, -1.24, 1.15, 2.6)
    bx("BLK_katgat", -1.8, -1.35, -1.29, -1.24, 2.25, 2.55)
    bx("BLK_raam_boven", -1.45, -0.55, -1.29, -1.24, 3.35, 4.05)
    # bonte schoorsteen links tegen de gevel (snoepmozaiek)
    cyl("BLK_bonte_schoorsteen", -3.45, -1.0, 0.33, 0, 4.6, 12)
    # toren rechtsachter (BAG-uitbouw x 1.25..2.2, y 0.46..2.66)
    cyl("BLK_toren", 0.7, 2.2, 1.0, 0, 4.7, 24)
    cyl("BLK_toren_kraag", 0.7, 2.2, 1.25, 4.7, 5.0, 24)
    cone("BLK_toren_kegel", 0.7, 2.2, 1.3, 5.0, 6.7, 24)
    # overstek met steunbalken op de zuidgevel (x=1.25) + dakkapel
    bx("BLK_overstek", 1.25, 1.65, -1.2, 0.5, 1.75, 2.45)
    bx("BLK_dakkapel", 0.3, 1.5, -0.9, 0.2, 2.6, 3.5)
    # kooi van Hans rechts (goot 1.8, voorkant y -0.35)
    bx("BLK_kooi", 1.25, 3.4, 0.0, 2.2, 0, 1.8)
    roof_y("BLK_kooidak", 1.1, 3.65, -0.25, 2.4, 1.75, 2.7)
    bx("BLK_kooiraam", 1.85, 2.85, -0.05, 0.01, 0.55, 1.4)
    bx("BLK_grietje", 1.6, 2.05, -0.85, -0.4, 0, 0.75)
    # oven rechtsachter (vrijstaand)
    bx("BLK_oven", 5.2, 6.5, 0.2, 1.4, 0, 1.6)
    roof_y("BLK_ovendak", 5.05, 6.65, 0.05, 1.55, 1.55, 2.15)
    # tuin: binnenhek y -4.7, snoeppad, buitenmuur langs het hoofdpad (y -11.2) met tuinhek bij x -2.4
    bx("BLK_binnenhek_l", -4.2, -0.9, -4.75, -4.65, 0, 0.9); bx("BLK_binnenhek_r", 0.05, 2.6, -4.75, -4.65, 0, 0.9)
    bx("BLK_snoeppad", -1.0, 0.1, -10.9, -2.3, 0, 0.04)
    bx("BLK_muur_l", -8.5, -3.0, -11.4, -11.05, 0, 0.7); bx("BLK_muur_r", -1.8, 3.2, -11.4, -11.05, 0, 0.7)
    bx("BLK_muur_zij", -9.5, -9.15, -10.5, -5.0, 0, 0.7)
    for x in (-3.2, -1.6):
        bx("BLK_pijler", x - 0.25, x + 0.25, -11.5, -11.0, 0, 1.0)
    bx("BLK_maaiveld", -13, 13, -14, 8, -0.05, 0)
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]))

if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
