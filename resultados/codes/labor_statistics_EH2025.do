*==============================================================================
* ESTADÍSTICAS LABORALES DE BOLIVIA - Encuesta de Hogares 2025 (INE)
* Base:   EH2025_Persona.dta   
*------------------------------------------------------------------------------
* Definiciones:
*   pet     = 1 si tiene 14 años o más (población en edad de trabajar)
*   pea/pei = población económicamente activa / inactiva
*   condact = 1 ocupado, 2 cesante, 3 aspirante,
*             4 inactivo temporal, 5 inactivo permanente
*   Desocupados = cesantes + aspirantes
*   El módulo de empleo se aplica a personas de 7 años o más, pero las
*   tasas oficiales se calculan sobre la PET (14 años o más).
*
*==============================================================================

clear all
set more off
cd "E:\William Collegue\Fall - First Semester\Developing Macroeconomics 505 Kuttner\Memo Cesar\code_hs_bol25"
global datas "Survey_Household"
global res   "resultados"
capture mkdir "res"
use "$datas/EH2025_Persona.dta", clear

* 1. sampling design
egen upm_n     = group(upm) // Renumber PSUs
egen estrato_n = group(estrato) // Renumber strata
svyset upm_n [pw=factor], strata(estrato_n) singleunit(centered) // Set survey design

* 2. Variables 0/1 (PET = 14 años o más)
gen pob_total   = 1
gen pob_pet     = (pet == 1)
gen pob_pea     = (pea == 1)     & pet == 1
gen pob_pei     = (pei == 1)     & pet == 1
gen ocupados    = (condact == 1) & pet == 1
gen desocupados = inlist(condact, 2, 3) & pet == 1

* 3. Tabla
svy: total pob_total pob_pet pob_pea pob_pei ocupados desocupados, cformat(%9.0fc) 

* Install this package to export tables in Latex
// ssc install estout, replace

* Export totals to LaTeX
eststo clear
eststo: svy: total pob_total pob_pet pob_pea pob_pei ocupados desocupados

esttab using "$res/totales.tex", replace booktabs ///
    cells("b(fmt(%12.0fc)) se(fmt(%12.0fc)) ci_l(fmt(%12.0fc)) ci_u(fmt(%12.0fc))") ///
    collabels("Total" "Std. err." "95\% CI lower" "95\% CI upper") ///
    coeflabels(pob_total   "Total population"        ///
               pob_pet     "Working-age population"  ///
               pob_pea     "Labor force"             ///
               pob_pei     "Inactive population"     ///
               ocupados    "Employed"                ///
               desocupados "Unemployed")             ///
    nomtitles nonumbers noobs ///
    title("Population estimates, EH 2025")
	
	
	
* 3. Labor market rates (%)
gen pea100   = 100*pob_pea        // Labor force x100
gen pei100   = 100*pob_pei        // Inactive x100
gen ocup100  = 100*ocupados       // Employed x100
gen desoc100 = 100*desocupados    // Unemployed x100

eststo clear
eststo rates: svy: ratio (participation: pea100/pob_pet)   ///
                         (inactivity:    pei100/pob_pet)   ///
                         (employment:    ocup100/pob_pet)  ///
                         (unemployment:  desoc100/pob_pea), cformat(%9.2f)
						 

* Export rates to LaTeX
esttab rates using "$res/tasas.tex", replace booktabs ///
    cells("b(fmt(%9.2f)) se(fmt(%9.2f)) ci_l(fmt(%9.2f)) ci_u(fmt(%9.2f))") ///
    collabels("Rate (\%)" "Std. err." "95\% CI lower" "95\% CI upper") ///
    coeflabels(participation "Participation rate" ///
               inactivity    "Inactivity rate"    ///
               employment    "Employment rate"    ///
               unemployment  "Unemployment rate") ///
    nomtitles nonumbers noobs ///
    title("Labor market indicators, EH 2025")
	
* Export rates to Excel
esttab rates using "$res/tasas.csv", replace plain ///
    cells("b(fmt(%9.2f)) se(fmt(%9.2f)) ci_l(fmt(%9.2f)) ci_u(fmt(%9.2f))") ///
    collabels("Rate (%)" "Std. err." "95% CI lower" "95% CI upper") ///
    coeflabels(participation "Participation rate" ///
               inactivity    "Inactivity rate"    ///
               employment    "Employment rate"    ///
               unemployment  "Unemployment rate") ///
    nomtitles nonumbers noobs
