--!strict
-- PagodeRit: laat de Pagode rijden (Daan 17 nov: "laat eerst de attractie werken"). Hoort in ServerScriptService.
-- Ritverloop naar de on-ride video _Wz0aORIVaM (5 min): instappen in de bak, stijgen (~55 s), boven ~1 volle draai (~180 s),
-- dalen (~55 s). De arm draait om de draaias; de gondel blijft waterpas en draait om zijn eigen as.
-- De gondel is een losse (niet verankerde) groep, gestuurd met starre AlignPosition/AlignOrientation: zo beweegt hij met echte
-- snelheid en rijden spelers die erop staan mee. Arm en hefcilinders zijn verankerd en worden elk frame neergezet.
-- Opzet (modellen, lassen, cilinders): roblox/pagode_rit.luau. Maten: Blender-meters x 3 = stud.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local PhysicsService = game:GetService("PhysicsService")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local arm = pag:WaitForChild("Arm") :: Model
local gondel = pag:WaitForChild("Gondel") :: Model
local kern = gondel:WaitForChild("Kern") :: BasePart
local ap = kern:WaitForChild("AlignPosition") :: AlignPosition
local ao = kern:WaitForChild("AlignOrientation") :: AlignOrientation
local PIV = (pag:WaitForChild("AsFrame") :: CFrameValue).Value          -- draaias, stand omhoog
local JL = pag:GetAttribute("GondelLokaal") :: Vector3                     -- gondelmidden t.o.v. de as (lokaal, stud)
local Y_INSTAP = 2 + 1.3 * S                                               -- vlonder/instapniveau NAP 11.3
local DEK = 2.2 * S                                                        -- dek boven het gondelmidden
local BAK = Vector3.new(360.0 * S, 0, -47.5 * S)                           -- bakmidden

-- botsgroepen: de gondel botst niet met de wereld (hij zakt in de bak en de put), wel met spelers
pcall(function() PhysicsService:RegisterCollisionGroup("PagodeGondel") end)
pcall(function() PhysicsService:RegisterCollisionGroup("PagodeSpeler") end)
PhysicsService:CollisionGroupSetCollidable("PagodeGondel", "Default", false)
PhysicsService:CollisionGroupSetCollidable("PagodeGondel", "PagodeSpeler", true)
for _, p in gondel:GetDescendants() do if p:IsA("BasePart") then p.CollisionGroup = "PagodeGondel" end end
local function speler(ch: Model)
	for _, p in ch:GetDescendants() do if p:IsA("BasePart") then p.CollisionGroup = "PagodeSpeler" end end
	ch.DescendantAdded:Connect(function(p) if p:IsA("BasePart") then p.CollisionGroup = "PagodeSpeler" end end)
end
for _, pl in Players:GetPlayers() do if pl.Character then speler(pl.Character) end; pl.CharacterAdded:Connect(speler) end
Players.PlayerAdded:Connect(function(pl) pl.CharacterAdded:Connect(speler) end)

-- stand beneden: hoek waarbij het dek op instapniveau ligt (bisectie)
local function Jw(th: number): Vector3 return (PIV * CFrame.Angles(0, 0, th)):PointToWorldSpace(JL) end
local lo, hi = math.rad(70), math.rad(120)
for _ = 1, 50 do
	local m = (lo + hi) / 2
	if Jw(m).Y + DEK > Y_INSTAP then lo = m else hi = m end
end
local TH_D = (lo + hi) / 2
-- de armmaat uit de foto komt ~2.7 m tekort voor het bakmidden: kleine schuif die pas onderin meetelt
local jd = Jw(TH_D)
local CORR = Vector3.new(BAK.X - jd.X, 0, BAK.Z - jd.Z)
local function schuif(th: number): Vector3 local t = math.clamp(th / TH_D, 0, 1); return CORR * t ^ 4 end
pag:SetAttribute("HoekBeneden", math.deg(TH_D)); pag:SetAttribute("SchuifBeneden", CORR.Magnitude / S)

