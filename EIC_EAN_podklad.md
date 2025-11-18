# Standardy a normy pro generování EIC a EAN kódů v energetice ČR

Oficiální pravidla, struktura a generování EIC (Energy Identification Code) a EAN (European Article Number) kódů jsou dány evropskými a mezinárodními standardy. Tyto normy jsou závazné pro všechny provozovatele energetických sítí, distributory i národní operátory trhu.

---

## EIC (Energy Identification Code)

### Norma / Standard

- Správu a strukturu EIC určuje evropská organizace **ENTSO-E** (European Network of Transmission System Operators for Electricity) a **ENTSO-G** (pro plyn)
- EIC Reference Manual stanovuje podrobně typy kódů, délky, významy pozic i algoritmus kontrolního znaku
- Standard je jednotný napříč celou Evropou

### Základní formát

**16 znaků: `XXYAAAAAAAAAAAAK`**

| Pozice | Délka | Význam | Příklad |
|--------|-------|--------|---------|
| XX | 2 znaky | Identifikátor lokální kanceláře (Office ID) | `27` (Česká republika) |
| Y | 1 znak | Typ entity (Entity Type) | `X` (Electrical area) |
| A... | 12 znaků | Individuální identifikátor | `GOEPS000001` |
| K | 1 znak | Kontrolní znak (Check Digit) | `Z` |

**Úplný příklad:** `27XGOEPS000001Z`

### Identifikátory lokální kanceláře (Office ID)

Podporované kódy zahrnují:
- **Numerické:** `10`-`59` (jednotlivé země, např. `27` = Česká republika)
- **Alfanumerické:** `X1`-`X9`, `Y1`-`Y9`, `Z1`-`Z9`

### Typy entit (Entity Type)

| Kód | Typ entity | Popis |
|-----|------------|-------|
| T | Control Area | Oblast řízení přenosové soustavy |
| Y | TSO | Provozovatel přenosové soustavy |
| X | Electrical Area | Elektrická oblast |
| Z | Metering Point | Odběrné/předávací místo |
| A | Generation Unit | Výrobní jednotka |
| V | Generation Module | Výrobní modul |
| W | Production Unit | Produkční jednotka |
| B | Bidding Zone | Obchodní zóna |
| ... | ... | A dalších 15+ typů |

### Algoritmus kontrolního znaku

EIC kódy používají **ISO 7064 Mod 37,36** algoritmus:

1. Každému znaku je přiřazena číselná hodnota:
   - `0-9` → hodnoty `0-9`
   - `A-Z` → hodnoty `10-35`

2. Výpočet:
   ```
   P = 36
   Pro každý znak z (zleva doprava, kromě posledního):
       P = ((P + hodnota_znaku) mod 37) * 2 mod 37

   check_digit_value = (37 - P + 1) mod 37
   ```

3. Kontrolní znak je znak odpovídající vypočtené hodnotě (`0-9` nebo `A-Z`)

**Implementace v Pythonu:**
```python
def calculate_eic_check_digit(code_without_check: str) -> str:
    """Vypočítá kontrolní znak pro EIC kód pomocí ISO 7064 Mod 37,36."""
    char_values = {
        **{str(i): i for i in range(10)},
        **{chr(65 + i): 10 + i for i in range(26)}
    }

    p = 36
    for char in code_without_check:
        p = ((p + char_values[char]) % 37) * 2 % 37

    check_value = (37 - p + 1) % 37
    return '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[check_value]
```

### Použití

- Zajišťuje **unikátní identifikaci** zařízení a subjektů napříč evropskými trhy s elektřinou a plynem
- Používá se v EDI (Electronic Data Interchange) systémech
- Povinný pro obchodování na energetických burzách
- Nezbytný pro komunikaci mezi TSO a DSO

---

## EAN (European Article Number) v energetice

### Norma / Standard

- Základ vychází ze systému **GS1** (Global Standards One, původně European Article Numbering)
- **Normy:**
  - ISO/IEC 15420 - Mezinárodní standard pro EAN/UPC čárové kódy
  - GS1 General Specifications - Obecné specifikace GS1
- **Národní autorita:** GS1 Czech Republic

### Formáty EAN kódů

#### EAN-8
- **Formát:** 8 číslic celkem
- **Struktura:** 7 datových číslic + 1 kontrolní číslice
- **Příklad:** `12345670`
- **Použití:** Malé produktové obaly, drobné zboží

#### EAN-13
- **Formát:** 13 číslic celkem
- **Struktura:** 12 datových číslic + 1 kontrolní číslice
- **Příklad:** `4006381333931`
- **Použití:**
  - Standardní produktové čárové kódy
  - Identifikace odběrných míst v energetice (často s prefixem 859 pro ČR)
  - Nejběžnější formát v energetickém sektoru

#### EAN-14
- **Formát:** 14 číslic celkem
- **Struktura:** 13 datových číslic + 1 kontrolní číslice
- **Příklad:** `14006381333938`
- **Použití:** Logistické jednotky, balení

### EAN v českém energetickém sektoru

**Formát pro odběrná místa (EAN-13):**
```
859 XXXXX YYYYYYY C
│   │     │       │
│   │     │       └─ Kontrolní číslice
│   │     └───────── Identifikátor odběrného místa
│   └─────────────── Kód distributora/OTE
└─────────────────── Prefix pro Českou republiku
```

