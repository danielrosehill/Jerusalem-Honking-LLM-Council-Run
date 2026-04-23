#set document(title: "Jerusalem Honking — Focused Policy Digest", author: "LLM Council")
#set page(
  paper: "a4",
  margin: (x: 2cm, y: 2.2cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(110))
    Jerusalem Unnecessary Honking · Focused Policy Digest · 23 April 2026
    #h(1fr)
    #counter(page).display("1 / 1", both: true)
  ],
)
#set text(font: ("Libertinus Serif", "Linux Libertine", "Nimbus Roman No9 L", "Noto Serif"), size: 10.5pt, lang: "en")
#set par(justify: true, leading: 0.62em)
#show heading.where(level: 1): set text(size: 17pt, weight: 800)
#show heading.where(level: 2): set text(size: 13pt, weight: 700, fill: rgb("#123a5e"))
#show heading.where(level: 3): set text(size: 10.8pt, weight: 700)
#show heading: it => { v(0.45em); it; v(0.2em) }

#let src(name) = box(
  inset: (x: 3pt, y: 0pt),
  outset: (y: 1pt),
  fill: luma(235),
  radius: 2pt,
  text(size: 7.8pt, font: ("Fira Mono", "DejaVu Sans Mono", "monospace"), fill: luma(60), name),
)

#align(center)[
  #text(size: 21pt, weight: 800)[Jerusalem Unnecessary Honking]
  #v(0.25em)
  #text(size: 13pt, weight: 600, fill: luma(65))[Focused Policy Digest]
  #v(0.65em)
  #text(size: 9.5pt, fill: luma(110))[
    Prepared by the LLM Council for the Jerusalem Municipality Working Group
    and the Jerusalem Green Fund · Reference date 23 April 2026
  ]
]
#v(0.8em)
#line(length: 100%, stroke: 0.5pt + luma(180))
#v(0.4em)

= 1. Executive Summary

Jerusalem is no longer at the agenda-setting stage. As of January 2026, the Ministry of Environmental Protection (MoEP) has awarded the city approximately NIS 1 million under the national "Quiet Cities" programme, eight NOize-type acoustic enforcement systems are scheduled for deployment around May 2026, the applicable fine is set at 250 NIS, and the Mayor has publicly committed to a two-month pre-deployment awareness campaign #src("10-kolhair-jerusalem-quiet-cities.md"). The by-law is pending Ministry of Interior and Privacy Protection Authority sign-off #src("07-themarker-interior-ministry-approval.md").

The central risk is not failure to launch — it is the documented Israeli pattern of pilot programmes that generate press coverage and then disappear. The working group's primary tasks are therefore: holding the implementation pipeline to publicly committed milestones; building the inspector workflow before cameras go live; establishing cross-community legitimacy (particularly with Arab and Haredi residents); and anchoring accountability in the contractual MoEP grant conditions rather than in political goodwill.

= 2. The Five Most Useful Recommendations

== Rank 1 — Build and Staff the Electronic Enforcement Unit Before Cameras Go Live

*Surfaced by:* Service Delivery Practitioner (most developed); Legal & Regulatory Analyst; Urban Planner.

*Why additive.* The MoEP funding condition explicitly requires inspector training #src("05-calcalist-environment-ministry-funding.md"). The Petah Tikva experience shows the operational bottleneck is human review, not camera detection — the system currently flags hundreds of events; the only constraint is staffing the review unit #src("03-geektime-noize-tel-aviv.md"). The Jerusalem Municipality has not yet publicly addressed this. Without a staffed workflow, eight cameras will produce data that sits in a folder.

*Actor who must act.* Jerusalem Municipality Environmental Enforcement Department, with MoEP technical support #src("07-themarker-interior-ministry-approval.md").

*Estimated effort.* Medium — budget line for inspector FTEs, IT procurement for case-management system, and training programme.