-- hefcilinders: voet vast in de put, kop op de arm; huis schuift over de zuigerstang
type Cil = {voet: Vector3, kop: Vector3, huis: BasePart, stang: BasePart, Lh: number, Ls: number}
local cils: {Cil} = {}
for _, c in (pag:WaitForChild("Cilinders") :: Folder):GetChildren() do
	if c:IsA("Folder") then
		local v, k = c:GetAttribute("Voet") :: Vector3, c:GetAttribute("Kop") :: Vector3
		local Lup = (k - v).Magnitude
		table.insert(cils, {voet = PIV:PointToWorldSpace(v), kop = k, huis = c:WaitForChild("Huis") :: BasePart,
			stang = c:WaitForChild("Stang") :: BasePart, Lh = 0.62 * Lup + 0.9, Ls = 0.38 * Lup + 0.6})
	end
end
local function staaf(p: BasePart, a: Vector3, richting: Vector3, L: number)
	p.Size = Vector3.new(L, p.Size.Y, p.Size.Z)
	p.CFrame = CFrame.lookAt(a + richting * (L / 2), a + richting * L) * CFrame.Angles(0, math.pi / 2, 0)
end

-- hekken: open bij het instappen (reling op de gondel en rond de bak), dicht tijdens de rit
local function hekken(open: boolean)
	for _, p in gondel:GetDescendants() do if p:IsA("BasePart") and p.Name == "reling" then p.CanCollide = not open end end
	local st = pag:FindFirstChild("Station")
	if st then for _, p in st:GetDescendants() do if p:IsA("BasePart") and p.Name == "bakreling" then p.CanCollide = not open end end end
end

local FASEN = {{"instappen", 25}, {"sluiten", 5}, {"omhoog", 55}, {"boven", 180}, {"omlaag", 55}}
local T_RIT = 55 + 180 + 55
local function e(t: number): number return (1 - math.cos(math.pi * math.clamp(t, 0, 1))) / 2 end

local function stand(th: number, phi: number)
	arm:PivotTo(PIV * CFrame.Angles(0, 0, th))
	local rot = PIV.Rotation * CFrame.Angles(0, phi, 0)
	ap.Position = Jw(th) + schuif(th)
	ao.CFrame = rot
	local A = PIV * CFrame.Angles(0, 0, th)
	for _, c in cils do
		local k = A:PointToWorldSpace(c.kop); local u = (k - c.voet).Unit
		staaf(c.huis, c.voet, u, c.Lh)
		staaf(c.stang, k, -u, c.Ls)
	end
end

-- beginnen in de bak
local rot0 = PIV.Rotation
kern.CFrame = CFrame.new(Jw(TH_D) + schuif(TH_D)) * rot0
stand(TH_D, 0)
pcall(function() kern:SetNetworkOwner(nil) end)
pag:SetAttribute("Fase", "instappen")

while true do
	local t_rit = 0
	for _, f in FASEN do
		local naam, duur = f[1] :: string, f[2] :: number
		pag:SetAttribute("Fase", naam)
		hekken(naam == "instappen")
		local t0 = os.clock()
		while os.clock() - t0 < duur do
			local t = (os.clock() - t0) / duur
			local th = TH_D
			if naam == "omhoog" then th = TH_D * (1 - e(t))
			elseif naam == "boven" then th = 0
			elseif naam == "omlaag" then th = TH_D * e(t) end
			local phi = 0
			if naam == "omhoog" or naam == "boven" or naam == "omlaag" then
				phi = 2 * math.pi * e((t_rit + (os.clock() - t0)) / T_RIT)       -- een volle draai over de hele rit, zacht in/uit
			end
			stand(th, phi)
			RunService.Heartbeat:Wait()
		end
		if naam == "omhoog" or naam == "boven" or naam == "omlaag" then t_rit += duur end
	end
end
