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
    "beton_groen": ((0.035, 0.07, 0.04), 0.85, 0.0, None, 0),     # donkergroen geverfd beton (Pagodegewicht.jpg)
    "beton_donker": ((0.05, 0.05, 0.05), 0.9, 0.0, None, 0),
    "rooster":   ((0.18, 0.19, 0.19), 0.55, 0.7, None, 0),
    "hek":       ((0.02, 0.02, 0.02), 0.45, 0.6, None, 0),
    "staal":     ((0.25, 0.26, 0.27), 0.4, 0.9, None, 0),
    "chroom":    ((0.8, 0.8, 0.8), 0.15, 1.0, None, 0),
    "wit_glans": ((0.82, 0.80, 0.74), 0.3, 0.0, None, 0),
    "grind":     ((0.20, 0.18, 0.15), 0.95, 0.0, None, 0),
    "beton_groen_licht": ((0.12, 0.20, 0.14), 0.9, 0.0, None, 0),   # groene bakvloer (Pagode-bak-2023.jpg)
    "natuursteen": ((1, 1, 1), 0.85, 0.0, "natuursteen", 0.8),
    "vlonder":   ((1, 1, 1), 0.8, 0.0, "vlonder", 0.4),
    "klinker":   ((1, 1, 1), 0.85, 0.0, "klinker", 0.5),
    "bord":      ((1, 1, 1), 0.4, 0.0, "bord", 0),
    "staal_groen": ((0.03, 0.12, 0.08), 0.5, 0.6, None, 0),
    "hek_open":  ((0.03, 0.12, 0.08), 0.5, 0.6, None, 0),
    "armzijde":  ((0.78, 0.72, 0.62), 0.5, 0.0, None, 0),
    # 12_omgeving (video fmEZsIkqsl8)
    "brons":     ((0.09, 0.06, 0.035), 0.45, 0.8, None, 0),      # lantaarnpalen
    "lamp":      ((1.0, 0.84, 0.58), 0.3, 0.0, None, 0),         # lantaarnglas (Neon in Roblox)
    "lamp_groen": ((0.2, 1.0, 0.45), 0.3, 0.0, None, 0),         # tourniquetlampjes
    "glas":      ((0.55, 0.65, 0.66), 0.05, 0.0, None, 0),       # ramen controlehuisje
    "dak_donker": ((0.06, 0.06, 0.07), 0.7, 0.0, None, 0),
    "aarde":     ((0.07, 0.045, 0.03), 0.95, 0.0, None, 0),      # bloemenperk
    "reling":    ((0.02, 0.045, 0.03), 0.4, 0.6, None, 0),       # donkergroene wachtrijreling
    "bord_blauw": ((0.48, 0.74, 0.80), 0.4, 0.0, None, 0),
    "ingangsbord": ((1, 1, 1), 0.4, 0.0, "ingangsbord", 0),
    "uitgangsbord": ((1, 1, 1), 0.4, 0.0, "uitgangsbord", 0),
    "uitgangsboog": ((1, 1, 1), 0.4, 0.0, "uitgangsboog", 0),
    "breuksteen": ((1, 1, 1), 0.9, 0.0, "breuksteen", 0.9),      # keermuren wachtrij (video 0:04-0:30)
    # 14_planten
    "bamboe":    ((1, 1, 1), 0.6, 0.0, "bamboe", 0),             # bladkaart (alpha)
    "blad":      ((1, 1, 1), 0.6, 0.0, "blad", 0),               # bladkaart (alpha)
    "spar":      ((1, 1, 1), 0.7, 0.0, "spar", 0),               # sparrentak (alpha)
    "naald":     ((1, 1, 1), 0.8, 0.0, "naald", 0),
    "haag":      ((1, 1, 1), 0.8, 0.0, "haag", 0),
    "bloem":     ((1, 1, 1), 0.7, 0.0, "bloem", 0),
    "schors":    ((1, 1, 1), 0.9, 0.0, "schors", 0),
    "bamboestam": ((0.42, 0.45, 0.16), 0.45, 0.0, None, 0),
    # 15_toko (video 1:02)
    "tokorand":  ((1, 1, 1), 0.5, 0.0, "tokorand", 0),
    "tokopaneel": ((1, 1, 1), 0.5, 0.0, "tokopaneel", 0),
    "parasol":   ((1, 1, 1), 0.8, 0.0, "parasol", 0),
    "dak_toko":  ((0.22, 0.23, 0.25), 0.7, 0.0, None, 0),
    "rotan":     ((0.48, 0.34, 0.18), 0.8, 0.0, None, 0),
    # 16_gondoletta
    "rood_hek":  ((0.55, 0.04, 0.05), 0.5, 0.0, None, 0),
    "beton_licht": ((0.55, 0.52, 0.47), 0.85, 0.0, None, 0),
    "asfalt":    ((0.22, 0.22, 0.22), 0.9, 0.0, None, 0),
    "wilg":      ((1, 1, 1), 0.7, 0.0, "wilg", 0),
    # 17_steenwerk (losse 3D-stenen, video 0:04-0:39)
    "steen":     ((1, 1, 1), 0.9, 0.0, "steen", 0.6),
    "pluk":      ((1, 1, 1), 0.8, 0.0, "pluk", 0),               # naaldplukken niwaki (alpha)
    "naald_donker": ((0.025, 0.045, 0.025), 0.9, 0.0, None, 0),  # kern van de niwakiwolken
    "voeg":      ((0.045, 0.04, 0.035), 0.95, 0.0, None, 0),     # achterwand tussen de stenen
    "graniet":   ((0.34, 0.33, 0.31), 0.8, 0.0, None, 0),        # neuzen tribunerijen
    "huisrand":  ((1, 1, 1), 0.5, 0.0, "huisrand", 0),           # kroonrand controlehuisje (04g)
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
        if tex in ("bamboe", "blad", "spar", "wilg", "pluk"):          # bladkaarten: alpha uit de textuur
            nt.links.new(it.outputs["Alpha"], b.inputs["Alpha"])
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
    """Doosprojectie in wereldmaat. Per vlak een geheel getal eraf: Roblox bewaart UV's met beperkte precisie, bij
    parkcoordinaten (~350) verschoof de textuur per driehoek. Voor herhalende texturen is een hele verschuiving onzichtbaar."""
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    mw = ob.matrix_world; alle = []
    for f in bm.faces:
        n = (mw.to_3x3() @ f.normal); a = max(range(3), key=lambda i: abs(n[i]))
        uvs = []
        for l in f.loops:
            p = mw @ l.vert.co
            u, v = [(p.y, p.z), (p.x, p.z), (p.x, p.y)][a]
            uvs.append((u / schaal, v / schaal))
        alle.append((f, uvs, a))
    zet_uv(bm, uv, alle)
    bm.to_mesh(me); bm.free()


