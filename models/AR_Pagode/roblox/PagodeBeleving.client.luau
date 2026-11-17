--!strict
-- PagodeBeleving (StarterPlayerScripts): rit-ervaring voor wie op de gondel staat (Daan 17 nov: "rit-ervaring").
-- 1. omroepteksten onderin beeld bij elke fase (welkom, hekjes sluiten, omhoog, uitzicht, dalen, welkom terug + uitgang)
-- 2. camera deint heel licht mee met optrekken en afremmen (versnelling van de gondelkern), alleen tijdens de rit
-- Leest Pagode.FaseLokaal (gezet door PagodeRitClient) en de positie van Gondel.Kern; verandert niets aan de rit zelf.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local kern = (pag:WaitForChild("Gondel") :: Model):WaitForChild("Kern") :: BasePart
local plr = Players.LocalPlayer
local cam = workspace.CurrentCamera

local TEKST = {
	welkom = "Welkom aan boord van de Pagode! Loop gerust rond over het dek.",
	sluiten = "De hekjes sluiten. Wij wensen u een prettige reis!",
	omhoog = "We gaan omhoog, hoog boven de Efteling…",
	boven = "Geniet van het uitzicht! De Pagode draait rustig rond.",
	omlaag = "We dalen weer af. Blijf nog even binnen de hekjes.",
	terug = "Welkom terug! De uitgang is aan de oostkant: volg de borden UITGANG.",
}

-- ondertitel: donker pilletje onderin beeld, vloeiend in en uit
local gui = Instance.new("ScreenGui"); gui.Name = "PagodeOmroep"; gui.ResetOnSpawn = false; gui.IgnoreGuiInset = true
local kader = Instance.new("Frame"); kader.AnchorPoint = Vector2.new(0.5, 1); kader.Position = UDim2.new(0.5, 0, 1, -110)
kader.Size = UDim2.fromOffset(0, 46); kader.AutomaticSize = Enum.AutomaticSize.X; kader.BackgroundColor3 = Color3.fromRGB(16, 22, 20)
kader.BackgroundTransparency = 1; kader.Parent = gui
Instance.new("UICorner", kader).CornerRadius = UDim.new(1, 0)
local pad = Instance.new("UIPadding", kader); pad.PaddingLeft = UDim.new(0, 22); pad.PaddingRight = UDim.new(0, 22)
local rand = Instance.new("UIStroke", kader); rand.Color = Color3.fromRGB(214, 168, 70); rand.Thickness = 1.5; rand.Transparency = 1
local lab = Instance.new("TextLabel"); lab.BackgroundTransparency = 1; lab.Size = UDim2.new(0, 0, 1, 0); lab.AutomaticSize = Enum.AutomaticSize.X
lab.Font = Enum.Font.GothamMedium; lab.TextSize = 18; lab.TextColor3 = Color3.fromRGB(246, 238, 220); lab.TextTransparency = 1; lab.Text = ""
lab.Parent = kader
gui.Parent = plr:WaitForChild("PlayerGui")

local volg = 0
local function zeg(sleutel: string)
	volg += 1; local mijn = volg
	lab.Text = TEKST[sleutel]
	local inn = TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TweenService:Create(lab, inn, {TextTransparency = 0}):Play()
	TweenService:Create(kader, inn, {BackgroundTransparency = 0.25}):Play()
	TweenService:Create(rand, inn, {Transparency = 0.3}):Play()
	task.delay(6, function()
		if mijn ~= volg then return end
		local uit = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		TweenService:Create(lab, uit, {TextTransparency = 1}):Play()
		TweenService:Create(kader, uit, {BackgroundTransparency = 1}):Play()
		TweenService:Create(rand, uit, {Transparency = 1}):Play()
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
		zeg(fase)
		if fase == "omhoog" then gereden = true end
	end
	vorige = fase
end)

-- camera deint mee: versnelling van de kern -> heel kleine kanteling (max ~0.7 graad), plus trage golf tijdens het rijden
local vorigPos, vorigV, versn = kern.Position, Vector3.zero, Vector3.zero
local t = 0
RunService:BindToRenderStep("PagodeDeinen", Enum.RenderPriority.Camera.Value + 1, function(dt: number)
	if dt <= 0 then return end
	local pos = kern.Position
	local v = (pos - vorigPos) / dt
	local a = (v - vorigV) / dt
	vorigPos, vorigV = pos, v
	versn = versn:Lerp(a, math.clamp(dt * 3, 0, 1))
	if not opDek() or v.Magnitude < 0.05 then return end
	t += dt
	local lok = cam.CFrame:VectorToObjectSpace(versn)
	local kantel = math.clamp(-lok.X * 0.004, -0.012, 0.012)
	local knik = math.clamp(lok.Z * 0.003, -0.01, 0.01)
	local golf = math.sin(t * 0.9) * 0.0025 * math.clamp(v.Magnitude / 6, 0, 1)
	cam.CFrame = cam.CFrame * CFrame.Angles(knik + golf, 0, kantel)
end)
