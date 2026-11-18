--!strict
-- SiroccoRitClient (StarterPlayerScripts): laat de Sirocco draaien op deze client (Pagode-methode: alles verankerd, BulkMoveTo
-- in PreSimulation, stand uit workspace:GetServerTimeNow() - RitStart, dus iedereen ziet hetzelfde).
-- Drie bewegingen opgeteld: hoofdschijf (m) om het midden, subschijven (sa..sc) tegen de draairichting in om hun eigen midden,
-- elke boot (ba..bl) om zijn voet, plus licht dobberen. Onderdelen heten ..._rt<groep> (11_export); draaipunten als attribuut
-- P_<groep> op Rit (sirocco_rit.luau). Hele omwentelingen per rit: na de rit staat alles weer in de instapstand.
-- Wie in een boot zit hangt met een SeatWeld aan de (verankerde) stoel en gaat vanzelf mee; de camera draait mee.
-- Beleving (Daan 18 nov): titel bij het instappen, "Hold on tight!" bij vertrek, na de rit direct zwart (server); eigen
-- instapknop (ProximityPrompt Style Custom); klapdeuren bij instap (open tijdens het instappen) en uitstap (open tijdens het
-- uitstappen), scharnier + hoek als attribuut op de deur (sirocco_rit.luau). Teksten Engels, nl in SiroccoTeksten.
-- Zelf draaien (Daan 18 nov: "kan ik mijn karretje zelf laten draaien"): tijdens de rit A/D (pijltjes, L1/R1, op mobiel twee
-- knoppen) geeft je boot extra draai met vaart en uitlopen. Je eigen boot reageert direct; de stand gaat via RemoteEvent
-- SiroccoDraai naar de server, die hem als attribuut X_<boot> = (hoek, snelheid, servertijd) op Rit zet voor de anderen.
-- Bij het uitlopen draait elke boot terug naar een hele omwenteling, zodat hij weer in de instapstand eindigt.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local PPS = game:GetService("ProximityPromptService")
local CAS = game:GetService("ContextActionService")
local UIS = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local T_IN, T_RIT, T_UIT, RAMP = 15, 60, 8, 5      -- = SiroccoRit; RAMP = optrekken / uitlopen (s)
local CYCLUS = T_IN + T_RIT + T_UIT
local OMW_M, OMW_S = 5, -11                         -- hele omwentelingen per rit: hoofdschijf, subschijf (t.o.v. de hoofdschijf)
local I_TOT = T_RIT - RAMP

local sir = workspace:WaitForChild("Sirocco") :: Model
local rit = sir:WaitForChild("Rit") :: Model
local MIDDEN = rit:GetAttribute("Midden") :: Vector3
local nDelen = (rit:GetAttribute("Delen") :: number?) or 0
local tel = 0
repeat
	tel = 0
	for _, p in rit:GetChildren() do if p:IsA("BasePart") then tel += 1 end end
	if tel < nDelen then task.wait(0.5) end
until tel >= nDelen