def zet_uv(bm, uv, alle):
    """Een geheel getal per OBJECT eraf (rond het midden): naadloos binnen het vlak, kleine getallen. Per vlak verschuiven gaf
    in Roblox lijnen langs elke driehoek (mipmap op de sprong); niets verschuiven gaf bij ~350 verschoven driehoeken (precisie)."""
    groepen = {}
    for f, uvs, g in alle: groepen.setdefault(g, []).extend(uvs)        # per projectierichting een eigen verschuiving
    schuif = {g: (round(sum(u for u, _ in l) / len(l)), round(sum(v for _, v in l) / len(l))) for g, l in groepen.items()}
    for f, uvs, g in alle:
        du, dv = schuif[g]
        for l, (u, v) in zip(f.loops, uvs): l[uv].uv = (u - du, v - dv)


def uv_muur(ob, schaal, cx=360.0, cy=47.5):
    """Muren: u langs de muur, v = hoogte. Gebogen muren (straal rond het bakmidden ~constant): booglengte; rechte/schuine
    muren: langs de hoofdrichting. Bovenvlakken: x/y. Per vlak een geheel getal eraf (precisie in Roblox)."""
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    mw = ob.matrix_world
    pts = [mw @ v.co for v in bm.verts]
    rs = [math.hypot(p.x - cx, p.y - cy) for p in pts]
    boog = (max(rs) - min(rs)) < 1.0
    if boog:
        rm = sum(rs) / len(rs)
    else:
        mx = sum(p.x for p in pts) / len(pts); my = sum(p.y for p in pts) / len(pts)
        sxx = sum((p.x - mx) ** 2 for p in pts); syy = sum((p.y - my) ** 2 for p in pts); sxy = sum((p.x - mx) * (p.y - my) for p in pts)
        hoek = 0.5 * math.atan2(2 * sxy, sxx - syy); dx, dy = math.cos(hoek), math.sin(hoek)
    alle = []
    for f in bm.faces:
        n = (mw.to_3x3() @ f.normal)
        uvs = []
        for l in f.loops:
            p = mw @ l.vert.co
            if abs(n.z) > 0.7: u, v = p.x, p.y
            elif boog: u, v = rm * math.atan2(p.y - cy, p.x - cx), p.z
            else: u, v = p.x * dx + p.y * dy, p.z
            uvs.append((u / schaal, v / schaal))
        alle.append((f, uvs, abs(n.z) > 0.7))
    zet_uv(bm, uv, alle)
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


