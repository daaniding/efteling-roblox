-- De Rode Schoentjes: loggia + symmetrische stenen muur (x -3.74..7.34). Plakken in Studio execute_luau.
local ID = 134454081581695
local TEX = {hout = {81472054670694, 85629092080186}, mural = {124287892024974}, pannen = {96729143021074, 100110566945474}, rots = {81326043261864, 92530187225438}, stuc = {89844253411773, 82763351226057}}
local COLL = {{1.8, 0.65, 1.7, 3.6, 0.3, 3.4, 0.0}, {0.16, -2.1, 1.225, 0.4, 0.4, 2.45, 0.0}, {3.44, -2.1, 1.225, 0.4, 0.4, 2.45, 0.0}, {3.44, 0.34, 1.225, 0.4, 0.4, 2.45, 0.0}, {0.16, 0.34, 1.225, 0.4, 0.4, 2.45, 0.0}, {1.8, -0.525, 0.45, 2.36, 1.45, 0.9, 0.0}, {0.32, -0.575, 0.55, 0.1, 2.05, 1.1, 0.0}, {1.8, -1.6, 0.55, 2.96, 0.1, 1.1, 0.0}, {3.28, -0.575, 0.55, 0.1, 2.05, 1.1, 0.0}, {1.8, 1.4, 2.2, 11.08, 1.2, 4.4, 0.0}, {-1.1, -0.9, 0.5, 0.7, 0.4, 1.0, 10}}
local F = Vector3.new(0.808, 0, -0.589)
local ORIGIN = CFrame.new(49.59, 2.0, 141.45) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(226, 214, 190), "Plastic"}, zuil = {Color3.fromRGB(214, 190, 130), "SmoothPlastic"}, pannen = {Color3.fromRGB(150, 82, 56), "ClayRoofTiles"},
	groen = {Color3.fromRGB(34, 88, 80), "SmoothPlastic"}, rots = {Color3.fromRGB(150, 150, 146), "Rock"}, baksteen = {Color3.fromRGB(160, 80, 58), "Brick"},
	tegelA = {Color3.fromRGB(96, 150, 150), "Glass"}, tegelB = {Color3.fromRGB(214, 224, 220), "Glass"}, zigzagdonker = {Color3.fromRGB(48, 32, 52), "SmoothPlastic"},
	creme = {Color3.fromRGB(232, 222, 192), "SmoothPlastic"}, ijzer = {Color3.fromRGB(20, 20, 20), "Metal"}, kaars = {Color3.fromRGB(244, 240, 222), "SmoothPlastic"},
	vlam = {Color3.fromRGB(255, 180, 80), "Neon"}, rood = {Color3.fromRGB(190, 20, 16), "SmoothPlastic"}, goud = {Color3.fromRGB(205, 160, 60), "Metal"},
	hout = {Color3.fromRGB(80, 54, 34), "Wood"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"},
}
local TINT = {stuc = Color3.fromRGB(240, 234, 222), rots = Color3.fromRGB(214, 214, 210)}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("RodeSchoentjes"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "RodeSchoentjes"
for _, o in ipairs(objs) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
local lampen = Instance.new("Folder"); lampen.Name = "Lampen"; lampen.Parent = m
local onb, pre = {}, {}
for _, p in ipairs(m:GetChildren()) do
	if not p:IsA("BasePart") then continue end
	p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
	if string.match(p.Name, "^COLL_") then p:Destroy()
	elseif string.match(p.Name, "^LAMP_") then
		p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
		local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 176, 96); pl.Range = 8; pl.Brightness = 0.8; pl.Parent = p
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if TINT[tex] then sa.Color = TINT[tex] end; sa.Parent = p; table.insert(pre, sa.ColorMap)
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "tegelA" or key == "tegelB" then p.Transparency = 0.15 end
			if key == "vlam" then p.CastShadow = false end
			if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); pcall(function() p.MaterialVariant = "VV_Grind" end) end
		else table.insert(onb, p.Name) end
	end
end
for _, c in ipairs(COLL) do
	local b = Instance.new("Part"); b.Name = "Bots"; b.Anchored = true; b.Transparency = 1; b.CastShadow = false; b.CanTouch = false
	b.Size = Vector3.new(c[4] * S, c[6] * S, c[5] * S); b.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]), 0); b.Parent = bots
end
m.WorldPivot = ORIGIN
local weg = 0
for _, c in ipairs(workspace.RodeSchoentjesGroen:GetChildren()) do
	local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
	if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
		if (x > -4.6 and x < 6.0 and y > -6.8 and y < 2.3) or (x > -4.2 and x < 7.8 and y > 0.4 and y < 2.4) then c:Destroy(); weg += 1 end end
end
local ok = 0
pcall(function() local dec = {}; for _, id in ipairs(pre) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end) end)
local cam = function(x, y, z) return (ORIGIN * CFrame.new(-x * S, z * S, y * S)).Position end
local a, b, c2, d = cam(6.5, -9.5, 1.5), cam(1.8, -0.8, 1.8), cam(1.8, -9.5, 2.0), cam(1.8, 0, 2.2)
return string.format("%d delen; planten weg %d; texturen %d/%d; onb %s | schuin %.1f,%.1f,%.1f -> %.1f,%.1f,%.1f | voor %.1f,%.1f,%.1f -> %.1f,%.1f,%.1f", #m:GetChildren(), weg, ok, #pre, #onb > 0 and table.concat(onb, ",") or "-", a.X, a.Y, a.Z, b.X, b.Y, b.Z, c2.X, c2.Y, c2.Z, d.X, d.Y, d.Z)