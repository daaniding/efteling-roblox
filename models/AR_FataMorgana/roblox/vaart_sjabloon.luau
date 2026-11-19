-- FataMorganaVaart (ServerScriptService): sloepen varen over het vaarpad (Daan 19 nov: "zorg nu ook echt even dat de boten varen dan
-- kan ik de route checken en het gevoel"). GEGENEREERD door build/19_vaarpad.py uit roblox/vaart_sjabloon.luau: niet met de hand
-- aanpassen, maar het sjabloon of het pad.
-- Sjabloon = workspace.FataMorgana.Boten (17_boten: één sloep, midden model (0,5; -326), vaart naar -X). Het script zet zitplaatsen op
-- de banken, verhuist het sjabloon naar ServerStorage en zet <Aantal> klonen gelijk verdeeld op de lus. Ze varen met <Snelheid> m/s
-- (attributen op dit script, live aan te passen). Alles verankerd, verplaatst met PivotTo; wie zit, vaart mee.
local RunService = game:GetService("RunService")
local ServerStorage = game:GetService("ServerStorage")

local P = {--[[PUNTEN]]}   -- X, Z (studs), elke 1 m (3 studs), gesloten lus
local N = #P // 2
local STAP = 3
local TOTAAL = N * STAP
if script:GetAttribute("Snelheid") == nil then script:SetAttribute("Snelheid", 1.0) end   -- m/s
if script:GetAttribute("Aantal") == nil then script:SetAttribute("Aantal", 8) end

local fm = workspace:WaitForChild("FataMorgana")
local sjabloon = fm:WaitForChild("Boten")
local y0 = sjabloon:GetPivot().Position.Y
sjabloon.WorldPivot = CFrame.lookAt(Vector3.new(1.5, y0, 978), Vector3.new(0.5, y0, 978))

-- zitplaatsen op de vijf banken (17_boten: s 0,24..0,70 van achter naar voor, boot 6 m), twee per bank
local ZIT_Y = 0.91 + 3 * (-3.2 + 0.42)
for _, s in {0.24, 0.355, 0.47, 0.585, 0.70} do
	for _, lat in {-1.3, 1.3} do
		local z = Instance.new("Seat")
		z.Name = "Zitplaats"
		z.Size = Vector3.new(2, 0.3, 1.6)
		z.Transparency = 1
		z.CanCollide = false
		z.Anchored = true
		z.CFrame = sjabloon.WorldPivot * CFrame.new(lat, ZIT_Y - y0, -(s - 0.5) * 6 * 3 + 0.6)
		z.Parent = sjabloon
	end
end
sjabloon.Parent = ServerStorage

local map = fm:FindFirstChild("Vaart") or Instance.new("Model")
map.Name = "Vaart"
map:ClearAllChildren()
map.Parent = fm

local function punt(s)
	s = s % TOTAAL
	local i = s // STAP
	local f = (s - i * STAP) / STAP
	local j = (i + 1) % N
	return Vector3.new(P[2 * i + 1] + (P[2 * j + 1] - P[2 * i + 1]) * f, y0, P[2 * i + 2] + (P[2 * j + 2] - P[2 * i + 2]) * f)
end

local boten = {}
local function vloot()
	local n = script:GetAttribute("Aantal")
	for _, b in boten do b.m:Destroy() end
	table.clear(boten)
	for k = 1, n do
		local m = sjabloon:Clone()
		m.Name = "Sloep" .. k
		m.Parent = map
		table.insert(boten, {m = m, s = (k - 1) * TOTAAL / n})
	end
end
vloot()
script:GetAttributeChangedSignal("Aantal"):Connect(vloot)

RunService.Heartbeat:Connect(function(dt)
	local v = script:GetAttribute("Snelheid") * 3 * dt
	for _, b in boten do
		b.s = (b.s + v) % TOTAAL
		local c = punt(b.s)
		local r = punt(b.s + 6) - punt(b.s - 6)
		if r.Magnitude > 0.01 then b.m:PivotTo(CFrame.lookAt(c, c + r)) end
	end
end)
