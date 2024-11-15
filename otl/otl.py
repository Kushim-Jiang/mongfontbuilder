from tptq.feacomposer import FeaComposer


c = FeaComposer()

required_writing_systems = {"hud"}

### glyph class definition for letters

### glyph class definition for categories

### cursive joining

default_forms = {
    "isol": {"uni1820": "uni1820.AA.isol"},
    "init": {"uni1820": "uni1820.AA.init"},
    "medi": {"uni1820": "uni1820.A.medi"},
    "fina": {"uni1820": "uni1820.A.fina"},
}
for joining_form in ["isol", "init", "medi", "fina"]:
    with c.Lookup(feature=joining_form, name=f"IIa.{joining_form}"):
        for nominal_glyph, default_glyph in default_forms.get(joining_form).items():
            c.sub(nominal_glyph, default_glyph)

### rclt

# control character: preprocessing

# III.1: Phonetic - Chachlag

# III.2: Phonetic - Syllabic

# III.3: Phonetic - Particle

# III.4: Graphemic - Devsger

# III.5: Graphemic - Postbowed

# III.6: Uncaptured - FVS

# IIb.1: ligature

# IIb.2: cleanup of format controls

# IIb.3: optional treatments

### vert

# Ib: vertical punctuation

### rlig

# Ib: punctuation ligature

### vpal

# Ib: propotional punctuation

### mark

# Ib: marks position

print(c.code())
