"""C# desktop recipes: executable code-only UI applications."""
from __future__ import annotations
import json
from catalog_support import Book, STACKS
from desktop_tools_common import save_book

AVALONIA = [
("text", "Mostrare un testo con ritorno a capo", "Usare TextBlock per un messaggio adattabile alla larghezza.", 'panel.Children.Add(new TextBlock { Text="Testo lungo che può andare a capo senza tagli", TextWrapping=TextWrapping.Wrap });'),
("button", "Gestire il clic di un pulsante", "Collegare un evento e mantenere il contatore nella closure.", 'int count=0; var label=new TextBlock { Text="0" }; var button=new Button { Content="Incrementa" }; button.Click+=(_,_)=>label.Text=(++count).ToString(); panel.Children.Add(label); panel.Children.Add(button);'),
("textbox", "Osservare il testo digitato", "Usare TextChanged di TextBox per aggiornare un riepilogo.", 'var label=new TextBlock(); var edit=new TextBox { Watermark="Nome" }; edit.TextChanged+=(_,_)=>label.Text=$"Caratteri: {edit.Text?.Length ?? 0}"; panel.Children.Add(edit); panel.Children.Add(label);'),
("password", "Mascherare un campo password", "Configurare PasswordChar senza conservare la password su disco.", 'panel.Children.Add(new TextBox { Watermark="Password", PasswordChar=\'●\' });'),
("numeric", "Selezionare un valore numerico", "Configurare limiti e incremento di NumericUpDown.", 'panel.Children.Add(new NumericUpDown { Minimum=0, Maximum=100, Increment=5, Value=10 });'),
("combo", "Selezionare una voce da una combo", "Associare ItemsSource a un insieme di stringhe.", 'panel.Children.Add(new ComboBox { ItemsSource=new[]{"JSON","CSV","XML"}, SelectedIndex=0 });'),
("checkbox", "Attivare e disattivare un'opzione", "Leggere il valore nullable di IsChecked nell'evento.", 'var check=new CheckBox { Content="Mostra dettagli" }; var label=new TextBlock(); check.IsCheckedChanged+=(_,_)=>label.Text=check.IsChecked==true ? "Attivo" : "Inattivo"; panel.Children.Add(check); panel.Children.Add(label);'),
("radio", "Creare opzioni radio esclusive", "Usare GroupName per raggruppare pulsanti.", 'panel.Children.Add(new RadioButton { Content="Locale", GroupName="mode", IsChecked=true }); panel.Children.Add(new RadioButton { Content="Remoto", GroupName="mode" });'),
("slider", "Regolare una percentuale", "Aggiornare una label quando cambia il valore dello slider.", 'var label=new TextBlock(); var slider=new Slider { Minimum=0, Maximum=100, Value=25 }; slider.PropertyChanged+=(_,e)=>{if(e.Property==Slider.ValueProperty) label.Text=$"{slider.Value:F0}%";}; panel.Children.Add(slider); panel.Children.Add(label);'),
("progress", "Mostrare una percentuale di avanzamento", "Configurare un indicatore determinato.", 'panel.Children.Add(new ProgressBar { Minimum=0, Maximum=100, Value=65, Height=18 });'),
("busy", "Mostrare una durata sconosciuta", "Attivare la modalità indeterminata della progress bar.", 'panel.Children.Add(new ProgressBar { IsIndeterminate=true, Height=18 });'),
("calendar", "Selezionare una data", "Usare CalendarDatePicker con data iniziale.", 'panel.Children.Add(new CalendarDatePicker { SelectedDate=DateTime.Today });'),
("time", "Selezionare un orario", "Impostare TimePicker con formato a 24 ore.", 'panel.Children.Add(new TimePicker { SelectedTime=new TimeSpan(9,30,0), ClockIdentifier="24HourClock" });'),
("list", "Mostrare una lista selezionabile", "Collegare ItemsSource a ListBox e leggere SelectedItem.", 'var list=new ListBox { ItemsSource=new[]{"Qt","Avalonia","WinUI"} }; var label=new TextBlock(); list.SelectionChanged+=(_,_)=>label.Text=list.SelectedItem?.ToString(); panel.Children.Add(list); panel.Children.Add(label);'),
("observable", "Aggiornare una lista tramite collezione osservabile", "Aggiungere elementi senza ricreare la vista.", 'var rows=new ObservableCollection<string>{"Prima nota"}; var list=new ListBox{ItemsSource=rows}; var b=new Button{Content="Aggiungi"}; b.Click+=(_,_)=>rows.Add($"Nota {rows.Count+1}"); panel.Children.Add(list); panel.Children.Add(b);'),
("filter", "Filtrare un elenco in memoria", "Applicare un confronto OrdinalIgnoreCase sui dati originali.", 'var all=new[]{"Python","PySide6","Rust","PostgreSQL"}; var edit=new TextBox{Watermark="Cerca"}; var list=new ListBox{ItemsSource=all}; edit.TextChanged+=(_,_)=>list.ItemsSource=all.Where(x=>x.Contains(edit.Text ?? "",StringComparison.OrdinalIgnoreCase)).ToArray(); panel.Children.Add(edit); panel.Children.Add(list);'),
("grid", "Disporre controlli in due colonne", "Usare Grid.SetColumn per una struttura proporzionale.", 'var grid=new Grid{ColumnDefinitions=new ColumnDefinitions("Auto,*")}; var label=new TextBlock{Text="Nome",Margin=new Thickness(0,0,12,0)}; var edit=new TextBox(); Grid.SetColumn(edit,1); grid.Children.Add(label); grid.Children.Add(edit); panel.Children.Add(grid);'),
("dock", "Ancorare una barra al bordo superiore", "Usare DockPanel con ultimo figlio espanso.", 'var dock=new DockPanel{Height=220}; var bar=new TextBlock{Text="Barra superiore"}; DockPanel.SetDock(bar,Dock.Top); dock.Children.Add(bar); dock.Children.Add(new TextBox{AcceptsReturn=true,Text="Contenuto"}); panel.Children.Add(dock);'),
("wrap", "Disporre pulsanti su più righe", "Usare WrapPanel quando cambia la larghezza disponibile.", 'var wrap=new WrapPanel(); foreach(var name in new[]{"Inizializza","Compila","Debug","Esporta"}) wrap.Children.Add(new Button{Content=name,Margin=new Thickness(4)}); panel.Children.Add(wrap);'),
("scroll", "Scorrere un contenuto esteso", "Inserire una pila lunga dentro ScrollViewer.", 'var content=new StackPanel{Spacing=6}; for(int i=1;i<=40;i++) content.Children.Add(new TextBlock{Text=$"Riga {i}"}); panel.Children.Add(new ScrollViewer{Height=250,Content=content});'),
("tabs", "Dividere un'interfaccia in schede", "Creare TabItem con intestazione e contenuto indipendenti.", 'panel.Children.Add(new TabControl{ItemsSource=new[]{new TabItem{Header="Codice",Content=new TextBox{AcceptsReturn=true}},new TabItem{Header="Guida",Content=new TextBlock{Text="Passi operativi"}}}});'),
("expander", "Mostrare dettagli su richiesta", "Usare Expander per informazioni secondarie.", 'panel.Children.Add(new Expander{Header="Dettagli tecnici",Content=new TextBlock{Text="Runtime .NET e Avalonia Desktop"}});'),
("border", "Disegnare una scheda con bordo arrotondato", "Raggruppare contenuto con padding e sfondo.", 'panel.Children.Add(new Border{Background=Brushes.LightBlue,CornerRadius=new CornerRadius(12),Padding=new Thickness(18),Child=new TextBlock{Text="Scheda informativa"}});'),
("tooltip", "Associare una descrizione al controllo", "Usare la proprietà associata ToolTip.Tip.", 'var b=new Button{Content="Esporta"}; ToolTip.SetTip(b,"Crea una copia del documento"); panel.Children.Add(b);'),
("context-menu", "Aggiungere un menu contestuale", "Associare un ContextMenu alla casella testuale.", 'var edit=new TextBox{Text="Tasto destro"}; var item=new MenuItem{Header="Svuota"}; item.Click+=(_,_)=>edit.Text=""; edit.ContextMenu=new ContextMenu{ItemsSource=new[]{item}}; panel.Children.Add(edit);'),
("clipboard", "Copiare testo negli appunti", "Ottenere il clipboard dal TopLevel soltanto dopo il clic.", 'var edit=new TextBox{Text="Codice da copiare"}; var b=new Button{Content="Copia"}; b.Click+=async (_,_)=>{var clipboard=TopLevel.GetTopLevel(b)?.Clipboard; if(clipboard is not null) await clipboard.SetTextAsync(edit.Text ?? "");}; panel.Children.Add(edit); panel.Children.Add(b);'),
("theme", "Alternare tema chiaro e scuro", "Impostare RequestedThemeVariant a livello applicazione.", 'var b=new Button{Content="Tema scuro"}; b.Click+=(_,_)=>Application.Current!.RequestedThemeVariant=Avalonia.Styling.ThemeVariant.Dark; panel.Children.Add(b);'),
("timer", "Aggiornare un orologio nel thread UI", "Usare DispatcherTimer per evitare accessi UI dal thread errato.", 'var label=new TextBlock(); var timer=new DispatcherTimer{Interval=TimeSpan.FromSeconds(1)}; timer.Tick+=(_,_)=>label.Text=DateTime.Now.ToString("HH:mm:ss"); label.AttachedToVisualTree+=(_,_)=>timer.Start(); label.DetachedFromVisualTree+=(_,_)=>timer.Stop(); panel.Children.Add(label);'),
("delay", "Attendere senza bloccare la finestra", "Disabilitare il pulsante durante Task.Delay e ripristinarlo in finally.", 'var b=new Button{Content="Attendi"}; b.Click+=async (_,_)=>{b.IsEnabled=false; try{await Task.Delay(1000); b.Content="Pronto";}finally{b.IsEnabled=true;}}; panel.Children.Add(b);'),
("background", "Calcolare su un worker e tornare alla UI", "Usare Task.Run per un calcolo e await nel gestore evento.", 'var label=new TextBlock(); var b=new Button{Content="Somma quadrati"}; b.Click+=async (_,_)=>{b.IsEnabled=false; try{long result=await Task.Run(()=>Enumerable.Range(0,10000).Sum(x=>(long)x*x)); label.Text=result.ToString();}finally{b.IsEnabled=true;}}; panel.Children.Add(b); panel.Children.Add(label);'),
("json", "Salvare impostazioni JSON nella cartella utente", "Creare una directory dedicata prima della scrittura asincrona.", 'var b=new Button{Content="Salva preferenze"}; var label=new TextBlock(); b.Click+=async (_,_)=>{try{var dir=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"AvaloniaRecipe"); Directory.CreateDirectory(dir); var path=Path.Combine(dir,"settings.json"); await File.WriteAllTextAsync(path,JsonSerializer.Serialize(new { theme="dark",zoom=110})); label.Text=path;}catch(Exception ex){label.Text=ex.Message;}}; panel.Children.Add(b); panel.Children.Add(label);'),
("validation", "Segnalare un input non numerico", "Validare il testo senza lanciare eccezioni per un input incompleto.", 'var edit=new TextBox{Watermark="Numero intero"}; var label=new TextBlock(); edit.TextChanged+=(_,_)=>label.Text=int.TryParse(edit.Text,out int number) ? $"Valore: {number}" : "Inserisci un intero valido"; panel.Children.Add(edit); panel.Children.Add(label);'),
("focus", "Portare il focus su un campo dopo il caricamento", "Inviare Focus al dispatcher quando il controllo è nell'albero visivo.", 'var edit=new TextBox{Watermark="Focus iniziale"}; edit.AttachedToVisualTree+=(_,_)=>Dispatcher.UIThread.Post(()=>edit.Focus()); panel.Children.Add(edit);'),
("visibility", "Mostrare o nascondere una zona dettagli", "Legare il comportamento di IsVisible a un controllo di scelta.", 'var details=new TextBlock{Text="Dettagli",IsVisible=false}; var check=new CheckBox{Content="Mostra dettagli"}; check.IsCheckedChanged+=(_,_)=>details.IsVisible=check.IsChecked==true; panel.Children.Add(check); panel.Children.Add(details);'),
]

