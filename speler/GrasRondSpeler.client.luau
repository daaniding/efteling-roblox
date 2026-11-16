-- StarterPlayer.StarterPlayerScripts.GrasRondSpeler (LocalScript).
-- Echte 3D-grasplukjes (models/LI_Grond, ReplicatedStorage.Gras.plukje0-2) alleen rond de camera, alleen op terrein-gras.
-- Verderop doet de grasfoto (MaterialVariant EF_Gras) het werk. Vast patroon per cel: niets verspringt als je loopt.
-- Aan de rand krimpen de plukjes, zodat ze niet zichtbaar 'ploppen'.
-- Schaalt mee met de speler: grafische kwaliteit bepaalt het maximum, en zakt de fps onder 40 dan gaat er een stand af
-- (stand 0 = geen 3D-gras, alleen de foto). Komt de fps weer ruim boven 58, dan gaat hij na een tijdje weer een stand op.
local RunService = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local RS = game:GetService("ReplicatedStorage")
local bron = RS:WaitForChild("Gras")
local SJ = { bron:WaitForChild("plukje0"), bron:WaitForChild("plukje1"), bron:WaitForChild("plukje2") }

--            straal, dicht, per cel   (stud, stud, plukjes)
local STANDEN = {
	[1] = { 8, 4, 1 },
	[2] = { 12, 6, 2 },
	[3] = { 16, 9, 3 },
}
local CEL = 0.9        -- stud
local RAND = 4         -- laatste 4 stud: krimpen
local BUDGET = 200     -- cellen per frame (tegen haperen)

-- maximum uit de grafische instelling van de speler
local function maxStand()
	local ok, q = pcall(function() return UserSettings():GetService("UserGameSettings").SavedQualityLevel end)
	local n = ok and tonumber(tostring(q):match("(%d+)$")) or nil      -- QualityLevel1..10, of Automatic (nil)
	local m = 3
	if n then m = n >= 7 and 3 or n >= 4 and 2 or n >= 2 and 1 or 0 end
	if UIS.TouchEnabled and not UIS.KeyboardEnabled then m = math.min(m, 2) end   -- telefoon/tablet
	return m
end
local stand = maxStand()
local STRAAL, DICHT, PER_CEL = 0, 0, 0
local function pasToe() local s = STANDEN[stand]; if s then STRAAL, DICHT, PER_CEL = s[1], s[2], s[3] end end
pasToe()

local map = Instance.new("Folder"); map.Name = "GrasLokaal"; map.Parent = workspace
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = { workspace.Terrain }; rp.IgnoreWater = true

local cellen = {}      -- key -> {i, j, plukjes = {{part, k, schaal, x, y0, z, rot}}}
local pool = { {}, {}, {} }
local WEG = CFrame.new(0, -1e4, 0)

local function haal(k)
	local p = table.remove(pool[k])
	if not p then p = SJ[k]:Clone(); p.Parent = map end
	return p
end

local function hash(i, j, n)
	local h = bit32.bxor(i * 73856093 % 4294967296, j * 19349663 % 4294967296, n * 83492791 % 4294967296)
	h = bit32.bxor(h, bit32.rshift(h, 13)) * 1274126177 % 4294967296
	h = bit32.bxor(h, bit32.rshift(h, 16))
	return (h % 100000) / 100000
end

local function factor(d) return 0.3 + 0.7 * math.clamp((STRAAL - d) / RAND, 0, 1) end

local function zet(e, f, aan)
	local p, k = e[1], e[2]
	if not aan then p.CFrame = WEG; return end
	p.Size = SJ[k].Size * (e[3] * f)
	p.CFrame = CFrame.new(e[4], e[5] + p.Size.Y / 2 - 0.02, e[6]) * CFrame.Angles(0, e[7], 0)
end

local function leeg(key, c)
	for _, e in ipairs(c.plukjes) do e[1].CFrame = WEG; table.insert(pool[e[2]], e[1]) end
	cellen[key] = nil
end

