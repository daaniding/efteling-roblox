--!strict
-- PagodeBeleving (StarterPlayerScripts): tekst in beeld voor wie op de gondel staat (Daan 17 nov: "gewoon in het beeld,
-- iets vets en natuurlijk, in het Engels en dan vertalen"). Bij het instappen een titel: groot PAGODE in goudkleurige
-- schreefletters met daaronder "Welcome aboard"; vlak voor vertrek "Gates closing"; na de rit "Exit: follow the signs".
-- Plus muziek aan boord die met de gondel meereist.
-- Teksten zijn Engels; de vertaling (nl) staat in LocalizationService.PagodeTeksten (maak_ritscript), Roblox vertaalt
-- automatisch naar de taal van de speler (AutoLocalize). Leest Pagode.FaseLokaal en Gondel.Kern; verandert niets aan de rit.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local kern = (pag:WaitForChild("Gondel") :: Model):WaitForChild("Kern") :: BasePart
local plr = Players.LocalPlayer

local GOUD = Color3.fromRGB(232, 196, 120)
local gui = Instance.new("ScreenGui"); gui.Name = "PagodeOmroep"; gui.ResetOnSpawn = false; gui.IgnoreGuiInset = true

local function label(tekst: string, font: Enum.Font, grootte: number, y: number, kleur: Color3): TextLabel
	local l = Instance.new("TextLabel"); l.AnchorPoint = Vector2.new(0.5, 0.5); l.Position = UDim2.new(0.5, 0, y, 0)
	l.Size = UDim2.new(1, 0, 0, grootte + 8); l.BackgroundTransparency = 1; l.Font = font; l.TextSize = grootte
	l.TextColor3 = kleur; l.TextStrokeColor3 = Color3.new(0, 0, 0); l.TextStrokeTransparency = 1; l.TextTransparency = 1
	l.Text = tekst; l.Parent = gui
	return l
end
-- titel (eigennaam, niet vertalen) en onderregel; korte meldingen onderin
local titel = label("P A G O D E", Enum.Font.Bodoni, 64, 0.30, GOUD); titel.AutoLocalize = false
local onder = label("Welcome aboard", Enum.Font.Bodoni, 26, 0.30 + 0.075, Color3.fromRGB(250, 244, 230))
local melding = label("", Enum.Font.SourceSansSemibold, 24, 0.84, Color3.new(1, 1, 1))
gui.Parent = plr:WaitForChild("PlayerGui")

local volg = 0
local function toon(labels: {TextLabel}, duur: number)
	volg += 1; local mijn = volg
	for k, l in labels do
		local inn = TweenInfo.new(1.2, Enum.EasingStyle.Sine, Enum.EasingDirection.Out, 0, false, (k - 1) * 0.5)
		TweenService:Create(l, inn, {TextTransparency = 0, TextStrokeTransparency = 0.75}):Play()
	end
	task.delay(duur, function()
		if mijn ~= volg then return end
		for _, l in labels do
			TweenService:Create(l, TweenInfo.new(1.0, Enum.EasingStyle.Sine, Enum.EasingDirection.In), {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
		end
	end)
end
local function meld(tekst: string) melding.Text = tekst; toon({melding}, 3.5) end

-- staat de speler op het dek? (binnen de rand, op dekhoogte t.o.v. de kern)
local function opDek(): boolean
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hrp then return false end
	local rel = kern.CFrame:PointToObjectSpace(hrp.Position)
	return math.sqrt(rel.X * rel.X + rel.Z * rel.Z) < 8.3 * S and rel.Y > 6 and rel.Y < 16
end

-- muziek aan boord: speelt vanuit de gondel (hangt aan de kern, reist mee), zwelt aan bij vertrek en sterft weg bij aankomst
-- (Daan 17 nov: "waar is de muziek in de pagode zelf"). Ruimtelijk: aan boord duidelijk, vanaf de grond niet als hij hoog is.
local RIT_MUZIEK = 1845854732          -- APM "Plum Blossoms" (rustig, Oosters); wachtrij heeft "Fortune's Smiling"
local aanBoordMuziek = Instance.new("Sound"); aanBoordMuziek.Name = "RitMuziek"
aanBoordMuziek.SoundId = "rbxassetid://" .. RIT_MUZIEK; aanBoordMuziek.Looped = true; aanBoordMuziek.Volume = 0
aanBoordMuziek.RollOffMode = Enum.RollOffMode.InverseTapered; aanBoordMuziek.RollOffMinDistance = 30; aanBoordMuziek.RollOffMaxDistance = 90
aanBoordMuziek.Parent = kern
local RIJDEN = {sluiten = 0.25, omhoog = 0.45, boven = 0.45, omlaag = 0.4}
RunService.Heartbeat:Connect(function(dt)
	local fase = pag:GetAttribute("FaseLokaal") :: string?
	local doel = fase and RIJDEN[fase] or 0
	if doel > 0 and not aanBoordMuziek.IsPlaying then aanBoordMuziek:Play() end
	aanBoordMuziek.Volume += (doel - aanBoordMuziek.Volume) * math.clamp(dt * 0.6, 0, 1)
	if doel == 0 and aanBoordMuziek.Volume < 0.005 and aanBoordMuziek.IsPlaying then aanBoordMuziek:Pause() end
end)

local vorige, welkomGezegd, gereden = "", false, false
RunService.Heartbeat:Connect(function()
	local fase = pag:GetAttribute("FaseLokaal") :: string?
	if not fase then return end
	local aanBoord = opDek()
	if fase == "instappen" then
		if vorige ~= "instappen" then welkomGezegd = false end
		if aanBoord and not welkomGezegd then
			welkomGezegd = true
			if gereden then meld("Exit: follow the signs") else toon({titel, onder}, 4.5) end
		end
		if not aanBoord then gereden = false end
	elseif fase ~= vorige and aanBoord then
		if fase == "sluiten" then meld("Gates closing") end
		if fase == "omhoog" then gereden = true end
	end
	vorige = fase
end)
