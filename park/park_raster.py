"""OSM -> materiaalraster (4 studs per cel) + boomposities + hagen, voor Roblox Terrain."""
import xml.etree.ElementTree as ET, math, json, random, sys
from PIL import Image, ImageDraw
random.seed(3)
root=ET.parse("reference/data/efteling_osm.xml").getroot()
LAT0,LON0=51.6500,5.0455
def xy(lat,lon): return ((lon-LON0)*111320*math.cos(math.radians(LAT0)), (lat-LAT0)*110574)
nodes={n.get("id"):xy(float(n.get("lat")),float(n.get("lon"))) for n in root.iter("node")}
ways={}
for w in root.iter("way"):
    tags={t.get("k"):t.get("v") for t in w.findall("tag")}
    pts=[nodes[nd.get("ref")] for nd in w.findall("nd") if nd.get("ref") in nodes]
    if len(pts)>=2: ways[w.get("id")]={"tags":tags,"pts":pts}
rels=[]
for r in root.iter("relation"):
    tags={t.get("k"):t.get("v") for t in r.findall("tag")}
    if tags.get("type")!="multipolygon": continue
    outers=[ways[m.get("ref")]["pts"] for m in r.findall("member") if m.get("type")=="way" and m.get("role")!="inner" and m.get("ref") in ways]
    inners=[ways[m.get("ref")]["pts"] for m in r.findall("member") if m.get("type")=="way" and m.get("role")=="inner" and m.get("ref") in ways]
    rels.append({"tags":tags,"outers":outers,"inners":inners})
# --- raster
CELL=4/3.0; X0,X1,Y0,Y1=-700,650,-700,750
NX=int((X1-X0)/CELL); NY=int((Y1-Y0)/CELL)
MAT={"grass":0,"water":1,"cobble":2,"asphalt":3,"ground":4,"sand":5,"wood":6,"concrete":7,"leafy":8,"mud":9,"pavement":10,"rock":11,"building":12}
img=Image.new("L",(NX,NY),MAT["grass"]); d=ImageDraw.Draw(img)
def P(p): return ((p[0]-X0)/CELL, (Y1-p[1])/CELL)
def poly(pts,v):
    if len(pts)>=3: d.polygon([P(p) for p in pts],fill=v)
def line(pts,width_m,v):
    w=max(1,int(round(width_m/CELL)))
    d.line([P(p) for p in pts],fill=v,width=w,joint="curve")
    r=w/2
    for p in pts: q=P(p); d.ellipse([q[0]-r,q[1]-r,q[0]+r,q[1]+r],fill=v)
def area_mat(t):
    if t.get("natural")=="water" or t.get("water") or t.get("landuse") in ("reservoir","basin"): return "water"
    if t.get("landuse") in ("forest",) or t.get("natural") in ("wood",): return "leafy"
    if t.get("natural") in ("scrub","shrubbery","heath"): return "leafy"
    if t.get("landuse") in ("grass","meadow","orchard","farmland") or t.get("natural")=="grassland" or t.get("leisure") in ("garden","park","playground","pitch"): return "grass"
    if t.get("landuse")=="flowerbed": return "mud"
    if t.get("natural") in ("sand","beach"): return "sand"
    if t.get("natural") in ("bare_rock","rock"): return "rock"
    if t.get("amenity")=="parking" or t.get("landuse") in ("retail","commercial","industrial"): return "asphalt"
    if t.get("highway") in ("pedestrian","footway") and t.get("area")=="yes": return surf_mat(t,"pavement")
    if t.get("leisure") in ("outdoor_seating",): return "pavement"
    return None
def surf_mat(t,default):
    s=t.get("surface","")
    return {"paving_stones":"cobble","sett":"cobble","cobblestone":"cobble","asphalt":"asphalt","paved":"pavement","concrete":"concrete","fine_gravel":"ground","gravel":"ground","compacted":"ground","sand":"sand","wood":"wood","grass":"grass","dirt":"ground","ground":"ground","unpaved":"ground"}.get(s,default)
