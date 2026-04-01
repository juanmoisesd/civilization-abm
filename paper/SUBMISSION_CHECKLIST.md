# Checklist de Envío — Social Science Computer Review (SSCR)
# SAGE Publications — ISSN 0894-4393

**Paper:** Emergent Wealth Inequality in Agent-Based Civilizations
**Autor:** De la Serna Tuya, Juan Moisés — UNIR, Spain
**ORCID:** 0000-0002-8401-8018
**Revista:** https://journals.sagepub.com/home/ssc
**Coste:** €0 — sin APC, sin tasas de envío ✅
**Revisión:** Double-anonymized — doble ciego ⚠️ *La web de SSCR muestra "Single anonymized" en el bloque de datos rápidos, pero la sección detallada "Peer review policy" especifica explícitamente "Double-anonymized". Enviar siempre versión anonimizada.*
**Factor de impacto:** 2.7 / IF a 5 años: 4.2

---

## PASO 1 — Figuras ✅ YA GENERADAS

```
paper/figures/
├── Figure_1_baseline_panel.png      ✅  (300 dpi)
├── Figure_2_fiscal_policy.png       ✅  (300 dpi)
├── Figure_3_initial_inequality.png  ✅  (300 dpi)
├── Figure_4_network_topology.png    ✅  (300 dpi)
├── Figure_5_floor_policy.png        ✅  (300 dpi)
└── Figure_6_summary_heatmap.png     ✅  (300 dpi)
```

*Nota: Figuras en color son gratuitas en versión online. Si quieres color en impresión: $800 primera figura + $200 cada adicional — pero el 99% de los lectores ve la versión online.*

---

## PASO 2 — Convertir a Word (SSCR requiere .docx)

```powershell
cd "C:\Users\DELL\Pictures\Claude Industrial\civilization-abm"
pandoc paper/manuscript.md -o paper/manuscript.docx --standalone
```

Si pandoc no está instalado: https://pandoc.org/installing.html (instalador Windows)

- [ ] `paper/manuscript.docx` creado

---

## PASO 3 — Crear Title Page separado

SSCR requiere **doble ciego**: el manuscrito enviado a revisores NO debe tener datos del autor.

**Crear `paper/title_page.docx`** con este contenido:

```
Title:
  Emergent Wealth Inequality in Agent-Based Civilizations:
  Effects of Fiscal Policy, Network Topology, and Initial Conditions

Author:
  Juan Moisés de la Serna Tuya

Affiliation:
  Universidad Internacional de La Rioja (UNIR), Spain

Postal address:
  Av. de la Paz, 137, 26006 Logroño, La Rioja, Spain

Phone:
  [tu número de teléfono — requerido por SSCR]

Email:
  juanmoises.delaserna@unir.net

ORCID:
  0000-0002-8401-8018

Acknowledgements:
  The author used Claude (Anthropic) for assistance with manuscript
  drafting and editorial revision. All scientific concepts, research
  design, model implementation, experimental execution, data analysis,
  and intellectual conclusions are entirely the author's own.

Declaration of conflicting interest:
  The author declared no potential conflicts of interest with respect
  to the research, authorship, and/or publication of this article.

Funding statement:
  This research received no external funding.

Ethical approval:
  Not required. This study uses only computational simulation data.
  No human participants, human data, or human tissue were involved.

Consent to participate: Not applicable.

Consent for publication: Not applicable.

Data availability:
  All code and data are openly available at:
  https://github.com/jmdelaserna/civilization-abm (MIT license)
  and at the CoMSES Computational Model Library.
```

⚠️ **El teléfono es obligatorio** según las instrucciones de SSCR (contact information for the corresponding author: name, institutional address, phone, email).

---

## PASO 4 — Anonimizar el manuscrito

Abrir `manuscript.docx` → guardar como `manuscript_anon.docx` → eliminar:
- [ ] Nombre del autor en texto principal
- [ ] Afiliación (UNIR) en texto principal
- [ ] Email y ORCID del cuerpo del texto
- [ ] Sección "Bibliographic Information" inicial (es solo para el Title Page)
- [ ] Mantener: sección "Author Contributions" pero cambiar nombre por "The author"

*El nombre del archivo tampoco debe contener el apellido del autor.*

---

## PASO 5 — Subir a GitHub

```powershell
cd "C:\Users\DELL\Pictures\Claude Industrial\civilization-abm"
git init
git add .
git commit -m "Initial commit: Civilization-ABM complete project and paper"
git branch -M main

# Crear repo PÚBLICO en: https://github.com/new
# Nombre: civilization-abm | Visibilidad: Public
git remote add origin https://github.com/jmdelaserna/civilization-abm.git
git push -u origin main
```

- [ ] Repositorio público en GitHub ✓ URL: https://github.com/jmdelaserna/civilization-abm

---

## PASO 6 — Subir a CoMSES Net

1. Ir a: https://www.comses.net/codebases/
2. Crear cuenta o iniciar sesión
3. "Publish a model" → subir código + README + requirements.txt
4. Anotar URL del modelo

- [ ] Modelo en CoMSES Net
- [ ] URL de CoMSES anotada

---

## PASO 7 — Registro y envío en Sage Track

**URL de envío:** https://mc.manuscriptcentral.com/sscr

*(Sage Track es el sistema de envío de SSCR)*

1. Crear cuenta o iniciar sesión en Sage Track
2. "Submit new manuscript"
3. Tipo de artículo: **Research Article**

---

## PASO 8 — Datos del envío

