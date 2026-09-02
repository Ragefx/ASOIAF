# Character Bible

Covers the two protagonists: naming, voice, mechanical identity, and the romance arc's rules.

**On the names.** The brief left the Knight's name, his house, the Girl's name, and her specific
backstory undecided. Leaving them undecided blocks every scene file, so this document **commits to
a recommended default** and shows its work. Alternates are listed. Both names live in exactly one
file — `data/npcs/protagonists.json` — and every line of dialogue refers to them through the
`{knight}`, `{house}`, and `{girl}` tokens, so changing a name is a one-line edit and zero
rewrites.

---

## 1. Ser Torren Slate of Blackpool

**Age 23. Household knight. POV of Acts 1, 3, 5.**

### Why this name

- **Torren** — Northern first names in canon are blunt, hard-consonant, and Anglo-Saxon-adjacent:
  Torrhen, Rickard, Cregan, Benjen, Halys, Wyman. *Torren* sits inside that sound world and is
  deliberately one letter off **Torrhen Stark**, the King Who Knelt — a man whose whole legend is
  bending the knee to survive. That is the joke the North would make about a boy from Blackpool
  wanting glory, and it is also Act 5's ending, where the player chooses *when* to kneel.
- **Slate** — House Slate of Blackpool is **canon**: a real, named, barely-described Northern
  house sworn to Winterfell. Using a canon minor house rather than inventing one keeps the promise
  that the story is faithful, and it gives the writers total freedom, because canon says almost
  nothing about them. Lord **Ondrew Slate** is the canon head of the house and can appear.
- **Blackpool** is their canon seat.

**Alternates, if the default is rejected:** *Ser Halys Slate* · *Ser Rickon Stout of Goldgrass*
(House Stout, also canon minor) · *Ser Torren Mollen*. Invented houses (House Rennick, House
Vaile) are available but cost the "it's really the North" texture for nothing gained.

### Backstory

Fourth son. There was no land for him and there was never going to be. Knighted at nineteen by a
hedge knight his father paid, which is legal, and which every proper southron knight can hear in
the way he says *ser*. Seconded to Winterfell's guard for the summer muster because Blackpool owes
Winterfell men and Torren was the man they could most afford to lose.

He has never fought an armed man. He has trained constantly. He is very aware of the difference,
and pretends not to be.

**The want:** for House Slate to be a name someone says out loud in a hall.
**The need:** to find out whether he is brave, which is not the same question and cannot be
answered by wanting.
**The lie he believes:** that recognition is earned, and that the people handing it out are
watching.

### Voice

Formal in the wrong register — he over-uses honorifics with people who don't need them and drops
them entirely when frightened. Short declaratives. Says "aye" not "yes." Never jokes first, but
laughs early and too loud at other people's jokes. When he is out of his depth he asks a practical
question about logistics.

> **Torren:** "How many horses."
> **Jory:** "That's what you want to know."
> **Torren:** "It's what I can count."

**Never:** eloquent speeches, courtly flirtation, cynicism about knighthood. He believes in it.
That belief surviving Act 5 — or not — is his whole arc.

### Mechanics

| | |
|---|---|
| Starting HP | 40 |
| Kit | Sword, shield, Blackpool mail (poor armour, and the game says so) |
| Act boundaries | +8 max HP, one battle trait chosen from three |
| Key relationships | Robb Stark, Jory Cassel, Theon Greyjoy, Greatjon Umber, Ondrew Slate |
| Trait pressure | `bold` and `loyal` are the axes his choices actually move |

---

## 2. Nyra

**Age 18. Servant, the queen's household. POV of Acts 2 and 4.**

### Why this name

Smallfolk in canon get one name, and it is short: Wylla, Mya, Jeyne, Bella, Kyra, Talla. **Nyra**
belongs to that set and passes completely as a common Crownlands name — while carrying, to an ear
that knows Valyrian naming (Rhaenyra, Naerys, Daenerys), a faint wrongness. Nobody in Westeros
would notice. Every player who knows the books will.

She has **no surname**, which is not an omission but a plot point: she does not know her parents'
names either.

**Alternates:** *Sarra* (flatter, hides the hint completely — better if the reveal should land
purely on the silver hair) · *Elenya* (too obvious) · *Mysa*.

### Backstory — the committed version

Left at the **motherhouse at Rosby** as an infant, in autumn 280 AC, wrapped in a cloak too good
for a foundling. The septas dyed her hair with walnut stain until she was eleven, told her it was
for lice, and were doing it to keep her alive. She has silver-blonde hair and dark violet eyes and
has been told all her life that this means her mother was a Lysene whore, which is the only
explanation anyone in the Crownlands has for a face like that, and which she believes.

She came to the Red Keep at fifteen through a household steward who took a bribe from the
motherhouse to make her someone else's problem. She has been invisible for three years and is
extremely good at it.

**She can read.** A septa taught her, badly and in secret, and it is the single most dangerous
thing about her — servants who can read do not stay servants, they stay disappeared. This is what
makes Act 2's ledger scene possible, and it is set up in Act 2 Scene 1 so that it does not arrive
as a convenience.

