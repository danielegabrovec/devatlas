## Debug dei due lati IPC
Installa le dipendenze dalla cartella esportata. In VS Code usa Debug Electron main e imposta un breakpoint nel corpo di total in totals.cjs. Premi F5, poi Calcola nella finestra. Il percorso è renderer.js → API invoice del preload → handler invoice:total del main → totals.cjs. Il canale è fisso e il main verifica il frame chiamante. Per il renderer puoi aprire gli strumenti Chromium durante lo sviluppo; il debugger Node controlla invece il main.

## Build dell'app
npm run package crea una directory Windows x64 tramite electron-builder --dir. Non crea né pubblica un installer e non firma eseguibili. Distribuisci l'intera cartella win-unpacked generata sotto dist, non il solo file EXE: Chromium, Node, risorse e licenze fanno parte dell'app. Il manifest include esplicitamente il modulo totals.cjs richiamato dall'handler.

## Controllo finale
Avvia la cartella su un altro Windows x64 e premi Calcola: il risultato deve essere 19.75. L'esito di packaging e prova su macchina pulita non è attestato dal catalogo.