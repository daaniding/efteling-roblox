-- Ezeltje Strek Je: ezel op sokkel (build/03_ezel.py -> exports/AR_Ezeltje.fbx) midden op het ronde pleintje van het Herautenplein
-- (OSM 55423191, Herautenplein-frame (5.96, -64.45)), kop naar de Prinsenpoort (Eftepedia).
local MODEL = 79079378764880
local TEX = {ezel = {119585118176594, 139416635340800}, dekje = {89288262847523}, bord = {128244839705244}}   -- {kleur, normal}
local FP = Vector3.new(-0.968, 0, 0.250); local OP = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-FP.X, -FP.Z), 0)
local pos = (OP * CFrame.new(-5.96 * 3, 0.08 * 3, -64.45 * 3)).Position
local FE = -FP                                                                -- kop naar de Prinsenpoort = plein +y
local ORIGIN = CFrame.new(pos) * CFrame.Angles(0, math.atan2(-FE.X, -FE.Z), 0)
local S = 3
local M = {ijssel = {Color3.fromRGB(176, 160, 128), "Brick"}, beton = {Color3.fromRGB(222, 210, 178), "Concrete"}, rood = {Color3.fromRGB(160, 34, 28), "SmoothPlastic"},
	deur = {Color3.fromRGB(150, 156, 130), "Metal"}, ijzer = {Color3.fromRGB(20, 20, 20), "Metal"}, hoef = {Color3.fromRGB(96, 104, 116), "SmoothPlastic"},
	oog = {Color3.fromRGB(230, 228, 220), "SmoothPlastic"}, pupil = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"}, manen = {Color3.fromRGB(100, 96, 90), "SmoothPlastic"},
	tuig = {Color3.fromRGB(170, 30, 26), "SmoothPlastic"}, goud = {Color3.fromRGB(222, 176, 76), "Metal"},
	ezelhuid = {Color3.fromRGB(184, 176, 164), "SmoothPlastic"}, neus = {Color3.fromRGB(60, 54, 50), "SmoothPlastic"}, oorbinnen = {Color3.fromRGB(140, 130, 124), "SmoothPlastic"}, iris = {Color3.fromRGB(82, 52, 30), "SmoothPlastic"}}
local oud = workspace:FindFirstChild("Ezeltje"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Ezeltje"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. MODEL)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local onb = {}
for _, p in ipairs(m:GetChildren()) do
	p.Anchored = true; p.CanTouch = false; p.CanCollide = true
	local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
	if tex and TEX[tex] then
		p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
		local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
		if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
		if tex == "dekje" or tex == "bord" then sa.AlphaMode = Enum.AlphaMode.Transparency end
		if tex == "ezel" then sa.Color = Color3.fromRGB(228, 220, 208) end   -- lichte warme grijs van de foto
		sa.Parent = p
	elseif key and M[key] then p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
	else table.insert(onb, p.Name) end
end
m.WorldPivot = ORIGIN
-- planten van andere scenes op de sokkelplek weg
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if string.find(f.Name, "Groen") or string.find(f.Name, "Bos") then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p and (Vector3.new(p.X, 0, p.Z) - Vector3.new(pos.X, 0, pos.Z)).Magnitude < 8 then t:Destroy(); weg += 1 end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if string.find(string.lower(d.Name), "ezel") then d:Destroy() end end end
return string.format("ezel %d delen, %d planten weg; onbekend: %s", #m:GetChildren(), weg, table.concat(onb, ","))
