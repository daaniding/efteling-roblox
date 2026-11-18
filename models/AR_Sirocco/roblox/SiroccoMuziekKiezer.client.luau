--!strict
-- SiroccoMuziekKiezer (StarterPlayerScripts, alleen in Studio): K = volgend nummer voor de wachtrijspeakers, L = volgend nummer
-- voor de muziek in de attractie; naam linksboven (onder die van de Pagode-kiezer). Alleen lokaal: de gekozen ID daarna
-- vastzetten in roblox/sirocco_rit.luau (MUZIEK.rij / MUZIEK.rit). Allemaal gelicentieerde Creator Store-muziek.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then return end
local UIS = game:GetService("UserInputService")
local RIJ = {
	{"Desert Sands (APM)", 1836725599}, {"Sand Dance (APM)", 1836357161}, {"Temple Dance (APM)", 1836376446},
	{"Arabian Dance - Notenkraker (APM)", 1836281829}, {"Lanterns in the Sand", 111877745518357},
	{"Mystic Sunset in the Arabian Desert", 138183693923881}, {"Sahara By Night", 92883899625211},
	{"Arabian Sands Reverie", 103198544664262},
}
local RIT = {
	{"Land Of Adventure (APM)", 1840889607}, {"Arabian Nightride", 106593797194565}, {"Arabian Nights", 134897287500569},
	{"Desert Sands (APM)", 1836725599}, {"Sand Dance (APM)", 1836357161},
}
local gui = Instance.new("ScreenGui"); gui.Name = "SiroccoMuziekKiezer"; gui.ResetOnSpawn = false
local function regel(y: number): TextLabel
	local l = Instance.new("TextLabel"); l.Size = UDim2.fromOffset(520, 30); l.Position = UDim2.fromOffset(12, y)
	l.BackgroundTransparency = 0.35; l.BackgroundColor3 = Color3.fromRGB(20, 20, 24); l.TextColor3 = Color3.new(1, 1, 1)
	l.Font = Enum.Font.GothamMedium; l.TextSize = 15; l.TextXAlignment = Enum.TextXAlignment.Left; l.Parent = gui
	return l
end
local labRij, labRit = regel(50), regel(84)
gui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")
local g = workspace:WaitForChild("Sirocco"):WaitForChild("Geluid")
local iRij, iRit = 1, 1
local function zet(naam: string, lijst: {{any}}, i: number, lab: TextLabel, wat: string, toets: string)
	local id = lijst[i][2] :: number
	for _, s in g:GetDescendants() do
		if s:IsA("Sound") and s.Name == naam then s.SoundId = "rbxassetid://" .. id; s.TimePosition = 0; s:Play() end
	end
	lab.Text = string.format("  Sirocco %s %d/%d: %s  (%d)   [%s = volgende]", wat, i, #lijst, lijst[i][1] :: string, id, toets)
end
UIS.InputBegan:Connect(function(inp, bezet)
	if bezet then return end
	if inp.KeyCode == Enum.KeyCode.K then iRij = iRij % #RIJ + 1; zet("muziekRij", RIJ, iRij, labRij, "wachtrij", "K")
	elseif inp.KeyCode == Enum.KeyCode.L then iRit = iRit % #RIT + 1; zet("muziekRit", RIT, iRit, labRit, "attractie", "L") end
end)
task.wait(2)
labRij.Text = string.format("  Sirocco wachtrij 1/%d: %s   [K = volgende]", #RIJ, RIJ[1][1] :: string)
labRit.Text = string.format("  Sirocco attractie 1/%d: %s   [L = volgende]", #RIT, RIT[1][1] :: string)
