"""05_materials: materialen + UV's per rol voor de Pagode-gondel. Draai NA 02_blockout.py en 03_forms.py.
Rollen (ob["rol"]) -> materiaal; UV per soort onderdeel:
  sierveld  : driehoek van het object (lokaal x,z) -> 0..1 (foto-textuur, voet onder, punt boven)
  windveer  : u langs de veer (1 m per herhaling), v over de breedte
  trommel   : per zijvlak u = 0..1 over het vlak, v = 0..1 over de hoogte (een paneel per zijde)
  sierrand, kernwand : cilindrisch (u = boog / herhaallengte)
  pannen en de rest : doosprojectie in wereldmaat (1 textuur = 1.5 m)
Gebruik: blender --background --python build/05_materials.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math, argparse
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(D, 'textures')

# rol -> (kleur, ruwheid, metaal, textuur-naam of None, normaal-sterkte)
ROLLEN = {
    "pannen":    ((0.62, 0.20, 0.07), 0.45, 0.0, "pannen", 0.6),
    "sierveld":  ((1, 1, 1), 0.55, 0.0, "sierveld", 0.8),
    "windveer":  ((1, 1, 1), 0.5, 0.0, "windveer", 0.5),
    "trommel":   ((1, 1, 1), 0.6, 0.0, "trommel", 0.8),
    "sierrand":  ((1, 1, 1), 0.55, 0.0, "sierrand", 0.4),
    "kernwand":  ((1, 1, 1), 0.5, 0.0, "kernwand", 0.3),
    "groen":     ((0.012, 0.22, 0.14), 0.4, 0.0, None, 0),
    "rib":       ((0.85, 0.83, 0.78), 0.45, 0.0, None, 0),
    "vlam":      ((0.86, 0.83, 0.76), 0.4, 0.0, None, 0),
    "goud":      ((0.66, 0.42, 0.10), 0.3, 1.0, None, 0),
    "rood":      ((0.30, 0.025, 0.03), 0.5, 0.0, None, 0),
    "onderkant": ((0.045, 0.012, 0.012), 0.75, 0.0, None, 0),   # bijna zwart-roodbruin (foto van onder)
    "dek":       ((0.25, 0.20, 0.16), 0.8, 0.0, None, 0),
    "wit":       ((0.80, 0.80, 0.76), 0.6, 0.0, None, 0),
    "arm":       ((1, 1, 1), 0.5, 0.0, "arm", 0.4),
    "armzijde":  ((0.78, 0.72, 0.62), 0.5, 0.0, None, 0),
}


def materiaal(rol):
    naam = "PG_" + rol
    m = bpy.data.materials.get(naam)
    if m: bpy.data.materials.remove(m)
    m = bpy.data.materials.new(naam); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    kleur, ruw, met, tex, ns = ROLLEN[rol]
    b.inputs["Base Color"].default_value = (*kleur, 1); b.inputs["Roughness"].default_value = ruw; b.inputs["Metallic"].default_value = met
    if tex:
        it = nt.nodes.new("ShaderNodeTexImage"); it.image = bpy.data.images.load(os.path.join(T, f"PG_{tex}_kleur.png"), check_existing=True)
        nt.links.new(it.outputs["Color"], b.inputs["Base Color"])
        if rol == "pannen":     # pannen: textuur x oranje is al in de textuur; vermenigvuldigen niet nodig
            pass
        nn = os.path.join(T, f"PG_{tex}_normaal.png")
        if os.path.exists(nn) and ns > 0:
            ni = nt.nodes.new("ShaderNodeTexImage"); ni.image = bpy.data.images.load(nn, check_existing=True); ni.image.colorspace_settings.name = "Non-Color"
            nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = ns
            nt.links.new(ni.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def uv_laag(me):
    return me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")


def uv_doos(ob, schaal=1.5):
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    mw = ob.matrix_world
    for f in bm.faces:
        n = (mw.to_3x3() @ f.normal); a = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = mw @ l.vert.co
            u, v = [(p.y, p.z), (p.x, p.z), (p.x, p.y)][a]
            l[uv].uv = (u / schaal, v / schaal)
    bm.to_mesh(me); bm.free()


def uv_driehoek(ob):
    me = ob.data; xs = [v.co.x for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops:
            c = l.vert.co; l[uv].uv = ((c.x - x0) / (x1 - x0), (c.z - z0) / (z1 - z0))
    bm.to_mesh(me); bm.free()


def uv_veer(ob):
    me = ob.data; vs = [v.co.copy() for v in me.vertices]
    as_ = (vs[1] - vs[0]); as_.y = 0; L = as_.length; as_.normalize()
    dw = Vector((-as_.z, 0, as_.x))
    br = max(abs((v - vs[0]).dot(dw)) for v in vs) or 1
    bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops:
            q = l.vert.co - vs[0]; l[uv].uv = (q.dot(as_) / 1.0, abs(q.dot(dw)) / br)
    bm.to_mesh(me); bm.free()


def uv_cilinder(ob, herhaal, hoogte=None):
    me = ob.data; mw = ob.matrix_world
    zs = [(mw @ v.co).z for v in me.vertices]; z0 = min(zs); h = hoogte or (max(zs) - z0) or 1
    bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        c = mw @ f.calc_center_median(); ac = math.atan2(c.y, c.x)
        for l in f.loops:
            p = mw @ l.vert.co; a = math.atan2(p.y, p.x)
            if a - ac > math.pi: a -= 2 * math.pi
            if ac - a > math.pi: a += 2 * math.pi
            r = math.hypot(p.x, p.y)
            l[uv].uv = (a * r / herhaal, (p.z - z0) / h)
    bm.to_mesh(me); bm.free()


def uv_trommel(ob):
    """Een paneel per zijvlak: u over de breedte van het vlak, v over de hoogte."""
    me = ob.data; zs = [v.co.z for v in me.vertices]; z0, z1 = min(zs), max(zs)
    bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        if abs(f.normal.z) > 0.7:
            for l in f.loops: l[uv].uv = (0.5, 0.5)
            continue
        vs = [l.vert.co for l in f.loops]
        t = Vector((-f.normal.y, f.normal.x, 0)).normalized()
        us = [v.dot(t) for v in vs]; u0, u1 = min(us), max(us)
        for l in f.loops:
            l[uv].uv = ((l.vert.co.dot(t) - u0) / (u1 - u0), (l.vert.co.z - z0) / (z1 - z0))
    bm.to_mesh(me); bm.free()


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    p = argparse.ArgumentParser(); p.add_argument("--master", required=True); arg = p.parse_args(a)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(arg.master))
    mats = {r: materiaal(r) for r in ROLLEN}
    n = 0
    for ob in bpy.data.objects:
        if not ob.name.startswith("AR_Pagode") or ob.type not in ("MESH", "CURVE"):
            continue
        rol = ob.get("rol", "rood")
        if ob.name.startswith("AR_Pagode_sierrand"): rol = "sierrand"
        if rol not in mats: rol = "rood"
        ob.data.materials.clear(); ob.data.materials.append(mats[rol])
        if rol == "arm":                 # 08_arm: vlak 0 = zijvlak met ruiten (UV al gezet), vlak 1 = effen randvlak
            ob.data.materials.append(mats["armzijde"]); n += 1; continue
        if ob.type == "MESH":
            uv_laag(ob.data)
            if rol == "sierveld": uv_driehoek(ob)
            elif rol == "windveer": uv_veer(ob)
            elif rol == "trommel" and "trommel2" not in ob.name and "trommel3" not in ob.name: uv_trommel(ob)
            elif rol == "sierrand": uv_cilinder(ob, 1.0)
            elif rol == "kernwand": uv_cilinder(ob, 1.2)
            else: uv_doos(ob, 1.5)
        n += 1
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(arg.master))
    print("[05_materials]", n, "objecten, materialen:", sorted(mats))


main()