MAUI = [
("label", "Mostrare un'etichetta con stile", "Configurare dimensione e colore di Label.", 'panel.Children.Add(new Label{Text="Guida MAUI",FontSize=24,TextColor=Colors.DarkBlue});'),
("button", "Gestire un contatore al clic", "Aggiornare un Label da Button.Clicked.", 'int count=0; var label=new Label{Text="0"}; var b=new Button{Text="Incrementa"}; b.Clicked+=(_,_)=>label.Text=(++count).ToString(); panel.Children.Add(label); panel.Children.Add(b);'),
("entry", "Leggere un campo di input", "Osservare TextChanged di Entry.", 'var edit=new Entry{Placeholder="Nome"}; var label=new Label(); edit.TextChanged+=(_,e)=>label.Text=$"Caratteri: {e.NewTextValue?.Length ?? 0}"; panel.Children.Add(edit); panel.Children.Add(label);'),
("password", "Mascherare una password", "Usare IsPassword senza persistere il contenuto.", 'panel.Children.Add(new Entry{Placeholder="Password",IsPassword=true});'),
("editor", "Consentire l'inserimento di testo multilinea", "Configurare Editor con altezza richiesta.", 'panel.Children.Add(new Editor{Text="Prima riga\\nSeconda riga",HeightRequest=180,AutoSize=EditorAutoSizeOption.TextChanges});'),
("search", "Filtrare stringhe con SearchBar", "Aggiornare una CollectionView con i risultati della ricerca.", 'var all=new[]{"Python","PySide6","Rust","PostgreSQL"}; var search=new SearchBar{Placeholder="Cerca"}; var list=new CollectionView{ItemsSource=all,HeightRequest=160}; search.TextChanged+=(_,e)=>list.ItemsSource=all.Where(x=>x.Contains(e.NewTextValue ?? "",StringComparison.OrdinalIgnoreCase)).ToArray(); panel.Children.Add(search); panel.Children.Add(list);'),
("checkbox", "Gestire una casella di controllo", "Aggiornare lo stato tramite CheckedChanged.", 'var check=new CheckBox(); var label=new Label{Text="Disattivo"}; check.CheckedChanged+=(_,e)=>label.Text=e.Value?"Attivo":"Disattivo"; panel.Children.Add(check); panel.Children.Add(label);'),
("switch", "Usare un interruttore di preferenza", "Ricevere il valore booleano di Toggled.", 'var toggle=new Switch(); var label=new Label(); toggle.Toggled+=(_,e)=>label.Text=$"Notifiche: {e.Value}"; panel.Children.Add(toggle); panel.Children.Add(label);'),
("slider", "Controllare una percentuale", "Usare Minimum, Maximum e ValueChanged.", 'var slider=new Slider{Minimum=0,Maximum=100,Value=25}; var label=new Label(); slider.ValueChanged+=(_,e)=>label.Text=$"{e.NewValue:F0}%"; panel.Children.Add(slider); panel.Children.Add(label);'),
("stepper", "Incrementare una quantità a passi", "Configurare Stepper con incremento e limiti.", 'var stepper=new Stepper{Minimum=0,Maximum=50,Increment=5}; var label=new Label{Text="0"}; stepper.ValueChanged+=(_,e)=>label.Text=e.NewValue.ToString(); panel.Children.Add(stepper); panel.Children.Add(label);'),
("picker", "Scegliere un formato da Picker", "Impostare ItemsSource e SelectedIndex.", 'panel.Children.Add(new Picker{Title="Formato",ItemsSource=new[]{"JSON","CSV","XML"},SelectedIndex=0});'),
("date", "Selezionare un giorno", "Limitare un DatePicker al mese successivo.", 'panel.Children.Add(new DatePicker{Date=DateTime.Today,MinimumDate=DateTime.Today,MaximumDate=DateTime.Today.AddMonths(1),Format="dd/MM/yyyy"});'),
("time", "Selezionare un orario", "Configurare TimePicker in formato 24 ore.", 'panel.Children.Add(new TimePicker{Time=new TimeSpan(9,30,0),Format="HH:mm"});'),
("progress", "Mostrare avanzamento determinato", "Configurare ProgressBar usando valori tra zero e uno.", 'panel.Children.Add(new ProgressBar{Progress=0.65,ProgressColor=Colors.SteelBlue});'),
("activity", "Mostrare un'attività indeterminata", "Attivare ActivityIndicator per un lavoro senza percentuale.", 'panel.Children.Add(new ActivityIndicator{IsRunning=true,Color=Colors.SteelBlue});'),
("grid", "Creare una riga con etichetta e campo", "Usare due colonne Grid Auto e Star.", 'var grid=new Grid{ColumnDefinitions={new ColumnDefinition{Width=GridLength.Auto},new ColumnDefinition{Width=GridLength.Star}},ColumnSpacing=12}; var label=new Label{Text="Nome"}; var edit=new Entry(); grid.Add(label,0,0); grid.Add(edit,1,0); panel.Children.Add(grid);'),
("horizontal", "Disporre azioni su una riga", "Usare HorizontalStackLayout con spaziatura.", 'var row=new HorizontalStackLayout{Spacing=12}; row.Children.Add(new Button{Text="Salva"}); row.Children.Add(new Button{Text="Annulla"}); panel.Children.Add(row);'),
("border", "Creare una scheda con sfondo", "Usare Border al posto di Frame per il contenuto.", 'panel.Children.Add(new Border{Padding=20,Stroke=Colors.SteelBlue,Background=Colors.AliceBlue,Content=new Label{Text="Scheda informativa"}});'),
("collection", "Aggiornare una CollectionView osservabile", "Associare una ObservableCollection alla vista.", 'var rows=new ObservableCollection<string>{"Prima nota"}; var view=new CollectionView{ItemsSource=rows,HeightRequest=160}; var b=new Button{Text="Aggiungi"}; b.Clicked+=(_,_)=>rows.Add($"Nota {rows.Count+1}"); panel.Children.Add(view); panel.Children.Add(b);'),
("selection", "Leggere la selezione di CollectionView", "Abilitare la selezione singola e gestire SelectionChanged.", 'var list=new CollectionView{ItemsSource=new[]{"A","B","C"},SelectionMode=SelectionMode.Single,HeightRequest=150}; var label=new Label(); list.SelectionChanged+=(_,e)=>label.Text=e.CurrentSelection.FirstOrDefault()?.ToString(); panel.Children.Add(list); panel.Children.Add(label);'),
("alert", "Mostrare un messaggio asincrono", "Usare DisplayAlertAsync nell'handler di un pulsante.", 'var b=new Button{Text="Informazioni"}; b.Clicked+=async (_,_)=>await DisplayAlertAsync("Informazioni","Operazione locale completata","OK"); panel.Children.Add(b);'),
("confirm", "Richiedere conferma prima di svuotare", "Usare la risposta boolean di DisplayAlertAsync.", 'var edit=new Entry{Text="Dato"}; var b=new Button{Text="Svuota"}; b.Clicked+=async (_,_)=>{if(await DisplayAlertAsync("Conferma","Svuotare il campo?","Sì","No")) edit.Text="";}; panel.Children.Add(edit); panel.Children.Add(b);'),
("clipboard", "Copiare una stringa negli appunti", "Chiamare Clipboard.Default in risposta a un gesto utente.", 'var b=new Button{Text="Copia"}; b.Clicked+=async (_,_)=>await Clipboard.Default.SetTextAsync("Testo MAUI"); panel.Children.Add(b);'),
("preferences", "Ricordare una preferenza locale", "Usare Preferences.Default per un valore semplice.", 'var toggle=new Switch{IsToggled=Preferences.Default.Get("details",false)}; toggle.Toggled+=(_,e)=>Preferences.Default.Set("details",e.Value); panel.Children.Add(toggle);'),
("appdata", "Salvare un file nell'area dati dell'app", "Usare FileSystem.AppDataDirectory senza presumere percorsi Windows.", 'var label=new Label(); var b=new Button{Text="Salva appunto"}; b.Clicked+=async (_,_)=>{try{var path=Path.Combine(FileSystem.AppDataDirectory,"note.txt"); await File.WriteAllTextAsync(path,"Nota UTF-8"); label.Text=path;}catch(Exception ex){label.Text=ex.Message;}}; panel.Children.Add(b); panel.Children.Add(label);'),
("delay", "Attendere senza congelare la UI", "Disabilitare e ripristinare il pulsante durante un await.", 'var b=new Button{Text="Attendi"}; b.Clicked+=async (_,_)=>{b.IsEnabled=false; try{await Task.Delay(1000); b.Text="Pronto";}finally{b.IsEnabled=true;}}; panel.Children.Add(b);'),
("background", "Aggiornare la UI dopo un calcolo parallelo", "Usare Task.Run per un calcolo puro e await per tornare alla UI.", 'var label=new Label(); var b=new Button{Text="Calcola"}; b.Clicked+=async (_,_)=>{long value=await Task.Run(()=>Enumerable.Range(0,10000).Sum(i=>(long)i*i)); label.Text=value.ToString();}; panel.Children.Add(b); panel.Children.Add(label);'),
("visibility", "Alternare la visibilità dei dettagli", "Collegare un Switch alla proprietà IsVisible.", 'var label=new Label{Text="Dettagli aggiuntivi",IsVisible=false}; var toggle=new Switch(); toggle.Toggled+=(_,e)=>label.IsVisible=e.Value; panel.Children.Add(toggle); panel.Children.Add(label);'),
("semantic", "Descrivere un'azione agli strumenti di accessibilità", "Assegnare Description e Hint semantici.", 'var b=new Button{Text="?"}; SemanticProperties.SetDescription(b,"Apri guida"); SemanticProperties.SetHint(b,"Mostra le istruzioni dell\'applicazione"); panel.Children.Add(b);'),
]

