
clear all
set maxvar 5000
cd "E:\William Collegue\Fall - First Semester\Developing Macroeconomics 505 Kuttner\Memo Cesar\code_hs_bol25"

global datas = "Survey_Household"

pwd 
dir $datas/ 

** Uncomment after save at dta **

// import spss using "$datas/EH2025_Persona.sav", clear
// save "$datas/EH2025_Persona.dta", replace
// import spss using "$datas/EH2025_Discriminacion.sav", clear
// save "$datas/EH2025_Discriminacion.dta", replace
// import spss using "$datas/EH2025_Equipamiento.sav", clear
// save "$datas/EH2025_Equipamiento.dta", replace
// import spss using "$datas/EH2025_Gastos_Alimentarios.sav", clear
// save "$datas/EH2025_Gastos_Alimentarios.dta", replace
// import spss using "$datas/EH2025_Gastos_No_Alimentarios.sav", clear
// save "$datas/EH2025_Gastos_No_Alimentarios.dta", replace
// import spss using "$datas/EH2025_Persona.sav", clear
// save "$datas/EH2025_Persona.dta", replace
// import spss using "$datas/EH2025_Seguridad_Alimentaria.sav", clear
// save "$datas/EH2025_Seguridad_Alimentaria.dta", replace
// import spss using "$datas/EH2025_Vivienda_1.sav", clear
// save "$datas/EH2025_Vivienda_1.dta", replace

pwd 
dir "$datas/*.dta"

** upload dta format **
use "$datas/EH2025_Persona.dta", clear

