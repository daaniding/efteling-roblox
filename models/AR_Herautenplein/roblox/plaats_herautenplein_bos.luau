-- Herautenplein bosrand: 59 bomen (beuk/eik uit MagischeKlokBos) in een band van 1.2-15 m rond de OSM-omtrek, niet op paden/gebouwen/MK/Prinsenpoort.
-- Posities: exports/bosrand.json (berekend in Python). Daan: luchtfoto toont bos tot aan de rand van het plein.
local P = {{10.6,8.6,"beuk",1.01}, {15.3,9.6,"eik",1.17}, {-24.8,3.0,"eik",1.01}, {-13.0,3.7,"beuk",1.08}, {28.0,2.9,"eik",1.07}, {-24.8,-2.3,"eik",1.13}, {-13.2,-3.8,"beuk",1.18}, {31.9,-2.8,"eik",0.91}, {-25.3,-11.0,"eik",1.13}, {32.8,-10.8,"eik",1.11}, {-31.7,-14.9,"beuk",1.02}, {-25.3,-14.9,"beuk",1.07}, {27.9,-16.2,"eik",1.02}, {32.9,-16.5,"eik",0.92}, {28.1,-20.8,"eik",1.12}, {32.0,-20.1,"beuk",1.23}, {-31.2,-27.6,"beuk",0.86}, {21.3,-26.5,"eik",1.02}, {28.0,-28.0,"eik",1.19}, {21.2,-33.4,"eik",1.12}, {28.3,-33.6,"beuk",1.11}, {17.2,-37.1,"eik",1.13}, {21.2,-37.5,"eik",0.99}, {26.4,-38.9,"eik",1.07}, {21.6,-45.5,"eik",0.98}, {26.6,-45.7,"beuk",0.91}, {23.2,-50.0,"beuk",1.0}, {27.8,-49.5,"eik",1.04}, {-30.1,-56.9,"eik",1.05}, {-25.6,-72.4,"beuk",1.0}, {-19.0,-72.5,"eik",0.94}, {26.9,-74.2,"beuk",1.15}, {34.7,-71.7,"eik",1.1}, {-19.4,-78.5,"beuk",0.91}, {-13.0,-77.5,"beuk",0.9}, {-6.4,-78.5,"beuk",1.17}, {16.4,-80.2,"beuk",0.92}, {20.2,-80.0,"beuk",1.02}, {27.8,-77.7,"beuk",0.97}, {33.2,-77.8,"beuk",1.04}, {-18.0,-85.0,"eik",0.93}, {-12.1,-85.6,"eik",0.94}, {-8.5,-83.2,"eik",1.14}, {-1.7,-85.2,"beuk",1.24}, {14.5,-83.5,"beuk",0.9}, {20.3,-84.1,"beuk",0.9}, {26.5,-85.0,"eik",0.86}, {-11.8,-90.1,"eik",1.15}, {-5.9,-91.9,"eik",0.99}, {-0.6,-90.5,"beuk",1.18}, {3.5,-91.9,"beuk",0.88}, {11.4,-90.4,"eik",1.17}, {16.8,-89.1,"eik",1.07}, {20.5,-91.2,"beuk",0.89}, {26.1,-90.5,"eik",0.86}, {-2.0,-96.3,"eik",1.23}, {3.8,-97.9,"eik",1.16}, {9.3,-95.2,"eik",0.96}, {15.6,-95.6,"beuk",0.99}}
local F = Vector3.new(-0.968, 0, 0.250); local O = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local function L(x, y) return (O * CFrame.new(-x * 3, 0, y * 3)).Position end
local SRC = {}
for _, n in ipairs({"beuk", "eik"}) do for _, c in ipairs(workspace.MagischeKlokBos:GetChildren()) do if string.match(c.Name, "^" .. n) then SRC[n] = c break end end end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local oud = workspace:FindFirstChild("HerautenpleinBos"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "HerautenpleinBos"
local rnd = Random.new(7); local n = 0
for _, t in ipairs(P) do
	local src = SRC[t[3]]
	if src then
		local p = L(t[1], t[2]); local r = workspace:Raycast(p + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp)
		local c = src:Clone(); c:ScaleTo(c:GetScale() * t[4])
		c:PivotTo(CFrame.new(Vector3.new(p.X, r and r.Position.Y or 2, p.Z)) * CFrame.Angles(0, rnd:NextNumber(0, 6.28), 0))
		c.Parent = map; n += 1
	end
end
map.Parent = workspace
return n .. " bomen"
