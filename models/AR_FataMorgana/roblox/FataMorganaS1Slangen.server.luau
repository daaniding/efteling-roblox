-- FataMorganaS1Slangen (ServerScriptService): sectie 1d. De slangen in de knoestboom zwaaien traag aan hun tak en bewegen hun kop
-- (Eftepedia: "Na enkele meters hangen er slangen boven ons in de bomen"; video 171-174 s), de vlammen in de vuurschalen flakkeren.
-- Slangen = workspace.FataMorgana.Junglenacht.Slang_a/b/c (plaats_s1d); draaipunt = bovenkant van het onderdeel (waar hij om de tak zit).
local RunService = game:GetService("RunService")
local fm = workspace:WaitForChild("FataMorgana")
local jn = fm:WaitForChild("Junglenacht")

local slangen = {}
for i, naam in {"Slang_a", "Slang_b", "Slang_c"} do
	local p = jn:WaitForChild(naam)
	local cf = p.CFrame
	local top = cf.Position + Vector3.new(0, p.Size.Y / 2 - 0.3, 0)
	table.insert(slangen, {p = p, rel = CFrame.new(top):Inverse() * cf, top = top, fase = i * 2.1, snel = 0.55 + i * 0.12})
end
local vlammen = {}
for _, d in jn:GetDescendants() do if d:IsA("PointLight") and d.Name == "Vlamlicht" then table.insert(vlammen, d) end end

local t = 0
RunService.Heartbeat:Connect(function(dt)
	t += dt
	for _, s in slangen do
		local a = math.sin(t * s.snel + s.fase)
		local b = math.sin(t * s.snel * 1.7 + s.fase * 0.6)
		s.p.CFrame = CFrame.new(s.top) * CFrame.Angles(math.rad(5) * a, math.rad(8) * b, math.rad(4) * a) * s.rel
	end
	for i, l in vlammen do
		l.Brightness = 1.2 + 0.35 * math.noise(t * 6, i * 3.3) + 0.15 * math.sin(t * 17 + i)
	end
end)
