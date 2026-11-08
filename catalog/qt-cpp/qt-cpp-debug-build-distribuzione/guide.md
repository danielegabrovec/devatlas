## Debug del programma esatto
I file forniti costruiscono una finestra con pulsante Calcola e una funzione total separata. Prepara build/debug con il primo gruppo di comandi. In VS Code installa l'estensione C/C++, apri totals.cpp e metti un breakpoint nel ciclo che somma price. Seleziona Qt C++ MSVC Debug e premi F5. Premi Calcola: osserva prices, subtotal e il call stack dello slot.

## Build Release
Il secondo gruppo usa una directory distinta build/release: non mescola DLL Debug e Release. L'eseguibile viene copiato in dist e windeployqt raccoglie soltanto le dipendenze del runtime Qt richieste dal programma. Distribuisci tutta dist, inclusa la directory platforms. Il runtime del compilatore viene fornito con il redistributable Microsoft ufficiale, predisposto separatamente.

## Accettazione
Su un Windows x64 pulito avvia dist/{{project_name}}.exe e verifica il totale. Compilazione, raccolta DLL e prova sulla destinazione sono passaggi da eseguire: il catalogo non li dichiara già riusciti.