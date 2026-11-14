-- Dagritme (Script in ServerScriptService): zachte overgang ochtend -> dag -> gouden uur -> roze zonsondergang -> blauw uur -> sterrennacht.
-- Lantaarns gaan aan in de schemering (met lichtcirkels en gloed), sprookjesstof wordt 's nachts vuurvliegjes, lichtbundels door de bomen
-- volgen de zon. Instellen via attributen op Lighting: DagritmeAan (true/false: stilzetten), DagMinuten (lengte van een dag in echte minuten).
local L = game:GetService("Lighting")
local RS = game:GetService("RunService")
if L:GetAttribute("DagritmeAan") == nil then L:SetAttribute("DagritmeAan", true) end
if L:GetAttribute("DagMinuten") == nil then L:SetAttribute("DagMinuten", 30) end
if L:GetAttribute("StartTijd") then L.ClockTime = L:GetAttribute("StartTijd") end

local function c(r, g, b) return Color3.fromRGB(r, g, b) end
-- sleutelmomenten (uur): waarden worden ertussen vloeiend gemengd
local K = {
	{t = 5.0,  br = 0.7, ex = 0.6, od = c(60, 64, 96),    am = c(32, 32, 52), ac = c(90, 92, 130),  ad = c(44, 46, 80),   de = 0.44, hz = 1.8, gl = 0.2, ti = c(205, 214, 255), co = 0.1,  sa = 0.0,  bl = 1.5, sr = 0.0,  lamp = 1.6, stof = 60, ster = 2500, bun = 0.0, wo = c(150, 156, 190)},
	{t = 6.6,  br = 1.7, ex = 0.25, od = c(116, 106, 122), am = c(48, 44, 56), ac = c(214, 186, 196), ad = c(130, 108, 150), de = 0.42, hz = 2.6, gl = 0.9, ti = c(255, 232, 224), co = 0.12, sa = 0.04, bl = 1.0, sr = 0.14, lamp = 0.4, stof = 20, ster = 0,    bun = 0.9, wo = c(255, 220, 214)},
	{t = 9.5,  br = 3.0, ex = 0.0, od = c(128, 128, 132), am = c(52, 52, 58), ac = c(200, 206, 214), ad = c(106, 112, 126), de = 0.3,  hz = 1.4, gl = 0.3, ti = c(255, 250, 244), co = 0.12, sa = 0.06, bl = 0.5, sr = 0.08, lamp = 0.0, stof = 8,  ster = 0,    bun = 0.35, wo = c(255, 255, 255)},
	{t = 15.5, br = 3.0, ex = 0.05, od = c(132, 126, 126), am = c(54, 52, 56), ac = c(212, 204, 196), ad = c(120, 112, 120), de = 0.32, hz = 1.6, gl = 0.5, ti = c(255, 246, 234), co = 0.13, sa = 0.07, bl = 0.6, sr = 0.1,  lamp = 0.0, stof = 10, ster = 0,    bun = 0.55, wo = c(255, 246, 236)},
	{t = 17.6, br = 3.2, ex = 0.3, od = c(138, 124, 130), am = c(52, 48, 58), ac = c(232, 200, 172), ad = c(158, 116, 142), de = 0.38, hz = 2.4, gl = 1.6, ti = c(255, 236, 214), co = 0.16, sa = 0.1,  bl = 1.1, sr = 0.16, lamp = 1.0, stof = 26, ster = 0,    bun = 1.0, wo = c(255, 238, 222)},
	{t = 19.2, br = 1.2, ex = 0.5, od = c(80, 84, 120),   am = c(36, 36, 56), ac = c(122, 120, 170), ad = c(60, 60, 110),  de = 0.42, hz = 2.2, gl = 0.2, ti = c(222, 228, 255), co = 0.12, sa = 0.02, bl = 1.4, sr = 0.0,  lamp = 1.4, stof = 40, ster = 1200, bun = 0.0, wo = c(190, 180, 220)},
	{t = 22.5, br = 0.6, ex = 0.6, od = c(52, 58, 92),    am = c(30, 30, 50), ac = c(62, 68, 102),  ad = c(30, 34, 62),   de = 0.45, hz = 1.5, gl = 0.1, ti = c(200, 212, 255), co = 0.1,  sa = 0.0,  bl = 1.6, sr = 0.0,  lamp = 1.6, stof = 60, ster = 3000, bun = 0.0, wo = c(120, 128, 160)},
}
local function meng(t)
	local n = #K
	for i = 1, n do
		local a, b = K[i], K[i % n + 1]
		local ta, tb = a.t, b.t; local tt = t
		if tb <= ta then tb += 24; if tt < ta then tt += 24 end end
		if tt >= ta and tt < tb then
			local f = (tt - ta) / (tb - ta); f = f * f * (3 - 2 * f)
			local r = {}
			for k, va in pairs(a) do
				local vb = b[k]
				if typeof(va) == "Color3" then r[k] = va:Lerp(vb, f) elseif type(va) == "number" then r[k] = va + (vb - va) * f end
			end
			return r
		end
	end
	return K[1]
end

