"""maak_ritscript: schrijft roblox/pagode_rit.luau (opzet van de rijdende Pagode in Studio).
- laadt voet, arm en gondel (exports via build/11_export.py, ids in exports/asset_ids.json) met dezelfde aankleding als plaats_pagode.luau
- workspace.Pagode = Model met Voet, Arm, Gondel, Cilinders, Station; AsFrame (CFrameValue, draaias stand omhoog)
- afwerking (afwerking_pagode.luau) in de gondel, behalve de bakreling en de lantaarnlichten (Station)
- gondel: alle delen gelast aan een Kern (niet verankerd) met starre AlignPosition/AlignOrientation
- zet ServerScriptService.PagodeRit neer met de bron uit roblox/PagodeRit.server.luau
Draai NA maak_plaatsscript.py (gebruikt de kop van plaats_pagode.luau). Gebruik: python3 roblox/maak_ritscript.py"""
import os, json

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(D, 'roblox')
info = json.load(open(os.path.join(D, 'exports', 'export_info.json')))
kop = open(os.path.join(R, 'plaats_pagode.luau')).read().split('\n')[:76]
assert kop[-1].strip() == 'end', 'kop van plaats_pagode.luau veranderd'
plaats = open(os.path.join(R, 'plaats_pagode.luau')).read()
import re
regel = next(r for r in plaats.split('\n') if r.startswith('gondel:PivotTo('))
PIV = regel[len('gondel:PivotTo('):-1]
AS = info['draaias_lokaal']
JL = (-(0 - AS[0]) * 3, (0 - AS[2]) * 3, 0.0)          # gondelmidden (Blender 0,0,0) t.o.v. de as, lokaal in stud


def L(b): return 'Vector3.new(%.4f, %.4f, %.4f)' % (-b[0] * 3, b[2] * 3, b[1] * 3)


afw = open(os.path.join(R, 'afwerking_pagode.luau')).read()
afw = afw.replace('local g = workspace:WaitForChild("Pagode")', 'local g = gondel')
afw = afw.replace('return "afwerking: " .. #map:GetChildren() .. " onderdelen"', '')
cil = '\n'.join(
    f'''do local f = Instance.new("Folder"); f.Name = "Cil{k}"; f.Parent = cils
  f:SetAttribute("Voet", {L(c["voet"])}); f:SetAttribute("Kop", {L(c["kop"])})
  for _, d in ipairs({{{{"Huis", 0.72, Color3.fromRGB(228, 222, 206), Enum.Material.SmoothPlastic}}, {{"Stang", 0.34, Color3.fromRGB(205, 205, 210), Enum.Material.Metal}}}}) do
    local p = Instance.new("Part"); p.Name = d[1]; p.Shape = Enum.PartType.Cylinder; p.Anchored = true; p.CanCollide = false; p.CanTouch = false
    p.Size = Vector3.new(1, d[2] * S, d[2] * S); p.Color = d[3]; p.Material = d[4]; p.Parent = f
  end
end''' for k, c in enumerate(info['cilinders']))

bron = open(os.path.join(R, 'PagodeRit.server.luau')).read()
luau = '\n'.join(kop) + f'''

-- ===== rijdende Pagode: opzet (gegenereerd door roblox/maak_ritscript.py) =====
local PIV = {PIV}
local oudS = game:GetService("ServerScriptService"):FindFirstChild("PagodeRit"); if oudS then oudS:Destroy() end
local oud = workspace:FindFirstChild("Pagode"); if oud then oud:Destroy() end
local pag = Instance.new("Model"); pag.Name = "Pagode"; pag.Parent = workspace
local av = Instance.new("CFrameValue"); av.Name = "AsFrame"; av.Value = PIV; av.Parent = pag
pag:SetAttribute("GondelLokaal", Vector3.new({JL[0]:.4f}, {JL[1]:.4f}, {JL[2]:.4f}))
local function zet(id, naam) local m = laad(id, naam); aankleden(m, true); m:PivotTo(PIV); m.Parent = pag; return m end
local voet = zet(ID.AR_Pagode_voet, "Voet")
local arm = zet(ID.AR_Pagode_arm, "Arm")
local gondel = zet(ID.AR_Pagode_gondel, "Gondel")
for _, p in ipairs(arm:GetChildren()) do if p:IsA("BasePart") then p.CanCollide = false end end
-- afwerking (lampjes, lichtsnoeren, reling) in de gondel
do
{afw}
end
local station = Instance.new("Folder"); station.Name = "Station"; station.Parent = pag
for _, p in ipairs(gondel:GetDescendants()) do
  if p:IsA("BasePart") and (p.Name == "bakreling" or p.Name == "lantaarnlicht") then p.Parent = station end
end
-- hefcilinders (bewegen mee met de arm, zie PagodeRit)
local cils = Instance.new("Folder"); cils.Name = "Cilinders"; cils.Parent = pag
{cil}
-- gondel als een losse groep: alles gelast aan de kern, kern gestuurd door starre Align-constraints
local kern = Instance.new("Part"); kern.Name = "Kern"; kern.Size = Vector3.new(2, 2, 2); kern.Transparency = 1; kern.CanCollide = false
kern.CanQuery = false; kern.CanTouch = false; kern.Anchored = false
kern.CFrame = CFrame.new(PIV:PointToWorldSpace(pag:GetAttribute("GondelLokaal"))) * PIV.Rotation; kern.Parent = gondel
for _, p in ipairs(gondel:GetDescendants()) do
  if p:IsA("BasePart") and p ~= kern then
    p.Anchored = false; p.Massless = true
    local w = Instance.new("WeldConstraint"); w.Part0 = kern; w.Part1 = p; w.Parent = p
  end
end
gondel.PrimaryPart = kern
local at = Instance.new("Attachment"); at.Name = "Doel"; at.Parent = kern
local ap = Instance.new("AlignPosition"); ap.Mode = Enum.PositionAlignmentMode.OneAttachment; ap.Attachment0 = at
ap.RigidityEnabled = true; ap.Position = kern.Position; ap.Parent = kern
local ao = Instance.new("AlignOrientation"); ao.Mode = Enum.OrientationAlignmentMode.OneAttachment; ao.Attachment0 = at
ao.RigidityEnabled = true; ao.CFrame = kern.CFrame.Rotation; ao.Parent = kern
-- ritscript
local sc = Instance.new("Script"); sc.Name = "PagodeRit"; sc.Source = [==[{bron}]==]; sc.Parent = game:GetService("ServerScriptService")
local n = 0; for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") then n += 1 end end
return "Pagode rijklaar: gondel " .. n .. " delen, cilinders " .. #cils:GetChildren()
'''
open(os.path.join(R, 'pagode_rit.luau'), 'w').write(luau)
print('pagode_rit.luau', len(luau), 'tekens; PIV', PIV, 'JL', JL)