```
Título:
  Emergent Wealth Inequality in Agent-Based Civilizations:
  Effects of Fiscal Policy, Network Topology, and Initial Conditions

Autor:
  De la Serna Tuya, Juan Moisés

Afiliación:
  Universidad Internacional de La Rioja (UNIR), Spain

Email:
  juanmoises.delaserna@unir.net

ORCID:
  0000-0002-8401-8018

Tipo de artículo:
  Research Article

Palabras clave (mínimo 5):
  agent-based modeling; wealth inequality; fiscal policy;
  social networks; Gini coefficient; emergence

Número de figuras: 6
Número de tablas: 2
Número de palabras: ~5,700
```

---

## PASO 9 — Archivos a subir en Sage Track

| Archivo | Tipo en sistema | Descripción |
|---|---|---|
| `title_page.docx` | Title Page | Info del autor (NO va a revisores) |
| `manuscript_anon.docx` | Main Document | Texto anonimizado (VA a revisores) |
| `Figure_1_baseline_panel.png` | Figure | Figura 1 (300 dpi) |
| `Figure_2_fiscal_policy.png` | Figure | Figura 2 (300 dpi) |
| `Figure_3_initial_inequality.png` | Figure | Figura 3 (300 dpi) |
| `Figure_4_network_topology.png` | Figure | Figura 4 (300 dpi) |
| `Figure_5_floor_policy.png` | Figure | Figura 5 (300 dpi) |
| `Figure_6_summary_heatmap.png` | Figure | Figura 6 (300 dpi) |
| `all_conditions.csv` | Supplemental File | Supporting data (S1) |

---

## PASO 10 — Cover Letter

```
Dear Professor Rohlinger and the Editorial Board of Social Science
Computer Review,

I submit for your consideration the manuscript "Emergent Wealth
Inequality in Agent-Based Civilizations: Effects of Fiscal Policy,
Network Topology, and Initial Conditions" for publication as a
Research Article in Social Science Computer Review.

This study presents Civilization-ABM, a fully reproducible,
open-source, Mesa-based agent-based simulation platform that
systematically investigates how initial conditions, fiscal
institutions, and social network topology jointly shape the
emergence of wealth inequality in an artificial society. Across
11 experimental conditions and 330 replications (66,000 simulation
runs), I identify two theoretically unexpected emergent findings:

(1) A redistribution amplification paradox: high initial wealth
dispersion (σ = 1.5) produces the lowest final Gini coefficient
of all conditions tested (0.185), because greater absolute wealth
activates progressive tax brackets more intensively.

(2) A floor-policy backfire effect: minimum wealth guarantees
counterproductively increase inequality (+3.5% Gini) by hollowing
out the middle class through asymmetric transfer obligations.

This manuscript aligns directly with SSCR's scope in computational
social science, agent-based modeling, and methodological innovation.
All code, data, and experimental configurations are openly available
at https://github.com/jmdelaserna/civilization-abm under MIT
license. There are no competing interests and the research received
no external funding.

I also wish to declare that Claude (Anthropic) was used for
assistance with manuscript drafting and editorial revision. All
scientific concepts, research design, model implementation,
experimental execution, data analysis, and intellectual conclusions
are entirely my own.

Sincerely,
Juan Moisés de la Serna Tuya
Universidad Internacional de La Rioja (UNIR), Spain
ORCID: 0000-0002-8401-8018
juanmoises.delaserna@unir.net
```

---

## PASO 11 — Verificación final del manuscrito (v0.5)

- [x] Título descriptivo
- [x] Abstract 183 palabras, sin estructura, sin citas ✅
- [x] Keywords ≥ 5: tenemos 6 ✅
- [x] Citas APA 7ª edición: (Autor, Año) con coma, `&` para múltiples autores ✅
- [x] Referencias APA 7ª: sin MAYÚSCULAS en apellidos, `&`, sin ciudad editorial ✅
- [x] Tabla 1 — condiciones experimentales
- [x] Tabla 2 — resultados completos
- [x] 6 figuras generadas a 300 dpi
- [x] GitHub URL incluida en texto
- [x] CoMSES Net mencionado
- [x] Sección Author Contributions ✅
- [x] Acknowledgements con declaración de asistencia de IA (Claude) ✅
- [x] Author Contributions ✅
- [x] Statements and Declarations completos:
  - [x] Ethical considerations (no approval required, computational) ✅
  - [x] Consent to participate (N/A) ✅
  - [x] Consent for publication (N/A) ✅
  - [x] Declaration of conflicting interest ✅
  - [x] Funding statement ✅
  - [x] Data availability ✅
- [x] ~5,700 palabras (por debajo del límite de 10,000) ✅
- [ ] manuscript.docx generado
- [ ] title_page.docx creado (con teléfono incluido — OBLIGATORIO)
- [ ] manuscript_anon.docx creado (anonimizado para revisión doble ciega)

---

## Comparativa JASSS vs SSCR

| | JASSS | **SSCR** ✅ |
|---|---|---|
| APC | €1,000 | **€0** |
| Formato | Word/LaTeX | Word/LaTeX |
| Abstract | 200–300 palabras | 150–200 palabras |
| Keywords | 3–6 | Mínimo 5 |
| Citas | APA modificado (sin coma) | **APA 7ª** (con coma, `&`) |
| Revisión | Single-blind | **Double-blind** |
| Factor de impacto | ~2.1 | **2.7** |
| IF a 5 años | ~3.5 | **4.2** |
| Scope | ABM/Sim social | Computación + CCSS |
| Envío | epress.ac.uk | manuscriptcentral.com/sscr |

---

*Checklist actualizado: 2026-04-01*
*Manuscrito: v0.5 — APA 7ª edición — Adaptado a SSCR — Listo para envío*