*Concrete first step.* The Jerusalem Green Fund submits a written question to the Environmental Quality Committee (chaired by Yonatan Peleg #src("02-mynet-jerusalem-bylaw.md")) requesting answers before April 2026: (a) how many inspector FTEs are allocated; (b) who delivers the training; (c) target turnaround time from detection to fine issuance; (d) which IT system will manage the case queue.

== Rank 2 — Publish and Enforce the MoEP 70% Incident-Handling Grant Condition as a Public Accountability Metric

*Surfaced by:* Urban Planner, Municipal Fiscal Officer, Community & Equity Advocate, Legal & Regulatory Analyst, Service Delivery Practitioner (all five lenses independently).

*Why additive.* The MoEP funding programme requires municipalities to "handle at least 70% of incidents flagged by the digital enforcement device" #src("05-calcalist-environment-ministry-funding.md"). This is a contractual grant condition — not a political promise — and therefore the single most durable accountability mechanism available. It is not yet publicly reported or tracked for Jerusalem.

*Actor who must act.* Environmental Quality Committee, with pressure from the Jerusalem Green Fund.

*Estimated effort.* Low — an FOI request for the grant agreement and a committee resolution to place the handling rate on the standing agenda.

*Concrete first step.* File a freedom-of-information request for Jerusalem's specific grant agreement with the MoEP. Once confirmed, request that the Environmental Quality Committee adopt a standing agenda item publishing the detection-to-fine handling rate quarterly.

== Rank 3 — Publish a Data-Retention and Access-Limitation Policy for Enforcement Footage Before Deployment

*Surfaced by:* Community & Equity Advocate (most developed); Legal & Regulatory Analyst.

*Why additive.* The NOize system photographs licence plates and records audio #src("03-geektime-noize-tel-aviv.md"). Privacy Protection Authority approval is a legal prerequisite for system operation #src("07-themarker-interior-ministry-approval.md"). Arab Jerusalemites — approximately 37% of the city's population — have well-founded concerns about surveillance infrastructure being repurposed for non-noise enforcement. No published data-retention policy exists. Absent one, the deployment is politically vulnerable and Arab community trust will not be secured.

*Actor who must act.* Jerusalem Municipality Legal Department, in coordination with the Privacy Protection Authority and the MoEP.

*Estimated effort.* Medium — drafting, legal review, and publication; the PPA engagement is a legal prerequisite in any case.

*Concrete first step.* The Jerusalem Green Fund formally requests, in writing, that the Municipality publish the draft data-retention policy and Privacy Protection Authority correspondence before cameras go live. Frame this as facilitating the PPA approval process, not opposing it — the Legal & Regulatory Analyst correctly identifies the PPA as a stakeholder to engage, not an adversary.

== Rank 4 — Institute Six-Month and Twelve-Month Post-Deployment Reviews at the Environmental Quality Committee

*Surfaced by:* Urban Planner, Legal & Regulatory Analyst, Service Delivery Practitioner, Community & Equity Advocate.

*Why additive.* The Jerusalem by-law process was raised in the previous council term and not completed #src("02-mynet-jerusalem-bylaw.md"). The 2020 joint MoEP–Police operation produced 12 tickets in Jerusalem and then nothing further #src("08-gov-il-moep-police-enforcement.md"). The Rechavia petition gained press coverage and produced no structural change #src("09-kolhair-rechavia-petition.md"). A pre-scheduled, publicly committed review cycle — with named metrics — is the only structural counter to this pattern.

*Actor who must act.* Environmental Quality Committee (Yonatan Peleg, chair); Jerusalem Green Fund as requesting party.

*Estimated effort.* Low — a committee resolution; no new budget required.

*Concrete first step.* Submit a formal written request to the Environmental Quality Committee before May 2026 asking it to schedule reviews at six and twelve months post-deployment. Proposed metrics: systems installed vs. target (8); by-law Reshumot publication date; inspector FTEs deployed; incidents flagged; fines issued; contest rate; 70% handling rate against grant condition. Commit to attending and publishing the minutes.

== Rank 5 — Deploy Pre-Activation Deterrence Signage at the Eight Enforcement Intersections

*Surfaced by:* Urban Planner, Service Delivery Practitioner.

*Why additive.* The Mayor has committed to a two-month pre-deployment awareness campaign #src("10-kolhair-jerusalem-quiet-cities.md") but this has not been operationalised. Physical signage at the specific enforcement junctions — stating that acoustic cameras will activate at a named date with a 250 NIS fine — creates deterrence before the first ticket is issued, fulfils the awareness commitment, and is consistent with the campaign's existing "Kan Garim Lo Tzofrim" sticker model #src("13-facebook-tzfira-group.md"). It also directly serves the "inform, don't accuse" driver-messaging principle that the council's legal and communications analyses consistently recommend.

*Actor who must act.* Jerusalem Municipality Communications Department and the campaign, jointly.

*Estimated effort.* Low — design, print, and installation at eight intersections; well within the NIS 1 million allocation.

*Concrete first step.* The Jerusalem Green Fund formally offers, in writing, to co-produce bilingual (Hebrew / Arabic) signage for the eight deployment sites, citing the existing "Kan Garim Lo Tzofrim" template #src("13-facebook-tzfira-group.md") and the Ministry of Education worksheet's civic framing #src("12-education-ministry-no-car-horns-worksheet.md").

= 3. Points of Convergence

The following recommendations were reached independently by three or more council lenses, making them the highest-confidence proposals in this digest.

- *Deploy the eight funded systems on schedule and ensure actual fine issuance, not merely detection.* _All six lenses._ Already in motion as a commitment #src("10-kolhair-jerusalem-quiet-cities.md"); the convergence point is that implementation follow-through — not initiation — is where the campaign's energy should be concentrated.

- *Use the MoEP 70% incident-handling grant condition as the primary accountability lever.* _Five lenses: Urban Planner, Municipal Fiscal Officer, Community & Equity Advocate, Legal & Regulatory Analyst, Service Delivery Practitioner._ Robustness derives from the contractual rather than political nature of this obligation #src("05-calcalist-environment-ministry-funding.md").

- *Frame the issue as public health, not policing or nuisance.* _Urban Planner, Community & Equity Advocate, Policy Innovation & Comparative Scholar, Municipal Fiscal Officer._ Grounded in the MoEP's own framing and the 60 dB cardiovascular evidence #src("06-auto-co-il-petah-tikva-500-tickets.md") #src("08-gov-il-moep-police-enforcement.md"). The most cross-community-legible frame in Jerusalem's demography.

- *Do not route enforcement demands through the Israel Police.* _Urban Planner, Community & Equity Advocate, Legal & Regulatory Analyst, Service Delivery Practitioner._ Jerusalem Police denied the phenomenon existed in 2020 despite 150 petition signatures and video evidence #src("09-kolhair-rechavia-petition.md"). The targeted joint operation produced only 12 tickets #src("08-gov-il-moep-police-enforcement.md"). The correct institutional pathway is municipal inspectors under the Environmental Enforcement Law #src("02-mynet-jerusalem-bylaw.md").

- *Describe the NOize system as "camera-assisted human enforcement," not "automated surveillance."* _Urban Planner, Legal & Regulatory Analyst, Service Delivery Practitioner, Policy Innovation & Comparative Scholar._ Grounded in the operational reality that every detection is reviewed by a human inspector before a fine is issued #src("03-geektime-noize-tel-aviv.md") #src("02-mynet-jerusalem-bylaw.md"). This is the factual answer to both the "Big Brother" objection and the "court overload" concern.

- *Adopt the registered-owner liability doctrine in the Jerusalem by-law.* _Legal & Regulatory Analyst, Service Delivery Practitioner, Policy Innovation & Comparative Scholar._ Already embedded in Tel Aviv's model #src("11-tel-aviv-municipality-end-of-honking.md") and consistent with speed-camera and red-light-camera precedent. Essential for remote enforcement to function without requiring driver identification at the junction.

- *Deploy the Ministry of Education's anti-honking civic worksheet in Jerusalem schools.* _Urban Planner, Community & Equity Advocate, Service Delivery Practitioner._ The 12-page worksheet already exists, is state-produced, and is designed for Arabic-speaking elementary learners in Hebrew as a second language #src("12-education-ministry-no-car-horns-worksheet.md"). The campaign should advocate for its adoption across Hebrew and Arab school tracks in Jerusalem as part of the pre-deployment awareness campaign.

= 4. Points of Divergence and Live Tensions

*Tension 1 — Revenue framing vs. cultural-change framing.* The Municipal Fiscal Officer proposes positioning fine revenue as offsetting the Electronic Enforcement Unit's operating costs — a fiscally sound argument for municipal officials. The Community & Equity Advocate and Urban Planner warn that messaging implying a revenue scheme will collapse public support. Kazakov of the Tzfira initiative is explicit: "Fine revenue isn't the goal — cultural change is" #src("01-mako-smart-cameras.md"). _The tension is real and unresolved: the fiscal argument is useful in closed budget discussions; it is toxic in public communications._

*Tension 2 — Surveillance governance and Arab community trust vs. deployment speed.* The Community & Equity Advocate recommends that the campaign publicly oppose any data-sharing with law enforcement for immigration or security purposes and include Arab community representatives on oversight bodies before deployment. The Legal & Regulatory Analyst and Service Delivery Practitioner treat PPA approval as a regulatory gate to clear efficiently rather than a political statement to make. _The tension is between a maximally privacy-protective public position (which may slow or politicise the approval process) and a technically minimal compliance approach (which may not secure Arab community legitimacy)._

*Tension 3 — Announcement timing vs. accountability pressure.* The Service Delivery Practitioner argues that public communications should trail operational deployment — announce that cameras are live after they are live, announce fine totals after they exist — to prevent the credibility damage of raised-and-dashed expectations. The Urban Planner and Legal & Regulatory Analyst recommend pre-deployment pressure (published timelines, FOI requests, committee commitments) to prevent quiet abandonment. _Both are correct for different audiences: pre-deployment pressure should be directed at municipal officials and the press; public deterrence messaging should be deployed only when infrastructure is operational._

*Tension 4 — Enforcement-first vs. structural change.* The Community & Equity Advocate argues that over-reliance on acoustic cameras will produce a cat-and-mouse dynamic and that the equity dimension (the most noise-burdened residents are often those without cars, on lower incomes, in less walkable areas) is obscured if the frame is "ticketing bad drivers." The Urban Planner, Legal & Regulatory Analyst, and Service Delivery Practitioner are more pragmatic about enforcement as the achievable near-term intervention. _The council does not resolve this; it notes that pedestrianisation and traffic calming are longer-horizon levers that should not displace the immediate enforcement ask, but should be advocated concurrently._

*Tension 5 — Optimal fine level.* Some stakeholders may push for the full 475 NIS statutory fine rather than the 250 NIS by-law fine #src("01-mako-smart-cameras.md") #src("10-kolhair-jerusalem-quiet-cities.md"). The Legal & Regulatory Analyst correctly argues that reopening the fine-level debate risks delaying the entire by-law implementation pipeline. _The council's view: accept 250 NIS as the operational fine; a functioning lower-fine system has more deterrent effect than a stalled higher-fine aspiration._

= 5. Novel Ideas Worth Prototyping

The following appeared in one or two lenses but are materially additive to the current Quiet Cities programme and are not covered by existing commitments.

- *The "Shabbat contrast" audio format.* (Urban Planner only.) Side-by-side recordings of the same intersection on Friday night and Tuesday morning — no narration required. Legible across all of Jerusalem's demographic communities because Shabbat quiet is a shared lived experience. Feasibility: very low cost; resident volunteers can produce; distributable via WhatsApp. _Not yet in use as a formalised campaign asset._

- *Formal submission to the Light Rail traffic-management planning process.* (Urban Planner only.) The Light Rail construction has created new honking hotspots by rerouting traffic through previously quiet intersections. Submitting formal observations to the Light Rail planning committee requesting noise-impact assessments of rerouted traffic flows creates a documented planning record and forces traffic engineers to address noise in design. Feasibility: low cost; requires only planning-process participation. _Genuinely novel — no other lens identified this lever._

- *Inter-city benchmarking as political pressure.* (Service Delivery Practitioner only.) Nine municipalities and 43 systems are included in the MoEP national programme #src("07-themarker-interior-ministry-approval.md"). Publishing comparative performance data — "City X issued Y tickets in month 1; Jerusalem is at Z" — creates competitive political pressure on laggard municipalities. Feasibility: depends on MoEP publishing city-level data; requires a periodic reporting request. _Not yet proposed; low cost if data is available._

- *Billboard-design exercise from the Ministry of Education worksheet as community engagement in public space.* (Urban Planner, Community & Equity Advocate.) The existing MoEP-produced worksheet already includes a creative activity in which students design "Quiet City" billboards #src("12-education-ministry-no-car-horns-worksheet.md"). Running this exercise in schools near the eight deployment zones and exhibiting the results in public space at those intersections generates child-led advocacy that is politically clean and community-visible. Feasibility: coordination with school principals and the Municipality's Education Department; no budget requirement beyond display boards. _Not yet proposed for Jerusalem._

- *Publicly nominate the campaign as a co-producer of the Mayor's pre-deployment awareness campaign.* (Service Delivery Practitioner, Urban Planner.) The Mayor has committed but has not operationalised #src("10-kolhair-jerusalem-quiet-cities.md"). Formally offering to share content production with the municipality — citing the existing bilingual petition model #src("02-mynet-jerusalem-bylaw.md") and the "Kan Garim Lo Tzofrim" sticker template #src("13-facebook-tzfira-group.md") — reduces the municipality's excuse for inaction and gives the campaign quality control over messaging. Feasibility: low cost; the offer itself is a public accountability mechanism whether accepted or declined. _Not yet formalised._

- *Run the Petah Tikva pilot-sequencing approach: deploy under existing noise-nuisance regulations before the by-law clears the full approval pipeline.* (Service Delivery Practitioner only.) Petah Tikva issued approximately 500 tickets in its first weeks by operating under existing regulations while the by-law completed approval #src("03-geektime-noize-tel-aviv.md") #src("06-auto-co-il-petah-tikva-500-tickets.md"). If the Jerusalem by-law is still stalled at Ministry of Interior when the cameras go live in May 2026, this sequencing may be legally viable and would prevent further delay. Feasibility: requires legal confirmation from the Municipality's legal department. _Additive but conditional on legal advice._

= 6. What to Drop

- *Demanding that the Israel Police prioritise honking enforcement.* Outside effective influence; documented failure mode. Jerusalem Police denied the phenomenon existed in 2020 despite 150 signatures and video evidence #src("09-kolhair-rechavia-petition.md"). The targeted joint MoEP–Police operation produced 12 tickets in Jerusalem in total #src("08-gov-il-moep-police-enforcement.md"). Israel Police is nationally controlled; the municipality cannot direct its priorities. Campaign energy directed here is structurally wasted.

- *Flyering as a primary campaign tactic.* Explicitly identified as ineffective in the problem statement; confirmed by the Urban Planner's spatial analysis. Drivers creating the nuisance at central intersections are commuters, not residents of adjacent streets who would receive the flyer. Resident-facing stickers and intersection signage have more durable presence at lower cost.

- *Confronting individual motorists at junctions.* Politically toxic in Jerusalem's charged environment. A resident confronting a driver risks escalation that will dominate subsequent press coverage and displace the noise issue. Every council lens confirms this.

- *Holding out for the 475 NIS statutory fine instead of the 250 NIS by-law fine.* Already in motion at 250 NIS; reopening the debate risks the implementation pipeline #src("10-kolhair-jerusalem-quiet-cities.md"). A functioning lower-fine system produces more deterrence than a stalled higher-fine debate.

- *Advocating nationally for transfer of enforcement authority from police to municipalities as a near-term campaign ask.* Requires primary legislation; outside Israeli municipal authority in the near term. Prof. Bar-Yosef's call for this transfer #src("02-mynet-jerusalem-bylaw.md") is the correct long-term structural fix and worth including in a national legislative advocacy programme; it should not consume near-term campaign resources.

- *Positioning the campaign as a revenue-generating enforcement scheme.* Directly contradicted by the campaign's own position and by Kazakov #src("01-mako-smart-cameras.md"): "Fine revenue isn't the goal — cultural change is." Any framing implying municipal cash generation will collapse public support, particularly in communities already sceptical of state surveillance.

- *Framing the campaign as targeting any specific community or demographic.* Politically infeasible in Jerusalem's demography and structurally counterproductive. Acoustic cameras enforce uniformly at the intersections where they are deployed; any implication to the contrary is both factually incorrect about the technology's operation and sufficient to sink the campaign politically.

= 7. Evidence Gaps

The council identified the following facts that cannot be determined from the grounding corpus and would require fresh research.

- *Has Jerusalem's specific MoEP grant agreement been published, and does it include the 70% incident-handling condition?* #src("05-calcalist-environment-ministry-funding.md") documents the condition for the national programme; whether Jerusalem's specific agreement replicates it is unconfirmed. Requires: FOI request to the Jerusalem Municipality or MoEP.

- *What is the current legal status of the Jerusalem noise-prevention by-law — specifically, has it cleared Ministry of Interior review?* The by-law was expected to clear Ministry of Interior in 2025 #src("02-mynet-jerusalem-bylaw.md") #src("07-themarker-interior-ministry-approval.md"), but no subsequent confirmation appears in the grounding corpus. Requires: written inquiry to the Municipal Legal Department or the Environmental Quality Committee.

- *Has the Privacy Protection Authority been formally engaged, and if so, what are its outstanding concerns?* #src("07-themarker-interior-ministry-approval.md") identifies PPA approval as a prerequisite; no PPA correspondence is documented. Requires: FOI request or direct inquiry to the PPA.

- *What are the specific eight intersection locations selected for the May 2026 deployment?* #src("10-kolhair-jerusalem-quiet-cities.md") confirms eight systems but does not name the sites. Requires: written request to the Municipality's Environmental Quality Committee or MoEP project lead.

- *What operational lessons has Petah Tikva's enforcement unit drawn after approximately 500 initial tickets?* #src("06-auto-co-il-petah-tikva-500-tickets.md") documents the initial ticket count but provides no follow-up data on contest rate, system accuracy in practice, handling rate, or staffing levels. Requires: direct interview with Petah Tikva's Environmental Enforcement Department.

- *What is the actual honking-fine volume in Jerusalem since January 2026, and has any enforcement begun under the Quiet Cities programme?* The grounding corpus contains no post-January 2026 enforcement data. Requires: FOI request to the Jerusalem Municipality for fine-issuance records under noise-nuisance regulations.

- *Has the Mayor's office produced a written schedule for the committed two-month pre-deployment awareness campaign?* #src("10-kolhair-jerusalem-quiet-cities.md") records a verbal commitment; no written plan or timeline is documented. Requires: written inquiry to the Mayor's Communications Department.

#v(1.2em)
#line(length: 100%, stroke: 0.5pt + luma(180))
#v(0.4em)
#text(size: 8.5pt, fill: luma(110))[
  Source run: #raw("run-20260423T150817") · Chairman model: #raw("anthropic/claude-sonnet-4.6") · Grounding corpus aggregated 23 April 2026. Inline grey tags such as #src("10-kolhair-jerusalem-quiet-cities.md") reference files in the repo's `grounding/` directory.
]