**The want:** to not be noticed, ever, by anyone.
**The need:** to be someone, which requires the exact opposite.
**The lie she believes:** that she is nobody, and that being nobody is safe. Act 4 destroys the
second half of that. Chapters 3+ destroy the first.

### The Valyrian question — Chapter 1 rules

Chapter 1 **never explains her**. It only lets the world react:

1. Three separate NPCs remark on her hair or eyes. Each has a different, wrong theory. None is
   corrected.
2. Nobody ever says the word *Valyrian* in Chapter 1. Not once. It is in no dialogue file.
3. She is *never* unusually good at anything. No fire immunity, no dragon-adjacent intuition, no
   dreams. She is a servant girl with a memorable face.
4. The one hard seed: in Act 4, in the crowd at the Sept, a stranger stares at her too long and
   says *"I knew a woman with your eyes."* — then the crowd surges and he is gone. Flag:
   `act4_stranger_recognized_her`. It is never resolved in Chapter 1. It is the Chapter 2 hook.

Everything else (heritage revealed, and eventually a dragon) is a **later-chapter arc**. Nothing
in Chapter 1 pays it off, and no scene file may imply otherwise.

### Voice

Economical. She answers questions with the fewest words that end the conversation. Deflects with
politeness — "As you say, m'lord" is her shield and she uses it when she is furious. Her interior
narration (used in stage directions and a small number of italic lines) is much sharper than
anything she says aloud, and the gap between the two *is* the character.

> **Guard:** "You see a girl come through here? Skinny thing, dark hair."
> **Nyra:** "No, ser."
> *(She had. She had watched her go. She had, for one moment, wanted to go with her.)*

**Never:** sass to a superior, precocious wisdom, a moment where she "finds her voice" and tells
Cersei off. She survives. That is the achievement.

### Mechanics

| | |
|---|---|
| No combat. | She has no HP bar in Acts 2 and 4. |
| Threat resource | **Detection** (0–4). Rises when seen where she shouldn't be, decays over time. At 4, the scene fails forward — she is caught, and the story continues worse. |
| Toolkit | Carry-an-object (justifies presence), serving-hatch listening posts, timed lingering, service corridors as a parallel map |
| Key relationships | Cersei, Littlefinger, Sansa, Old Mabb (the head laundress — invented, her only friend) |
| Trait pressure | `honest` and `merciful` are the axes her choices actually move |

**Failing forward.** No scene in Act 2 or 4 can be lost. Being caught costs relationship, sets a
`noticed` flag, and changes Act 4's interrogation scene. The player is never sent back to a
checkpoint for being seen — the game just gets harder to live in.

---

## 3. The Two of Them

Rules for the romance arc, so nobody writes past them:

- In Chapter 1 they exchange **zero words**. Twice on screen, in Act 1, both under thirty seconds.
  See the staging notes in `CHAPTER1_PERSPECTIVE_MAP.md`.
- Neither learns the other's name in Chapter 1.
- Neither character *thinks about* the other on screen. No wistful callback lines. The encounters
  are the player's memory, not the characters'.
- They share no musical motif yet. The shared theme debuts in Chapter 2 and earns its landing
  precisely because it was withheld.
- The flags `act1_encounter_feast` and `act1_encounter_departure` persist through the save file
  forever and are read by Chapter 3. A player who somehow missed both gets a different, colder
  version of their real meeting — the design does not require the encounters, it rewards them.

---

## 4. Supporting Original Characters

Canon characters are canon; these are the invented few needed to make the households work.

| Name | Who | Where |
|---|---|---|
| **Lord Ondrew Slate** | Torren's father. Canon name, invented characterization: tired, practical, unimpressed. | Acts 1, 3 |
| **Serjeant Hune** | Winterfell guard serjeant. Torren's superior. Blunt, fair, dies at the Whispering Wood. | Acts 1, 3, 5 |
| **Old Mabb** | Head laundress, Red Keep. Sixty years in the castle. Nyra's only friend and her source of gossip. | Acts 2, 4 |
| **Pate of the Kitchens** | Kitchen boy, fourteen, talks too much. Nyra's information network and her liability. | Acts 2, 4 |
| **Ser Emmon Wells** | Southron knight in the royal party. Contemptuous of Northern hedge-knighting. Torren's foil. | Acts 1, 5 |

---

## 5. Canonical Characters — Voice Guardrails

Original dialogue only; no verbatim book quotes. The rule for every canon character is: **write
what they would say in this specific room, not their greatest hits.** No character delivers their
famous line. Ned never says "winter is coming." Robert is never introduced with a joke about his
weight. If a line could be a t-shirt, cut it.

Named canon speakers used in Chapter 1: Eddard, Catelyn, Robb, Bran, Theon, Jory Cassel, Robert,
Cersei, Joffrey, Sandor Clegane, Petyr Baelish, Varys, Pycelle, Sansa, Arya, Septa Mordane,
Greatjon Umber, Rickard Karstark, Galbart Glover, Wyman Manderly, Maege Mormont, Walder Frey,
Ilyn Payne, Meryn Trant, Tobho Mott, Gendry.
