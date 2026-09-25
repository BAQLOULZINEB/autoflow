# 11 — Cinematic Video Prompt (reusable production prompt)

**Deliverable:** 60-second cinematic business-case video · **Source spec:** `VIDEO-PROMPT.md`
**Use:** paste the *Master Prompt* into an AI video tool (Kling, Runway, Veo, Sora, Pika) or hand it to a videographer. Scene prompts below are for tools that generate shot-by-shot.

---

## 1. Master prompt (paste as-is)

```
Create a 60-second premium cinematic case-study video about a supervised AI workflow in a small car rental agency in Rabat, Morocco. Realistic business film, not an AI advertisement.

STORY. Open on a competent, calm employee at a modest, real-looking rental office in Rabat, morning light through a window, city texture hinted outside (white facades, a palm, traffic sounds) — no stereotypes. Customer requests arrive from everywhere: WhatsApp-style messages on a phone, a ringing desk phone, a spreadsheet of vehicles on a laptop, handwritten notes on a pad. The employee reads a message, re-types dates into the spreadsheet, scrolls to check whether an SUV is free, answers the same question about deposit for the third time, and glances at a sticky note that says "relancer M. Alaoui". Handheld close-ups, quick but elegant cuts. The feeling is pressure and fragmentation carried by a capable person — never chaos, never incompetence.

Then, hidden friction in fast close-ups: a message missing dates; a request sitting unanswered; a finger tracing a spreadsheet row; a quote sent three days ago with no reply.

Match-cut from the scattered screens to a single clean interface: a calm, minimal workflow view with French labels. A customer request card moves left to right along a thin teal line through: "Demande client → Comprendre la demande → Orchestrateur → Vérifier la disponibilité → Réponse / Alternative → Relancer et suivre → Validation humaine si nécessaire". Show the first step extracting dates and vehicle type into a structured card; the availability step checking a small fleet table and proposing an alternative vehicle; the follow-up step preparing a polite reminder draft; and the orchestrator routing one ambiguous request ("le week-end prochain", price question) to a real staff member, whose hand taps "Valider". The interface is realistic and restrained: white cards, navy text, one teal accent, no glow.

After: the same employee, same desk, now steadier framing and cleaner light. On the screen: a structured request, an availability result, a suggested reply, a follow-up reminder, and a manager's status board with clear columns (Nouvelles, En attente client, À valider, Confirmées). The employee closes the laptop halfway and speaks to a customer at the counter, confident, unhurried.

Close on a clean three-box graphic on off-white: "Problème → Système → Résultat", then the closing line and signature.

ON-SCREEN TEXT (French, in order, one at a time, clean sans-serif, navy on off-white or white on navy):
1. "Chaque demande mérite une réponse rapide."
2. "Demandes dispersées. Vérifications manuelles. Relances oubliées."
3. "Un workflow simple. Des décisions supervisées."
4. "Répondre plus vite. Ne rien oublier. Garder le contrôle."
5. "Moins de tâches répétitives. Plus de temps pour le client."
Final signature: "AI Engineer & Automation Architect — Des workflows intelligents pour les opérations réelles."

VISUAL DIRECTION. Premium, believable, cinematic. Before: warm natural light, muted warm neutrals, handheld, shallow depth of field, quick cuts. After: balanced cleaner light, stable tripod compositions, slower cuts. Restrained teal (#0E9C99) as the only accent for the system and dashboard; deep navy (#0B1F3A) for text; warm off-white (#FAF8F4) for graphics. Match-cut transitions from messy manual action to structured digital state. No robots, no holograms, no glowing brain, no sci-fi UI, no floating particles, no code scrolling, no purple gradients, no stock "AI" imagery. If a KPI board appears, label it "Indicateurs suivis — objectif du pilote", never as achieved results.

SOUND. Subtle rhythmic pulse under the friction section; confident, minimal, warm rise under the resolution; room tone and a distant city. Optional French voice-over, calm and warm, neutral Moroccan/French accent.

PACING. 0–12 s pressure; 12–20 s hidden friction; 20–34 s the workflow; 34–50 s clarity and control; 50–60 s result and signature. Fast enough to feel pressure, slow enough to understand.

INTEGRITY. Do not show numbers of hours, percentages or revenue saved. Do not imply employees are replaced: the system prepares, the person decides. The emotion is clarity, trust and operational relief, understandable by a non-technical owner in 30 seconds.

Output: 16:9, 1920×1080 (also deliver 9:16 crop-safe framing), 24 fps, 60 seconds.
```

---

## 2. Scene-by-scene prompts (for shot-based tools)

Common style suffix for every scene:
`— cinematic realism, premium business film, Rabat Morocco office, warm off-white and navy palette, restrained teal accent only on screens, no robots, no holograms, no sci-fi, no glow, no purple, shallow depth of field, 24 fps, 16:9`

