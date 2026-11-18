-- FataMorganaSfeer (StarterPlayerScripts, LocalScript): binnen in Fata Morgana (instaphal, halletje, uitganggang, Bazaar) wordt
-- het donker en warm, zoals in het echt (video's 2020/2025): alleen de lampen en de verlichte achterwanden geven licht.
-- Buiten weer de gewone parkbelichting. Zones in het modelstelsel (meters; Roblox X = 3x, Z = -3y, Y = 0,91 + 3z).
local Lighting = game:GetService("Lighting")
local TweenService = game:GetService("TweenService")
local ZONES = {
	{-3.6, -348.5, 17.8, -323.5, -4.0, 5.0},   -- instaphal + doorgang halletje
	{17.2, -330.6, 21.0, -327.4, -1.0, 4.0},   -- halletje minaretvoet (binnenkant)
	{12.9, -315.6, 17.6, -301.3, -1.0, 3.0},   -- uitganggang aanbouw
	{17.8, -313.7, 24.2, -301.3, -1.0, 3.0},   -- De Bazaar
	{-74.0, -352.0, 12.6, -294.0, -4.0, -0.1},  -- vaarroute (onder de begane grond, 18_route)
}
local BINNEN = {Ambient = Color3.fromRGB(16, 12, 10), OutdoorAmbient = Color3.fromRGB(20, 15, 12),
	EnvironmentDiffuseScale = 0.05, EnvironmentSpecularScale = 0.15, ExposureCompensation = 0.3}
local BUITEN = {}
for k in BINNEN do BUITEN[k] = Lighting[k] end
local function binnen(p)
	local x, y, z = p.X / 3, -p.Z / 3, (p.Y - 0.91) / 3
	for _, b in ZONES do
		if x > b[1] and x < b[3] and y > b[2] and y < b[4] and z > b[5] and z < b[6] then return true end
	end
	return false
end
local nu = false
local info = TweenInfo.new(1.2, Enum.EasingStyle.Sine)
while true do
	local plr = game.Players.LocalPlayer
	local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
	local w = hrp and binnen(hrp.Position) or false
	if w ~= nu then
		nu = w
		if w then for k in BINNEN do BUITEN[k] = Lighting[k] end end
		TweenService:Create(Lighting, info, w and BINNEN or BUITEN):Play()
	end
	task.wait(0.25)
end
