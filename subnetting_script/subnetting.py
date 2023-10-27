import sys
import time
from py_markdown_table.markdown_table import markdown_table
from colorama import Fore, Style, deinit, init

# Inizializza il modulo "colorama" per colorare l'output del terminale
init(autoreset=True)

# Funzione per stampare il testo di un colore
def print_color(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")

# Definizione lista di colori per effetto arcobaleno
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

# ASCII art per la presentazione iniziale
sub_ascii = """

 *********************************************************************************
 *                                                                               *
 *     _________    ___.                  __   _________       .__               *
 *   /   _____/__ _\\_ |__   ____   _____/  |_ \\_   ___ \\ _____ |  |   ____       *
 *   \\_____  \\|  |  \\ __ \\ /    \\_/ __ \\   __\\/    \\  \\/\\ __  \\|  | _/ ___\\      *
 *   /        \\  |  / \\_\\ \\   |  \\  ___/|  |  \\     \\____/ __ \\|  |_\\  \\___      *
 *   /_______  /____/|___  /___|  /\\___  >__|   \\______  (____  /____/\\___  >    *
 *           \\/          \\/     \\/     \\/              \\/     \\/          \\/     *
 *                                                                               *
 *                            Creato da: Greta Toniolo                           *
 *                                                                               *
 *                         GitHub: github.com/Greta-Toniolo                      *
 *                                                                               *
 *********************************************************************************
"""

# Colora ciascun carattere con un colore diverso seguendo la lista definita prima
rainbow_text = ''
for i, char in enumerate(sub_ascii):
    color = colors[i % len(colors)]
    rainbow_text += f"{color}{char}"
print(rainbow_text)

# Funzione per controllare la validità della forma dell'indirizzo IP e della subnet
def controlli_ip_mask(ip, subnet):
    if int(subnet)>1 and int(subnet)<=30:
        ottetti = ip.split('.')
        for ottetto in ottetti:
            try:
                ottetto_numero = int(ottetto)
                if ottetto_numero < 0 or ottetto_numero > 255:
                    return False
            except ValueError:
                return False 
        return True 
    else:
        return False
    
# Restituuisce la classe dell'indirizzo ip inserito dall'utente
def getclass(ip):
    ottetti = ip.split('.')

    primo_ottetto = int(ottetti[0])

    if 1 <= primo_ottetto <= 126:
        return 'A'
    elif 128 <= primo_ottetto <= 191:
        return 'B'
    elif 192 <= primo_ottetto <= 223:
        return 'C'
    elif 224 <= primo_ottetto <= 239:
        return 'D'
    elif 240 <= primo_ottetto <= 255:
        return 'E'

# Determina se l'indirizzo IP inserito è privato o pubblico.
def ip_privato_pubblico(ip):
    ottetti = [int(ottetti) for ottetti in ip.split('.')]

    if ottetti[0] == 10:
        return "privato" 
    elif ottetti[0] == 172 and 16 <= ottetti[1] <= 31:
        return "privato"  
    elif ottetti[0] == 192 and ottetti[1] == 168:
        return "privato" 
    else:
        return "pubblico"  

# Funzione che porta in formato binario l'indirizzo ip inserito     
def ip_in_bin(ip):
    ip_bin = []
    array_ottetti = ip.split('.')
    if (len(array_ottetti) == 4):
        for hex in array_ottetti:
            ip_bin.append(format(int(hex), '08b'))

        ip_bin = ''.join(ip_bin)
    else:
        print_color('formato ip invalido', Fore.RED)
    
    return ip_bin

# Funzione che porta in formato binario la subnet mask inserita
def subnet_in_bin(subnet):
    subnet_bin = '1' * int(subnet) + '0' * (32 - int(subnet))

    return subnet_bin

# Calcolo dell'indirizzo di rete della subnet
def calc_id_rete(ip, subnet):
    ip_bin = ip_in_bin(ip)
    subnet_bin = subnet_in_bin(subnet)

    id_rete_bin = []
    for i in range(32):
        id_rete_bin.append(str(int(ip_bin[i]) & int(subnet_bin[i])))
    id_rete_bin = ''.join(id_rete_bin)
    
    id_rete = []
    # da 0 a 32 con incrementi di 8
    for i in range (0,32,8):
        id_rete.append(str(int(id_rete_bin[i:i+8], 2)))
    id_rete = '.'.join(id_rete)
    
    return id_rete

# Calcolo dell'indirizzo di broadcast della subnet
def calc_broadcast(ip, subnet):
    ip_bin = ip_in_bin(ip)
    subnet_bin = subnet_in_bin(subnet)

    inverti_subnet_bin = []
    for bit in subnet_bin:
        inverti_subnet_bin.append('1' if bit == '0' else '0')
    inverti_subnet_bin = ''.join(inverti_subnet_bin)
    
    broadcast_bin = []
    for i in range(32):
        broadcast_bin.append(str(int(ip_bin[i]) | int(inverti_subnet_bin[i])))
    broadcast_bin = ''.join(broadcast_bin)
        
    broadcast = []
    for i in range (0,32,8):
        broadcast.append(str(int(broadcast_bin[i:i+8], 2)))
    broadcast = '.'.join(broadcast)

    return str(broadcast)

# Calcolo del numero di host disponibili nella subnet
def calc_numero_host(subnet):
    host_calc = 2**(32 - int(subnet)) - 2
    return str(host_calc)

# Porto la subnet mask in formato decimale puntato
def calc_subnet_mask(subnet):
    subnet_mask_bin = subnet_in_bin(subnet)

    subnet_mask = []
    for i in range(0, 32, 8):
        subnet_mask.append(str(int(subnet_mask_bin[i:i+8], 2)))
    subnet_mask = '.'.join(subnet_mask)
    return str(subnet_mask)

# Calcolo il range di indirizzi disponibili da assegnare agli host della subnet
def calc_range_indirizzi(id_rete, broadcast):
    id_rete_ottetti = id_rete.split('.')
    broadcast_ottetti = broadcast.split('.')
    id_rete_ottetti[-1] = str(int(id_rete_ottetti[-1]) + 1)
    broadcast_ottetti[-1] = str(int(broadcast_ottetti[-1]) - 1)
    range_disp = '.'.join(id_rete_ottetti) + ' - ' + '.'.join(broadcast_ottetti)
    return str(range_disp)

# Funzione principale che crea il report dei parametri della subnet
def subnet_info(ip, subnet):
    data = []
# Crea una tabella Markdown con i risultati.
    subnet_calc = {
        "Classe": "",
        "IP":"",
        "ID di Rete": "",
        "Broadcast": "",
        "numero Host": "",
        "Subnet Mask": "",
        "Range indirizzi utili": ""
    }
    subnet_calc["Classe"] = getclass(ip)
    subnet_calc["IP"] = ip_privato_pubblico(ip)
    subnet_calc["ID di Rete"] = calc_id_rete(ip, subnet)
    subnet_calc["Broadcast"] = calc_broadcast(ip, subnet)
    subnet_calc["numero Host"] = calc_numero_host(subnet)
    subnet_calc["Subnet Mask"] = calc_subnet_mask(subnet)
    subnet_calc["Range indirizzi utili"] = calc_range_indirizzi(subnet_calc["ID di Rete"], subnet_calc["Broadcast"])

# Effetto caricamento dei risultati
    parola = "Calculating subnet"

    for _ in range(1):
        for i in range(len(parola)):
            nuova_parola = parola[:i].lower() + parola[i].upper() + parola[i+1:].lower()
            sys.stdout.write(nuova_parola)
# Scrive tutti i dati accumulati nel buffer sul dispositivo di output subito
            sys.stdout.flush()
            time.sleep(0.1) 
            sys.stdout.write('\r' + " " * len(nuova_parola) + '\r')  
            sys.stdout.flush()

  #  print("\n")
# Stampa della tabella con il report dei parametri della subnet
    data.append(subnet_calc)
    markdown = markdown_table(data).set_params(quote=False).get_markdown()
    print_color(f"{markdown}", Fore.WHITE)

# Chiude il modulo colorama in modo che non vengano più applicati colori
deinit()

# Input principali dell'indirizzo dell'host e della maschera di rete della subnet
ip = input("Inserisci l'indirizzo IP (es. 192.168.1.12): ")
subnet = input("Inserisci la subnet (es. 24 per /24): ")

# Controlla se i controlli sono andati a buon fine
if (controlli_ip_mask(ip, subnet)):
    ipclass= getclass(ip)
    # Controlla che la scelta della subnet sia opportuna per la classe dell'indirizzo inserito
    if(ipclass=="A" and int(subnet)>=8) or (ipclass=="B" and int(subnet)>=16) or (ipclass=="C" and int(subnet)>=24):
        subnet_info(ip, subnet)
    elif ipclass=="D":
        print_color("attenzione! la classe D è riservata agli indirizzi MULTICAST", Fore.RED)
    elif ipclass=="E":
        print_color("attenzione! la classe E è riservata a scopi di RICERCA",Fore.RED)
    else:
        print_color("attenzione! lunghezza della maschera non valida per la classe inserita", Fore.RED)
else:
    print_color("attenzione! il formato di indirizzo ip o la maschera non sono validi", Fore.RED)
