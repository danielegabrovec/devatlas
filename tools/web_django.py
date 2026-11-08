from catalog_support import Book
from web_support import add

SETTINGS="""from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY='solo-laboratorio-locale-non-usare-in-produzione'
DEBUG=True
ALLOWED_HOSTS=['127.0.0.1','localhost','testserver']
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','notes']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
USE_TZ=True
TIME_ZONE='Europe/Rome'
STATIC_URL='static/'
LOGIN_REDIRECT_URL='/'
"""
MODEL="""from django.db import models
class Note(models.Model):
    title=models.CharField(max_length=100)
    body=models.TextField(blank=True)
    done=models.BooleanField(default=False)
    priority=models.PositiveSmallIntegerField(default=1)
    created=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title
"""
MIGRATION="""from django.db import migrations,models
class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[migrations.CreateModel(name='Note',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('title',models.CharField(max_length=100)),('body',models.TextField(blank=True)),('done',models.BooleanField(default=False)),('priority',models.PositiveSmallIntegerField(default=1)),('created',models.DateTimeField(auto_now_add=True))])]
"""
BASE={
'manage.py':"import os,sys\nos.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
'config/__init__.py':'', 'config/settings.py':SETTINGS,
'config/urls.py':"from django.urls import path\nfrom notes import views\nurlpatterns=[path('',views.home,name='home')]\n",
'notes/__init__.py':'','notes/models.py':MODEL,
'notes/views.py':"from django.http import JsonResponse\nfrom .models import Note\ndef home(request): return JsonResponse({'items':list(Note.objects.values('id','title','done'))})\n",
'notes/migrations/__init__.py':'','notes/migrations/0001_initial.py':MIGRATION,
'seed.py':"from notes.models import Note\nNote.objects.all().delete()\nNote.objects.bulk_create([Note(title='Python',body='Leggere file',priority=2),Note(title='SQL',body='Unire tabelle',priority=3),Note(title='React',body='Gestire form',done=True)])\nprint('Creati3dati sintetici')\n",
'requirements.txt':'Django==5.2.6\n',
}
OPS=[
("Filtrare oggetti ORM per stato","from notes.models import Note\nprint(list(Note.objects.filter(done=False).values('title')))"),
("Cercare testo senza distinzione maiuscole","from notes.models import Note\nprint(list(Note.objects.filter(title__icontains='py').values_list('title',flat=True)))"),
("Combinare alternative con oggetti Q","from django.db.models import Q\nfrom notes.models import Note\nprint(list(Note.objects.filter(Q(priority__gte=3)|Q(done=True)).values('title')))"),
("Escludere righe da un queryset","from notes.models import Note\nprint(list(Note.objects.exclude(done=True).values('title')))"),
("Selezionare soltanto le colonne necessarie","from notes.models import Note\nprint(list(Note.objects.values('id','title')))"),
("Ordinare risultati per più campi","from notes.models import Note\nprint(list(Note.objects.order_by('-priority','id').values_list('title',flat=True)))"),
("Aggregare conteggi e priorità media","from django.db.models import Count,Avg\nfrom notes.models import Note\nprint(Note.objects.aggregate(total=Count('id'),mean=Avg('priority')))"),
("Raggruppare queryset con annotate","from django.db.models import Count\nfrom notes.models import Note\nprint(list(Note.objects.values('done').annotate(total=Count('id')).order_by('done')))"),
("Aggiornare valori atomicamente con F","from django.db.models import F\nfrom notes.models import Note\nNote.objects.filter(done=False).update(priority=F('priority')+1)\nprint(list(Note.objects.values('title','priority')))"),
("Creare o recuperare senza duplicare","from notes.models import Note\nnote,created=Note.objects.get_or_create(title='Nuova',defaults={'body':'Esempio'})\nprint(note.title,created)"),
("Eseguire inserimento batch con bulk_create","from notes.models import Note\nrows=Note.objects.bulk_create([Note(title='Go'),Note(title='Rust')])\nprint([x.title for x in rows])"),
("Rendere atomiche più modifiche ORM","from django.db import transaction\nfrom notes.models import Note\nwith transaction.atomic():\n    Note.objects.filter(title='Python').update(done=True)\n    Note.objects.create(title='Verifica completata')\nprint(Note.objects.count())"),
("Paginare queryset con Paginator","from django.core.paginator import Paginator\nfrom notes.models import Note\np=Paginator(Note.objects.order_by('id'),2)\npage=p.get_page(1)\nprint([x.title for x in page],page.has_next())"),
("Iterare grandi queryset a blocchi","from notes.models import Note\nfor note in Note.objects.order_by('id').iterator(chunk_size=100):\n    print(note.id,note.title)"),
("Verificare esistenza senza caricare oggetti","from notes.models import Note\nprint(Note.objects.filter(done=False).exists())"),
("Ispezionare SQL generato dal queryset","from notes.models import Note\nprint(Note.objects.filter(priority__gte=2).query)"),
]
VIEWS=[
("Restituire404 con get_object_or_404",{'notes/views.py':"from django.http import JsonResponse\nfrom django.shortcuts import get_object_or_404\nfrom .models import Note\ndef home(request):\n    note=get_object_or_404(Note,pk=request.GET.get('id',0))\n    return JsonResponse({'title':note.title})\n"}),
("Limitare una vista al metodo GET",{'notes/views.py':"from django.http import JsonResponse\nfrom django.views.decorators.http import require_GET\n@require_GET\ndef home(request): return JsonResponse({'ok':True})\n"}),
("Validare input usando Django Forms",{'notes/forms.py':"from django import forms\nclass SearchForm(forms.Form):\n    q=forms.CharField(min_length=2,max_length=50)\n",'notes/views.py':"from django.http import JsonResponse\nfrom .forms import SearchForm\ndef home(request):\n    form=SearchForm(request.GET)\n    if not form.is_valid(): return JsonResponse({'errors':form.errors.get_json_data()},status=400)\n    return JsonResponse(form.cleaned_data)\n"}),
("Normalizzare un campo con clean",{'notes/forms.py':"from django import forms\nclass NameForm(forms.Form):\n    name=forms.CharField()\n    def clean_name(self):\n        value=self.cleaned_data['name'].strip()\n        if len(value)<3: raise forms.ValidationError('Almeno3caratteri')\n        return value\n",'notes/views.py':"from django.http import JsonResponse\nfrom .forms import NameForm\ndef home(request):\n    f=NameForm(request.GET)\n    return JsonResponse(f.cleaned_data if f.is_valid() else {'errors':f.errors.get_json_data()})\n"}),
("Renderizzare un template con autoescape",{'notes/views.py':"from django.shortcuts import render\ndef home(request): return render(request,'hello.html',{'name':request.GET.get('name','Ada')})\n",'templates/hello.html':'<!doctype html><html lang="it"><title>Saluto</title><h1>Ciao {{ name }}</h1></html>'}),
("Elencare oggetti con template for empty",{'notes/views.py':"from django.shortcuts import render\nfrom .models import Note\ndef home(request): return render(request,'list.html',{'notes':Note.objects.order_by('id')})\n",'templates/list.html':'<!doctype html><html lang="it"><title>Note</title><ul>{% for note in notes %}<li>{{ note.title }}</li>{% empty %}<li>Nessuna nota</li>{% endfor %}</ul></html>'}),
("Comporre template con ereditarietà",{'notes/views.py':"from django.shortcuts import render\ndef home(request): return render(request,'page.html')\n",'templates/base.html':'<!doctype html><html lang="it"><title>{% block title %}Atlante{% endblock %}</title><main>{% block content %}{% endblock %}</main></html>','templates/page.html':'{% extends "base.html" %}{% block title %}Guida{% endblock %}{% block content %}<h1>Guida</h1>{% endblock %}'}),
("Inviare ModelForm con protezione CSRF",{'notes/forms.py':"from django.forms import ModelForm\nfrom .models import Note\nclass NoteForm(ModelForm):\n    class Meta:\n        model=Note\n        fields=['title','body']\n",'notes/views.py':"from django.shortcuts import render,redirect\nfrom .forms import NoteForm\ndef home(request):\n    f=NoteForm(request.POST or None)\n    if request.method=='POST' and f.is_valid():\n        f.save()\n        return redirect('home')\n    return render(request,'form.html',{'form':f})\n",'templates/form.html':'<!doctype html><html lang="it"><title>Nuova nota</title><form method="post">{% csrf_token %}{{ form.as_p }}<button>Salva</button></form></html>'}),
("Memorizzare una preferenza in sessione",{'notes/views.py':"from django.http import JsonResponse\ndef home(request):\n    request.session['visits']=request.session.get('visits',0)+1\n    return JsonResponse({'visits':request.session['visits']})\n"}),
("Aggiungere messaggi dopo redirect",{'notes/views.py':"from django.contrib import messages\nfrom django.shortcuts import render,redirect\ndef home(request):\n    if request.method=='POST':\n        messages.success(request,'Operazione completata')\n        return redirect('home')\n    return render(request,'messages.html')\n",'templates/messages.html':'<!doctype html><html lang="it"><title>Messaggi</title>{% for message in messages %}<p role="status">{{ message }}</p>{% endfor %}<form method="post">{% csrf_token %}<button>Conferma</button></form></html>'}),
("Applicare cache temporale alla vista",{'notes/views.py':"from django.http import JsonResponse\nfrom django.views.decorators.cache import cache_page\nfrom django.utils import timezone\n@cache_page(30)\ndef home(request): return JsonResponse({'generated':timezone.now().isoformat()})\n"}),
("Restituire un download CSV",{'notes/views.py':"import csv\nfrom django.http import HttpResponse\nfrom .models import Note\ndef home(request):\n    r=HttpResponse(content_type='text/csv')\n    r['Content-Disposition']='attachment; filename=notes.csv'\n    w=csv.writer(r)\n    w.writerow(['id','title','done'])\n    for row in Note.objects.values_list('id','title','done'): w.writerow(row)\n    return r\n"}),
("Registrare un ModelAdmin con ricerca",{'notes/admin.py':"from django.contrib import admin\nfrom .models import Note\n@admin.register(Note)\nclass NoteAdmin(admin.ModelAdmin):\n    list_display=['title','done','priority']\n    search_fields=['title','body']\n    list_filter=['done']\n",'config/urls.py':"from django.urls import path\nfrom django.contrib import admin\nurlpatterns=[path('admin/',admin.site.urls)]\n"}),
("Definire ListView con paginazione",{'notes/views.py':"from django.views.generic import ListView\nfrom .models import Note\nclass Notes(ListView):\n    model=Note\n    paginate_by=2\n    ordering='id'\n    template_name='notes.html'\nhome=Notes.as_view()\n",'templates/notes.html':'<!doctype html><html lang="it"><title>Note</title><ul>{% for n in object_list %}<li>{{ n.title }}</li>{% endfor %}</ul>{% if page_obj.has_next %}<a href="?page={{ page_obj.next_page_number }}">Successiva</a>{% endif %}</html>'}),
("Proteggere una vista con login_required",{'notes/views.py':"from django.contrib.auth.decorators import login_required\nfrom django.http import JsonResponse\n@login_required\ndef home(request): return JsonResponse({'username':request.user.username})\n",'config/urls.py':"from django.urls import path,include\nfrom notes import views\nurlpatterns=[path('',views.home,name='home'),path('accounts/',include('django.contrib.auth.urls'))]\n",'templates/registration/login.html':'<!doctype html><html lang="it"><title>Login</title><form method="post">{% csrf_token %}{{ form.as_p }}<button>Accedi</button></form></html>'}),
("Testare una vista con TestCase",{'notes/tests.py':"from django.test import TestCase\nfrom .models import Note\nclass ViewTests(TestCase):\n    def test_list(self):\n        Note.objects.create(title='Prova')\n        response=self.client.get('/')\n        self.assertEqual(response.status_code,200)\n        self.assertEqual(response.json()['items'][0]['title'],'Prova')\n"}),
("Testare un form invalido",{'notes/forms.py':"from django import forms\nclass NoteForm(forms.Form):\n    title=forms.CharField(min_length=3)\n",'notes/tests.py':"from django.test import SimpleTestCase\nfrom .forms import NoteForm\nclass FormTests(SimpleTestCase):\n    def test_short(self):\n        self.assertFalse(NoteForm({'title':'x'}).is_valid())\n    def test_ok(self):\n        self.assertTrue(NoteForm({'title':'Python'}).is_valid())\n"}),
("Aggiungere un comando management personalizzato",{'notes/management/__init__.py':'','notes/management/commands/__init__.py':'','notes/management/commands/countnotes.py':"from django.core.management.base import BaseCommand\nfrom notes.models import Note\nclass Command(BaseCommand):\n    help='Conta note incomplete'\n    def handle(self,*args,**options):\n        self.stdout.write(str(Note.objects.filter(done=False).count()))\n"}),
]

