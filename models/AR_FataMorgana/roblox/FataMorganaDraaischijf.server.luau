-- FataMorganaDraaischijf (ServerScriptService, Script): laat de draaischijf in de instaphal langzaam ronddraaien
-- (Daan 18 nov: "laat hem ronddraaien"). workspace.FataMorgana.Draaischijf bevat het bovenblad (FM_dekhout), de rand (FM_dekrand)
-- en de witte streepjes (FM_witlijn); alle drie gecentreerd op het midden van de schijf. Het controlehok in het midden staat stil.
-- De onderdelen blijven verankerd: het beeld draait via CFrame, en AssemblyAngularVelocity zorgt dat spelers op de schijf
-- meedraaien (zoals een draaiende lopende band). Snelheid: 1 omwenteling per 2 minuten (rand ~0,4 m/s).
local RunService = game:GetService("RunService")
local OMEGA = 2 * math.pi / 120                       -- rad/s (positief = tegen de klok in van boven gezien)
local schijf = workspace:WaitForChild("FataMorgana"):WaitForChild("Draaischijf")
local delen = {}
local midden
for _, p in schijf:GetChildren() do
	if p:IsA("BasePart") then
		midden = midden or Vector3.new(p.Position.X, 0, p.Position.Z)
		table.insert(delen, p)
	end
end
if not midden then return end
local as = CFrame.new(midden.X, 0, midden.Z)
local rel = {}
for _, p in delen do
	rel[p] = as:ToObjectSpace(p.CFrame)
	p.AssemblyAngularVelocity = Vector3.new(0, OMEGA, 0)
end
local hoek = 0
RunService.Heartbeat:Connect(function(dt)
	hoek = (hoek + OMEGA * dt) % (2 * math.pi)
	local r = as * CFrame.Angles(0, hoek, 0)
	for _, p in delen do
		p.CFrame = r * rel[p]
	end
end)
