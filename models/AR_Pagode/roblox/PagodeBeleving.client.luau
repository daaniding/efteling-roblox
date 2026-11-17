--!strict
-- PagodeBeleving (StarterPlayerScripts): rit-ervaring voor wie op de gondel staat (Daan 17 nov: "rit-ervaring").
-- Korte tekst in beeld (Daan: "gewoon in je beeld alleen de tekst"): welkom, hekjes gaan dicht, uitgang. Geen camera-effect
-- (Daan: "die camera is niet top").
-- Leest Pagode.FaseLokaal (gezet door PagodeRitClient) en de positie van Gondel.Kern; verandert niets aan de rit zelf.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local kern = (pag:WaitForChild("Gondel") :: Model):WaitForChild("Kern") :: BasePart
local plr = Players.LocalPlayer

local TEKST = {
	welkom = "Welkom in de Pagode",
	sluiten = "De hekjes gaan dicht",
	terug = "Uitgang: volg de borden",
}

-- alleen tekst in beeld, met een lichte schaduw voor leesbaarheid
local gui = Instance.new("ScreenGui"); gui.Name = "PagodeOmroep"; gui.ResetOnSpawn = false; gui.IgnoreGuiInset = true
local lab = Instance.new("TextLabel"); lab.AnchorPoint = Vector2.new(0.5, 1); lab.Position = UDim2.new(0.5, 0, 1, -120)
lab.Size = UDim2.fromOffset(600, 30); lab.BackgroundTransparency = 1; lab.Font = Enum.Font.SourceSansSemibold; lab.TextSize = 24
lab.TextColor3 = Color3.new(1, 1, 1); lab.TextStrokeColor3 = Color3.new(0, 0, 0); lab.TextStrokeTransparency = 1
lab.TextTransparency = 1; lab.Text = ""; lab.Parent = gui
gui.Parent = plr:WaitForChild("PlayerGui")

local volg = 0
local function zeg(sleutel: string)
	volg += 1; local mijn = volg
	lab.Text = TEKST[sleutel]
	local inn = TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TweenService:Create(lab, inn, {TextTransparency = 0, TextStrokeTransparency = 0.7}):Play()
	task.delay(4, function()
		if mijn ~= volg then return end
		local uit = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		TweenService:Create(lab, uit, {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
	end)
end

-- staat de speler op het dek? (binnen de rand, op dekhoogte t.o.v. de kern)
local function opDek(): boolean
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hrp then return false end
	local rel = kern.CFrame:PointToObjectSpace(hrp.Position)
	return math.sqrt(rel.X * rel.X + rel.Z * rel.Z) < 8.3 * S and rel.Y > 6 and rel.Y < 16
end

-- fasen volgen: teksten alleen voor wie aan boord is
local vorige, welkomGezegd, gereden = "", false, false
RunService.Heartbeat:Connect(function()
	local fase = pag:GetAttribute("FaseLokaal") :: string?
	if not fase then return end
	local aanBoord = opDek()
	if fase == "instappen" then
		if vorige ~= "instappen" then welkomGezegd = false end
		if aanBoord and not welkomGezegd then
			welkomGezegd = true
			zeg(gereden and "terug" or "welkom")
		end
		if not aanBoord then gereden = false end
	elseif fase ~= vorige and aanBoord then
		if fase == "sluiten" then zeg("sluiten") end
		if fase == "omhoog" then gereden = true end
	end
	vorige = fase
end)
