"""02_blockout Assepoester: meters, Z op, gevel kijkt naar -Y (west), +X = zuid, z=0 = maaiveld binnenplaats.
Maten uit asset-brief.md: BAG-footprint (ref/osm_lokaal.json) voor de plattegrond, ref/front.jpg (98 px/m display) voor hoogtes.
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
PHASE = "02_blockout"; OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns); globals().update({k: v for k, v in _ns.items() if callable(v)})

# ---- plattegrond (BAG-footprint in modelcoordinaten) ------------------------------------------
WING = (-6.34, -2.33, 0.90, 4.12)       # entreevleugel x0,x1,y0,y1
GAL_Y = 1.62                            # voorvlak gaanderij
MAIN = (-3.80, 5.19, 4.72, 11.67)       # hoofdhuis 9.0 m (BAG); front.jpg: 0.62 m zuidelijker t.o.v. de vleugel dan BAG -> foto aangehouden
BACK = (-3.80, 5.19, 11.67, 14.21)
TOWER = (2.42, 5.19)                    # front.jpg (overlay 104.5 px/m): 1045-1340 px
TOWER_OUT = 0.30                        # uitsprong toren (inferred)
PORCH = (3.25, 5.95, 0.0, 4.71)           # BAG x1 6.34; front.jpg stijlen tot 5.8, dakrand 5.91 -> foto aangehouden voor het zichtbare portiek
# ---- hoogtes (front.jpg, grond y=845 display, 98 px/m) ----------------------------------------
WING_EAVE, WING_CORN, WING_TOP = 2.65, 3.03, 4.16
GAL_HIGH, GAL_LOW, PLINTH = 3.03, 2.10, 0.77
MAIN_EAVE, MAIN_CORN = 5.30, 5.60
MANS_BREAK, MANS_TOP = 6.42, 6.52        # front.jpg: dakrand op 6.5 m -> steile kraag (60 gr) met vrijwel plat bovendak (inferred, showhal eronder)
TOWER_CORN, TOWER_TOP, TOWER_FIN = 5.10, 7.65, 8.00
PORCH_EAVE, PORCH_TOP = 2.60, 2.86
BACK_H = 5.0                             # achterbouw (inferred, niet zichtbaar op front.jpg)


def roof(name, x0, x1, y0, y1, z0, z1, inset_x, inset_y, z2=None, inset2=None, L="LOW"):
    """schild/mansarde/piramide: ring op z0 (dakrand), ring op z1 ingesprongen, optioneel 3e ring."""
    bm = bmesh.new()
    def ring(ix, iy, z):
        return [bm.verts.new(p) for p in ((x0 + ix, y0 + iy, z), (x1 - ix, y0 + iy, z), (x1 - ix, y1 - iy, z), (x0 + ix, y1 - iy, z))]
    rs = [ring(0, 0, z0), ring(inset_x, inset_y, z1)]
    if z2 is not None:
        rs.append(ring(inset2[0], inset2[1], z2))
    for a, b in zip(rs, rs[1:]):
        for i in range(4):
            bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    top = [v for v in bm.verts if abs(v.co.z - (z2 if z2 is not None else z1)) < 1e-4]
    if len(top) >= 3:
        try: bm.faces.new(top)
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object(name, bm, L)


def bx(name, x0, x1, y0, y1, z0, z1, L="LOW"):
    return box(name, (x1 - x0, y1 - y0, z1 - z0), L, ((x0 + x1) / 2, (y0 + y1) / 2, z0), base_at_origin=True)


def build(master):
    open_master(master); clear_owned(); L = "LOW"
    O = 0.25   # dakoverstek
    # 1 entreevleugel + schilddak (nok langs x)
    x0, x1, y0, y1 = WING
    bx("BLK_vleugel", x0, x1, y0, y1 + 0.6, 0, WING_EAVE)
    bx("BLK_vleugel_kroonlijst", x0 - 0.08, x1 + 0.08, y0 - 0.08, y1 + 0.6, WING_EAVE, WING_CORN)
    d = (y1 - y0) / 2 + O
    roof("BLK_vleugel_dak", x0 - 0.1, x1 + 0.1, y0 - O, y1 + 0.6, WING_CORN, WING_TOP, 1.6, d)
    for x in (-4.57, -3.56):    # pinakels op de nokuiteinden (front.jpg 325 / 430 px), tot 4.6 m
        cylinder("BLK_pinakel", 0.06, 0.45, L, segments=8, location=(x, (y0 - O + y1 + 0.6) / 2, WING_TOP + 0.22))
    bx("BLK_entree_boog", -4.35 - 0.54, -4.35 + 0.54, y0 - 0.05, y0 + 0.02, 0, 2.14)
    for x in (-5.7, -3.0):
        bx("BLK_raam_vleugel", x - 0.25, x + 0.25, y0 - 0.05, y0 + 0.02, 1.2, 2.35)
    # 3 gaanderij: lessenaarsdak van hoofdhuis (3.03) naar goot (2.10) voor het voorvlak
    gx0, gx1 = WING[1], PORCH[0]
    bx("BLK_gaanderij_plint", gx0, gx1, GAL_Y, MAIN[2], 0, PLINTH)
    bx("BLK_gaanderij_planken", gx0, gx1, GAL_Y - 0.05, GAL_Y + 0.05, PLINTH, GAL_LOW)
    bm = bmesh.new()
    yf = GAL_Y - 0.35
    vs = [bm.verts.new(p) for p in ((gx0, yf, GAL_LOW), (gx1, yf, GAL_LOW), (gx1, MAIN[2], GAL_HIGH), (gx0, MAIN[2], GAL_HIGH))]
    bm.faces.new(vs); f2 = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in f2["geom"] if isinstance(e, bmesh.types.BMVert)]: v.co.z += 0.12
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_mesh_object("BLK_gaanderij_dak", bm, L)
    bx("BLK_gaanderij_baksteenrand", gx0, gx1, MAIN[2] - 0.12, MAIN[2], GAL_HIGH, GAL_HIGH + 0.12)
    # 4 hoofdhuis + kroonlijst + mansarde
    x0, x1, y0, y1 = MAIN
    bx("BLK_hoofdhuis", x0, x1, y0, y1, 0, MAIN_EAVE)
    bx("BLK_kroonlijst", x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, MAIN_EAVE, MAIN_CORN)
    roof("BLK_mansarde", x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, MAIN_CORN, MANS_BREAK, 0.55, 0.55, MANS_TOP, (2.2, 2.2))
    bx("BLK_achterbouw", BACK[0] + 0.5, BACK[1] - 0.5, BACK[2], BACK[3], 0, BACK_H)
    for x in (-2.97, -1.70, 1.32):     # front.jpg overlay 492/625/940 px
        bx("BLK_raam_1e", x - 0.34, x + 0.34, y0 - 0.05, y0 + 0.02, 3.7, 4.9)
    bx("BLK_raam_1e_breed", -0.17 - 0.43, -0.17 + 0.43, y0 - 0.05, y0 + 0.02, 3.7, 4.9)
    for x in (-0.87, 0.55):
        bx("BLK_luik", x - 0.22, x + 0.22, y0 - 0.1, y0 - 0.02, 3.7, 4.9)
    for x in (-0.95, 0.45):    # dakkapellen front.jpg overlay 700 / 850 px
        bx("BLK_dakkapel", x - 0.3, x + 0.3, y0 + 0.2, y0 + 1.2, MAIN_CORN, 6.45)
        roof("BLK_dakkapel_spits", x - 0.36, x + 0.36, y0 + 0.15, y0 + 1.2, 6.45, 6.95, 0.36, 0.0)
    for x, h in ((-1.75, 6.89), (0.69, 6.70)):
        bx("BLK_schoorsteen", x - 0.18, x + 0.18, y0 + 1.6, y0 + 2.0, 5.5, h)
    # 8 toren
    tx0, tx1 = TOWER
    ty0 = y0 - TOWER_OUT; ty1 = ty0 + (tx1 - tx0)
    bx("BLK_toren", tx0, tx1, ty0, ty1, 0, TOWER_CORN - 0.25)
    bx("BLK_toren_kroonlijst", tx0 - 0.12, tx1 + 0.12, ty0 - 0.12, ty1 + 0.12, TOWER_CORN - 0.25, TOWER_CORN)
    c = (tx1 - tx0) / 2 + 0.12
    roof("BLK_toren_spits", tx0 - 0.12, tx1 + 0.12, ty0 - 0.12, ty1 + 0.12, TOWER_CORN, TOWER_TOP, c, c)
    cylinder("BLK_makelaar", 0.04, TOWER_FIN - TOWER_TOP, L, segments=8, location=((tx0 + tx1) / 2, (ty0 + ty1) / 2, (TOWER_TOP + TOWER_FIN) / 2))
    bx("BLK_toren_dakkapel", 3.46, 3.96, ty0 - 0.05, ty0 + 0.6, 5.3, 6.2)
    bx("BLK_toren_raam", 4.07 - 0.12, 4.07 + 0.12, ty0 - 0.05, ty0 + 0.02, 3.65, 4.5)
    # 9 uitgangsportiek (lessenaar tegen de toren)
    px0, px1, py0, py1 = PORCH
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((px0 - 0.2, py0 - 0.2, PORCH_EAVE), (px1 + 0.05, py0 - 0.2, PORCH_EAVE), (px1 + 0.05, ty0, PORCH_TOP + 0.4), (px0 - 0.2, ty0, PORCH_TOP + 0.4))]
    bm.faces.new(vs); f2 = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in f2["geom"] if isinstance(e, bmesh.types.BMVert)]: v.co.z += 0.1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_mesh_object("BLK_portiek_dak", bm, L)
    bx("BLK_portiek_plankwand", px0, px0 + 0.12, py0, py1, 0, PORCH_EAVE)
    for x in (px0 + 0.75, px1 - 0.1):
        bx("BLK_portiek_stijl", x - 0.08, x + 0.08, py0 + 0.05, py0 + 0.21, 0, PORCH_EAVE)
    bx("BLK_portiek_achterwand", px0, px1, py1 - 0.2, py1, 0, PORCH_EAVE)
    bx("BLK_portiek_zijwand", px1 - 0.12, px1, py0 + 0.3, py1, 0, PORCH_EAVE)
    bx("BLK_maaiveld", -9, 9, -6, 16, -0.05, 0)
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