type Groep = {naam: string, ouder: string?, P: Vector3, i: number}
local NAMEN = {"m", "sa", "sb", "sc"}
local LETTERS = "abcdefghijkl"
for i = 1, 12 do table.insert(NAMEN, "b" .. LETTERS:sub(i, i)) end
local groepen: {[string]: Groep} = {}
for _, n in NAMEN do
	local g: Groep = {naam = n, ouder = nil, P = MIDDEN, i = 0}
	if n:sub(1, 1) == "s" then
		g.ouder = "m"; g.P = rit:GetAttribute("P_" .. n) :: Vector3
	elseif n:sub(1, 1) == "b" then
		local i = (LETTERS:find(n:sub(2, 2)) :: number) - 1    -- boot00..11 (03_forms: per subschijf 3 boten, dan 1 op de hoofdschijf)
		g.i = i
		g.ouder = (i % 4 == 3) and "m" or ("s" .. ("abc"):sub(i // 4 + 1, i // 4 + 1))
		g.P = rit:GetAttribute("P_" .. n) :: Vector3
	end
	groepen[n] = g
end

local delen: {BasePart} = {}
local rust: {CFrame} = {}
local groepVan: {string} = {}
local prompts: {ProximityPrompt} = {}
for _, p in rit:GetChildren() do
	if p:IsA("BasePart") then
		local g = p.Name:match("_rt(%a+)$")
		if g and groepen[g] then
			p.Anchored = true
			table.insert(delen, p); table.insert(rust, p.CFrame); table.insert(groepVan, g)
		end
		local pr = p:FindFirstChildOfClass("ProximityPrompt")
		if pr then table.insert(prompts, pr) end
	end
end

-- klapdeuren (07_omgeving.poorten): attribuut Scharnier (wereld) en Hoek (rad, dicht -> open) op elk blad
type Deur = {p: BasePart, rust: CFrame, H: Vector3, hoek: number, uit: boolean}
local deuren: {Deur} = {}
local om = sir:WaitForChild("Omgeving")
for _, naam in {"poort_in_l", "poort_in_r", "poort_uit_l", "poort_uit_r"} do
	local p = om:WaitForChild("SI_" .. naam .. "_0_om", 10) :: BasePart?
	if p and p:GetAttribute("Scharnier") then
		table.insert(deuren, {p = p, rust = p.CFrame, H = p:GetAttribute("Scharnier") :: Vector3, hoek = p:GetAttribute("Hoek") :: number,
			uit = naam:find("uit") ~= nil})
	end
end
local deurStand = {in_ = -1, uit = -1}

local function e(x: number): number return (1 - math.cos(math.pi * math.clamp(x, 0, 1))) / 2 end
local function opgebouwd(x: number): number return RAMP * (x - math.sin(math.pi * x) / math.pi) / 2 end   -- integraal van e
local function voortgang(t: number): (number, number)       -- 0..1 over de rit + huidige snelheid 0..1
	t = math.clamp(t, 0, T_RIT)
	local I, v
	if t < RAMP then I = opgebouwd(t / RAMP); v = e(t / RAMP)
	elseif t <= T_RIT - RAMP then I = RAMP / 2 + (t - RAMP); v = 1
	else I = I_TOT - opgebouwd((T_RIT - t) / RAMP); v = e((T_RIT - t) / RAMP) end
	return I / I_TOT, v
end
local function draai(P: Vector3, th: number): CFrame return CFrame.new(P) * CFrame.Angles(0, th, 0) * CFrame.new(-P) end
local TAU = 2 * math.pi
local function bootHoek(i: number, F: number): number
	local richting = (i % 2 == 0) and 1 or -1
	return richting * (6 + i % 3) * TAU * F + 0.9 * math.sin(TAU * (1 + i % 2) * F)   -- vrij draaiend, elke boot anders
end
local function dobber(i: number, t: number, v: number): CFrame              -- golfjes: rol en stamp, alleen tijdens het varen
	local a = math.rad(3.2) * v
	return CFrame.Angles(a * math.sin(t * 2.1 + i * 1.7), 0, a * 0.8 * math.sin(t * 1.6 + i * 2.3))
end

local plr = Players.LocalPlayer
local GOUD = Color3.fromRGB(232, 190, 96)
local NACHT = Color3.fromRGB(18, 30, 62)

-- ===== beeld: titel, meldingen, zwart bij de medewerker =====
local gui = Instance.new("ScreenGui"); gui.Name = "SiroccoBeeld"; gui.IgnoreGuiInset = true; gui.ResetOnSpawn = false; gui.DisplayOrder = 50
local function label(tekst: string, font: Enum.Font, grootte: number, y: number, kleur: Color3): TextLabel
	local l = Instance.new("TextLabel"); l.AnchorPoint = Vector2.new(0.5, 0.5); l.Position = UDim2.new(0.5, 0, y, 0)
	l.Size = UDim2.new(1, 0, 0, grootte + 10); l.BackgroundTransparency = 1; l.Font = font; l.TextSize = grootte
	l.TextColor3 = kleur; l.TextStrokeColor3 = Color3.fromRGB(20, 10, 0); l.TextStrokeTransparency = 1; l.TextTransparency = 1
	l.Text = tekst; l.ZIndex = 3; l.Parent = gui
	return l
end
local titel = label("S I R O C C O", Enum.Font.Fantasy, 70, 0.28, GOUD); titel.AutoLocalize = false
local titelSchaal = Instance.new("UIScale"); titelSchaal.Parent = titel
local onder = label("", Enum.Font.Fantasy, 28, 0.28 + 0.08, Color3.fromRGB(250, 240, 220))
local lijn = Instance.new("Frame"); lijn.AnchorPoint = Vector2.new(0.5, 0.5); lijn.Position = UDim2.new(0.5, 0, 0.28 + 0.045, 0)
lijn.Size = UDim2.new(0, 0, 0, 2); lijn.BackgroundColor3 = GOUD; lijn.BorderSizePixel = 0; lijn.BackgroundTransparency = 0.2; lijn.Parent = gui
local melding = label("", Enum.Font.Fantasy, 30, 0.82, Color3.new(1, 1, 1))
local zwart = Instance.new("Frame"); zwart.Size = UDim2.fromScale(1, 1); zwart.BackgroundColor3 = Color3.new(0, 0, 0)
zwart.BackgroundTransparency = 1; zwart.BorderSizePixel = 0; zwart.ZIndex = 5; zwart.Parent = gui
local zwartTekst = label("", Enum.Font.Fantasy, 30, 0.5, Color3.fromRGB(240, 226, 190)); zwartTekst.ZIndex = 6
gui.Parent = plr:WaitForChild("PlayerGui")

local volg = 0
local function toonTitel(sub: string, duur: number)
	volg += 1; local mijn = volg
	onder.Text = sub
	titelSchaal.Scale = 1.25
	TweenService:Create(titelSchaal, TweenInfo.new(1.1, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Scale = 1}):Play()
	TweenService:Create(titel, TweenInfo.new(0.9, Enum.EasingStyle.Sine), {TextTransparency = 0, TextStrokeTransparency = 0.6}):Play()
	TweenService:Create(lijn, TweenInfo.new(1.0, Enum.EasingStyle.Quart, Enum.EasingDirection.Out, 0, false, 0.3), {Size = UDim2.new(0, 420, 0, 2)}):Play()
	TweenService:Create(onder, TweenInfo.new(0.9, Enum.EasingStyle.Sine, Enum.EasingDirection.Out, 0, false, 0.6), {TextTransparency = 0, TextStrokeTransparency = 0.7}):Play()
	task.delay(duur, function()
		if mijn ~= volg then return end
		local uit = TweenInfo.new(0.9, Enum.EasingStyle.Sine, Enum.EasingDirection.In)
		for _, l in {titel, onder} do TweenService:Create(l, uit, {TextTransparency = 1, TextStrokeTransparency = 1}):Play() end
		TweenService:Create(lijn, uit, {Size = UDim2.new(0, 0, 0, 2)}):Play()
	end)
end
local mvolg = 0
local function meld(tekst: string, duur: number)
	mvolg += 1; local mijn = mvolg
	melding.Text = tekst; melding.Position = UDim2.new(0.5, 0, 0.85, 0)
	TweenService:Create(melding, TweenInfo.new(0.6, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Position = UDim2.new(0.5, 0, 0.82, 0), TextTransparency = 0, TextStrokeTransparency = 0.6}):Play()
	task.delay(duur, function()
		if mijn ~= mvolg then return end
		TweenService:Create(melding, TweenInfo.new(0.7, Enum.EasingStyle.Sine), {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
	end)
end
plr:GetAttributeChangedSignal("SiroccoUit"):Connect(function()
	local aan = (plr:GetAttribute("SiroccoUit") or 0) == 2
	zwartTekst.Text = (plr:GetAttribute("SiroccoTekst") :: string?) or ""
	local info = TweenInfo.new(aan and 0.5 or 0.9, Enum.EasingStyle.Sine)
	TweenService:Create(zwart, info, {BackgroundTransparency = aan and 0 or 1}):Play()
	TweenService:Create(zwartTekst, info, {TextTransparency = aan and 0 or 1}):Play()
	if not aan then                                   -- na de medewerker: camera de brug af (zuid = +Z, SiroccoRit.uitPlek); het
		local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart") :: BasePart?   -- lichaam volgt in 1e persoon de camera
		if hrp then
			local cam = workspace.CurrentCamera
			local oog = hrp.Position + Vector3.new(0, 1.5, 0)
			cam.CFrame = CFrame.lookAt(oog, oog + Vector3.new(0, -0.15, 1))
		end
	end
end)

-- ===== instapknop (ProximityPrompt Style Custom): donkerblauwe pil, gouden rand, gouden toets, vasthoudbalk =====
local knoppen: {[ProximityPrompt]: BillboardGui} = {}
local function toetsTekst(pr: ProximityPrompt, invoer: Enum.ProximityPromptInputType): string
	if invoer == Enum.ProximityPromptInputType.Touch then return "TAP" end
	if invoer == Enum.ProximityPromptInputType.Gamepad then return "X" end
	return pr.KeyboardKeyCode.Name
end
PPS.PromptShown:Connect(function(pr: ProximityPrompt, invoer: Enum.ProximityPromptInputType)
	if pr.Style ~= Enum.ProximityPromptStyle.Custom or not pr:IsDescendantOf(rit) then return end
	local bb = Instance.new("BillboardGui"); bb.Name = "SiroccoKnop"; bb.Adornee = pr.Parent :: BasePart
	bb.Size = UDim2.fromOffset(230, 70); bb.StudsOffset = Vector3.new(0, 4.2, 0); bb.AlwaysOnTop = true; bb.Active = true
	bb.ResetOnSpawn = false
	local schaal = Instance.new("UIScale"); schaal.Scale = 0.5; schaal.Parent = bb
	local pil = Instance.new("TextButton"); pil.Size = UDim2.fromScale(1, 1); pil.BackgroundColor3 = NACHT; pil.BackgroundTransparency = 1
	pil.AutoButtonColor = false; pil.Text = ""; pil.Parent = bb
	Instance.new("UICorner", pil).CornerRadius = UDim.new(1, 0)
	local rand = Instance.new("UIStroke"); rand.Color = GOUD; rand.Thickness = 2.5; rand.Transparency = 1; rand.Parent = pil
	local grad = Instance.new("UIGradient"); grad.Rotation = 90
	grad.Color = ColorSequence.new(Color3.fromRGB(40, 62, 120), Color3.fromRGB(14, 22, 48)); grad.Parent = pil
	local toets = Instance.new("TextLabel"); toets.AnchorPoint = Vector2.new(0, 0.5); toets.Position = UDim2.new(0, 10, 0.5, 0)
	toets.Size = UDim2.fromOffset(50, 50); toets.BackgroundColor3 = GOUD; toets.BackgroundTransparency = 1; toets.Font = Enum.Font.GothamBlack
	toets.TextSize = 22; toets.TextColor3 = NACHT; toets.TextTransparency = 1; toets.AutoLocalize = false
	toets.Text = toetsTekst(pr, invoer); toets.Parent = pil
	Instance.new("UICorner", toets).CornerRadius = UDim.new(1, 0)
	local ring = Instance.new("UIStroke"); ring.Color = Color3.fromRGB(255, 236, 180); ring.Thickness = 2; ring.Transparency = 1; ring.Parent = toets
	local actie = Instance.new("TextLabel"); actie.Position = UDim2.new(0, 72, 0, 10); actie.Size = UDim2.new(1, -86, 0, 30)
	actie.BackgroundTransparency = 1; actie.Font = Enum.Font.Fantasy; actie.TextSize = 28; actie.TextColor3 = Color3.fromRGB(255, 246, 225)
	actie.TextXAlignment = Enum.TextXAlignment.Left; actie.TextTransparency = 1; actie.Text = pr.ActionText; actie.Parent = pil
	local obj = Instance.new("TextLabel"); obj.Position = UDim2.new(0, 73, 0, 40); obj.Size = UDim2.new(1, -86, 0, 18)
	obj.BackgroundTransparency = 1; obj.Font = Enum.Font.GothamBold; obj.TextSize = 13; obj.TextColor3 = GOUD; obj.AutoLocalize = false
	obj.TextXAlignment = Enum.TextXAlignment.Left; obj.TextTransparency = 1; obj.Text = "S I R O C C O"; obj.Parent = pil
	local balk = Instance.new("Frame"); balk.AnchorPoint = Vector2.new(0, 1); balk.Position = UDim2.new(0, 72, 1, -8)
	balk.Size = UDim2.new(0, 0, 0, 3); balk.BackgroundColor3 = GOUD; balk.BorderSizePixel = 0; balk.Parent = pil
	Instance.new("UICorner", balk).CornerRadius = UDim.new(1, 0)
	bb.Parent = plr:WaitForChild("PlayerGui")
	knoppen[pr] = bb
	local IN = TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
	TweenService:Create(schaal, IN, {Scale = 1}):Play()
	TweenService:Create(pil, IN, {BackgroundTransparency = 0.08}):Play()
	TweenService:Create(rand, IN, {Transparency = 0}):Play()
	TweenService:Create(toets, IN, {BackgroundTransparency = 0, TextTransparency = 0}):Play()
	TweenService:Create(ring, IN, {Transparency = 0.3}):Play()
	TweenService:Create(actie, IN, {TextTransparency = 0}):Play()
	TweenService:Create(obj, IN, {TextTransparency = 0}):Play()
	-- vasthouden: balk loopt vol; tikken/klikken op de knop werkt ook (touch)
	local verb: {RBXScriptConnection} = {}
	table.insert(verb, pr.PromptButtonHoldBegan:Connect(function()
		TweenService:Create(balk, TweenInfo.new(pr.HoldDuration, Enum.EasingStyle.Linear), {Size = UDim2.new(1, -86, 0, 3)}):Play()
		TweenService:Create(schaal, TweenInfo.new(0.12), {Scale = 0.95}):Play()
	end))
	table.insert(verb, pr.PromptButtonHoldEnded:Connect(function()
		TweenService:Create(balk, TweenInfo.new(0.15), {Size = UDim2.new(0, 0, 0, 3)}):Play()
		TweenService:Create(schaal, TweenInfo.new(0.2, Enum.EasingStyle.Back), {Scale = 1}):Play()
	end))
	table.insert(verb, pr.Triggered:Connect(function()
		TweenService:Create(toets, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Size = UDim2.fromOffset(58, 58)}):Play()
	end))
	table.insert(verb, pil.InputBegan:Connect(function(io)
		if io.UserInputType == Enum.UserInputType.Touch or io.UserInputType == Enum.UserInputType.MouseButton1 then pr:InputHoldBegin() end
	end))
	table.insert(verb, pil.InputEnded:Connect(function(io)
		if io.UserInputType == Enum.UserInputType.Touch or io.UserInputType == Enum.UserInputType.MouseButton1 then pr:InputHoldEnd() end
	end))
	pr.PromptHidden:Once(function()
		for _, c in verb do c:Disconnect() end
		knoppen[pr] = nil
		local UIT = TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		TweenService:Create(schaal, UIT, {Scale = 0.5}):Play()
		TweenService:Create(pil, UIT, {BackgroundTransparency = 1}):Play()
		for _, l in {toets, actie, obj} do TweenService:Create(l, UIT, {TextTransparency = 1, BackgroundTransparency = 1}):Play() end
		TweenService:Create(rand, UIT, {Transparency = 1}):Play()
		task.delay(0.25, function() bb:Destroy() end)
	end)
end)

-- camera draait mee met je boot (Pagode-methode: draaiing om het focuspunt, rondkijken blijft gewoon werken)
local meeDraai = 0
RunService:BindToRenderStep("SiroccoMeedraaien", Enum.RenderPriority.Camera.Value + 2, function()
	if meeDraai == 0 then return end
	local cam = workspace.CurrentCamera
	local f = cam.Focus.Position
	cam.CFrame = CFrame.new(f) * CFrame.Angles(0, meeDraai, 0) * CFrame.new(-f) * cam.CFrame
	meeDraai = 0
end)

local cfs = table.create(#delen) :: {CFrame}
local T: {[string]: CFrame} = {}
local vorigF, vorigV = -1, -1
local vorigStoel: CFrame? = nil
local springUit = false
local vorigeFase = ""
local wasInBoot = false
local gemeld = false
plr.CharacterAdded:Connect(function() springUit = false; vorigStoel = nil; wasInBoot = false end)

-- ===== zelf draaien =====
local draaiEvent = ReplicatedStorage:WaitForChild("SiroccoDraai") :: RemoteEvent
local MAX_W, VERSNEL, REM = 2.6, 3.2, 1.6          -- rad/s extra draai, rad/s2 aandrijven, rad/s2 uitlopen
local eigenBoot: string? = nil
local eigenX, eigenW = 0, 0
local links, rechts = false, false
local gebonden = false
local verzonden, vorigZend = 0, 0
local gladX: {[string]: number} = {}
local function knop(naam: string, state: Enum.UserInputState): Enum.ContextActionResult
	local aan = state == Enum.UserInputState.Begin
	if state == Enum.UserInputState.Cancel then aan = false end
	if naam == "SiroccoLinks" then links = aan else rechts = aan end
	return Enum.ContextActionResult.Sink
end
local function binden(aan: boolean)
	if aan == gebonden then return end
	gebonden = aan
	if aan then
		CAS:BindActionAtPriority("SiroccoLinks", knop, true, 3000, Enum.KeyCode.A, Enum.KeyCode.Left, Enum.KeyCode.ButtonL1)
		CAS:BindActionAtPriority("SiroccoRechts", knop, true, 3000, Enum.KeyCode.D, Enum.KeyCode.Right, Enum.KeyCode.ButtonR1)
		CAS:SetTitle("SiroccoLinks", "<"); CAS:SetTitle("SiroccoRechts", ">")
		CAS:SetPosition("SiroccoLinks", UDim2.new(1, -230, 1, -130)); CAS:SetPosition("SiroccoRechts", UDim2.new(1, -120, 1, -130))
	else
		CAS:UnbindAction("SiroccoLinks"); CAS:UnbindAction("SiroccoRechts")
		links, rechts = false, false
	end
end
local function extraVan(n: string, nu: number, dt: number): number
	if n == eigenBoot then return eigenX end
	local x = rit:GetAttribute("X_" .. n) :: Vector3?
	local doel = 0
	if x then doel = x.X + x.Y * math.clamp(nu - x.Z, 0, 0.3) end
	local g = gladX[n] or doel
	if math.abs(doel - g) > 3 then g = doel end
	g += (doel - g) * math.min(1, dt * 10)
	gladX[n] = g
	return g
end

RunService.PreSimulation:Connect(function(dt: number)
	local start = rit:GetAttribute("RitStart") :: number?
	if not start then return end
	local nu = workspace:GetServerTimeNow()
	local tc = (nu - start) % CYCLUS
	local rijdt = tc >= T_IN and tc < T_IN + T_RIT
	local F, v = 0, 0
	if rijdt then F, v = voortgang(tc - T_IN) end
	local ch = plr.Character
	local hum = ch and ch:FindFirstChildOfClass("Humanoid")
	local zit = hum and hum.SeatPart
	local inBoot = zit ~= nil and zit:IsDescendantOf(rit)
	-- eigen boot: aandrijven alleen op volle vaart (niet bij optrekken/uitlopen), daarna uitlopen
	eigenBoot = inBoot and zit and zit.Name:match("_rt(%a+)$") or nil
	local mag = inBoot and rijdt and tc - T_IN > RAMP and tc - T_IN < T_RIT - RAMP
	binden(mag)
	if eigenBoot and rijdt then
		local invoer = mag and ((rechts and 1 or 0) - (links and 1 or 0)) or 0
		if invoer ~= 0 then eigenW = math.clamp(eigenW + invoer * VERSNEL * dt, -MAX_W, MAX_W)
		else eigenW -= math.sign(eigenW) * math.min(math.abs(eigenW), REM * dt) end
		eigenX += eigenW * dt
		if nu - verzonden > 0.1 and (math.abs(eigenX - vorigZend) > 1e-3 or eigenW ~= 0) then
			draaiEvent:FireServer(eigenX, eigenW); verzonden = nu; vorigZend = eigenX
		end
	else
		eigenX, eigenW, vorigZend = 0, 0, 0
	end
	if rijdt or F ~= vorigF or v ~= vorigV then
		T.m = draai(MIDDEN, OMW_M * TAU * F)
		local uitloop = rijdt and tc - T_IN > T_RIT - RAMP
		for _, n in NAMEN do
			local g = groepen[n]
			if n:sub(1, 1) == "s" then T[n] = T.m * draai(g.P, OMW_S * TAU * F)
			elseif n:sub(1, 1) == "b" then
				local P = g.P
				local x = rijdt and extraVan(n, nu, dt) or 0
				if uitloop then local doel = math.round(x / TAU) * TAU; x = doel + (x - doel) * v end   -- terug naar instapstand
				T[n] = T[g.ouder :: string] * CFrame.new(P) * CFrame.Angles(0, bootHoek(g.i, F) + x, 0) * dobber(g.i, tc, v) * CFrame.new(-P)
			end
		end
		for k, p in delen do cfs[k] = T[groepVan[k]] * rust[k] end
		workspace:BulkMoveTo(delen, cfs, Enum.BulkMoveMode.FireCFrameChanged)
		vorigF, vorigV = F, v
	end
	-- klapdeuren: 1,5 s open/dicht aan begin en eind van hun fase
	local openIn = tc < T_IN and e(math.min(tc, T_IN - tc) / 1.5) or 0
	local tu = tc - T_IN - T_RIT
	local openUit = tu >= 0 and e(math.min(tu - 0.5, T_UIT - tu) / 1.5) or 0
	if openIn ~= deurStand.in_ or openUit ~= deurStand.uit then
		for _, d in deuren do
			local f = d.uit and openUit or openIn
			d.p.CFrame = CFrame.new(d.H) * CFrame.Angles(0, d.hoek * f, 0) * CFrame.new(-d.H) * d.rust
			d.p.CanCollide = f < 0.5
		end
		deurStand.in_, deurStand.uit = openIn, openUit
	end
	-- eigen speler in een boot: camera mee, niet uit de boot springen tot het uitstappen, geen andere instapknoppen
	if inBoot and zit then
		local cf = zit.CFrame
		if vorigStoel then
			local _, dy, _ = (cf.Rotation * vorigStoel.Rotation:Inverse()):ToEulerAnglesYXZ()
			meeDraai += dy
		end
		vorigStoel = cf
		for _, pr in prompts do if pr.Enabled then pr.Enabled = false end end      -- alleen lokaal: je zit al
	else
		vorigStoel = nil
	end
	local blokkeer = inBoot
	if hum and blokkeer ~= springUit then
		hum:SetStateEnabled(Enum.HumanoidStateType.Jumping, not blokkeer)
		springUit = blokkeer
	end
	-- beleving
	local f = tc < T_IN and "instappen" or (rijdt and "rit" or "uitstappen")
	if inBoot and not wasInBoot and f == "instappen" then toonTitel("Welcome aboard, sailor", 4) end
	if f ~= vorigeFase then
		if f == "rit" and inBoot then meld("Hold on tight!", 2.5) end
		gemeld = false
		vorigeFase = f
	end
	if mag and not gemeld then                        -- uitleg zodra je zelf mag draaien
		gemeld = true
		local touch = UIS.TouchEnabled and not UIS.KeyboardEnabled
		meld(touch and "Spin your boat with the arrows" or "Spin your boat: A / D", 5)
	end
	wasInBoot = inBoot
end)
