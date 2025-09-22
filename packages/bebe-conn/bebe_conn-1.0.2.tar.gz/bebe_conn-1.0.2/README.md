# BebeConn - Monitorizare Laptop de la Distanță

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/bebe-conn.svg)](https://pypi.org/project/bebe-conn/)

O librărie Python simplă pentru monitorizarea laptopului de la distanță, cu interfață web și actualizări în timp real.

## 🚀 Caracteristici

- **Monitorizare în timp real** - Vezi starea sistemului live
- **Screenshots automate** - Capturi de ecran la interval regulat
- **Monitorizare procese** - Vezi ce aplicații rulează
- **Statistici sistem** - CPU, RAM, Disk usage
- **Interfață web modernă** - Dashboard responsive
- **Acces extern** - Prin ngrok pentru monitorizare din orice țară
- **Instalare simplă** - Doar `pip install bebe-conn`

## 📦 Instalare

```bash
pip install bebe-conn
```

## 🎯 Utilizare Rapidă

### Pornire Completă (Recomandat)

```bash
# Pornire locală
bebe-conn start

# Pornire cu acces extern (ngrok)
bebe-conn start --ngrok

# Pornire cu configurații personalizate
bebe-conn start --ngrok --port 8080 --screenshot 60
```

### Pornire Separată

```bash
# Doar serverul
bebe-conn server --port 5000

# Doar agentul
bebe-conn agent --server-url http://localhost:5000 --screenshot 120
```

### Utilizare în Python

```python
import bebe_conn

# Pornire simplă
bebe_conn.start()

# Pornire cu ngrok
bebe_conn.start(ngrok=True, port=5000, screenshot_interval=120)

# Pornire doar serverul
bebe_conn.start_server(port=5000)

# Pornire doar agentul
bebe_conn.start_agent(server_url="http://localhost:5000", screenshot_interval=120)
```

## 🌐 Acces Dashboard

După pornire, accesează dashboard-ul:

- **Local:** `http://localhost:5000`
- **Extern (ngrok):** URL-ul afișat în terminal

## 📱 Ce Vezi pe Dashboard

- ✅ **Status live** - dacă laptopul este online
- 📸 **Screenshots** - capturi de ecran automate
- 🔧 **Procese active** - lista programelor care rulează
- 📊 **Statistici sistem** - CPU, RAM, Disk usage
- 🕒 **Ultima actualizare** - timestamp curent

## ⚙️ Configurări

### Parametri CLI

- `--ngrok` - Folosește ngrok pentru acces extern
- `--port` - Portul pentru server (default: 5000)
- `--screenshot` - Intervalul pentru screenshot-uri în secunde (default: 120)
- `--server-url` - URL-ul serverului pentru agent

### Parametri Python

```python
bebe_conn.start(
    ngrok=False,              # Folosește ngrok
    port=5000,                # Portul serverului
    screenshot_interval=120   # Interval screenshot-uri (secunde)
)
```

## 🔧 Cerințe

- Python 3.8+
- Windows, macOS, sau Linux
- Pentru ngrok: instalează de la https://ngrok.com/download

## 📋 Dependențe

- Flask - Server web
- requests - Comunicare HTTP
- psutil - Monitorizare sistem
- Pillow - Procesare imagini
- pyautogui - Captură ecran

## 🚨 Securitate

**IMPORTANT:** Această librărie este destinată pentru monitorizarea propriului laptop. Nu folosiți pentru monitorizarea altor persoane fără consimțământul lor.

## 📝 Licență

MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 🤝 Contribuții

Contribuțiile sunt binevenite! Vă rugăm să:

1. Fork repository-ul
2. Creați o ramură pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit modificările (`git commit -m 'Add some AmazingFeature'`)
4. Push la ramură (`git push origin feature/AmazingFeature`)
5. Deschideți un Pull Request

## 📞 Suport

Pentru probleme sau întrebări:

- https://github.com/me-suzy/bebeconnlibrary
- Deschideți un issue pe GitHub  https://github.com/me-suzy/bebeconnlibrary/issues
- Contactați autorul: ioan.fantanaru@gmail.com

## 🎉 Mulțumiri

- Flask pentru framework-ul web
- psutil pentru monitorizarea sistemului
- pyautogui pentru capturarea ecranului
- ngrok pentru accesul extern

---

**BebeConn** - Monitorizare laptop simplă și eficientă! 🖥️📱
