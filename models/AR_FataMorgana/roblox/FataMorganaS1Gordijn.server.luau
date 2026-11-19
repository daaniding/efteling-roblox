-- FataMorganaS1Gordijn (ServerScriptService): sectie 1a, het gordijn in de westmuur van de instaphal gaat open als er een sloep
-- aankomt en weer dicht als hij erdoor is (POV 2025, 120-123 s: het gordijn schuift vanuit het midden naar beide kanten open).
-- Helften = workspace.FataMorgana.Junglegordijn FM_gordijn_l (noord) / FM_gordijn_r (zuid) uit 20_s1a_gordijn. Open = de helft
-- schuift samen tot 22 % van de breedte tegen de buitenkant (plooien bundelen). Sloepen = workspace.FataMorgana.Vaart (FataMorganaVaart).
local TweenService = game:GetService("TweenService")
local fm = workspace:WaitForChild("FataMorgana")
local g = fm:WaitForChild("Junglegordijn")
local MIDDEN = Vector3.new(3 * -3.62, 0, -3 * -326.5)   -- waar het vaarpad door het gordijn gaat
local OPEN_AFSTAND, DICHT_AFSTAND = 27, 33               -- studs (sloep-midden tot het gordijn)
local BUNDEL = 0.22
local INFO = TweenInfo.new(2.4, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)

local helften = {}
for _, naam in {"FM_gordijn_l_0_junglegordijn", "FM_gordijn_r_0_junglegordijn"} do
	local p = g:WaitForChild(naam)
	-- breedte-as: de langste horizontale as van het onderdeel; buitenkant = de kant weg van MIDDEN
	local lx, lz = p.Size.X, p.Size.Z
	local as = lx > lz and Vector3.new(1, 0, 0) or Vector3.new(0, 0, 1)
	local wereldas = p.CFrame:VectorToWorldSpace(as)
	local naarbuiten = ((p.Position - MIDDEN) * Vector3.new(1, 0, 1)).Unit
	if wereldas:Dot(naarbuiten) < 0 then wereldas = -wereldas end
	local breedte = lx > lz and lx or lz
	local dichtCF, dichtSize = p.CFrame, p.Size
	local openSize = lx > lz and Vector3.new(lx * BUNDEL, p.Size.Y, lz) or Vector3.new(lx, p.Size.Y, lz * BUNDEL)
	local openCF = dichtCF + wereldas * (breedte * (1 - BUNDEL) / 2)
	table.insert(helften, {p = p, dicht = {CFrame = dichtCF, Size = dichtSize}, open = {CFrame = openCF, Size = openSize}})
end

local isOpen = false
local function zet(open)
	if open == isOpen then return end
	isOpen = open
	for _, h in helften do TweenService:Create(h.p, INFO, open and h.open or h.dicht):Play() end
end

while true do
	local dichtst = math.huge
	local vaart = fm:FindFirstChild("Vaart")
	if vaart then
		for _, b in vaart:GetChildren() do
			local d = ((b:GetPivot().Position - MIDDEN) * Vector3.new(1, 0, 1)).Magnitude
			if d < dichtst then dichtst = d end
		end
	end
	if dichtst < OPEN_AFSTAND then zet(true) elseif dichtst > DICHT_AFSTAND then zet(false) end
	task.wait(0.1)
end
