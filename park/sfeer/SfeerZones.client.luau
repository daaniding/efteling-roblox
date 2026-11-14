-- SfeerZones (LocalScript in StarterPlayer.StarterPlayerScripts): sfeer per plek, alleen voor deze speler.
-- Onder het bladerdak: iets donkerder, koeler en groener (alsof je het bos in loopt); op open plekken en bij het water: warm en licht.
-- Werkt met een eigen ColorCorrection ("ZoneKleur") bovenop die van het dagritme, zodat de server hem niet overschrijft.
local L = game:GetService("Lighting")
local TS = game:GetService("TweenService")
local cam = workspace.CurrentCamera
local cc = Instance.new("ColorCorrectionEffect"); cc.Name = "ZoneKleur"; cc.Parent = L
local function bladeren()
	local t = {}
	for _, f in ipairs(workspace:GetChildren()) do
		if f:IsA("Folder") or f:IsA("Model") then
			local n = f.Name
			if string.find(n, "Groen") or string.find(n, "Bos") or string.find(n, "Bomen") then table.insert(t, f) end
		end
	end
	return t
end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = bladeren()
task.spawn(function() while true do task.wait(15); rp.FilterDescendantsInstances = bladeren() end end)
local ZONES = {
	bos  = {Brightness = -0.05, Contrast = 0.04, Saturation = -0.05, TintColor = Color3.fromRGB(226, 242, 226)},
	open = {Brightness = 0.0, Contrast = 0.0, Saturation = 0.0, TintColor = Color3.fromRGB(255, 255, 255)},
}
local huidig
while true do
	task.wait(0.4)
	local p = cam.CFrame.Position; local hits = 0
	for _, o in ipairs({Vector3.zero, Vector3.new(6, 0, 0), Vector3.new(-6, 0, 0), Vector3.new(0, 0, 6), Vector3.new(0, 0, -6)}) do
		if workspace:Raycast(p + o, Vector3.new(0, 80, 0), rp) then hits += 1 end
	end
	local zone = hits >= 3 and "bos" or "open"
	if zone ~= huidig then
		huidig = zone
		TS:Create(cc, TweenInfo.new(2.5, Enum.EasingStyle.Sine), ZONES[zone]):Play()
	end
end
