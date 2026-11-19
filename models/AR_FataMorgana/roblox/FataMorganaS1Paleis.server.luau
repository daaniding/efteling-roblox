-- FataMorganaS1Paleis (ServerScriptService): sectie 1c, de fata morgana. Het paleisje op het achterdoek verschijnt als een sloep uit de
-- grot de jungle in vaart en verdwijnt weer zodra hij de haarspeldbocht in draait (Eftepedia: "Voor ons is in de verte even een oosters
-- paleis te zien, dat ook snel weer verdwijnt - als een fata morgana"; video 126-140 s). Tijdens het zichtbaar zijn trilt het beeld licht
-- (luchtspiegeling). Paneel = workspace.FataMorgana.Junglegroen.Paleis (plaats_s1c).
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local fm = workspace:WaitForChild("FataMorgana")
local pal = fm:WaitForChild("Junglegroen"):WaitForChild("Paleis")
local beeld = pal:FindFirstChildWhichIsA("SurfaceGui"):FindFirstChild("Beeld")
local basis = pal.CFrame
local ZICHT = pal:GetAttribute("Zichtbaar") or 0.05

-- zone (modelmeters): sloepmidden van net in de grot tot het begin van de bocht
local function inZone(p)
	local x, y = p.X / 3, -p.Z / 3
	return x < -3.9 and x > -7.2 and y < -324.6 and y > -327.6
end

local zichtbaar = false
local function zet(aan)
	if aan == zichtbaar then return end
	zichtbaar = aan
	TweenService:Create(beeld, TweenInfo.new(aan and 1.6 or 1.1, Enum.EasingStyle.Sine), {ImageTransparency = aan and ZICHT or 1}):Play()
end

local t = 0
RunService.Heartbeat:Connect(function(dt)
	t += dt
	if beeld.ImageTransparency < 0.95 then                               -- luchtspiegeling: zacht golven
		pal.CFrame = basis * CFrame.new(0, math.sin(t * 2.3) * 0.06, 0)
	end
end)

while true do
	local iemand = false
	local vaart = fm:FindFirstChild("Vaart")
	if vaart then
		for _, b in vaart:GetChildren() do
			if inZone(b:GetPivot().Position) then iemand = true; break end
		end
	end
	zet(iemand)
	task.wait(0.15)
end