def uv_bord(ob):
    """Bordtekst (bovenste kwart van de textuur) op de twee grote vlakken, randen effen."""
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.verify()
    vs = [v.co for v in bm.verts]
    xs = sorted(set(round(v.x, 4) for v in vs)); zs = [v.z for v in vs]; z0, z1 = min(zs), max(zs)
    for f in bm.faces:
        n = f.normal
        groot = abs(n.z) < 0.3 and max(abs(n.x), abs(n.y)) > 0.9 and f.calc_area() > 0.5
        for l in f.loops:
            if groot:
                c = l.vert.co; t = Vector((-n.y, n.x, 0)).normalized(); us = [v.dot(t) for v in [ll.vert.co for ll in f.loops]]
                l[uv].uv = ((c.dot(t) - min(us)) / (max(us) - min(us)), 0.75 + 0.25 * (c.z - z0) / (z1 - z0))
            else:
                l[uv].uv = (0.5, 0.3)
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
        if rol == "arm":                 # 08_arm: zijvlakken (normaal langs y) = sier (UV al gezet), randvlakken = effen
            ob.data.materials.append(mats["armzijde"])
            for p in ob.data.polygons:   # materials.clear() zet de indexen terug op 0
                p.material_index = 0 if abs(p.normal.y) > 0.9 else 1
            n += 1; continue
        if ob.type == "MESH" and ob.get("uv_vast"):     # borden: UV gezet in 12_omgeving
            n += 1; continue
        if ob.type == "MESH":
            uv_laag(ob.data)
            if rol == "sierveld": uv_driehoek(ob)
            elif rol == "windveer": uv_veer(ob)
            elif rol == "trommel" and "trommel2" not in ob.name and "trommel3" not in ob.name: uv_trommel(ob)
            elif rol == "sierrand": uv_cilinder(ob, 1.0)
            elif rol == "kernwand": uv_cilinder(ob, 1.2)
            elif rol in ("klinker", "natuursteen", "vlonder"): uv_doos(ob, 1.0 if rol == "klinker" else 2.0)
            elif rol == "breuksteen" and len(ob.data.vertices) > 60: uv_muur(ob, 2.0)     # muren (rotsblokken: doos)
            elif rol == "tokopaneel": uv_doos(ob, 1.0)
            elif rol in ("breuksteen", "naald", "haag", "bloem", "schors"):
                uv_doos(ob, {"breuksteen": 2.0, "naald": 1.0, "haag": 0.8, "bloem": 0.6, "schors": 1.0}[rol])
            elif rol == "bord": uv_bord(ob)
            else: uv_doos(ob, 1.5)
        n += 1
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(arg.master))
    print("[05_materials]", n, "objecten, materialen:", sorted(mats))


main()
