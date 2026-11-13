-- Herberg De Ersteling (BAG/OSM 55447978) aan het Herautenplein. Model: x langs de voorgevel (0 = noordoosthoek, toren rechts bij x 12),
-- voorgevel y=0 kijkt naar het pleintje met het Ezeltje. Oorsprong = OSM-hoek (20.55, -73.97) in het Herautenplein-frame, grond Y=2.
local MODEL = 126789978359252
local TEX = {stuc = {120408701098907, 96387308402680}, natuursteen = {87834715418672, 73862908816880}, hout = {105985817932858, 80074867891453},
	riet = {71279290305545, 73332071549205}, pannen = {122051816225591}, leien = {80701431268197, 104757125539862}, bord = {119068939521945}}
local FP = Vector3.new(-0.968, 0, 0.250); local OP = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-FP.X, -FP.Z), 0)
local function P(x, y) return (OP * CFrame.new(-x * 3, 0, y * 3)).Position end
local pos = P(20.55, -73.97)
local F = OP:VectorToWorldSpace(Vector3.new(0.494, 0, 0.869))               -- voorgevel-normaal (-0.494, 0.869) in het pleinframe -> wereld
local ORIGIN = CFrame.new(pos) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local M = {deur = {Color3.fromRGB(86, 56, 34), "Wood"}, luik = {Color3.fromRGB(92, 62, 44), "Wood"}, venster = {Color3.fromRGB(22, 24, 26), "Glass"},
	ijzer = {Color3.fromRGB(26, 26, 26), "Metal"}, glaslamp = {Color3.fromRGB(255, 226, 170), "Glass"}, zink = {Color3.fromRGB(110, 112, 112), "Metal"},
	vat = {Color3.fromRGB(116, 78, 46), "WoodPlanks"}, goud = {Color3.fromRGB(214, 168, 72), "Metal"}}
local oud = workspace:FindFirstChild("HerbergErsteling"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "HerbergErsteling"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. MODEL)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
local onb = {}
for _, p in ipairs(m:GetChildren()) do
	if not p:IsA("BasePart") then continue end
	p.Anchored = true; p.CanTouch = false; p.CanCollide = false
	if string.match(p.Name, "^LAMP_") then
		p.Transparency = 1; p.CastShadow = false; p.CanQuery = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"
		local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = 14; pl.Brightness = 1.2; pl.Parent = p
	elseif string.match(p.Name, "^COLL_") then
		p.Transparency = 1; p.CanCollide = true; p.CastShadow = false; p.CanQuery = false; p.CollisionFidelity = Enum.CollisionFidelity.Box; p.Parent = bots
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
		if key == "bordtex" then tex = "bord" end
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if tex == "bord" then sa.AlphaMode = Enum.AlphaMode.Transparency end
			if tex == "pannen" then sa.Color = Color3.fromRGB(225, 200, 190) end   -- vorsten iets gedempt (Studio rendert feller)
			sa.Parent = p; p.CanCollide = (tex ~= "bord")
		elseif key and M[key] then p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
		else table.insert(onb, p.Name) end
	end
end
m.WorldPivot = ORIGIN
-- bomen/planten/layout in de footprint weg
local FOOT = {{20.55, -73.97}, {18.72, -75.22}, {12.29, -79.64}, {12.15, -79.33}, {10.14, -79.41}, {9.17, -80.2}, {8.21, -80.99}, {8.72, -82.41}, {9.64, -83.94},
	{10.92, -84.01}, {12.54, -86.37}, {14.16, -88.75}, {20.9, -84.12}, {19.11, -81.49}, {20.1, -80.81}, {20.5, -81.41}, {24.0, -79.01}}
local function inpoly(x, y) local c = false; local j = #FOOT
	for i = 1, #FOOT do local a, b = FOOT[i], FOOT[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if string.find(f.Name, "Groen") or string.find(f.Name, "Bos") or string.find(f.Name, "Horizon") then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p then local l = OP:PointToObjectSpace(p); local x, y = -l.X / 3, l.Z / 3
				local near = false; for dx = -1.5, 1.5, 1.5 do for dy = -1.5, 1.5, 1.5 do if inpoly(x + dx, y + dy) then near = true end end end
				if near then t:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do local n = string.lower(d.Name); if string.find(n, "herberg") or string.find(n, "tafeltje") then d:Destroy() end end end
local ids = {}; for _, t in pairs(TEX) do for _, id in ipairs(t) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(ids, d) end end
local ok = 0; game:GetService("ContentProvider"):PreloadAsync(ids, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
local cam = P(5.0, -66.5) + Vector3.new(0, 5.5, 0)
return string.format("herberg %d delen, botsing %d, %d planten weg, tex %d/%d; onbekend: %s | cam %.1f,%.1f,%.1f doel %.1f,%.1f,%.1f", #m:GetChildren(), #bots:GetChildren(), weg, ok, #ids, table.concat(onb, ","), cam.X, cam.Y, cam.Z, P(15.5, -79.5).X, 9, P(15.5, -79.5).Z)