def line_mat_w(t):
    h=t.get("highway"); 
    if t.get("waterway") in ("stream","ditch","canal"): return "water",float(t.get("width",2.5))
    if t.get("railway") in ("narrow_gauge","light_rail","monorail"): return None,0
    if h in ("pedestrian",): return surf_mat(t,"cobble"),float(t.get("width",6))
    if h in ("footway","path","steps"): return surf_mat(t,"pavement"),float(t.get("width",3))
    if h in ("cycleway",): return surf_mat(t,"asphalt"),float(t.get("width",3))
    if h in ("service","track","busway","platform"): return surf_mat(t,"asphalt"),float(t.get("width",4))
    if h in ("residential","unclassified","tertiary","secondary","trunk","trunk_link","primary"): return "asphalt",float(t.get("width",7))
    return None,0
# tekenvolgorde: grote vlakken eerst, dan water, dan paden
order={"grass":0,"leafy":1,"mud":2,"sand":2,"rock":2,"asphalt":2,"pavement":3,"water":4}
items=[]
for w in ways.values():
    t=w["tags"]
    closed=w["pts"][0]==w["pts"][-1]
    if closed and (area_mat(t) or t.get("building")):
        m=area_mat(t) or "building"
        if t.get("building") and not area_mat(t): m="building"
        items.append((order.get(m,2),"poly",w["pts"],[],m))
for r in rels:
    m=area_mat(r["tags"])
    if m: items.append((order.get(m,2),"mp",r["outers"],r["inners"],m))
items.sort(key=lambda i:i[0])
for _,kind,outers,inners,m in items:
    if kind=="poly": poly(outers,MAT[m])
    else:
        for o in outers: poly(o,MAT[m])
        for i in inners: poly(i,MAT["grass"] if m!="water" else MAT["grass"])
for w in ways.values():
    m,wd=line_mat_w(w["tags"])
    if m: line(w["pts"],wd,MAT[m])
# gebouwen op het eind (worden later door modellen vervangen): beton
for w in ways.values():
    if w["tags"].get("building") and w["pts"][0]==w["pts"][-1]: poly(w["pts"],MAT["building"])
img.save("park/park_raster_preview.png")
# RLE per rij (van y=Y1 boven naar beneden), hex materiaal
px=img.load(); rows=[]
for j in range(NY):
    out=[]; cur=px[0,j]; n=1
    for i in range(1,NX):
        v=px[i,j]
        if v==cur: n+=1
        else: out.append(f"{cur:x}{n}"); cur=v; n=1
    out.append(f"{cur:x}{n}"); rows.append(",".join(out))
json.dump({"cell_studs":4,"x0_m":X0,"y1_m":Y1,"nx":NX,"ny":NY,"mat":MAT,"rows":rows},open("park/park_raster.json","w"))
# --- bomen: in leafy-cellen 1 per ~30 m2, in gras binnen park 1 per 400 m2; niet op paden/water/gebouw
trees=[]
for j in range(NY):
    for i in range(NX):
        v=px[i,j]
        if v==MAT["leafy"] and random.random()<CELL*CELL/30: trees.append((i,j,0))
        elif v==MAT["grass"] and random.random()<CELL*CELL/420: trees.append((i,j,1))
def ok(i,j):
    for di in (-1,0,1):
        for dj in (-1,0,1):
            ii,jj=i+di,j+dj
            if 0<=ii<NX and 0<=jj<NY and px[ii,jj] in (MAT["water"],MAT["cobble"],MAT["asphalt"],MAT["pavement"],MAT["building"],MAT["concrete"],MAT["wood"]): return False
    return True
tl=[]
for i,j,k in trees:
    if not ok(i,j): continue
    x=X0+(i+random.random())*CELL; y=Y1-(j+random.random())*CELL
    tl.append([round(x,1),round(y,1),random.choice([0,0,1,2]) if k==0 else random.choice([0,1]),round(random.uniform(0.8,1.3),2),round(random.uniform(0,6.28),2)])
json.dump(tl,open("park/trees.json","w"))
# --- hagen en muren/hekken als segmenten
hedges=[];fences=[]
for w in ways.values():
    b=w["tags"].get("barrier")
    if b=="hedge": hedges.append([[round(p[0],1),round(p[1],1)] for p in w["pts"]])
    elif b in ("fence","wall","retaining_wall"): fences.append([b,[[round(p[0],1),round(p[1],1)] for p in w["pts"]]])
json.dump({"hedges":hedges,"fences":fences},open("park/barriers.json","w"))
import collections
cnt=collections.Counter(px[i,j] for j in range(0,NY,3) for i in range(0,NX,3))
print("grid",NX,NY,"trees",len(tl),"hedges",len(hedges),"fences",len(fences))
print({k:cnt[v] for k,v in MAT.items()})
