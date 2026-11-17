"""05_materials: materiaal SI_<rol> en UV's per rol voor de Sirocco (draai NA 03_forms en 04_decor).
  riet, beschot : rond om het dak: u = boog / 2 m, v = straal / 2 m (riet loopt van nok naar rand; beschot = ringplanken)
  platform, subschijf : planair over de hele draaischijf (14 m = 1 textuur)
  romp, romp_hout : cilindrisch per boot: u = boog / 2 m, v = hoogte / 1 m;  schubben: 0,8 m per textuur
  sierpaneel : u = 0..1 over de breedte van het paneel, v = 0..1 over de hoogte
  net : u = langs het hek / 1 m, v = hoogte / 1 m;  overige : doosprojectie in wereldmaat (1 textuur = 1,5 m)
Gebruik: blender --background --python build/05_materials.py -- --master AR_Sirocco_master.blend"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
master = os.path.abspath(a[a.index("--master") + 1])
bpy.ops.wm.open_mainfile(filepath=master)


def mat(rol):
    n = "SI_" + rol
    m = bpy.data.materials.get(n) or bpy.data.materials.new(n)
    return m


def hoek_uv(bm, uvl, f_uv):
    """per vlak: u via hoek (zonder sprong over -pi/pi binnen een vlak)"""
    for f in bm.faces:
        ref = None
        for lp in f.loops:
            u, v, h = f_uv(lp.vert.co)
            if ref is None: ref = h
            d = (h - ref + math.pi) % (2 * math.pi) - math.pi
            lp[uvl].uv = (u(ref + d), v)


n = 0
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render or "rol" not in o: continue
    rol = o["rol"]
    me = o.data
    me.materials.clear(); me.materials.append(mat(rol))
    for p in me.polygons: p.material_index = 0
    bm = bmesh.new(); bm.from_mesh(me)
    uvl = bm.loops.layers.uv.verify()
    M = o.matrix_world
    if o.get("uv_klaar"):
        pass                                           # UV's al gezet (07_omgeving: ingangsbord op de atlas)
    elif rol in ("riet", "beschot"):
        hoek_uv(bm, uvl, lambda co: ((lambda h: h * 8.85 / 2.0), math.hypot((M @ co).x, (M @ co).y) / 2.0, math.atan2((M @ co).y, (M @ co).x)))
    elif rol in ("platform", "subschijf"):
        for f in bm.faces:
            for lp in f.loops:
                w = M @ lp.vert.co; lp[uvl].uv = ((w.x + 7) / 14, (w.y + 7) / 14)
    elif rol == "schubben":
        pass                                           # UV's al gezet in 03_forms (vlak langs de boeg)
    elif rol in ("romp", "romp_hout", "romp_blauw", "sierpaneel"):
        ws = [M @ v.co for v in bm.verts]
        c = sum(ws, Vector()) / len(ws)
        if rol == "sierpaneel":
            hs = [math.atan2(w.y - c.y, w.x - c.x) for w in ws]
            gem = math.atan2(sum(math.sin(h) for h in hs), sum(math.cos(h) for h in hs))
            ds = [(h - gem + math.pi) % (2 * math.pi) - math.pi for h in hs]
            lo, hi = min(ds), max(ds); zs = [w.z for w in ws]; z0, z1 = min(zs), max(zs)
            for f in bm.faces:
                for lp in f.loops:
                    w = M @ lp.vert.co; d = (math.atan2(w.y - c.y, w.x - c.x) - gem + math.pi) % (2 * math.pi) - math.pi
                    lp[uvl].uv = ((d - lo) / max(1e-6, hi - lo), (w.z - z0) / max(1e-6, z1 - z0))
        else:
            per = 0.8 if rol == "schubben" else 2.0; hoog = 0.8 if rol == "schubben" else 1.0
            # bootmidden = middelpunt van de voet: neem het gemiddelde van alle hoekpunten van dit deel
            hoek_uv(bm, uvl, lambda co: ((lambda h: h * 0.85 / per), ((M @ co).z) / hoog, math.atan2((M @ co).y - c.y, (M @ co).x - c.x)))
    elif rol == "net" and o.get("owner") == "phase:07_omgeving":     # rechte hekstukken langs de wachtrij: u langs het vlak
        for f in bm.faces:
            a0, a1 = M @ f.loops[0].vert.co, M @ f.loops[1].vert.co
            d = Vector((a1.x - a0.x, a1.y - a0.y, 0)); d = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
            for lp in f.loops:
                w = M @ lp.vert.co; lp[uvl].uv = (w.x * d.x + w.y * d.y, w.z)
    elif rol == "net":
        for f in bm.faces:
            for lp in f.loops:
                w = M @ lp.vert.co; lp[uvl].uv = (math.atan2(w.y, w.x) * 7.25 / 1.0, w.z / 1.0)
    else:
        S = 1.5
        for f in bm.faces:
            nrm = (M.to_3x3() @ f.normal); ax = max(range(3), key=lambda i: abs(nrm[i]))
            for lp in f.loops:
                w = M @ lp.vert.co
                lp[uvl].uv = ((w.y / S, w.z / S) if ax == 0 else (w.x / S, w.z / S) if ax == 1 else (w.x / S, w.y / S))
    bm.to_mesh(me); bm.free(); n += 1
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=master)
print("[05_materials]", n, "objecten")
