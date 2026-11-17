--!strict
-- MuziekKiezer (StarterPlayerScripts, alleen in Studio): druk M om de wachtrijmuziek op alle Pagode-speakers te wisselen,
-- naam linksboven. Alleen lokaal; de gekozen ID daarna vastzetten in maak_ritscript (GELUID.muziek).
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then return end
local UIS = game:GetService("UserInputService")
local LIJST = {
	{"Fortune's Smiling (gekozen)", 1840841073}, {"One World (a)", 1839842602}, {"Cultures And Colours (A)", 1840397475}, {"World Of Wonder", 1836330626},
	{"The Legend of the Monkey King", 1837190707}, {"Kawachi Ondo (c)", 1842506077},
	{"Lightly Magical", 1837777641}, {"Fairy Doll", 1846356693}, {"The Carousel Waltz", 132619984017094},
	{"Outward Bound", 1842179736}, {"Plum Blossoms", 1845854732}, {"Peach Blossom Spring", 1840540291},
}
local gui = Instance.new("ScreenGui"); gui.Name = "MuziekKiezer"; gui.ResetOnSpawn = false
local lab = Instance.new("TextLabel"); lab.Size = UDim2.fromOffset(460, 34); lab.Position = UDim2.fromOffset(12, 12)
lab.BackgroundTransparency = 0.35; lab.BackgroundColor3 = Color3.fromRGB(20, 20, 24); lab.TextColor3 = Color3.new(1, 1, 1)
lab.Font = Enum.Font.GothamMedium; lab.TextSize = 16; lab.TextXAlignment = Enum.TextXAlignment.Left; lab.Parent = gui
gui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")
local pag = workspace:WaitForChild("Pagode"); local g = pag:WaitForChild("Geluid")
local i = 1
local function zet()
	local naam, id = LIJST[i][1], LIJST[i][2]
	for _, s in g:GetDescendants() do
		if s:IsA("Sound") and s.Name == "muziek" then s.SoundId = "rbxassetid://" .. id; s.TimePosition = 0; s:Play() end
	end
	lab.Text = string.format("  Muziek %d/%d: %s  (%d)   [M = volgende]", i, #LIJST, naam, id)
end
UIS.InputBegan:Connect(function(inp, bezet)
	if bezet or inp.KeyCode ~= Enum.KeyCode.M then return end
	i = i % #LIJST + 1; zet()
end)
task.wait(2); zet()
