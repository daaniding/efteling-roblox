--!strict
-- Voetstappen (StarterPlayerScripts): het standaard loopgeluid (RbxCharacterSounds, Sound "Running" in de HumanoidRootPart)
-- krijgt een opname die bij de ondergrond past (Daan 17 nov: "mijn loop sound moet realistischer"). Ondergrond via een
-- straal omlaag: rol van het Pagode-onderdeel (PG_<rol>_n) of het terreinmateriaal (gras).
local Players = game:GetService("Players")
local STAP = {
	steen = "rbxassetid://91557584218550",   -- "Brick Footsteps": klinkers, natuursteen, graniet, beton
	hout = "rbxassetid://6506537704",        -- "Floor Footsteps": vlonder, gondeldek
	metaal = "rbxassetid://6362185620",      -- "Concrete Footsteps": roosters, staal
	gras = "rbxassetid://106672010112184",   -- "walk_grass": terrein (Roblox-standaard klinkt als plastic)
}
local ROL = {klinker = "steen", natuursteen = "steen", breuksteen = "steen", graniet = "steen", voeg = "steen", steen = "steen",
	beton_groen = "steen", beton_groen_licht = "steen", beton_licht = "steen", asfalt = "steen", grind = "steen",
	vlonder = "hout", dek = "hout", rooster = "metaal", staal = "metaal", platform = "hout", subschijf = "hout", bestrating = "steen"}
local plr = Players.LocalPlayer
local ray = RaycastParams.new(); ray.FilterType = Enum.RaycastFilterType.Exclude

local function soort(hit: RaycastResult?): string?
	if not hit then return nil end
	local inst = hit.Instance
	if inst:IsA("Terrain") then return hit.Material == Enum.Material.Grass and "gras" or "steen" end
	local rol = string.match(inst.Name, "^PG_(.-)_%d+") or string.match(inst.Name, "^SI_(.-)_%d+")   -- ook de Sirocco (Daan 18 nov)
	return rol and ROL[rol] or "steen"
end

local function volg(ch: Model)
	local hrp = ch:WaitForChild("HumanoidRootPart", 10) :: BasePart?
	if not hrp then return end
	local run = hrp:WaitForChild("Running", 10) :: Sound?
	if not run then return end
	local standaard = run.SoundId
	ray.FilterDescendantsInstances = {ch}
	local huidig = ""
	while ch.Parent do
		local s = soort(workspace:Raycast(hrp.Position, Vector3.new(0, -6, 0), ray))
		local id = s and STAP[s] or standaard
		if id ~= huidig then run.SoundId = id; huidig = id end
		task.wait(0.15)
	end
end
plr.CharacterAdded:Connect(volg)
if plr.Character then task.spawn(volg, plr.Character) end