WINUI = [
("text", "Mostrare testo con ritorno a capo", "Usare TextBlock e TextWrapping.Wrap.", 'panel.Children.Add(new TextBlock{Text="Messaggio leggibile nella finestra",TextWrapping=TextWrapping.Wrap,FontSize=22});'),
("button", "Gestire un contatore al clic", "Connettere Click a un gestore con stato locale.", 'int count=0; var label=new TextBlock{Text="0"}; var b=new Button{Content="Incrementa"}; b.Click+=(_,_)=>label.Text=(++count).ToString(); panel.Children.Add(label); panel.Children.Add(b);'),
("textbox", "Osservare un campo di testo", "Ricevere TextChanged e aggiornare un riepilogo.", 'var edit=new TextBox{PlaceholderText="Nome"}; var label=new TextBlock(); edit.TextChanged+=(_,_)=>label.Text=$"Caratteri: {edit.Text.Length}"; panel.Children.Add(edit); panel.Children.Add(label);'),
("password", "Inserire una password con controllo dedicato", "Usare PasswordBox senza registrare il contenuto.", 'panel.Children.Add(new PasswordBox{PlaceholderText="Password"});'),
("number", "Accettare un numero con limiti", "Configurare NumberBox con validazione numerica.", 'panel.Children.Add(new NumberBox{Header="Quantità",Minimum=0,Maximum=100,Value=10,SpinButtonPlacementMode=NumberBoxSpinButtonPlacementMode.Inline});'),
("combo", "Scegliere una voce da ComboBox", "Impostare ItemsSource e indice selezionato.", 'panel.Children.Add(new ComboBox{Header="Formato",ItemsSource=new[]{"JSON","CSV","XML"},SelectedIndex=0});'),
("check", "Gestire una casella di controllo", "Usare Checked e Unchecked per aggiornare una label.", 'var check=new CheckBox{Content="Dettagli"}; var label=new TextBlock(); check.Checked+=(_,_)=>label.Text="Attivo"; check.Unchecked+=(_,_)=>label.Text="Inattivo"; panel.Children.Add(check); panel.Children.Add(label);'),
("toggle", "Inserire un interruttore di preferenza", "Usare ToggleSwitch con OnContent e OffContent.", 'panel.Children.Add(new ToggleSwitch{Header="Notifiche",OnContent="Attive",OffContent="Disattive"});'),
("radio", "Creare scelte radio esclusive", "Usare GroupName per isolare il gruppo.", 'panel.Children.Add(new RadioButton{Content="Locale",GroupName="mode",IsChecked=true}); panel.Children.Add(new RadioButton{Content="Remoto",GroupName="mode"});'),
("slider", "Selezionare una percentuale", "Configurare Slider con tick e valore iniziale.", 'panel.Children.Add(new Slider{Header="Zoom",Minimum=50,Maximum=200,StepFrequency=10,Value=100});'),
("progress", "Mostrare progresso determinato", "Impostare valore e massimo in ProgressBar.", 'panel.Children.Add(new ProgressBar{Minimum=0,Maximum=100,Value=70,Height=16});'),
("ring", "Mostrare un'attività senza percentuale", "Usare ProgressRing attivo durante l'attesa.", 'panel.Children.Add(new ProgressRing{IsActive=true,Width=40,Height=40});'),
("date", "Selezionare una data con popup", "Usare CalendarDatePicker per un valore DateTimeOffset.", 'panel.Children.Add(new CalendarDatePicker{Date=DateTimeOffset.Now,PlaceholderText="Scegli data"});'),
("time", "Selezionare un orario a 24 ore", "Configurare TimePicker.", 'panel.Children.Add(new TimePicker{Time=new TimeSpan(9,30,0),ClockIdentifier="24HourClock"});'),
("list", "Mostrare una lista selezionabile", "Assegnare un elenco a ListView.", 'panel.Children.Add(new ListView{ItemsSource=new[]{"Qt","Avalonia","WinUI"},SelectionMode=ListViewSelectionMode.Single});'),
("observable", "Aggiornare un elenco osservabile", "Associare ObservableCollection a ListView.", 'var rows=new ObservableCollection<string>{"Prima nota"}; var list=new ListView{ItemsSource=rows}; var b=new Button{Content="Aggiungi"}; b.Click+=(_,_)=>rows.Add($"Nota {rows.Count+1}"); panel.Children.Add(list); panel.Children.Add(b);'),
("search", "Filtrare suggerimenti di ricerca", "Usare AutoSuggestBox.TextChanged controllando il motivo della modifica.", 'var all=new[]{"Python","PySide6","PostgreSQL","Rust"}; var search=new AutoSuggestBox{PlaceholderText="Cerca"}; search.TextChanged+=(sender,e)=>{if(e.Reason==AutoSuggestionBoxTextChangeReason.UserInput) sender.ItemsSource=all.Where(x=>x.Contains(sender.Text,StringComparison.OrdinalIgnoreCase)).ToArray();}; panel.Children.Add(search);'),
("grid", "Disporre un'etichetta e un campo su due colonne", "Usare Grid.Column con unità Auto e Star.", 'var grid=new Grid{ColumnSpacing=12}; grid.ColumnDefinitions.Add(new ColumnDefinition{Width=GridLength.Auto}); grid.ColumnDefinitions.Add(new ColumnDefinition{Width=new GridLength(1,GridUnitType.Star)}); var label=new TextBlock{Text="Nome"}; var edit=new TextBox(); Grid.SetColumn(edit,1); grid.Children.Add(label); grid.Children.Add(edit); panel.Children.Add(grid);'),
("expander", "Espandere dettagli secondari", "Raggruppare testo sotto un'intestazione richiudibile.", 'panel.Children.Add(new Expander{Header="Dettagli",Content=new TextBlock{Text="Informazioni tecniche"}});'),
("tooltip", "Aggiungere un suggerimento a un pulsante", "Usare ToolTipService.ToolTip.", 'var b=new Button{Content="Esporta"}; ToolTipService.SetToolTip(b,"Crea una copia locale del documento"); panel.Children.Add(b);'),
("dialog", "Aprire un ContentDialog con XamlRoot", "Assegnare XamlRoot prima di ShowAsync.", 'var b=new Button{Content="Informazioni"}; b.Click+=async (_,_)=>{var dialog=new ContentDialog{Title="Informazioni",Content="Operazione locale completata",CloseButtonText="OK",XamlRoot=panel.XamlRoot}; await dialog.ShowAsync();}; panel.Children.Add(b);'),
("infobar", "Mostrare un messaggio non modale", "Usare InfoBar per notifiche integrate nella pagina.", 'panel.Children.Add(new InfoBar{IsOpen=true,Severity=InfoBarSeverity.Success,Title="Pronto",Message="Catalogo caricato",IsClosable=true});'),
("theme", "Cambiare tema della pagina", "Impostare RequestedTheme sul contenitore principale.", 'var b=new Button{Content="Tema scuro"}; b.Click+=(_,_)=>panel.RequestedTheme=ElementTheme.Dark; panel.Children.Add(b);'),
("delay", "Eseguire un'attesa asincrona nel gestore evento", "Ripristinare IsEnabled in finally.", 'var b=new Button{Content="Attendi"}; b.Click+=async (_,_)=>{b.IsEnabled=false; try{await Task.Delay(1000); b.Content="Pronto";}finally{b.IsEnabled=true;}}; panel.Children.Add(b);'),
]

