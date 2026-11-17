--!strict
-- PagodeRit (server): zet alleen de starttijd van de ritcyclus (servertijd). De beweging zelf draait op elke client
-- (PagodeRitClient.client.luau, StarterPlayerScripts) met workspace:GetServerTimeNow(): iedereen ziet dezelfde stand,
-- zonder netwerkvertraging. Daan 17 nov: de server-gestuurde gondel trilde, belichting bleekte uit (losse physics-delen) en
-- spelers zakten weg. Nu blijft alles verankerd.
local pag = workspace:WaitForChild("Pagode") :: Model
pag:SetAttribute("RitStart", workspace:GetServerTimeNow())
