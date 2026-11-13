-- Kikkerkoning: 4 fonteinkikkers (build/03e_kikker.py -> exports/AR_Kikker.fbx) op de binnenhoeken van de bak, kijkend naar de rotsen.
-- Zelfde frame als Herautenplein/Prinsenpoort. Kikker x1.25 t.o.v. het Blender-model (foto 2023: iets groter).
local MODEL, TEXK = 70914706705065, 75961250645608
local F = Vector3.new(-0.968, 0, 0.250); local O = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local function L(x, y, z) return (O * CFrame.new(-x * 3, z * 3, y * 3)).Position end
local S = 3 * 1.25
local KLEUR = {oogring = Color3.fromRGB(222, 208, 150), pupil = Color3.fromRGB(8, 8, 8)}
local oud = workspace:FindFirstChild("Kikkerkoning"); if oud then oud:Destroy() end
local map = Instance.new("Model"); map.Name = "Kikkerkoning"; map.Parent = workspace
local cx, cy, BH = -0.22, -28.48, 0.82
local mid = L(cx, cy, BH)
local function een(pos)
	local m = Instance.new("Model"); m.Name = "Kikker"
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. MODEL)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = map; m:ScaleTo(S)
	local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	local told = CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0))
	local dir = Vector3.new(mid.X - pos.X, 0, mid.Z - pos.Z).Unit
	m:PivotTo(CFrame.lookAt(pos, pos + dir) * told:Inverse() * m:GetPivot()); anker:Destroy()
	for _, p in ipairs(m:GetChildren()) do
		p.Anchored = true; p.CanCollide = false; p.CanTouch = false
		if string.find(p.Name, "TEX_kikker") then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEXK; sa.Color = Color3.fromRGB(205, 205, 178); sa.Parent = p
		else
			local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if key and KLEUR[key] then p.Color = KLEUR[key]; p.Material = Enum.Material.SmoothPlastic end
		end
	end
end
for _, s in ipairs({{-1, -1}, {-1, 1}, {1, -1}, {1, 1}}) do een(L(cx + s[1] * 2.1, cy + s[2] * 2.1, BH - 0.02)) end
return "kikkers " .. #map:GetChildren()
