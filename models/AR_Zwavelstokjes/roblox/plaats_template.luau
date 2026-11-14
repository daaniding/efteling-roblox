-- Het Meisje met de Zwavelstokjes (2004): stadje op de heuvel, keermuur, vijvertje, oprit, paden. Gegenereerd door maak_plaatsscript.py.
-- Modelframe: oorsprong = OSM-zwaartepunt 279667968, voorkant (naar de vijver) = -Y, x = west, z = 0 pad, heuvel 0.9 m.
local STADJE = @STADJE@
local TEX = @TEX@
local F = Vector3.new(@FX@, 0, @FZ@)
local ORIGIN = CFrame.new(@OX@, 2.0, @OZ@) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	donker = {Color3.fromRGB(8, 8, 8), "SmoothPlastic"}, glasoranje = {Color3.fromRGB(255, 170, 80), "Neon"}, hout = {Color3.fromRGB(70, 46, 30), "Wood"},
	ijzer = {Color3.fromRGB(20, 20, 20), "Metal"}, goud = {Color3.fromRGB(214, 168, 72), "Metal"}, water = {Color3.fromRGB(30, 40, 32), "Glass"},
	bodem = {Color3.fromRGB(20, 18, 14), "Mud"}, leien = {Color3.fromRGB(80, 72, 66), "Slate"}, venster = {Color3.fromRGB(16, 16, 18), "SmoothPlastic"},
	dakplat = {Color3.fromRGB(50, 50, 50), "Slate"}, grond = {Color3.fromRGB(64, 78, 40), "Grass"}, klinker = {Color3.fromRGB(150, 104, 86), "Brick"},
	stuc = {Color3.fromRGB(220, 216, 206), "Plastic"}, papier = {Color3.fromRGB(236, 222, 186), "Fabric"}, bankgroen = {Color3.fromRGB(52, 84, 62), "WoodPlanks"}, pannen = {Color3.fromRGB(150, 80, 60), "Plastic"}, natuursteen = {Color3.fromRGB(150, 146, 136), "Plastic"},
}
local TINT = {stuc = Color3.fromRGB(232, 230, 222), natuursteen = Color3.fromRGB(170, 166, 158), pannen = Color3.fromRGB(150, 118, 100)}   -- daken donkerder/bemost (Meisjezij)
local objs = game:GetObjects("rbxassetid://" .. STADJE)
local oud = workspace:FindFirstChild("ZwavelstokjesStadje"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "ZwavelstokjesStadje"
for _, o in ipairs(objs) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
local lampen = Instance.new("Folder"); lampen.Name = "Lampen"; lampen.Parent = m
local onbekend = {}
for _, p in ipairs(m:GetChildren()) do
	if not p:IsA("BasePart") then continue end
	p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
	if string.match(p.Name, "^COLL_") then
		p.Transparency = 1; p.CanCollide = true; p.CanQuery = true; p.CastShadow = false; p.Parent = bots
		if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
	elseif string.match(p.Name, "^LAMP_") then
		p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
		local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 184, 104); pl.Range = 16; pl.Brightness = 1.4; pl.Shadows = true; pl.Parent = p
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if TINT[tex] then sa.Color = TINT[tex] end
			sa.Parent = p
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "water" then p.Transparency = 1; p.CastShadow = false end
			if key == "glasoranje" then p.Transparency = 0.2; p.CastShadow = false end
			if key == "grond" or key == "klinker" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
			if key == "klinker" and game.MaterialService:FindFirstChild("EftelingKlinkers") then p.MaterialVariant = "EftelingKlinkers" end
		else table.insert(onbekend, p.Name) end
	end
end
m.WorldPivot = ORIGIN
-- terrein: Ground onder het geheel, vijvertje uitgraven en met spiegelend terreinwater vullen
local T = workspace.Terrain
local c = {lokaal(-18, -15, 0).Position, lokaal(13, 8, 0).Position, lokaal(-18, 8, 0).Position, lokaal(13, -15, 0).Position}
local mn = Vector3.new(math.min(c[1].X, c[2].X, c[3].X, c[4].X), -8, math.min(c[1].Z, c[2].Z, c[3].Z, c[4].Z))
local mx = Vector3.new(math.max(c[1].X, c[2].X, c[3].X, c[4].X), 6, math.max(c[1].Z, c[2].Z, c[3].Z, c[4].Z))
T:ReplaceMaterial(Region3.new(mn, mx):ExpandToGrid(4), 4, Enum.Material.Grass, Enum.Material.Ground)
local VIJ = @VIJ@
local function inside(x, y, p) local cc = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then cc = not cc end; j = i end
	return cc end
local nw = 0
for i = math.floor(mn.X / 4), math.ceil(mx.X / 4) do
	for j = math.floor(mn.Z / 4), math.ceil(mx.Z / 4) do
		local X, Z = i * 4 + 2, j * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, 0, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, VIJ) then
			T:FillBlock(CFrame.new(X, -3, Z), Vector3.new(4, 10, 4), Enum.Material.Air)
			T:FillBlock(CFrame.new(X, (-4 + 1.05) / 2, Z), Vector3.new(4, 1.05 + 4, 4), Enum.Material.Water); nw += 1
		end
	end
end
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("stadje %d (botsing %d, lampen %d), watercellen %d; onbekend %s", #m:GetChildren(), #bots:GetChildren(), #lampen:GetChildren(), nw, onb(onbekend))
