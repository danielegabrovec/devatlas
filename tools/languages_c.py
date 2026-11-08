"""C17 operations with explicit ownership and bounds."""
from catalog_support import Book
from languages_common import program, require_count

HEADERS='''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <errno.h>
#include <limits.h>
'''


def build_all():
    b=Book("c","ISO C17, GCC 11+",["https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf", "https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html"],"Compilatore ISO C17 (GCC/Clang). Su Windows usare una toolchain GCC UCRT64 nel PATH. Nessuna estensione POSIX necessaria agli esempi.")
    def add(title,desc,code,expected,tags,definitions=""):
        program(b,title,desc,HEADERS+"\n"+definitions+"\nint main(void){\n"+code+"\nreturn 0;\n}\n",filename="main.c",command="gcc -std=c17 -Wall -Wextra -pedantic main.c -o demo.exe\n.\\demo.exe",expected=expected,tags=tags.split(),error="Non ignorare warning su puntatori e dimensioni. Controllare sempre il risultato di allocazioni e operazioni I/O prima di usare il dato.")
    add("Convertire un intero con strtol", "Verifica sintassi, fine del testo e limiti di rappresentazione prima di convertire in int.", '''const char *text="123";char *end=NULL;errno=0;long value=strtol(text,&end,10);
if(errno||end==text||*end!='\\0'||value<INT_MIN||value>INT_MAX){fputs("intero non valido\\n",stderr);return 1;}
printf("%d\\n",(int)value);''',"123; suffissi, input vuoto e overflow sono rifiutati.","strtol integer parsing validation")
    add("Formattare in un buffer con snprintf", "Rileva il troncamento confrontando la lunghezza richiesta con la capacità.", '''char buffer[16];int required=snprintf(buffer,sizeof buffer,"id=%d",42);
if(required<0||(size_t)required>=sizeof buffer){fputs("buffer insufficiente\\n",stderr);return 1;}
puts(buffer);''',"id=42; un buffer insufficiente viene segnalato.","snprintf buffer bounds")
    add("Leggere una riga con fgets", "Legge da un flusso sintetico con limite di dimensione e rimuove il newline finale.", '''FILE *stream=tmpfile();if(!stream)return 1;
fputs("Ada Rossi\\n",stream);rewind(stream);char line[64];
if(fgets(line,sizeof line,stream)){line[strcspn(line,"\\r\\n")]='\\0';puts(line);}fclose(stream);''',"Ada Rossi; righe più lunghe del buffer richiedono gestione esplicita della continuazione.","fgets input line safe")
    add("Spostare memoria sovrapposta con memmove", "Rimuove il primo carattere includendo il terminatore nullo nell'area spostata.", '''char text[]="ABCDE";memmove(text,text+1,strlen(text));puts(text);''',"BCDE; memcpy non è ammesso per intervalli sovrapposti.","memmove overlap buffer")
    add("Concatenare soltanto dopo un controllo di capacità", "Calcola lo spazio necessario e include il terminatore nullo.", '''char target[16]="Ciao ";const char *suffix="Ada";
size_t used=strlen(target),extra=strlen(suffix);
if(extra>=sizeof target-used)return 1;memcpy(target+used,suffix,extra+1);puts(target);''',"Ciao Ada", "string buffer capacity memcpy")
    add("Ordinare interi con qsort", "Usa un comparatore che non sottrae valori evitando overflow nel confronto.", '''int values[]={9,2,5};size_t count=sizeof values/sizeof values[0];qsort(values,count,sizeof values[0],compare_int);
for(size_t i=0;i<count;i++)printf("%d ",values[i]);puts("");''',"2 5 9", "qsort comparator sort", "static int compare_int(const void *left,const void *right){int a=*(const int*)left,b=*(const int*)right;return (a>b)-(a<b);}")
    add("Cercare in un array ordinato con bsearch", "Controlla il puntatore restituito prima di dereferenziare l'elemento trovato.", '''int values[]={2,5,9},key=5;const int *found=bsearch(&key,values,3,sizeof values[0],compare_int);
if(found)printf("%d\\n",*found);else puts("assente");''',"5; l'array deve essere ordinato secondo lo stesso comparatore.","bsearch sorted lookup", "static int compare_int(const void *left,const void *right){int a=*(const int*)left,b=*(const int*)right;return (a>b)-(a<b);}")
    add("Allocare un array controllando overflow di dimensione", "Verifica il prodotto di size_t prima di chiamare malloc e rilascia il risultato.", '''size_t count=5;if(count>SIZE_MAX/sizeof(int))return 1;
int *values=malloc(count*sizeof *values);if(!values)return 1;
for(size_t i=0;i<count;i++)values[i]=(int)i;
printf("%d\\n",values[4]);free(values);''',"4; nessuna lettura prima dell'inizializzazione.","malloc allocation overflow free")
    add("Inizializzare un array a zero con calloc", "Alloca contatori azzerati verificando il risultato dell'allocazione.", '''size_t count=4;int *values=calloc(count,sizeof *values);if(!values)return 1;
printf("%d %d\\n",values[0],values[3]);free(values);''',"0 0", "calloc zero allocation")
    add("Ridimensionare con realloc senza perdere il puntatore", "Conserva l'allocazione originale quando realloc fallisce.", '''size_t next_count=4;int *values=malloc(2*sizeof *values);if(!values)return 1;values[0]=7;
int *grown=realloc(values,next_count*sizeof *values);if(!grown){free(values);return 1;}values=grown;
values[2]=9;printf("%d %d\\n",values[0],values[2]);free(values);''',"7 9; i byte aggiunti non sono inizializzati automaticamente.","realloc ownership resize")
    add("Passare un record a una funzione", "Usa un puntatore const per leggere una struct senza copiarla né modificarla.", '''struct Point point={3,4};printf("%d\\n",length_squared(&point));''',"25", "struct const pointer record", "struct Point{int x;int y;};static int length_squared(const struct Point *point){return point->x*point->x+point->y*point->y;}")
    add("Rappresentare stati con enum", "Rende esplicito un insieme di stati e gestisce un valore non riconosciuto.", '''enum Status state=READY;switch(state){case READY:puts("pronto");break;case BUSY:puts("occupato");break;default:return 1;}''',"pronto", "enum switch state", "enum Status{READY,BUSY};")
    add("Leggere una union tramite un tag", "Controlla quale membro è attivo prima di interpretarne i byte.", '''struct Value value={.kind=INTEGER,.data.integer=42};
if(value.kind==INTEGER)printf("%d\\n",value.data.integer);''',"42; il tag viene mantenuto insieme al valore.","union tagged variant", "enum Kind{INTEGER,REAL};struct Value{enum Kind kind;union{int integer;double real;}data;};")
    add("Passare una funzione callback", "Riceve una trasformazione tramite puntatore a funzione con firma dichiarata.", '''printf("%d\\n",apply(7,twice));''',"14", "callback function pointer", "typedef int(*Transform)(int);static int twice(int n){return n*2;}static int apply(int n,Transform transform){return transform(n);}")
    add("Gestire opzioni come maschera di bit", "Imposta, controlla e rimuove un flag senza toccare gli altri bit.", '''unsigned flags=READABLE|WRITABLE;printf("%d\\n",(flags&READABLE)!=0);flags&=~WRITABLE;printf("%d\\n",(flags&WRITABLE)!=0);''',"1 e 0.","bitmask flags enum", "enum Permission{READABLE=1u<<0,WRITABLE=1u<<1};")
    add("Scrivere e rileggere byte con fread e fwrite", "Controlla il numero di elementi trasferiti su un file temporaneo.", '''FILE *stream=tmpfile();if(!stream)return 1;unsigned char source[]={0,127,255},target[3]={0};
if(fwrite(source,1,sizeof source,stream)!=sizeof source){fclose(stream);return 1;}rewind(stream);
size_t read=fread(target,1,sizeof target,stream);printf("%zu %u\\n",read,(unsigned)target[2]);fclose(stream);''',"3 255; un formato portabile deve dichiarare endian e larghezza dei numeri.","binary fread fwrite file")
    add("Distinguere fine file da errore di lettura", "Verifica ferror dopo un ciclo fgetc invece di assumere che ogni EOF sia normale.", '''FILE *stream=tmpfile();if(!stream)return 1;fputs("abc",stream);rewind(stream);int ch;size_t count=0;
while((ch=fgetc(stream))!=EOF)count++;if(ferror(stream)){fclose(stream);return 1;}printf("%zu\\n",count);fclose(stream);''',"3; ch è int per poter rappresentare sia i byte sia EOF.","eof ferror fgetc stream")
    add("Analizzare campi con larghezze limitate", "Usa sscanf con dimensione massima per il campo stringa e controlla i campi consumati.", '''char name[16];int age=0;int used=0;const char *line="Ada;36";
if(sscanf(line,"%15[^;];%d%n",name,&age,&used)==2&&line[used]=='\\0')printf("%s %d\\n",name,age);else return 1;''',"Ada 36; il formato è separato da punto e virgola e non è un parser CSV generale.","sscanf width parsing")
    add("Costruire e liberare una lista concatenata", "Collega nodi allocati e li rilascia uno per uno senza perdere il successivo.", '''struct Node *head=NULL;for(int i=3;i>=1;i--){struct Node *node=malloc(sizeof *node);if(!node){while(head){struct Node *next=head->next;free(head);head=next;}return 1;}node->value=i;node->next=head;head=node;}
while(head){struct Node *next=head->next;printf("%d ",head->value);free(head);head=next;}puts("");''',"1 2 3 e tutti i nodi rilasciati.","linked list malloc cleanup", "struct Node{int value;struct Node *next;};")
    add("Implementare uno stack limitato", "Controlla capacità e vuoto prima delle operazioni LIFO.", '''int stack[4];size_t size=0;if(size<4)stack[size++]=7;if(size<4)stack[size++]=9;
while(size>0)printf("%d ",stack[--size]);puts("");''',"9 7", "stack lifo bounds array")
    add("Implementare una coda circolare", "Riutilizza un buffer fisso con indici modulari senza spostare tutti gli elementi.", '''int buffer[4];size_t head=0,tail=0,count=0;
for(int value=1;value<=3;value++){if(count==4)return 1;buffer[tail]=value;tail=(tail+1)%4;count++;}
while(count){printf("%d ",buffer[head]);head=(head+1)%4;count--;}puts("");''',"1 2 3", "queue ring buffer fifo")
    add("Calcolare MCD con algoritmo di Euclide", "Riduce due interi non negativi con divisioni successive.", '''unsigned a=42,b=56;while(b){unsigned remainder=a%b;a=b;b=remainder;}printf("%u\\n",a);''',"14", "gcd euclid algorithm")
    add("Leggere errno soltanto dopo un fallimento", "Azzera errno prima di una funzione che lo può impostare e ne segnala l'errore.", '''errno=0;char *end;long value=strtol("999999999999999999999999999999999999",&end,10);(void)value;
if(errno==ERANGE)puts("numero fuori intervallo");else puts("conversione riuscita");''',"numero fuori intervallo", "errno erange diagnostics")
    add("Mantenere controlli di contratto nelle build ottimizzate", "Usa un controllo esplicito per un'invariante che non deve sparire con NDEBUG.", '''int actual=6*7;if(actual!=42){fputs("contratto violato\\n",stderr);return 1;}puts("contratto verificato");''',"contratto verificato", "invariant testing release")
    program(b,"Progetto completo statistiche su misure C", "Separa API, implementazione, programma e test di una funzione che calcola min/max/media senza dipendenze.", '''#include <stdio.h>
#include "stats.h"
int main(void){double values[]={2,4,9};struct Stats result;if(!stats(values,3,&result))return 1;printf("min=%.1f max=%.1f media=%.1f\\n",result.min,result.max,result.mean);return 0;}''',filename="main.c",files={
      "stats.h":'''#ifndef CATALOG_STATS_H
#define CATALOG_STATS_H
#include <stddef.h>
#include <stdbool.h>
struct Stats{double min,max,mean;};
bool stats(const double *values,size_t count,struct Stats *result);
#endif''',
      "stats.c":'''#include "stats.h"
#include <math.h>
bool stats(const double *values,size_t count,struct Stats *result){if(!values||!count||!result)return false;double min=values[0],max=values[0],mean=0;for(size_t i=0;i<count;i++){if(!isfinite(values[i]))return false;if(values[i]<min)min=values[i];if(values[i]>max)max=values[i];mean+=(values[i]-mean)/(double)(i+1);}*result=(struct Stats){min,max,mean};return true;}''',
      "test.c":'''#include "stats.h"
#include <stdio.h>
int main(void){double values[]={2,4,6};struct Stats result;if(!stats(values,3,&result)||result.min!=2||result.max!=6||result.mean!=4)return 1;if(stats(values,0,&result))return 2;puts("2 contratti verificati");return 0;}''',
      "README.md":"# Statistiche C17\n\nCompilare main.c e stats.c per il programma, test.c e stats.c per i test. Non unire main.c e test.c: entrambi hanno main. La funzione rifiuta input vuoti, puntatori nulli e misure non finite; gli input devono restare entro una scala che non provochi overflow dei calcoli double intermedi. Non alloca memoria e non conserva riferimenti ai dati. Nessuna libreria esterna.\n"},command="gcc -std=c17 main.c stats.c -o demo.exe\ngcc -std=c17 test.c stats.c -o tests.exe\n.\\tests.exe\n.\\demo.exe",expected="2 contratti verificati; min 2.0, max 9.0, media 5.0.",tags=("project","header","library","statistics","test"),project=True,section="Progetti completi")
    require_count(b,25)


if __name__=="__main__":build_all()