local function vul(i, j, d)
	local c = { i = i, j = j, plukjes = {} }
	cellen[i .. "," .. j] = c
	local cx, cz = (i + 0.5) * CEL, (j + 0.5) * CEL
	local hit = workspace:Raycast(Vector3.new(cx, 400, cz), Vector3.new(0, -800, 0), rp)
	if not hit or hit.Material ~= Enum.Material.Grass then return end
	for m = 1, PER_CEL do
		local k = 1 + math.floor(hash(i, j, m) * 3)
		local e = { haal(k), k, 0.8 + 0.5 * hash(i, j, m + 30),
			i * CEL + hash(i, j, m + 10) * CEL, hit.Position.Y, j * CEL + hash(i, j, m + 20) * CEL, hash(i, j, m + 40) * 6.283 }
		zet(e, factor(d), m == 1 or d < DICHT)
		table.insert(c.plukjes, e)
	end
end

local laatste, wachtrij, kop = nil, {}, 1

local function wissel(nieuw)
	if nieuw == stand then return end
	stand = nieuw; pasToe()
	for key, c in pairs(cellen) do leeg(key, c) end
	wachtrij, kop, laatste = {}, 1, nil
	if stand == 0 then   -- geheugen vrijgeven
		for k = 1, 3 do for _, p in ipairs(pool[k]) do p:Destroy() end; pool[k] = {} end
	end
end

-- fps bewaken (alleen tellen als er echt getekend wordt)
local beelden, sinds, goedSinds, laatsteWissel = 0, os.clock(), nil, 0
RunService.RenderStepped:Connect(function() beelden += 1 end)
task.spawn(function()
	while true do
		task.wait(3)
		local nu = os.clock(); local fps = beelden / (nu - sinds); beelden, sinds = 0, nu
		local max = maxStand()
		if stand > max then wissel(max)
		elseif fps > 5 and fps < 40 and stand > 0 and nu - laatsteWissel > 6 then wissel(stand - 1); laatsteWissel = nu; goedSinds = nil
		elseif fps > 58 and stand < max then
			goedSinds = goedSinds or nu
			if nu - goedSinds > 20 and nu - laatsteWissel > 20 then wissel(stand + 1); laatsteWissel = nu; goedSinds = nil end
		else goedSinds = nil end
		map:SetAttribute("Stand", stand); map:SetAttribute("Fps", math.floor(fps))
	end
end)

RunService.Heartbeat:Connect(function()
	if stand == 0 then return end
	local cam = workspace.CurrentCamera; if not cam then return end
	local pos = cam.CFrame.Position
	local p2 = Vector2.new(pos.X, pos.Z)
	if not laatste or (p2 - laatste).Magnitude > 1.5 then
		laatste = p2
		for key, c in pairs(cellen) do
			local d = (Vector2.new((c.i + 0.5) * CEL, (c.j + 0.5) * CEL) - p2).Magnitude
			if d > STRAAL + 2 then leeg(key, c)
			elseif d > DICHT - 2 then
				local f = factor(d); for m, e in ipairs(c.plukjes) do zet(e, f, m == 1 or d < DICHT) end
			end
		end
		wachtrij, kop = {}, 1
		local ci, cj = math.floor(pos.X / CEL), math.floor(pos.Z / CEL); local r = math.ceil(STRAAL / CEL)
		for i = ci - r, ci + r do for j = cj - r, cj + r do
			local d = (Vector2.new((i + 0.5) * CEL, (j + 0.5) * CEL) - p2).Magnitude
			if d <= STRAAL and not cellen[i .. "," .. j] then table.insert(wachtrij, { i, j, d }) end
		end end
		table.sort(wachtrij, function(a, b) return a[3] < b[3] end)
	end
	local stop = math.min(#wachtrij, kop + BUDGET - 1)
	for n = kop, stop do
		local c = wachtrij[n]
		if not cellen[c[1] .. "," .. c[2]] then vul(c[1], c[2], c[3]) end
	end
	kop = stop + 1
end)
