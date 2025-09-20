# SwedishFurniture

**SwedishFurniture** is a generator of totally useless but very IKEA-sounding product names.
It spits out pronounceable, vaguely Swedish-ish words — plus fake item cards with weight, size, and release date.

---

Install it like this:

```bash
pip install swedishfurniture
```

---

## Quick Example

```python
from swedishfurniture.generator import SwedishNameGenerator

gen = SwedishNameGenerator(pattern="CVVCVC", morpheme_chance=0.7)
print(gen.generate_name())

item = gen.generate_full_entry()
print(item)
```

You might get something like:

```
Zurühogüd

{'name': 'ZurühogÜD',
 'type': 'Shelf',
 'introduced': '2001-12-04',
 'weight_kg': 19.6,
 'dimensions': '91×16×7 cm'}
```

---

## What It Can Do

* Generate names based on patterns (`C` = consonant, `V` = vowel)
* Supports custom consonants and vowels
* Adds custom morphemes like `flö`, `sk`, or `ön` to boost the IKEA vibes
* Creates full item entries with weight, size, and date
* Export to **TXT**, **JSON**, or **CSV**

---

## 📦 Exporting

```python
from swedishfurniture.export import export_entry

export_entry(item, "output.txt", format="txt")
export_entry(item, "output.json", format="json")
export_entry(item, "output.csv", format="csv")
```

---

## Project Structure

```
swedishfurniture/
├── generator.py
├── patterns.py
├── morphemes.py
├── utils.py
├── data.py
└── export.py
```

---

## 🧪 CLI (Coming Soon)

At some point, you'll be able to run it like this:

```bash
swfgen --pattern CVCVC --count 5 --format json
```

---

## 🧠 Why Tho?

Because if you *can* randomly create something like **"FLÖFänokozÖN — Shelf, 19kg"**,
then... why the heck not?

---

## 👤 Author's Github

[https://github.com/DeltaFree](https://github.com/DeltaFree)
License: MIT
Not affiliated with IKEA™ (obviously).
