from tptq.feacomposer import FeaComposer

requiredWritingSystems = {"hud"}

assert requiredWritingSystems

languageSystems = {"mong": set()}
if "hud" in requiredWritingSystems or "hag" in requiredWritingSystems:
    languageSystems["mong"].add("MNG")
if "tod" in requiredWritingSystems or "tag" in requiredWritingSystems:
    languageSystems["mong"].add("TOD")
if "sib" in requiredWritingSystems:
    languageSystems["mong"].add("SIB")
if "man" in requiredWritingSystems or "mag" in requiredWritingSystems:
    languageSystems["mong"].add("MCH")
c = FeaComposer(languageSystems)

### glyph class definition for letters

### glyph class definition for categories

### cursive joining

defaultForms = {
    "isol": {"uni1820": "uni1820.AA.isol"},
    "init": {"uni1820": "uni1820.AA.init"},
    "medi": {"uni1820": "uni1820.A.medi"},
    "fina": {"uni1820": "uni1820.A.fina"},
}
for joiningForm in ["isol", "init", "medi", "fina"]:
    with c.Lookup(feature=joiningForm, name=f"IIa.{joiningForm}"):
        for nominalGlyph, defaultGlyph in defaultForms.get(joiningForm, {}).items():
            c.sub(nominalGlyph, defaultGlyph)

### rclt

# control character: preprocessing

# III.1: Phonetic - Chachlag

# III.2: Phonetic - Syllabic

# III.3: Phonetic - Particle

# III.4: Graphemic - Devsger

# III.5: Graphemic - Post bowed

# III.6: Uncaptured - FVS

# IIb.1: ligature

# IIb.2: cleanup of format controls

# IIb.3: optional treatments

### vert

# Ib: vertical punctuation

### rlig

# Ib: punctuation ligature

### vpal

# Ib: proportional punctuation

### mark

# Ib: marks position

print(c.code())
