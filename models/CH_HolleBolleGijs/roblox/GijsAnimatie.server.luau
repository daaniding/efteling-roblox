--!strict
-- Holle Bolle Gijs: roept "Papier hier!", kauwt als hij papier krijgt, knikt en bedankt.
-- Hoort als Script in het Model "HolleBolleGijs". Verwacht sub-modellen Head en Mouth (zie opbouwscript).
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local model = script.Parent :: Model
local head = model:WaitForChild("Head") :: Model
local mouth = head:WaitForChild("Mouth") :: Model
local hole = mouth:WaitForChild("MouthHole") :: BasePart
local lips = mouth:WaitForChild("Lips") :: BasePart
local prompt = hole:WaitForChild("GeefPapier") :: ProximityPrompt
local bubble = head:WaitForChild("Tekst") :: BillboardGui
local label = bubble:WaitForChild("Label") :: TextLabel
local sndCall = hole:FindFirstChild("SndRoep") :: Sound?
local sndEat = hole:FindFirstChild("SndEet") :: Sound?

-- scharnierpunten (wereld), vastgelegd bij start
local headRest = head:GetPivot()
local neckPivot = CFrame.new(headRest.Position - Vector3.new(0, 0.55 * 3, 0)) -- nek 0.55 m onder hoofdcentrum
local lipsRestSize = lips.Size
local busy = false

local function tweenPivot(target: Model, fromCF: CFrame, toCF: CFrame, t: number, style: Enum.EasingStyle?)
	local v = Instance.new("CFrameValue")
	v.Value = fromCF
	v.Changed:Connect(function(cf) target:PivotTo(cf) end)
	local tw = TweenService:Create(v, TweenInfo.new(t, style or Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), { Value = toCF })
	tw:Play()
	tw.Completed:Wait()
	v:Destroy()
end

-- hoofd kantelt om de nek: pitch (knikken) in graden
local function headTilt(pitchDeg: number, t: number)
	local rel = neckPivot:ToObjectSpace(headRest)
	local rot = CFrame.Angles(math.rad(pitchDeg), 0, 0)
	local toCF = neckPivot * rot * rel
	tweenPivot(head, head:GetPivot(), toCF, t)
end

local function lipsPulse(scale: number, t: number)
	local tw = TweenService:Create(lips, TweenInfo.new(t, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Size = lipsRestSize * scale })
	tw:Play(); tw.Completed:Wait()
end

local function say(text: string, seconds: number)
	label.Text = text
	bubble.Enabled = true
	task.delay(seconds, function()
		if label.Text == text then bubble.Enabled = false end
	end)
end

local function roep()
	if busy then return end
	busy = true
	if sndCall then sndCall:Play() end
	say("Papier hier!", 2.5)
	headTilt(-7, 0.35)              -- hoofd iets achterover
	for _ = 1, 3 do                 -- drie lettergrepen: pa-pier-hier
		lipsPulse(1.28, 0.14)
		lipsPulse(1.0, 0.16)
	end
	headTilt(0, 0.4)
	busy = false
end

local function eet(bron: Instance?)
	if busy then return end
	busy = true
	-- propje papier dat in de mond vliegt
	local prop = Instance.new("Part")
	prop.Shape = Enum.PartType.Ball
	prop.Size = Vector3.new(0.9, 0.9, 0.9)
	prop.Color = Color3.fromRGB(245, 243, 230)
	prop.Material = Enum.Material.SmoothPlastic
	prop.CanCollide = false; prop.Anchored = true
	local start = hole.Position + hole.CFrame.LookVector * -4 + Vector3.new(0, -1.5, 0)
	if bron and bron:IsA("BasePart") then start = bron.Position end
	prop.CFrame = CFrame.new(start)
	prop.Parent = workspace
	local tw = TweenService:Create(prop, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { CFrame = CFrame.new(hole.Position), Size = Vector3.new(0.3, 0.3, 0.3) })
	tw:Play(); tw.Completed:Wait()
	prop:Destroy()
	if sndEat then sndEat:Play() end
	-- kauwen: lippen knijpen, hoofd knikt mee
	for i = 1, 4 do
		task.spawn(headTilt, 5, 0.18)
		lipsPulse(0.72, 0.18)
		task.spawn(headTilt, 0, 0.18)
		lipsPulse(1.0, 0.18)
	end
	headTilt(-4, 0.25)
	say("Dank u wel!", 2.5)
	lipsPulse(1.2, 0.2); lipsPulse(1.0, 0.25)
	headTilt(0, 0.35)
	busy = false
end

prompt.Triggered:Connect(function(player) eet(nil) end)

-- los papier (onverankerde parts met naam "Papier") dat de mond raakt
hole.Touched:Connect(function(part)
	if part.Name == "Papier" and not part.Anchored then
		part:Destroy()
		task.spawn(eet, nil)
	end
end)

-- om de 9 tot 16 seconden roepen
task.spawn(function()
	while true do
		task.wait(math.random(9, 16))
		roep()
	end
end)
