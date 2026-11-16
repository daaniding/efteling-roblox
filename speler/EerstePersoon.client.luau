-- StarterPlayer.StarterPlayerScripts.EerstePersoon (LocalScript). Ook gezet: StarterPlayer.CameraMode = LockFirstPerson,
-- StarterPlayer.CharacterWalkSpeed = 10 (16 = draven). Ooghoogte gemeten: 4,6 stud = 1,55 m.
-- First person met eigen lichaam zichtbaar en een subtiele loopbeweging (Daan, 16 nov: "voor de echte feeling").
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local speler = Players.LocalPlayer
local camera = workspace.CurrentCamera
speler.CameraMode = Enum.CameraMode.LockFirstPerson
camera.FieldOfView = 78

local VOORUIT = -0.55     -- camera iets voor het hoofd: je kijkt niet vanuit je eigen nek
local fase = 0

local function lichaam(karakter)
	local hum = karakter:WaitForChild("Humanoid")
	local hoofd = karakter:WaitForChild("Head")
	RunService:BindToRenderStep("EerstePersoon", Enum.RenderPriority.Camera.Value + 1, function(dt)
		-- armen, romp en benen zichtbaar; hoofd en hoofdaccessoires niet
		for _, d in ipairs(karakter:GetDescendants()) do
			if d:IsA("BasePart") then
				local opHoofd = d == hoofd or (d.Parent:IsA("Accessory") and d:FindFirstChildWhichIsA("Attachment") and hoofd:FindFirstChild(d:FindFirstChildWhichIsA("Attachment").Name))
				d.LocalTransparencyModifier = opHoofd and 1 or 0
			end
		end
		-- loopbeweging: alleen als je echt loopt, klein en rustig
		local v = hum.RootPart and Vector3.new(hum.RootPart.AssemblyLinearVelocity.X, 0, hum.RootPart.AssemblyLinearVelocity.Z).Magnitude or 0
		local mate = math.clamp(v / hum.WalkSpeed, 0, 1)
		if hum.FloorMaterial == Enum.Material.Air then mate = 0 end
		fase += dt * (5 + 4 * mate) * mate
		local doel = Vector3.new(math.cos(fase) * 0.06 * mate, math.abs(math.sin(fase)) * 0.09 * mate, VOORUIT)
		hum.CameraOffset = hum.CameraOffset:Lerp(doel, math.clamp(dt * 12, 0, 1))
	end)
	hum.Died:Connect(function() pcall(function() RunService:UnbindFromRenderStep("EerstePersoon") end) end)
end
if speler.Character then lichaam(speler.Character) end
speler.CharacterAdded:Connect(lichaam)
speler.CharacterRemoving:Connect(function() pcall(function() RunService:UnbindFromRenderStep("EerstePersoon") end) end)
