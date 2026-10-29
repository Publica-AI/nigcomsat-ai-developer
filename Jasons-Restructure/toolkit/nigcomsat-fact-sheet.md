# NIGCOMSAT Fact Sheet

Real facts to use in examples, so every Naija story in this course stands on solid ground. Each fact has a source. **The course datasets are synthetic**: built to behave like this satellite, but not real NIGCOMSAT records.

## The company

| Fact | Detail | Source |
|---|---|---|
| Name | Nigerian Communications Satellite Limited (NIGCOMSAT) | [SpaceHubs Africa](https://data.spacehubs.africa/database/entity/companies/nigerian-communications-satellite/) |
| Role | Government-owned satellite operator under the federal ministry responsible for communications and the digital economy | [SpaceHubs Africa](https://data.spacehubs.africa/database/entity/companies/nigerian-communications-satellite/) |
| Leadership | Managing Director/CEO **Jane Nkechi Egerton-Idehen** (appointed 2023) | [TechEconomy](https://techeconomy.ng/meet-jane-amadi-nkechi-egerton-idehen-newly-appointed-md-ceo-nigcomsat/), [Techmoonshot](https://techmoonshot.com/2026/08/26/nigeria-approves-nigcomsat-2a-2b-satellites-for-broadband-push/) |
| Broadcast | Carries **over 50% of Nigeria's broadcast traffic**, including digital switch-over (DSO) traffic for the NBC | [Nairametrics](https://nairametrics.com/2026/04/12/nigcomsat-regains-major-clients-now-carries-50-of-broadcast-traffic/) |
| Clients named in the press | NBC, Galaxy Backbone, NIMC | [Nairametrics](https://nairametrics.com/2026/04/12/nigcomsat-regains-major-clients-now-carries-50-of-broadcast-traffic/) |
| Revenue | About ₦2 billion in 2025, up from about ₦650 million the year before | [Nairametrics](https://nairametrics.com/2026/04/12/nigcomsat-regains-major-clients-now-carries-50-of-broadcast-traffic/) |

## NigComSat-1R: the satellite in our data

| Fact | Detail | Source |
|---|---|---|
| Orbit | Geostationary, at **42.5° East** | [NIGCOMSAT fleet page](https://nigcomsat.gov.ng/fleet/nigcomsat), [SatBeams](https://satbeams.com/satellites/2515-nigcomsat-1r) |
| Launch | December 2011, on a Chinese Long March rocket | [Space.com](https://www.space.com/13975-china-rocket-launching-huge-nigeria-satellite.html), [CGWIC](https://cgwic.com/In-OrbitDelivery/CommunicationsSatellite/Program/NigComSat-1R.html) |
| Platform | DFH-4, built by the China Academy of Space Technology | [CGWIC](https://cgwic.com/In-OrbitDelivery/CommunicationsSatellite/Program/NigComSat-1R.html) |
| Design life | **15 years** | [CGWIC](https://cgwic.com/In-OrbitDelivery/CommunicationsSatellite/Program/NigComSat-1R.html), [NIGCOMSAT](https://www.nigcomsat.gov.ng/news-post/nigeria-to-maximize-nigcomsat-1rs-potential-as-expiration-nears-in-3-years) |
| Transponders | **28 active**: 4 C-band, 14 Ku-band, 8 Ka-band, 2 L-band (navigation) | [NASRDA](https://central.nasrda.gov.ng/?p=2625), [CGWIC](https://cgwic.com/In-OrbitDelivery/CommunicationsSatellite/Program/NigComSat-1R.html) |
| Ka-band | 8 channels of 120 MHz; spot beams over **Nigeria**, South Africa and Europe | [NASRDA](https://central.nasrda.gov.ng/?p=2625) |
| L-band | Navigation payload (L1, L5) supporting satellite-based augmentation for Africa and the Indian Ocean | [EnviroNews](https://www.environewsnigeria.com/?p=39887) |
| Services | Broadcasting (incl. direct-to-home TV), broadband, enterprise and government connectivity | [Space in Africa](https://spaceinafrica.com/2018/03/14/nigcomsat-wants-you-to-watch-cable-tv-for-free/) |

## History and what's next

| Fact | Detail | Source |
|---|---|---|
| NigComSat-1 | Launched 2007; **failed in November 2008 after a solar-array anomaly left it without power** | [Wikipedia](https://en.wikipedia.org/wiki/NigComSat-1) |
| The gap | Roughly four years without a satellite, and several clients left | [Nairametrics](https://nairametrics.com/2026/04/12/nigcomsat-regains-major-clients-now-carries-50-of-broadcast-traffic/) |
| Replacements | **NIGCOMSAT-2A and 2B**, high-throughput satellites, approved by the Federal Executive Council; built by Thales Alenia Space and Israel Aerospace Industries | [Techmoonshot](https://techmoonshot.com/2026/08/26/nigeria-approves-nigcomsat-2a-2b-satellites-for-broadband-push/) |
| Launch targets | 2A targeted for 2028, 2B for 2029 (agency targets: earlier plans slipped) | [Techmoonshot](https://techmoonshot.com/2026/08/26/nigeria-approves-nigcomsat-2a-2b-satellites-for-broadband-push/) |

## Nigerian context used in the course

| Fact | Detail | Source |
|---|---|---|
| Time zone | West Africa Time, **UTC + 1** all year, no daylight saving | — |
| Rainy season | Roughly April to October, earlier and longer in the south, shorter in the far north; NiMet publishes onset and end dates each year | [Guardian (NiMet outlook)](https://guardian.ng/news/lagos-12-other-states-to-experience-longer-rainfall-in-2026-nimet/) |
| Regions | Six geopolitical zones: North West, North East, North Central, South West, South East, South South (used in `vsat_uptime_by_region_weekly`) | — |

## Which fact powers which day

| Day | Fact | Why it lands |
|---|---|---|
| W1D1 | 42.5°E, 28 transponders, 15-year life | Meet the star of the course |
| W1D2 | Ka-band + rainy season | Rain fade is the “DStv in heavy rain” story |
| W3D1 | NigComSat-1 lost to a **solar-array failure** | Why we watch solar-array current so closely |
| W6D2 | 15-year design life from 2011, replacements targeted for 2028/2029 | Remaining useful life is a real national question |
| Final project | 50% of broadcast traffic, government clients | Why reliable monitoring matters |
