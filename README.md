# Connectathon-ObsGenTx
+ Generate Observation resources and transfer to the FHIR-server  
**2026-10-07**      
## Observation  
1. patient 4人  
2. date 3種類  2026-04-01, 2026-04-08, 2026-04-15
3. status 3種類  "final","preliminary","cancelled"
4. category/code 7種類  
   1. loinc: 8661-1 (主訴）
   2. loinc: 94500-6（COVID-19）
   3. IEEE: 131328（EKG）
   4. "loinc: 35094-2,  JP_Obs_VS_VS: blood-pressure (血圧)
   5. "IHE-hosp: IHE-local-379（体重）, JP_BM_CS: 31000296 
   6. "loinc: 78948-7, IHE-hosp: IHE-local-456, JP_SH_CS: MD0012920 (推奨)（喫煙指数）"
   7. "IHE-hosp: 05104,  JLAC10: 3C020000002327101 (推奨)（尿酸）"
5. 合計：  ２５２個のリソース (for 4 patients)  

## その他  
**Observation が、(resource id)参照しているもの**  
以下のファイルは、サーバーにPUT で 各リソースのIDをそのまま、サーバーに保存すること。
1. Patient resource  
2. Device resource  
3. Practitioner resource  
4. Specimen resource  