CMD='python -m venv .venv\n.venv\\Scripts\\python -m pip install -r requirements.txt\n.venv\\Scripts\\python manage.py migrate\n.venv\\Scripts\\python manage.py shell -c "exec(open(\'seed.py\',encoding=\'utf8\').read())"'

def build_all():
    b=Book('django','Django5.2.6 LTS; Python3.11+',['https://docs.djangoproject.com/en/5.2/'],'Python3.11+ e venv. SQLite incluso in Python. DEBUG e SECRET_KEY sono solo per localhost; non pubblicare queste impostazioni. Porta8000 libera.')
    for title,code in OPS:
        f={**BASE,'operation.py':code}
        add(b,title,f,commands=CMD+'\n.venv\\Scripts\\python manage.py shell -c "exec(open(\'operation.py\',encoding=\'utf8\').read())"',note='operation.py contiene l’operazione ORM completa. Prima migra lo schema e carica seed.py, che ricrea soltanto le note dimostrative del database locale. L’operazione viene eseguita tramite manage.py shell perché richiede il registro applicazioni di Django.')
    for title,changes in VIEWS:
        command=CMD+'\n.venv\\Scripts\\python manage.py runserver 127.0.0.1:8000'
        if 'Testare' in title:command=CMD+'\n.venv\\Scripts\\python manage.py test notes'
        if 'management' in title:command=CMD+'\n.venv\\Scripts\\python manage.py countnotes'
        if 'ModelAdmin' in title or 'login_required' in title:command=CMD+'\n.venv\\Scripts\\python manage.py createsuperuser\n.venv\\Scripts\\python manage.py runserver 127.0.0.1:8000'
        add(b,title,{**BASE,**changes},commands=command,note='Il progetto completo usa l’app notes e SQLite locale. Le modifiche specifiche sono nei file '+', '.join(changes)+'. I template mantengono autoescape e i form POST includono CSRF. Per admin/login crea un utente con createsuperuser; non sono presenti password predefinite.')
    title='Progetto: taccuino Django con creazione ricerca e test'
    changes={
'notes/forms.py':"from django.forms import ModelForm\nfrom .models import Note\nclass NoteForm(ModelForm):\n    class Meta:\n        model=Note\n        fields=['title','body','priority']\n",
'notes/views.py':"from django.shortcuts import render,redirect,get_object_or_404\nfrom django.views.decorators.http import require_POST\nfrom .models import Note\nfrom .forms import NoteForm\ndef home(request):\n    q=request.GET.get('q','')\n    rows=Note.objects.filter(title__icontains=q).order_by('-priority','id')\n    form=NoteForm(request.POST or None)\n    if request.method=='POST' and form.is_valid():\n        form.save()\n        return redirect('home')\n    return render(request,'notebook.html',{'notes':rows,'form':form,'q':q})\n@require_POST\ndef finish(request,pk):\n    n=get_object_or_404(Note,pk=pk)\n    n.done=True\n    n.save(update_fields=['done'])\n    return redirect('home')\n",
'config/urls.py':"from django.urls import path\nfrom notes import views\nurlpatterns=[path('',views.home,name='home'),path('notes/<int:pk>/done/',views.finish,name='finish')]\n",
'templates/notebook.html':'''<!doctype html><html lang='it'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Taccuino</title><style>body{font:16px system-ui;max-width:60rem;margin:2rem auto;padding:1rem}label{display:block}article{border:1px solid #abc;padding:1rem;margin:1rem 0}</style></head><body><h1>Taccuino</h1><form method='get'><label>Cerca<input name='q' value='{{ q }}'></label><button>Cerca</button></form><h2>Nuova nota</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button>Salva</button></form>{% for n in notes %}<article><h2>{{ n.title }}</h2><p>{{ n.body }}</p><p>Priorità{{ n.priority }}</p>{% if n.done %}<p>Completata</p>{% else %}<form method='post' action='{% url "finish" n.pk %}'>{% csrf_token %}<button>Completa</button></form>{% endif %}</article>{% empty %}<p>Nessuna nota</p>{% endfor %}</body></html>''',
'notes/tests.py':"from django.test import TestCase\nfrom .models import Note\nclass NotebookTests(TestCase):\n    def test_create(self):\n        r=self.client.post('/',{'title':'Prova','body':'Test','priority':2})\n        self.assertEqual(r.status_code,302)\n        self.assertEqual(Note.objects.count(),1)\n    def test_complete(self):\n        n=Note.objects.create(title='Prova')\n        self.assertEqual(self.client.post(f'/notes/{n.pk}/done/').status_code,302)\n        n.refresh_from_db()\n        self.assertTrue(n.done)\n    def test_search(self):\n        Note.objects.create(title='Python')\n        self.assertContains(self.client.get('/?q=Python'),'Python')\n",
'README.md':'# Taccuino locale\nInstallare requirements, eseguire migrate e manage.py test notes, avviare runserver127.0.0.1:8000.\nCreare note, cercare per titolo e completare con POST protetto daCSRF. SQLite persiste. Dati sintetici; DEBUG e chiave laboratorio vanno sostituiti per distribuzione.'}
    add(b,title,{**BASE,**changes},commands=CMD+'\n.venv\\Scripts\\python manage.py test notes\n.venv\\Scripts\\python manage.py runserver 127.0.0.1:8000',project=True,section='Progetti completi',note='Un taccuino funzionante separa modello, ModelForm, viste, URL, template e test. Creazione e completamento usano POST/CSRF; ricerca GET è senza effetti collaterali.',expected='Le note si creano, si trovano per titolo e si completano; i3test coprono i flussi principali.')
    from web_lifecycle import apply
    apply(b)
    assert len(b.recipes)==35,len(b.recipes)
    b.save()

if __name__=='__main__':build_all()
