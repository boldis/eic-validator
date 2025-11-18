# Standardy a normy pro generování EIC a EAN kódů v energetice ČR

Oficiální pravidla, struktura a generování EIC (Energy Identification Code) a EAN (European Article Number) kódů jsou dány evropskými a mezinárodními standardy. Tyto normy jsou závazné pro všechny provozovatele energetických sítí, distributory i národní operátory trhu.

---

## EIC (Energy Identification Code)

- **Norma / Standard:**
  - Správu a strukturu EIC určuje evropská organizace **ENTSO-E / ENTSO-G** (dříve ETSO).
  - EIC Reference Manual stanovuje podrobně typy kódů, délky, významy pozic i algoritmus kontrolního znaku.
- **Základní formát:**
  - 16 znaků: `XXYAAAAAAAAAAAAK`
    - XX - identifikátor lokální kanceláře (např. „27“ pro ČR, „ZG“ pro plynárenství)
    - Y - typ entit (A – stanice, Z – odběrné místo aj.)
    - A... - individuální identifikátor
    - K - kontrolní znak
- **Použití:**
  - Zajišťuje unikátní identifikaci zařízení a subjektů napříč evropskými trhy s elektřinou a plynem.

---

## EAN (European Article Number) v energetice

- **Norma / Standard:**
  - Základ vychází ze systému **GS1** (původně EAN, dnes mezinárodně „Global Location Number“).
  - Normy: ISO/IEC 15420, GS1 General Specifications upravované národní autoritou (GS1 Czech Republic).
- **Základní formát:**
  - 18 čísel: `859 + OTE/distributor kód + unikát místa + kontrolní číslo`
    - 859 - prefix pro ČR
    - OTE/distributor - 4–5 znaků specifických pro distributora
    - Unikátní identifikátor a kontrolní číslice dle standardu GS1
- **Použití:**
  - Jednoznačně identifikuje odběrné místo elektřiny v databázích a procesech trhu.

---

## Klíčové oficiální zdroje

- [ENTSO-E: Energy Identification Codes (EICs)](https://www.entsoe.eu/data/energy-identification-codes-eic/)  
- [ENTSO-E: EIC Reference Manual – CIO a LIO management](https://eepublicdownloads.entsoe.eu/clean-documents/EDI/Library/old-downloads/ENTSOE_LIO_Management.pdf)  
- [ENTSO-E: Electronic Data Interchange (EDI) Library](https://www.entsoe.eu/publications/electronic-data-interchange-edi-library/)  
- [GS1 Czech Republic](https://www.gs1cz.org/)  
- [GS1 General Specifications (anglicky, PDF)](https://www.gs1.org/standards/barcode-standards)  
- [GS1 – Historie EAN v ČR (PDF)](https://www.gs1cz.org/wp-content/uploads/2023/05/HISTORIE_WEB_EN.pdf)  


