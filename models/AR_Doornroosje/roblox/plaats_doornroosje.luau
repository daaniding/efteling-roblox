-- Doornroosje (Anton Pieck, 1952): kasteel (build/03_kasteel.py) en omgeving (build/03_omgeving.py: trappen, terras, poortgebouwen, rotswand).
-- Modelframe = OSM-assen (x oost, y noord), oorsprong = zwaartepunt OSM 55423166 = studs (362.96, -262.92). Blender (x,y,z) komt binnen als
-- (-x, z, y) * S; 180 graden draaien geeft (x, z, -y) = OSM-oost/noord. Draai daarna roblox/terrein_doornroosje.luau.
local KASTEEL = 72662319855699
local OMG = 81500410436295
local TEXK = {stuc = {77110781107423, 128120219253424}, pannen = {101795661533503, 119097044281865}, natuursteen = {87356248662327, 129593775568038}, hout = {127262555803237, 139506160174223}}
local TEXO = {natuursteen = {91479890265743, 122623927306763}, stuc = {127706923842439, 91768953229023}, pannen = {82422996216148, 120991762495924}, rots = {137203545511570, 118989078565245}}
local ORIGIN = CFrame.new(362.96, 2.0, -262.92) * CFrame.Angles(0, math.pi, 0)
local S = 3
local M = {venster = {Color3.fromRGB(14, 14, 16), "Glass"}, glas = {Color3.fromRGB(150, 130, 80), "Glass"}, ijzer = {Color3.fromRGB(20, 20, 20), "Metal"},
	goud = {Color3.fromRGB(214, 166, 60), "Metal"}, binnen = {Color3.fromRGB(26, 20, 16), "SmoothPlastic"}, hout = {Color3.fromRGB(70, 78, 72), "WoodPlanks"},
	stuc = {Color3.fromRGB(222, 216, 200), "Plastic"}, pannen = {Color3.fromRGB(130, 72, 52), "Slate"}, natuursteen = {Color3.fromRGB(150, 146, 136), "Slate"},
	rots = {Color3.fromRGB(140, 140, 132), "Rock"},
	kei = {Color3.fromRGB(128, 130, 132), "Slate"}, muur = {Color3.fromRGB(206, 198, 178), "Limestone"}, dekst = {Color3.fromRGB(184, 178, 162), "Limestone"},
	klimop = {Color3.fromRGB(40, 66, 30), "Grass"}, lamp = {Color3.fromRGB(255, 196, 120), "Neon"}, wapenrood = {Color3.fromRGB(150, 24, 20), "SmoothPlastic"}}
local function laad(id, naam, texmap)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
	local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
	local onb = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
		if string.match(p.Name, "^LAMP_") then                                              -- lantaarns: warm licht met schaduw
			p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 180, 110); pl.Range = 14; pl.Brightness = 1.3; pl.Shadows = true; pl.Parent = p
			continue
		end
		if string.match(p.Name, "^COLL_") then
			p.Transparency = 1; p.CanCollide = true; p.CanQuery = true; p.CastShadow = false; p.Parent = bots
			if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
			continue
		end
		local tex = string.match(p.Name, "__TEX_([%w_]-)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
		if tex and texmap[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.SmoothPlastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. texmap[tex][1]; sa.NormalMap = "rbxassetid://" .. texmap[tex][2]; sa.Parent = p
			pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
		elseif key and M[key] then p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
		else table.insert(onb, p.Name) end
	end
	m.WorldPivot = ORIGIN
	return m, #bots:GetChildren(), onb
end
local k, bk, o1 = laad(KASTEEL, "DoornroosjeKasteel", TEXK)
local o, bo, o2 = laad(OMG, "DoornroosjeOmgeving", TEXO)
local decs = {}
for _, t in ipairs({TEXK, TEXO}) do for _, v in pairs(t) do for _, id in ipairs(v) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(decs, d) end end end
pcall(function() game:GetService("ContentProvider"):PreloadAsync(decs) end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("kasteel %d (botsing %d), omgeving %d (botsing %d); onbekend %s %s", #k:GetChildren(), bk, #o:GetChildren(), bo, onb(o1), onb(o2))
