-- Sprookjesbos-paden (models/PR_Paden): BGT-padvlakken op het AHN-veld, gebakken in Blender (04_blender.py). Vervangt workspace.SprookjesbosPaden.
-- Terrein eronder (0,5 stud omlaag + Ground) doet ServerStorage.AHN_Delta.PadenTerrein, eenmalig (attribuut PadenTerreinBanden).
local MODEL = 132911656696735
local IDS = {
 klinker={70717503266138,80504200991154,133271566968418}, kassei={127574960591258,77871033037157,120119392898514},
 asfalt={85404863396414,125247639465688,117362102891321}, kantsteen={79255050163796,89521820345427,117750992401457},
 rand={116026820112420,138155942636706,91900900245966}}
local objs = game:GetObjects("rbxassetid://" .. MODEL)
local oud = workspace:FindFirstChild("SprookjesbosPaden"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "SprookjesbosPaden"
for _, o in ipairs(objs) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(3)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 6, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local n = 0
for _, p in ipairs(m:GetChildren()) do
	local mat = p.Name:match("^PD_(%a+)_"); local ids = IDS[mat]
	if p:IsA("MeshPart") and ids then
		p.Anchored = true; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic; p.Color = Color3.new(1, 1, 1)
		local sa = Instance.new("SurfaceAppearance")
		sa.ColorMap = "rbxassetid://" .. ids[1]; sa.NormalMap = "rbxassetid://" .. ids[2]; sa.RoughnessMap = "rbxassetid://" .. ids[3]
		if mat == "rand" then sa.AlphaMode = Enum.AlphaMode.Transparency; p.CanCollide = false; p.CanQuery = false
		else p.CanCollide = true; p.CanQuery = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end
		sa.Parent = p; p:SetAttribute("Padmateriaal", mat); n += 1
		if n % 30 == 0 then task.wait() end
	end
end
return n .. " paddelen geplaatst"