AVALONIA_HEAD = '''using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.ObjectModel;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Themes.Fluent;
using Avalonia.Threading;
namespace RecipeApp;
class Program { [STAThread] public static void Main(string[] args)=>AppBuilder.Configure<App>().UsePlatformDetect().StartWithClassicDesktopLifetime(args); }
class App:Application {
 public override void Initialize(){Styles.Add(new FluentTheme());}
 public override void OnFrameworkInitializationCompleted(){if(ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop) desktop.MainWindow=new MainWindow(); base.OnFrameworkInitializationCompleted();}
}
class MainWindow:Window {
 public MainWindow(){Title="Ricetta Avalonia";Width=760;Height=520; var panel=new StackPanel{Spacing=12,Margin=new Thickness(20)};
'''
MAUI_HEAD = '''using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.ObjectModel;
using Microsoft.Maui.Controls;
using Microsoft.Maui.Graphics;
using Microsoft.Maui.ApplicationModel.DataTransfer;
using Microsoft.Maui.Storage;
namespace RecipeApp;
public class MainPage:ContentPage {
 public MainPage(){ Title="Ricetta MAUI"; var panel=new VerticalStackLayout{Spacing=12,Padding=20};
'''
WIN_HEAD = '''using System;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.ObjectModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
namespace RecipeApp;
public class MainWindow:Window {
 public MainWindow(){Title="Ricetta WinUI"; var panel=new StackPanel{Spacing=12,Margin=new Thickness(20)};
'''

