import json,urllib.request,urllib.parse,time,os,re,sys
H={"User-Agent":"efteling-reference/1.0 (student project)"}
def api(p):
    p.update({"format":"json"})
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)
    for i in range(6):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
        except Exception as e:
            time.sleep(10*(i+1))
    return {}
def subcats(c):
    d=api({"action":"query","list":"categorymembers","cmtitle":c,"cmtype":"subcat","cmlimit":"500"})
    return [m["title"] for m in d.get("query",{}).get("categorymembers",[])]
def files(c,n=4):
    d=api({"action":"query","generator":"categorymembers","gcmtitle":c,"gcmtype":"file","gcmlimit":"40","prop":"imageinfo","iiprop":"url|size|mime|extmetadata","iiurlwidth":"1600"})
    out=[]
    for pg in d.get("query",{}).get("pages",{}).values():
        ii=pg.get("imageinfo",[{}])[0]
        if ii.get("mime","") in("image/jpeg","image/png") and ii.get("width",0)>=1000:
            out.append((pg["title"],ii.get("thumburl") or ii["url"],ii.get("extmetadata",{}).get("LicenseShortName",{}).get("value",""),ii.get("extmetadata",{}).get("Artist",{}).get("value","")))
    out.sort(key=lambda x:x[0])
    return out[:n]
time.sleep(5)
dark=subcats("Category:Dark ride in the Efteling"); time.sleep(5)
coast=subcats("Category:Roller coasters at Efteling"); time.sleep(5)
realms=subcats("Category:Realms in the Efteling"); time.sleep(5)
print("dark",dark); print("coast",coast); print("realms",realms)
prev=json.load(open("reference/data/commons_ride_cats.json"))
cats=["Category:Efteling"]+dark+coast+prev["rides"]+prev["sprookjesbos"]+["Category:Aquanura","Category:Raveleijn","Category:Huis van de Vijf Zintuigen","Category:Efteling Theater","Category:Sprookjesbos"]
seen=set(); credits=[]
for c in cats:
    if c in seen: continue
    seen.add(c)
    if "Category:Dark ride" in c or "Category:Roller coasters" in c or "Category:Rides in" in c: continue
    name=re.sub(r"[^A-Za-z0-9]+","_",c.replace("Category:","")).strip("_")
    d=os.path.join("reference/fotos",name); os.makedirs(d,exist_ok=True)
    fl=files(c, 6 if c=="Category:Efteling" else 4)
    for i,(t,u,lic,art) in enumerate(fl):
        ext=".jpg" if u.lower().endswith((".jpg",".jpeg")) or "jpg" in u.lower() else ".png"
        p=os.path.join(d,f"{i+1}{ext}")
        if os.path.exists(p): continue
        try:
            urllib.request.urlretrieve(u,p) if False else open(p,"wb").write(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read())
            credits.append(f"{p} | {t} | {lic} | {re.sub('<[^>]+>','',art)}")
        except Exception as e:
            print("ERR",t,e)
        time.sleep(1.5)
    print(c,len(fl),flush=True)
    time.sleep(4)
open("reference/fotos/BRONNEN.txt","w").write("Foto's van Wikimedia Commons. bestand | titel | licentie | auteur\n"+"\n".join(credits))
print("DONE")
