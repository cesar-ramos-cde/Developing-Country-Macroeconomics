*=====================================================================
* INFORMALIDAD LABORAL - Encuesta de Hogares 2025 (INE Bolivia)
*=====================================================================
clear all
set more off

cd "E:\William Collegue\Fall - First Semester\Developing Macroeconomics 505 Kuttner\Memo Cesar\code_hs_bol25"
global datas = "Survey_Household"
use "$datas/EH2025_Persona.dta", clear

* Diseño muestral (upm y estrato vienen como texto)
egen upm_n     = group(upm)
egen estrato_n = group(estrato)
svyset upm_n [pw=factor], strata(estrato_n) singleunit(centered)

* Ocupados de 14 años o más (PET)
gen ocupado = (condact == 1 & pet == 1)

*---------------------------------------------------------------------
* 1. MERCADO DE TRABAJO (enfoque productivo, como en 2017)
*
*   s04b_12 (antes s06b_16):
*     1 Obrero(a)/Empleado(a)
*     2 Empleador(a) o socio(a) que sí recibe salario
*     3 Trabajador(a) por cuenta propia
*     4 Empleador(a) o socio(a) que no recibe salario
*     5 Cooperativista de producción
*     6 Trabajador(a) familiar sin remuneración
*     7 Aprendiz o persona en formación sin remuneración
*     8 Empleado(a) del hogar
*   s04b_13 (antes s06b_18): 1 Adm. pública, 2 Empresa pública,
*     3-4 privada, 5 ONG, 6 organismos internacionales
*   s04b_14 (antes s06b_21): número de personas que trabajan en el
*     establecimiento (incluido el informante)
*---------------------------------------------------------------------
gen     mt = 1 if s04b_12 == 8                                   // Doméstico
replace mt = 2 if inlist(s04b_13, 1, 2) & mt == .                // Estatal
replace mt = 3 if inlist(s04b_12, 3, 6, 7) & mt == .             // Familiar
replace mt = 4 if inlist(s04b_12, 1, 2, 4, 5) & s04b_14 <= 5 ///
                  & mt == .                                      // Semiempresarial
replace mt = 5 if inlist(s04b_12, 1, 2, 4, 5) & s04b_14 > 5  ///
                  & !missing(s04b_14) & mt == .                  // Empresarial
replace mt = . if ocupado == 0
label var mt "Mercado de trabajo"
label define mt 1 "Doméstico" 2 "Estatal" 3 "Familiar" 4 "Semiempresarial" 5 "Empresarial"
label values mt mt

gen     formal = 1 if inlist(mt, 2, 5)
replace formal = 2 if inlist(mt, 3, 4)
replace formal = 3 if mt == 1
label var formal "Sector formal e informal"
label define formal 1 "Formal" 2 "Informal" 3 "Doméstico"
label values formal formal

*---------------------------------------------------------------------
* 2. EMPLEO INFORMAL 
*    - familiares y aprendices sin remuneración: siempre informales
*    - empleadores en unidades empresariales (más de 5 personas): formales
*---------------------------------------------------------------------
gen     informal = (s04f_36 != 1) if ocupado == 1
replace informal = 1 if inlist(s04b_12, 6, 7) & ocupado == 1
replace informal = 0 if inlist(s04b_12, 2, 4) & mt == 5 & ocupado == 1
label var informal "Empleo informal (enfoque OIT)"
label define informal 0 "Formal" 1 "Informal"
label values informal informal

*---------------------------------------------------------------------
* 3. RESULTADOS CON SVY
*---------------------------------------------------------------------
* Mercado de trabajo (%)
svy: tab mt, percent format(%5.1f)
svy: tab formal, percent format(%5.1f)

* Tasa de empleo informal (0.848 = 84.8%)
svy, subpop(ocupado): proportion informal
svy, subpop(ocupado): proportion informal, over(area)
svy, subpop(ocupado): proportion informal, over(s01a_02)
svy, subpop(ocupado): proportion informal, over(caeb_op)

* Solo 15 años o más (comparable con la OIT)
svy, subpop(if ocupado == 1 & s01a_03 >= 15): proportion informal

* Informalidad dentro de cada mercado de trabajo (% por fila)
svy: tab mt informal, row percent format(%5.1f)
