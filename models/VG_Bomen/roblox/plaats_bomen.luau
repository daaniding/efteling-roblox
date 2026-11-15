-- Sprookjesbos-bomen (models/VG_Bomen): elke echte boom uit AHN + luchtfoto (tools/bomen_ahn.py -> build/03_plaatsing.py).
-- Vereist: ServerStorage.BomenVB met de 12 sjablonen (VB_<soort>_stam/_kroon) en StringValue 'Plaatsing'
-- (exports/plaatsing.b64: per boom 11 tekens base64, 61 bit: soort 3 | draaiing 6 | kroonschaal 10 (/500) | hoogteschaal 10 (/500) | Z 16 | X 16 (0,1 stud, +2000)).
-- Oude v1-bomen (beuk/eik/den/berk/kastanje in de *Groen/*Bos-mappen, niet Villa Volta) -> ServerStorage.OudeBomen (attribuut Herkomst).
local S = {"beuk", "eik", "kastanje", "berk", "den", "spar"}
local OFF = {beuk_stam={1.82,20.58,-0.59},beuk_kroon={0.28,28.79,0.1},eik_stam={0.96,21.65,1.97},eik_kroon={-0.06,30.6,0.09},kastanje_stam={0.59,21.53,-3.32},kastanje_kroon={-0.42,30.12,0.76},berk_stam={-3.11,20.31,-1.7},berk_kroon={-0.26,29.48,0.13},den_stam={1.26,21.75,-0.89},den_kroon={-0.1,37.53,-0.27},spar_stam={-0.39,21.83,-0.16},spar_kroon={0.06,22.5,-1.0}}
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {}; for i = 1, #A do IDX[A:sub(i, i)] = i - 1 end

-- 1) oude bomen weg (terug te zetten)
local oud = game.ServerStorage:FindFirstChild("OudeBomen") or Instance.new("Folder", game.ServerStorage); oud.Name = "OudeBomen"
local weg = 0
for _, top in ipairs(workspace:GetChildren()) do
	if (top.Name:find("Groen") or top.Name:find("Bos")) and not top.Name:find("VillaVolta") then
		for _, d in ipairs(top:GetDescendants()) do
			if d:IsA("Model") and d.Parent and (d.Name:match("^beuk%d*$") or d.Name:match("^eik%d*$") or d.Name:match("^den%d*$") or d.Name:match("^berk%d*$") or d.Name:match("^kastanje%d*$")) then
				d:SetAttribute("Herkomst", d.Parent:GetFullName()); d.Parent = oud; weg += 1
				if weg % 200 == 0 then task.wait() end
			end
		end
	end
end
local proef = workspace:FindFirstChild("BomenProef"); if proef then proef:Destroy() end

-- 2) nieuwe bomen
local bron = game.ServerStorage.BomenVB; local data = bron.Plaatsing.Value
local t = workspace.Terrain
local rt = RaycastParams.new(); rt.FilterType = Enum.RaycastFilterType.Include; rt.FilterDescendantsInstances = {t}; rt.IgnoreWater = true
local map = workspace:FindFirstChild("SprookjesbosBomen"); if map then map:Destroy() end
map = Instance.new("Folder"); map.Name = "SprookjesbosBomen"; map.Parent = workspace
local function bits(chunk)
	local b = {}
	for i = 1, 11 do local v = IDX[chunk:sub(i, i)]; for j = 0, 5 do b[(i - 1) * 6 + j] = bit32.extract(v, j) end end
	local function veld(o, n) local s = 0; for j = n - 1, 0, -1 do s = s * 2 + b[o + j] end; return s end
	return veld(0, 3), veld(3, 6), veld(9, 10), veld(19, 10), veld(29, 16), veld(45, 16)
end
local n = 0
for i = 1, #data, 11 do
	local si, r, k, h, z, x = bits(data:sub(i, i + 10))
	local s = S[si + 1]; local X, Z = x / 10 - 2000, z / 10 - 2000; local sh, sk = h / 500, k / 500; local rot = r / 64 * 2 * math.pi
	local g = workspace:Raycast(Vector3.new(X, 200, Z), Vector3.new(0, -400, 0), rt)
	local y0 = (g and g.Position.Y or 0) - 0.4
	local stamS = math.clamp(sh, 0.45, 1.3)
	local rotc = CFrame.Angles(0, rot, 0)
	for _, deel in ipairs({"stam", "kroon"}) do
		local sj = bron["VB_" .. s .. "_" .. deel]; local p = sj:Clone()
		local sxz = deel == "stam" and stamS or sk
		p.Size = Vector3.new(sj.Size.X * sxz, sj.Size.Y * sh, sj.Size.Z * sxz)
		local o = OFF[s .. "_" .. deel]
		p.CFrame = CFrame.new(Vector3.new(X, y0, Z) + rotc:VectorToWorldSpace(Vector3.new(o[1] * sxz, o[2] * sh, o[3] * sxz))) * rotc * sj.CFrame.Rotation
		p:SetAttribute("Soort", s)
		p.Parent = map
	end
	n += 1
	if n % 60 == 0 then task.wait() end
end
return weg .. " oude bomen naar ServerStorage.OudeBomen, " .. n .. " nieuwe bomen geplaatst"