def avalonia_files(body):
    return {"RecipeApp.csproj": '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>WinExe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>enable</Nullable><ImplicitUsings>enable</ImplicitUsings></PropertyGroup><ItemGroup><PackageReference Include="Avalonia.Desktop" Version="11.3.0"/><PackageReference Include="Avalonia.Themes.Fluent" Version="11.3.0"/></ItemGroup></Project>\n', "Program.cs": AVALONIA_HEAD+body+'\n Content=new ScrollViewer{Content=panel}; }\n}\n'}

def maui_files(body):
    return {"RecipeApp.csproj": '''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0-windows10.0.19041.0</TargetFramework><OutputType>Exe</OutputType><RootNamespace>RecipeApp</RootNamespace><UseMaui>true</UseMaui><SingleProject>true</SingleProject><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><ApplicationTitle>RecipeApp</ApplicationTitle><ApplicationId>it.ricettario.recipeapp</ApplicationId><ApplicationDisplayVersion>1.0</ApplicationDisplayVersion><ApplicationVersion>1</ApplicationVersion><SupportedOSPlatformVersion>10.0.17763.0</SupportedOSPlatformVersion><TargetPlatformMinVersion>10.0.17763.0</TargetPlatformMinVersion><WindowsPackageType>None</WindowsPackageType></PropertyGroup><ItemGroup><PackageReference Include="Microsoft.Maui.Controls" Version="10.0.31"/></ItemGroup></Project>\n''', "MainPage.cs": MAUI_HEAD+body+'\n Content=new ScrollView{Content=panel}; }\n}\n', "App.cs": 'using Microsoft.Maui;\nusing Microsoft.Maui.Controls;\nnamespace RecipeApp;\npublic class App:Application { protected override Window CreateWindow(IActivationState? state)=>new Window(new MainPage()); }\n', "MauiProgram.cs": 'using Microsoft.Maui.Hosting;\nnamespace RecipeApp;\npublic static class MauiProgram { public static MauiApp CreateMauiApp()=>MauiApp.CreateBuilder().UseMauiApp<App>().Build(); }\n', "Platforms/Windows/App.xaml": '<maui:MauiWinUIApplication x:Class="RecipeApp.WinUI.App" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns:maui="using:Microsoft.Maui"/>\n', "Platforms/Windows/App.xaml.cs": 'using Microsoft.Maui;\nusing Microsoft.Maui.Hosting;\nnamespace RecipeApp.WinUI;\npublic partial class App:MauiWinUIApplication { public App(){InitializeComponent();} protected override MauiApp CreateMauiApp()=>MauiProgram.CreateMauiApp(); }\n'}

