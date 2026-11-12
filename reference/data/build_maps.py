import xml.etree.ElementTree as ET, math, json, os, csv
from PIL import Image, ImageDraw, ImageFont
root=ET.parse("reference/data/efteling_osm.xml").getroot()
nodes={}; 
for n in root.iter("node"): nodes[n.get("id")]=(float(n.get("lat")),float(n.get("lon")))
# local metric frame, origin = approx park centre (Pardoes Promenade / centre)
LAT0,LON0=51.6500,5.0455
def xy(lat,lon):
    x=(lon-LON0)*111320*math.cos(math.radians(LAT0)); y=(lat-LAT0)*110574
    return (round(x,2),round(y,2))
ways=[]
for w in root.iter("way"):
    tags={t.get("k"):t.get("v") for t in w.findall("tag")}
    pts=[xy(*nodes[nd.get("ref")]) for nd in w.findall("nd") if nd.get("ref") in nodes]
    if len(pts)<2: continue
    ways.append({"id":w.get("id"),"tags":tags,"pts":pts})
rels=[]
for r in root.iter("relation"):
    tags={t.get("k"):t.get("v") for t in r.findall("tag")}
    if tags.get("name"): rels.append({"id":r.get("id"),"tags":tags,"members":[(m.get("type"),m.get("ref"),m.get("role")) for m in r.findall("member")]})
def cat(t):
    if "attraction" in t: return "attraction:"+t["attraction"]
    if t.get("tourism")=="attraction": return "attraction"
    if "building" in t: return "building:"+t["building"]
    if t.get("natural")=="water" or t.get("waterway"): return "water"
    if "highway" in t: return "path:"+t["highway"]
    if t.get("railway"): return "rail:"+t["railway"]
    if t.get("leisure"): return "leisure:"+t["leisure"]
    if t.get("landuse"): return "landuse:"+t["landuse"]
    if t.get("amenity"): return "amenity:"+t["amenity"]
    return "other"
# export named objects with bbox/size
rows=[]
for w in ways:
    t=w["tags"]; c=cat(t)
    if not t.get("name") and not c.startswith("attraction"): continue
    xs=[p[0] for p in w["pts"]]; ys=[p[1] for p in w["pts"]]
    closed=w["pts"][0]==w["pts"][-1]
    L=sum(math.dist(w["pts"][i],w["pts"][i+1]) for i in range(len(w["pts"])-1))
    rows.append({"naam":t.get("name",""),"type":c,"x_min":min(xs),"x_max":max(xs),"y_min":min(ys),"y_max":max(ys),"breedte_m":round(max(xs)-min(xs),1),"diepte_m":round(max(ys)-min(ys),1),"omtrek_of_lengte_m":round(L,1),"gesloten":closed,"hoogte":t.get("height",""),"levels":t.get("building:levels",""),"osm_id":w["id"],"punten":w["pts"]})
# node attractions
for n in root.iter("node"):
    t={tt.get("k"):tt.get("v") for tt in n.findall("tag")}
    if t.get("name") and ("attraction" in t or t.get("tourism")=="attraction" or t.get("shop") or t.get("amenity")):
        x,y=xy(float(n.get("lat")),float(n.get("lon")))
        rows.append({"naam":t["name"],"type":"punt:"+cat(t),"x_min":x,"x_max":x,"y_min":y,"y_max":y,"breedte_m":0,"diepte_m":0,"omtrek_of_lengte_m":0,"gesloten":False,"hoogte":t.get("height",""),"levels":"","osm_id":n.get("id"),"punten":[(x,y)]})
rows.sort(key=lambda r:(r["type"],r["naam"]))
json.dump({"origin":{"lat":LAT0,"lon":LON0,"info":"x = oost (m), y = noord (m). Roblox: X=x, Z=-y, 1 stud = 0.28 m -> deel door 0.28 of gebruik 1 stud = 1 m"},"objecten":rows},open("reference/data/efteling_objecten_meters.json","w"),indent=1,ensure_ascii=False)
with open("reference/data/efteling_objecten_meters.csv","w",newline="") as f:
    wr=csv.DictWriter(f,fieldnames=[k for k in rows[0] if k!="punten"],extrasaction="ignore"); wr.writeheader(); wr.writerows(rows)