local function effect(cls) return L:FindFirstChildOfClass(cls) end
local lampen, glazen = {}, {}
local function verzamel()
	lampen, glazen = {}, {}
	for _, d in ipairs(workspace:GetDescendants()) do
		if (d:IsA("PointLight") or d:IsA("SpotLight")) and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "Lampen" then
			table.insert(lampen, {d, d:GetAttribute("Basis") or d.Brightness}); d:SetAttribute("Basis", d:GetAttribute("Basis") or d.Brightness)
		elseif d:IsA("BasePart") and string.find(d.Name, "MAT_glaslamp") then table.insert(glazen, d) end
	end
end

-- lichtbundels: schuine banen gouden licht tussen de bomen, langs de zonrichting
local bundels = {}
local function maakBundels()
	local oud = workspace:FindFirstChild("Lichtbundels"); if oud then oud:Destroy() end
	local map = Instance.new("Folder"); map.Name = "Lichtbundels"
	local F = Vector3.new(0.1076, 0, 0.9942)
	local ORIGIN = CFrame.new(-108.77, 2.0, -301.0) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
	local rnd = Random.new(1812)
	local plekken = {}
	for _ = 1, 400 do
		if #plekken >= 18 then break end
		local x, y = rnd:NextNumber(-12, 21), rnd:NextNumber(-27, 8)
		local open = x > -8 and x < 10 and y > -22 and y < 8      -- niet midden boven vijver/kasteel: bundels vallen door de bosrand
		if not open then table.insert(plekken, (ORIGIN * CFrame.new(-x * 3, 0, y * 3)).Position) end
	end
	for i, p in ipairs(plekken) do
		local part = Instance.new("Part"); part.Name = "Bundel" .. i; part.Anchored = true; part.CanCollide = false; part.CanQuery = false; part.CanTouch = false
		part.Transparency = 1; part.Size = Vector3.new(0.2, 0.2, 0.2); part.CFrame = CFrame.new(p); part.Parent = map
		local a0 = Instance.new("Attachment"); a0.Parent = part; local a1 = Instance.new("Attachment"); a1.Parent = part
		local b = Instance.new("Beam"); b.Attachment0 = a0; b.Attachment1 = a1; b.FaceCamera = true; b.Segments = 1
		b.LightEmission = 1; b.LightInfluence = 0; b.Color = ColorSequence.new(c(255, 214, 160))
		local w = rnd:NextNumber(3, 7); b.Width0 = w * 0.6; b.Width1 = w * 1.6
		b.Parent = part
		table.insert(bundels, {beam = b, a0 = a0, a1 = a1, fase = rnd:NextNumber(0, 6.28), hoog = rnd:NextNumber(38, 55)})
	end
	map.Parent = workspace
end

verzamel(); maakBundels()
task.delay(10, verzamel)
local stof = workspace:FindFirstChild("Sfeer") and workspace.Sfeer:FindFirstChild("Sprookjesstof", true)
local tijd = 0
RS.Heartbeat:Connect(function(dt)
	tijd += dt
	if L:GetAttribute("DagritmeAan") then
		L.ClockTime = (L.ClockTime + dt * 24 / (60 * math.max(1, L:GetAttribute("DagMinuten") or 30))) % 24
	end
end)
while true do
	local r = meng(L.ClockTime)
	L.Brightness = r.br; L.ExposureCompensation = r.ex; L.OutdoorAmbient = r.od; L.Ambient = r.am
	local a = effect("Atmosphere"); if a then a.Color = r.ac; a.Decay = r.ad; a.Density = r.de; a.Haze = r.hz; a.Glare = r.gl end
	local cc = effect("ColorCorrectionEffect"); if cc then cc.TintColor = r.ti; cc.Contrast = r.co; cc.Saturation = r.sa end
	local bl = effect("BloomEffect"); if bl then bl.Intensity = r.bl end
	local sr = effect("SunRaysEffect"); if sr then sr.Intensity = r.sr end
	local sky = effect("Sky"); if sky then sky.StarCount = math.floor(r.ster) end
	local cl = workspace.Terrain:FindFirstChildOfClass("Clouds"); if cl then cl.Color = r.wo end
	for _, l in ipairs(lampen) do if l[1].Parent then l[1].Brightness = l[2] * r.lamp; l[1].Enabled = r.lamp > 0.05 end end
	for _, g in ipairs(glazen) do if g.Parent then
		if r.lamp > 0.3 then g.Material = Enum.Material.Neon; g.Color = c(255, 190, 110) else g.Material = Enum.Material.Glass; g.Color = c(255, 226, 170) end
	end end
	if not stof or not stof.Parent then stof = workspace:FindFirstChild("Sfeer") and workspace.Sfeer:FindFirstChild("Sprookjesstof", true) end
	if stof then stof.Rate = r.stof end
	-- bundels langs de zon; alleen als de zon laag-middelhoog staat
	local zon = L:GetSunDirection()
	local zicht = (zon.Y > 0.03) and r.bun or 0
	for _, b in ipairs(bundels) do
		local top = Vector3.new(0, b.hoog, 0)
		b.a0.Position = top; b.a1.Position = top - zon.Unit * (b.hoog / math.max(zon.Y, 0.25))
		local s = 0.74 + 0.05 * math.sin(tijd * 0.4 + b.fase)                  -- zacht ademen (0.86 was onzichtbaar door de nevel)
		local tr = 1 - (1 - s) * zicht
		b.beam.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, tr), NumberSequenceKeypoint.new(0.8, math.min(1, tr + 0.04)), NumberSequenceKeypoint.new(1, 1)})
		b.beam.Enabled = zicht > 0.01
	end
	task.wait(0.25)
end
