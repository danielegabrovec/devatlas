## Piano reale
Il laboratorio crea un indice stock e chiama explain executionStats. Esamina nReturned, totalDocsExamined e winningPlan nel formato restituito dal server. Tre documenti non rappresentano un benchmark; il planner può preferire una scansione.

## Limite
executionStats esegue davvero la lettura. Lo script usa solo dati sintetici in un database dal nome dedicato.