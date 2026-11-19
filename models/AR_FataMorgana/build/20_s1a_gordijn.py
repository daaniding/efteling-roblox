"""20_s1a_gordijn: sectie 1 (Jungle), stuk 1a: het gordijn waar de boot de instaphal verlaat (Daan 19 nov: "per sectie, en elke sectie
ook weer stuk voor stuk", "videos erbij pakken per fase", "het moet echt erop lijken, animaties etcetera").
Referentie: POV 2025 (youtube mV6qzpGgLjc, ref/video/s1/t118..t125.5): onder de westgaanderij hangt over de hele doorvaart een breed
grijsbeige plooigordijn aan een lichte rail, zoom net boven het water; het gaat in het midden open als de boot eraan komt (123 s) en
daarachter ligt de rotsboog met de jungle. Op de groene band onder de gaanderijrand erboven in lichtgele letters
"Niet schommelen // Nicht schaukeln / No rocking // Interdit de se balancer" (119,5 s). Eftepedia: "een opening, bedekt met een beige gordijn".
Maten: doorvaart in de westmuur y -328,9..-324,1 (16_instaphal GY0/GY1), bovenkant -0,4; gordijn in het muurvlak x -3,62.
Twee helften als losse onderdelen (gordijn_l = noord, gordijn_r = zuid) zodat FataMorganaS1Gordijn ze open kan schuiven.
Modelstelsel = 02/03. Deel "junglegordijn" (geen cijfers/underscores: plaats_modellen leest de rol uit FM_<rol>_<n>_<deel>). Gebruik: blender --background --python build/20_s1a_gordijn.py"""
import bpy, bmesh, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]; L = G3["L"]
OWNER = "phase:20_s1a_gordijn"
KL = {"gordijn_l": (0.66, 0.6, 0.53), "gordijn_r": (0.66, 0.6, 0.53), "gordijnrail": (0.72, 0.66, 0.58), "s1_bord": (1, 1, 1)}
G = {r: bmesh.new() for r in KL}
ZW = -3.2
XG = -3.62                       # gordijnvlak (in de muuropening, 0,12 m achter de halkant)
GY0, GY1, YM = -328.9, -324.1, -326.5
ZT, ZO = -0.5, ZW + 0.12         # bovenkant gordijn (onder de rail), zoom
XWI = -3.5 + 2.6                 # binnenrand westgaanderij (bord op de groene band eronder, kant hal)


def P(x, y, z): return L(x, y) + Vector((0, 0, z))


def helft(rol, ya, yb):
    """plooigordijn van ya naar yb: plooien ~0,2 m, diepte 0,1 m; zoom licht golvend; beide kanten zichtbaar (twee vlakken)"""
    bm = G[rol]; uvl = bm.loops.layers.uv.verify()
    n = max(8, round(abs(yb - ya) / 0.025)); rijen = [ZO, ZO + 0.35, (ZO + ZT) / 2, ZT]
    for kant in (1, -1):
        rij_v = []
        for z in rijen:
            rv = []
            for i in range(n + 1):
                t = i / n; y = ya + (yb - ya) * t
                golf = 0.05 * math.sin(2 * math.pi * (y - YM) / 0.2)
                zz = z + (0.03 * math.sin(7.3 * y) if z == ZO else 0.0)
                rv.append(bm.verts.new(P(XG + golf + kant * 0.006, y, zz)))
            rij_v.append(rv)
        for j in range(len(rijen) - 1):
            for i in range(n):
                q = [rij_v[j][i], rij_v[j][i + 1], rij_v[j + 1][i + 1], rij_v[j + 1][i]]
                f = bm.faces.new(q if kant > 0 else q[::-1])
                for lp, (u, v) in zip(f.loops if kant > 0 else f.loops, [(i / n, j), ((i + 1) / n, j), ((i + 1) / n, j + 1), (i / n, j + 1)] if kant > 0 else [(i / n, j + 1), ((i + 1) / n, j + 1), ((i + 1) / n, j), (i / n, j)]):
                    lp[uvl].uv = (u * 4, v)
    # kant 1 = normaal naar +x (jungle), kant -1 = naar de hal; omdraaien waar nodig
    bm.normal_update()


def doos(rol, x0, y0, x1, y1, z0, z1):
    bm = G[rol]; v = [bm.verts.new(P(x, y, z)) for z in (z0, z1) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[i] for i in f])


def bouw():
    helft("gordijn_l", YM + 0.02, GY1 - 0.05)          # noordhelft
    helft("gordijn_r", GY0 + 0.05, YM - 0.02)          # zuidhelft
    doos("gordijnrail", XG - 0.05, GY0 - 0.05, XG + 0.05, GY1 + 0.05, ZT, -0.41)
    for y in (GY0 + 0.1, YM, GY1 - 0.1):               # beugels
        doos("gordijnrail", XG - 0.04, y - 0.04, XG + 0.12, y + 0.04, -0.47, -0.41)
    # bord: op de groene band van de gaanderijrand (onderwand -0,45..0, 0,04 naar de hal), kant hal, gecentreerd boven de doorvaart
    bm = G["s1_bord"]; uvl = bm.loops.layers.uv.verify(); x = XWI + 0.05; ya, yb = YM - 0.3, YM - 4.1   # zuidelijk van de hoek met de noordgaanderij (YNI -326,2), anders half verstopt
    q = [bm.verts.new(P(x, ya, -0.41)), bm.verts.new(P(x, yb, -0.41)), bm.verts.new(P(x, yb, -0.04)), bm.verts.new(P(x, ya, -0.04))]
    f = bm.faces.new(q)
    for lp, uv in zip(f.loops, [(1, 0), (0, 0), (0, 1), (1, 1)]): lp[uvl].uv = uv   # leesbaar vanuit de hal


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in G.items():
        if not bm.faces: continue
        bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if rol == "gordijnrail"])
        if rol == "s1_bord":                                         # bord kijkt naar de hal (+x)
            for f in bm.faces:
                f.normal_update()
                if f.normal.dot(L(1, 0) - L(0, 0)) < 0: f.normal_flip()
        me = bpy.data.meshes.new("FM_s1_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_s1_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "junglegordijn"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL[rol], 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[20_s1a_gordijn] klaar:", {o.name: len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER})


main()
