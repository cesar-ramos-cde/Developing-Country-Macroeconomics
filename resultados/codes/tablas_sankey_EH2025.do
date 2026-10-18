*=====================================================================
* TABLAS DEL DIAGRAMA DE SANKEY - EH2025 (INE)
*=====================================================================
clear all
set more off

global datas "E:/William Collegue/Fall - First Semester/Developing Macroeconomics 505 Kuttner/Memo Cesar/Survey_Household"
use "$datas/EH2025_Persona.dta", clear

* Ocupados de 14 años o más
gen ocupado = (condact == 1 & pet == 1)

*---------------------------------------------------------------------
* 1. INFORMALIDAD (misma definición de siempre)
*---------------------------------------------------------------------
gen     mt = 1 if s04b_12 == 8                                   // Doméstico
replace mt = 2 if inlist(s04b_13, 1, 2) & mt == .                // Estatal
replace mt = 3 if inlist(s04b_12, 3, 6, 7) & mt == .             // Familiar
replace mt = 4 if inlist(s04b_12, 1, 2, 4, 5) & s04b_14 <= 5 ///
                  & mt == .                                      // Semiempresarial
replace mt = 5 if inlist(s04b_12, 1, 2, 4, 5) & s04b_14 > 5  ///
                  & !missing(s04b_14) & mt == .                  // Empresarial
replace mt = . if ocupado == 0

gen     informal = (s04f_36 != 1) if ocupado == 1               // no aporta a la Gestora
replace informal = 1 if inlist(s04b_12, 6, 7) & ocupado == 1    // familiares sin remuneración
replace informal = 0 if inlist(s04b_12, 2, 4) & mt == 5 & ocupado == 1  // empleadores > 5 personas
label define informal_lb 0 "Formal" 1 "Informal"
label values informal informal_lb

*---------------------------------------------------------------------
* 2. SEXO (columna 1)
*---------------------------------------------------------------------
gen sexo = s01a_02
label define sexo_lb 1 "Men" 2 "Women"
label values sexo sexo_lb

*---------------------------------------------------------------------
* 3. GRAN SECTOR ECONÓMICO (columna 2)
*    Primeros 2 dígitos del código CAEB 2022 de la ocupación principal
*---------------------------------------------------------------------
gen d2 = real(substr(s04b_10a_cod, 1, 2))

recode d2 (1/3   = 1)  /// Agricultura, ganadería, silvicultura y pesca
          (5/9   = 2)  /// Minería e hidrocarburos
          (10/33 = 3)  /// Industria manufacturera
          (35/43 = 4)  /// Electricidad, agua y construcción
          (45/47 = 5)  /// Comercio
          (49/53 = 6)  /// Transporte y almacenamiento
          (55/56 = 7)  /// Alojamiento y comidas
          (58/82 = 8)  /// Información, finanzas, inmobiliarias, profesionales, apoyo
          (84    = 9)  /// Administración pública
          (85/88 = 10) /// Educación y salud (privadas; las públicas se corrigen abajo)
          (90/98 = 10) /// Arte, otros servicios, trabajo doméstico
          (else  = .), gen(sector)

replace sector = 9 if inrange(d2, 85, 88) & inlist(s04b_13, 1, 2) // educación y salud públicas
replace sector = 4 if s04b_10a_cod == "F"                         // código solo con letra (construcción)

label define sector_lb 1 "Agriculture" 2 "Mining" 3 "Manufacturing"          ///
                       4 "Construction & utilities" 5 "Trade" 6 "Transport"  ///
                       7 "Hospitality" 8 "Business services" 9 "Public sector" ///
                       10 "Other services"
label values sector sector_lb

*---------------------------------------------------------------------
* 4. POBREZA DEL HOGAR (columna 4)
*---------------------------------------------------------------------
gen     pobreza = 1 if p0 == 0              // no pobre
replace pobreza = 2 if p0 == 1              // pobre (moderado)
replace pobreza = 3 if pext0 == 1           // pobre extremo
label define pobreza_lb 1 "Non-poor" 2 "Moderate poverty" 3 "Extreme poverty"
label values pobreza pobreza_lb

* Muestra del gráfico: ocupados con sector y pobreza conocidos
gen muestra = (ocupado == 1 & !missing(sector, pobreza))

*=====================================================================
* A. LAS CUATRO COLUMNAS (barras del gráfico)
*    "Freq." = personas; "Percent" = % del total de ocupados
*    La fila "Total" (5.97 millones) es la base de todos los porcentajes
*=====================================================================
tab sexo     if muestra [iw=factor]      // Columna 1: Men 56.0%, Women 44.0%
tab sector   if muestra [iw=factor]      // Columna 2: Agriculture 25.3%, Trade 17.7%...
tab informal if muestra [iw=factor]      // Columna 3: Formal 15.2%, Informal 84.8%
tab pobreza  if muestra [iw=factor]      // Columna 4: Non-poor 63.0%, Moderate 22.9%, Extreme 14.1%

*=====================================================================
* B. LOS FLUJOS (las cintas entre columnas)
*    Con la opción "cell", cada celda es una cinta: personas y % del total
*=====================================================================

* Flujo 1: Sexo -> Sector (cintas grises)
tab sector sexo if muestra [iw=factor], cell
tab sector sexo if muestra [iw=factor], row nofreq   // % de hombres y mujeres en cada sector

* Flujo 2: Sector -> Formal / Informal (cintas claras y oscuras)
tab sector informal if muestra [iw=factor], cell
tab sector informal if muestra [iw=factor], row nofreq   // tasa de informalidad de cada sector

* Flujo 3: Formal / Informal -> Pobreza
tab informal pobreza if muestra [iw=factor], cell
tab informal pobreza if muestra [iw=factor], row nofreq  // pobreza entre formales e informales
tab informal pobreza if muestra [iw=factor], col nofreq  // % de informales dentro de cada nivel de pobreza

*=====================================================================
* C. CIFRAS DE APOYO PARA EL TEXTO
*=====================================================================
* Informalidad de hombres y mujeres
tab sexo informal if muestra [iw=factor], row nofreq

* ¿Qué % de los trabajadores pobres (moderados + extremos) es informal?
gen pobre = (pobreza >= 2) if muestra
label define pobre_lb 0 "Non-poor" 1 "Poor"
label values pobre pobre_lb
tab informal pobre if muestra [iw=factor], col nofreq