| # | Time | Shot prompt | Text overlay |
|---|---|---|---|
| 1 | 0–4 s | Morning, small car rental office in Rabat; a professional employee (30s) sits at a desk with a laptop, a smartphone, a landline and a paper notepad; sunlight through blinds; handheld medium shot. | — |
| 2 | 4–8 s | Close-up: phone screen with several incoming WhatsApp-style messages in French; the desk phone starts ringing; the employee's eyes move between them; quick cut to a spreadsheet of vehicles on the laptop. | « Chaque demande mérite une réponse rapide. » |
| 3 | 8–12 s | Over-shoulder: employee types dates from the phone into the spreadsheet, scrolls to find an SUV row, sighs lightly, writes "relancer jeudi" on a sticky note. Competent, focused. | — |
| 4 | 12–16 s | Macro close-ups in sequence: a message that reads "dispo une voiture ?" with no dates; a request card timestamp; a finger tracing a spreadsheet row; a quote message with "Envoyé · il y a 3 jours" and no reply. | « Demandes dispersées. » |
| 5 | 16–20 s | Same close-up rhythm, slightly faster; a sticky note falls off the monitor edge. Elegant, not chaotic. | « Vérifications manuelles. Relances oubliées. » |
| 6 | 20–24 s | Match-cut: the cluttered laptop screen resolves into a single clean white interface on off-white; a request card labelled "Demande client" glides onto a thin teal line. | « Un workflow simple. » |
| 7 | 24–28 s | Interface animation: the card passes "Comprendre la demande" — fields fill in: Dates 12–15 oct · Citadine · Agdal; a small "1 information manquante ?" chip; then "Orchestrateur" node (navy) lights a subtle teal edge. | — |
| 8 | 28–31 s | "Vérifier la disponibilité": a small fleet table; requested SUV shows "Maintenance"; an alternative "Berline automatique — disponible" is proposed with a one-line reason. | — |
| 9 | 31–34 s | "Relancer et suivre": a polite French reminder draft appears; then "Validation humaine": an ambiguous request ("le week-end prochain", "un geste sur le prix") is routed to a staff queue; a real hand taps "Valider" on a tablet. | « Des décisions supervisées. » |
| 10 | 34–40 s | After: same employee, same desk, tripod, cleaner light. Screen shows structured request → availability → suggested reply → reminder. Employee reads, edits one word, clicks send with a small nod. | « Répondre plus vite. » |
| 11 | 40–45 s | Manager's screen: clean status board, four columns (Nouvelles · En attente client · À valider · Confirmées), small KPI tiles labelled "Indicateurs suivis — objectif du pilote" with placeholders, no numbers claimed. | « Ne rien oublier. » |
| 12 | 45–50 s | Employee half-closes the laptop, turns to a customer at the counter, hands over keys, calm and unhurried; soft city light. | « Garder le contrôle. » |
| 13 | 50–55 s | Clean graphic on off-white: three boxes "Problème → Système → Résultat" connected by thin teal arrows; minimal, editorial. | — |
| 14 | 55–60 s | Closing card, navy background, white text, generous whitespace. | « Moins de tâches répétitives. Plus de temps pour le client. » then « AI Engineer & Automation Architect — Des workflows intelligents pour les opérations réelles. » |

---

## 3. Optional voice-over script (French, ≈ 120 words, calm)

> Dans une agence de location, chaque demande mérite une réponse rapide.
> Mais les demandes arrivent de partout. Les disponibilités se vérifient à la main. Et les relances, parfois, s'oublient.
> Ce n'est pas un manque de compétence. C'est un travail éclaté sur trop d'outils.
> Nous proposons un workflow simple : la demande est comprise, la disponibilité vérifiée, une alternative proposée, la relance rappelée.
> Et chaque cas sensible est validé par une personne de l'équipe.
> Le système prépare. Vos collaborateurs décident.
> Répondre plus vite. Ne rien oublier. Garder le contrôle.
> Moins de tâches répétitives. Plus de temps pour le client.

---

## 4. Production notes

- **Text safety:** keep overlays inside the central 80 % for 9:16 crops.
- **Fonts:** Manrope or Inter; overlays ≥ 48 px at 1080p.
- **Colour grade:** before — warm neutrals, slight contrast; after — neutral-clean, lifted shadows; teal only ever on screens/graphics.
- **UI assets:** build the interface frames from the demo dashboard (doc 08) or from visuals B, C, E — do not let the video tool invent a UI.
- **Integrity check before publishing:** no number, no percentage, no "AI-powered", no robot, no replaced employee.
- **Variants:** 60 s master; 30 s cut (scenes 2, 4, 6, 9, 10, 14); 15 s teaser (scenes 4, 6, 14).