def winui_files(body):
    return {"RecipeApp.csproj": '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>WinExe</OutputType><TargetFramework>net8.0-windows10.0.19041.0</TargetFramework><TargetPlatformMinVersion>10.0.17763.0</TargetPlatformMinVersion><UseWinUI>true</UseWinUI><Nullable>enable</Nullable><ImplicitUsings>enable</ImplicitUsings><WindowsPackageType>None</WindowsPackageType><RuntimeIdentifier>win-x64</RuntimeIdentifier><WindowsAppSDKSelfContained>true</WindowsAppSDKSelfContained></PropertyGroup><ItemGroup><PackageReference Include="Microsoft.WindowsAppSDK" Version="1.8.260921001"/></ItemGroup></Project>\n', "MainWindow.cs": WIN_HEAD+body+'\n Content=panel; }\n}\n', "App.xaml": '<Application x:Class="RecipeApp.App" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"><Application.Resources><ResourceDictionary><ResourceDictionary.MergedDictionaries><XamlControlsResources xmlns="using:Microsoft.UI.Xaml.Controls"/></ResourceDictionary.MergedDictionaries></ResourceDictionary></Application.Resources></Application>\n', "App.xaml.cs": 'using Microsoft.UI.Xaml;\nnamespace RecipeApp;\npublic partial class App:Application { private Window? window; public App(){InitializeComponent();} protected override void OnLaunched(LaunchActivatedEventArgs args){window=new MainWindow();window.Activate();} }\n'}