print(len(rows),"named/attraction objects")
for r in rows:
    if r["type"].startswith("attraction") or r["type"].startswith("punt:attraction"): print(f'{r["naam"]:40s} {r["type"]:28s} {r["breedte_m"]:6.1f} x {r["diepte_m"]:6.1f} m  centre=({(r["x_min"]+r["x_max"])/2:.0f},{(r["y_min"]+r["y_max"])/2:.0f}) h={r["hoogte"]}')
# ---- scale map render (PNG) 0.25 m/px over park bbox
X0,X1,Y0,Y1=-700,650,-700,750
S=4 # px per m
W=(X1-X0)*S; Hh=(Y1-Y0)*S
im=Image.new("RGB",(W,Hh),(232,240,220)); d=ImageDraw.Draw(im)
def P(p): return ((p[0]-X0)*S, (Y1-p[1])*S)
try: font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",22); fs=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",16)
except: font=fs=ImageFont.load_default()
order=["landuse","leisure","water","building","attraction","path","rail","amenity","other"]
col={"water":(150,195,235),"building":(205,190,170),"attraction":(230,150,120),"leisure":(200,225,190),"landuse":(215,230,205)}
for key in order:
    for w in ways:
        c=cat(w["tags"]);
        if not c.startswith(key): continue
        pts=[P(p) for p in w["pts"]]; closed=w["pts"][0]==w["pts"][-1]
        if key in("water","building","attraction","leisure","landuse") and closed and len(pts)>2:
            d.polygon(pts,fill=col[key],outline=(90,80,70) if key!="water" else (110,150,200))
        elif key=="path":
            hw=w["tags"].get("highway"); d.line(pts,fill=(255,255,255) if hw in("footway","pedestrian","path") else (180,170,160),width=6 if hw in("footway","pedestrian") else 10)
        elif key=="rail": d.line(pts,fill=(60,60,60),width=3)
        elif key=="attraction": d.line(pts,fill=(200,80,60),width=4)
for r in rows:
    if r["naam"] and (r["type"].startswith("attraction") or r["type"].startswith("punt:attraction") or r["type"].startswith("building")):
        cx=(r["x_min"]+r["x_max"])/2; cy=(r["y_min"]+r["y_max"])/2; px,py=P((cx,cy))
        f=font if "attraction" in r["type"] else fs
        tw=d.textlength(r["naam"],font=f); d.rectangle([px-tw/2-3,py-12,px+tw/2+3,py+12],fill=(255,255,255,200)); d.text((px-tw/2,py-11),r["naam"],fill=(20,20,20),font=f)
# grid every 100 m + scale bar
for gx in range(X0,X1+1,100):
    x=(gx-X0)*S; d.line([(x,0),(x,Hh)],fill=(170,170,170),width=1); d.text((x+3,3),f"x={gx}",fill=(80,80,80),font=fs)
for gy in range(Y0,Y1+1,100):
    y=(Y1-gy)*S; d.line([(0,y),(W,y)],fill=(170,170,170),width=1); d.text((3,y+3),f"y={gy}",fill=(80,80,80),font=fs)
d.rectangle([60,Hh-80,60+200*S,Hh-60],fill=(0,0,0)); d.text((60,Hh-110),"200 m   (raster = 100 m, oorsprong 0,0 = midden park, x=oost y=noord)   © OpenStreetMap contributors",fill=(0,0,0),font=font)
im.save("reference/plattegrond/Efteling_op_schaal_OSM_4px_per_m.png")
# ---- stitch tiles
z=17; x0,x1,y0,y1=67368,67377,43496,43505
mpp=156543.03*math.cos(math.radians(51.65))/2**z
tim=Image.new("RGB",((x1-x0+1)*256,(y1-y0+1)*256),"white")
for x in range(x0,x1+1):
    for y in range(y0,y1+1):
        p=f"reference/data/tiles/{z}_{x}_{y}.png"
        if os.path.exists(p): tim.paste(Image.open(p).convert("RGB"),((x-x0)*256,(y-y0)*256))
td=ImageDraw.Draw(tim); px=int(200/mpp); th=tim.size[1]
td.rectangle([40,th-60,40+px,th-45],fill="black"); td.text((40,th-90),f"200 m  ({mpp:.3f} m/px)  © OpenStreetMap contributors",fill="black",font=font)
tim.save("reference/plattegrond/OSM_tegels_Efteling_z17.png")
print("maps written", im.size, tim.size, mpp)