**Příklad:** `8595850012345` (859 = ČR, 5850 = distributor, 0123456 = místo, 5 = check)

### Algoritmus kontrolního znaku (GS1 Mod 10)

Podle GS1 standardu se pozice číslují **zleva doprava** (1, 2, 3, ...):

1. **Sečíst číslice na sudých pozicích zleva** (2, 4, 6, ...) a **vynásobit 3**
2. **Sečíst číslice na lichých pozicích zleva** (1, 3, 5, ...)
3. **Sečíst oba výsledky**
4. **Kontrolní číslice** = `(10 - (součet mod 10)) mod 10`

**Příklad pro `400638133393`:**
```
Pozice zleva:  1  2  3  4  5  6  7  8  9 10 11 12
Číslice:       4  0  0  6  3  8  1  3  3  3  9  3

Liché pozice zleva (1,3,5,7,9,11):  4+0+3+1+3+9 = 20
Sudé pozice zleva (2,4,6,8,10,12):  0+6+8+3+3+3 = 23 → 23 × 3 = 69
Součet: 20 + 69 = 89
Kontrolní číslice: (10 - (89 mod 10)) mod 10 = (10 - 9) mod 10 = 1

Výsledek: 4006381333931
```

**Implementace v Pythonu:**
```python
def calculate_ean_check_digit(code_without_check: str) -> str:
    """Vypočítá kontrolní číslici pro EAN kód pomocí GS1 Mod 10."""
    digits = [int(d) for d in code_without_check]
    total = 0

    # Procházíme zleva doprava
    for i, digit in enumerate(digits):
        # Sudé pozice (index 1, 3, 5...) dostanou váhu 3
        # Liché pozice (index 0, 2, 4...) dostanou váhu 1
        weight = 3 if i % 2 == 1 else 1
        total += digit * weight

    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)
```

### Použití v energetice

- **Identifikace odběrných míst** elektřiny a plynu
- **Databázové systémy** distributorů a OTE
- **Fakturace a měření** spotřeby
- **Zákaznické portály** a mobilní aplikace
- **Migrace** mezi dodavateli energie

---

## Klíčové oficiální zdroje

### EIC (Energy Identification Code)

#### ENTSO-E Oficiální dokumentace
- [ENTSO-E: Energy Identification Codes (EICs)](https://www.entsoe.eu/data/energy-identification-codes-eic/)
  Hlavní stránka pro EIC kódy s aktuálními informacemi

- [ENTSO-E: Electronic Data Interchange (EDI) Library](https://www.entsoe.eu/publications/electronic-data-interchange-edi-library/)
  Kompletní knihovna EDI dokumentů včetně EIC specifikací

- [ENTSO-E: EIC Reference Manual](https://eepublicdownloads.entsoe.eu/clean-documents/EDI/Library/old-downloads/ENTSOE_LIO_Management.pdf)
  Referenční manuál pro CIO a LIO management

#### Standardy
- [ISO 7064: Mod 37,36 Check Character System](https://en.wikipedia.org/wiki/ISO_7064)
  Specifikace algoritmu pro výpočet kontrolního znaku

### EAN (European Article Number)

#### GS1 Oficiální dokumentace
- [GS1 Czech Republic](https://www.gs1cz.org/)
  Národní organizace pro správu GS1 standardů v ČR

- [GS1 Global: Barcode Standards](https://www.gs1.org/standards/barcode-standards)
  Mezinárodní standardy pro čárové kódy

- [GS1 General Specifications](https://www.gs1.org/docs/barcodes/GS1_General_Specifications.pdf)
  Komplexní specifikace GS1 standardů (anglicky)

#### Energetický sektor v ČR
- [OTE (Operátor trhu s elektřinou)](https://www.ote-cr.cz/)
  Provozovatel krátkodobého trhu s elektřinou a plynem v ČR

- [ERÚ (Energetický regulační úřad)](https://www.eru.cz/)
  Regulační úřad pro energetiku v České republice

### Standardy ISO/IEC
- [ISO/IEC 15420: EAN/UPC Bar Code Symbology](https://www.iso.org/standard/46143.html)
  Mezinárodní standard pro EAN a UPC čárové kódy

---

## Implementace v tomto projektu

Tento validační servis implementuje:
- ✅ **Plnou podporu EIC validace** podle ENTSO-E standardů
- ✅ **ISO 7064 Mod 37,36** algoritmus pro EIC check digit
- ✅ **Podporu všech tří EAN formátů** (EAN-8, EAN-13, EAN-14)
- ✅ **GS1 Mod 10** algoritmus pro EAN check digit
- ✅ **Generování platných kódů** s kryptograficky bezpečnou náhodností
- ✅ **Detailní validační zprávy** s popisem chyb
- ✅ **RESTful API** s OpenAPI 3.1.0 dokumentací
- ✅ **Komplexní testovací pokrytí** (112 testů)

---

## Licence a autorská práva

- **EIC standardy:** © ENTSO-E
- **GS1 standardy:** © GS1 Global
- **Tento implementační projekt:** Vytvořeno pro demonstrační účely