def build_all():
    assert len(AVALONIA)==34, len(AVALONIA)
    assert len(MAUI)==29, len(MAUI)
    assert len(WINUI)==24, len(WINUI)
    configs = [("avalonia",AVALONIA,avalonia_files,".NET 8; Avalonia 11.3.0",["https://docs.avaloniaui.net/docs/get-started","https://docs.avaloniaui.net/docs/reference/controls/"],".NET 8 SDK e runtime desktop del proprio sistema; nessun template richiesto.","dotnet restore\ndotnet run",["Windows","Linux","macOS"]), ("maui",MAUI,maui_files,".NET 10; MAUI Controls 10.0.31; destinazione Windows",["https://learn.microsoft.com/dotnet/maui/get-started/first-app","https://learn.microsoft.com/dotnet/maui/user-interface/controls/"],"Windows 10 build 19041+; .NET 10 SDK con workload MAUI Windows installato; Visual Studio 2026 con MAUI. Non occorrono Android o un Mac per questo esempio Windows.","dotnet restore\ndotnet build -f net10.0-windows10.0.19041.0\ndotnet run -f net10.0-windows10.0.19041.0",["Windows"]), ("winui",WINUI,winui_files,"C# .NET 8; WinUI 3 Windows App SDK 1.8.12",["https://learn.microsoft.com/windows/apps/winui/winui3/get-started-winui3-for-desktop","https://learn.microsoft.com/windows/apps/windows-app-sdk/downloads-archive"],"Windows 10 build 19041+; .NET 8 SDK, Windows SDK e workload WinUI in Visual Studio. Questa è una baseline compatibile Windows App SDK 1.8.12, non la versione più recente.","dotnet restore\ndotnet build -p:Platform=x64\ndotnet run -p:Platform=x64",["Windows"])]
    for stack,topics,files_fn,version,sources,prereq,commands,oses in configs:
        book=Book(stack,version,sources,prereq,os=oses,ide=["Visual Studio","Rider","VS Code"])
        for key,title,description,body in topics:
            book.add(key,title,description,files_fn(body),commands=commands,explanation=f"## Obiettivo\n{description}\n\n## Collocazione\nSalva tutti i file esportati mantenendo i percorsi indicati. Il file .csproj è nella cartella di lavoro dei comandi; non incollare il contenuto in un diverso progetto che abbia già una classe App o MainWindow omonima. L'esempio costruisce la UI in C#, senza richiedere file XAML aggiuntivi oltre a quelli forniti.\n\n## Prova\nAvvia e usa il controllo descritto: {title.lower()}. Il codice specifico della ricetta è nel costruttore della pagina/finestra.\n\n## Compatibilità\n{prereq} Esecuzione non attestata: Android, iOS e macOS non vengono simulati né dichiarati verificati.",expected=description,tags=[key,"desktop","C#",stack],errors=["Restore fallito: verificare accesso a NuGet e SDK indicato dal progetto.","Classe duplicata: usare una cartella nuova invece di aggiungere i file a un template che contiene già App."])
        if stack=="avalonia":
            body='''var rows=new ObservableCollection<string>(); var edit=new TextBox{Watermark="Nota"}; var list=new ListBox{ItemsSource=rows}; var button=new Button{Content="Aggiungi"}; var status=new TextBlock();
var dir=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"RecipeAvaloniaNotes"); Directory.CreateDirectory(dir); var path=Path.Combine(dir,"notes.json");
try{if(File.Exists(path)){var saved=JsonSerializer.Deserialize<string[]>(File.ReadAllText(path)) ?? Array.Empty<string>(); foreach(var value in saved) rows.Add(value);}}catch(Exception ex){status.Text=ex.Message;}
button.Click+=async (_,_)=>{var text=edit.Text?.Trim(); if(string.IsNullOrEmpty(text)) return; button.IsEnabled=false; try{var next=rows.Append(text).ToArray(); var temp=path+".tmp"; await File.WriteAllTextAsync(temp,JsonSerializer.Serialize(next)); File.Move(temp,path,true); rows.Add(text); edit.Text=""; status.Text="Salvato";}catch(Exception ex){status.Text=ex.Message;}finally{button.IsEnabled=true;}};
panel.Children.Add(edit); panel.Children.Add(button); panel.Children.Add(list); panel.Children.Add(status);'''
        elif stack=="maui":
            body='''var rows=new ObservableCollection<string>(); var edit=new Entry{Placeholder="Nota"}; var list=new CollectionView{ItemsSource=rows,HeightRequest=220}; var button=new Button{Text="Aggiungi"}; var status=new Label();
var path=Path.Combine(FileSystem.AppDataDirectory,"notes.json");
try{if(File.Exists(path)){var saved=System.Text.Json.JsonSerializer.Deserialize<string[]>(File.ReadAllText(path)) ?? Array.Empty<string>(); foreach(var value in saved) rows.Add(value);}}catch(Exception ex){status.Text=ex.Message;}
button.Clicked+=async (_,_)=>{var text=edit.Text?.Trim(); if(string.IsNullOrEmpty(text)) return; button.IsEnabled=false; try{var next=rows.Append(text).ToArray(); var temp=path+".tmp"; await File.WriteAllTextAsync(temp,System.Text.Json.JsonSerializer.Serialize(next)); File.Move(temp,path,true); rows.Add(text); edit.Text=""; status.Text="Salvato";}catch(Exception ex){status.Text=ex.Message;}finally{button.IsEnabled=true;}};
panel.Children.Add(edit); panel.Children.Add(button); panel.Children.Add(list); panel.Children.Add(status);'''
        else:
            body='''var rows=new ObservableCollection<string>(); var edit=new TextBox{PlaceholderText="Nota"}; var list=new ListView{ItemsSource=rows}; var button=new Button{Content="Aggiungi"}; var status=new TextBlock();
var dir=System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"RecipeWinUINotes"); System.IO.Directory.CreateDirectory(dir); var path=System.IO.Path.Combine(dir,"notes.json");
try{if(System.IO.File.Exists(path)){var saved=System.Text.Json.JsonSerializer.Deserialize<string[]>(System.IO.File.ReadAllText(path)) ?? Array.Empty<string>(); foreach(var value in saved) rows.Add(value);}}catch(Exception ex){status.Text=ex.Message;}
button.Click+=async (_,_)=>{var text=edit.Text.Trim(); if(string.IsNullOrEmpty(text)) return; button.IsEnabled=false; try{var next=rows.Append(text).ToArray(); var temp=path+".tmp"; await System.IO.File.WriteAllTextAsync(temp,System.Text.Json.JsonSerializer.Serialize(next)); System.IO.File.Move(temp,path,true); rows.Add(text); edit.Text=""; status.Text="Salvato";}catch(Exception ex){status.Text=ex.Message;}finally{button.IsEnabled=true;}};
panel.Children.Add(edit); panel.Children.Add(button); panel.Children.Add(list); panel.Children.Add(status);'''
        files=files_fn(body)
        files["README.md"]="# Note locali\nAvvia il progetto con i comandi della ricetta. Aggiungi note, chiudi e riapri. Il file notes.json viene conservato nell'area dati utente e sostituito dopo scrittura completa.\n"
        book.add("progetto-note","Progetto completo: note locali con persistenza JSON","Una app desktop aggiunge note non vuote, le salva e le ricarica all'avvio.",files,project=True,section="Progetti completi",commands=commands,explanation="## Progetto completo\nMantieni tutti i file nelle directory indicate. Il pulsante è disabilitato durante il salvataggio per evitare scritture concorrenti. Il nuovo elemento entra nella collezione osservabile soltanto dopo la scrittura e sostituzione del JSON. Le eccezioni previste vengono mostrate nel pannello di stato.\n\n## Verifica manuale\nAggiungi due note, riavvia e controlla il ripristino. Invia un campo vuoto: non deve aggiungere elementi. Il progetto è documentato; build e avvio sul computer dell'autore non sono attestati.",expected="Le note vengono conservate fra due avvii nello spazio utente.",tags=["project","JSON","persistence","async"],errors=["La cartella dati utente deve essere scrivibile.","Un JSON malformato viene segnalato nello stato."])
        assert len(book.recipes)==STACKS[stack][2]
        save_book(book)

if __name__=="__main__":
    build_all()
