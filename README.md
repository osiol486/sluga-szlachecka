# Instrukcja instalacji bota

**1. Informuję, że instrukcja dotyczy instalacji na systemie Windows.**

**2. Czemu instrukcja instalacji bota, a nie link do zaproszenia go?** Bota stworzyłem 4fun za pomocą chatu GPT, nie mam wiecznie włączonego komputera, aby bot działał, a discorda tak właściwie nie używam już praktycznie, więc tym bardziej bot jest przez większość czasu wyłączony.

## Spis folderów i plików:

**Folder główny:**

1. `Discordbot.py` - główny plik uruchamiający bota
2. `bot_roles.py` -
3. `libopus-0.dll` - plik potrzebny do odtwarzania muzyki
4. `logger_config.py` - tworzy logi do poszczególnych akcji z konsoli; przechowuje logi w utworzonym folderze "logs" w poszczególnych plikach .log
5. `requirements.txt` - plik z wszystkimi bibilotekami, które są używane w bocie, również te importowane ręcznie. Patrz punkt 5 na samym końcu.
6. `utils.py` - przydatne funkcje parsujące różne dane, np. nie trzeba pisać "60" (sekund) tylko można napisać w komendzie "1m" (minuta).
7. `token.env` - patrz pkt 6.

**Folder cogs:**

1. `antispam.py` - wykrywa to, gdy dany użytkownik spamuje komendami i następnie blokuje użytkownikowi możliwość korzystania z komend na jakiś czas.
2. `information.py` - znajdują się tam komendy informacyjne, np. help, komendy, ping.
3. `moderation.py` - znajdują się tam podstawowe komendy moderacyjne, np. mute, ban, kick, purge.
4. `music.py` - znajdują się tam komendy muzyczne, np. play, queue, loopqueue, seek, nowplaying.

**Folder logs**

Ten folder tworzy się po uruchomieniu bota. W 3 plikach zapisuje różne logi. 

**Folder ffmpeg**

Abyś nie musiał pobierać ręcznie ffmpeg, który służy do obsługi bota w zakresie muzyki, umieściłem ten folder również do pobrania na gotowo. Natomiast musisz w `music.py` zmienić lokalizację folderu ffmpeg na taką, gdzie jest ww. folder.

## Wymagania wstępne
Aby uruchomić bota muzycznego Discord, potrzebujesz kilku narzędzi i środowisk:

- polecam Visual Studio Code do edytowania kodu oraz do uruchamiania bota
- Python 3.8 lub nowszy
- FFMPEG (do obsługi dźwięku)
- Libopus.dll (też do obsługi dźwięku)
- Token bota Discord (wygenerowany na stronie Discord Developer Portal)

## Krok 1: Zainstaluj Pythona

1. Przejdź na stronę [Python.org](https://www.python.org/downloads/) i pobierz najnowszą wersję Pythona.
2. Podczas instalacji zaznacz opcję "Add Python to PATH", aby móc korzystać z polecenia `python` w wierszu poleceń.
3. Jeśli korzystasz z Visual Studio Code, zaleca się pobranie Pythona z Microsoft Store, aby lepiej zintegrować środowisko programistyczne.

## Krok 2: Zainstaluj FFMPEG

Bot korzysta z FFMPEG do odtwarzania muzyki, więc konieczne jest jego pobranie.

1. Przejdź na stronę [FFmpeg](https://ffmpeg.org/download.html) i pobierz odpowiednią wersję dla swojego systemu operacyjnego.
2. Wypakuj archiwum, które pobrałeś (np. za pomocą programu WinRAR lub 7-Zip). Archiwum wypakuj w folderze, gdzie masz plik discordbot.py
3. Znajdziesz tam folder o nazwie `ffmpeg`. Wewnątrz niego jest podfolder `bin` - to tam znajdują się najważniejsze pliki programu.
4. Aby bot mógł korzystać z FFMPEG, musisz dodać ten folder `bin` do zmiennych środowiskowych systemu (tzw. PATH). Dzięki temu system będzie wiedział, gdzie szukać FFMPEG, gdy będzie to potrzebne.
   - Kliknij prawym przyciskiem na "Mój komputer" > "Właściwości" > "Zaawansowane ustawienia systemu" > "Zmienna środowiskowa".
   - Znajdź zmienną `Path` i edytuj ją, dodając ścieżkę do folderu `bin` (np. `C:\ffmpeg\bin`).
5. Co więcej w pliku music.py (folder cogs) musisz zmienić ścieżkę do FFMPEG. Musisz tam podać ścieżkę do pliku ffmpeg.exe. Jest to plik w folderze bin (patrz pkt 2).

## Krok 3: Stwórz aplikację bota na stronie Discord Developer Portal

1. Przejdź na [Discord Developer Portal](https://discord.com/developers/applications).
2. Kliknij przycisk "New Application", aby stworzyć nową aplikację.
3. Wprowadź nazwę bota i kliknij "Create".
4. Przejdź do zakładki "Bot" i kliknij "Add Bot", aby dodać bota do swojej aplikacji.
5. Skopiuj token bota – będzie potrzebny do skonfigurowania bota.
6. Przejdź do zakładki "OAuth2" > "URL Generator". Zaznacz uprawnienia bota, takie jak `bot` oraz `administrator` (chyba że chcesz botowi nadać konkretne permisje, a nie od razu admina, to wybierz sobie jakieś poszczególne permisje, które musi posiadać bot), a następnie wygeneruj i skopiuj link do zaproszenia bota na swój serwer.
7. Otwórz wygenerowany link i zaproś bota na swój serwer Discord.

## Krok 4: Pobranie plików bota

Aby pobrać kod źródłowy bota, możesz skorzystać z opcji pobrania pliku .zip z repozytorium.
1. Przejdź na [stronę repozytorium bota na GitHubie](https://github.com/osiol486/discordbot/).
2. kliknij przycisk **Code** (Zielony przycisk na stronie repozytorium).
3. Wybierz **Download ZIP**.
4. Rozpakuj pobrany plik `.zip` w miejscu, w którym chcesz przechowywać pliki bota.

## Krok 5: Zainstaluj wymagane biblioteki

Aby uruchomić bota, musisz zainstalować kilka bibliotek Pythona. W terminalu (`CMD`), w katalogu projektu (czyli musisz przez `CMD` wejść do folderu, gdzie masz pobranego bota, więc musisz wpisać komendę `cd C:/lokalizacja-twojego-projektu`), wpisz poniższe polecenia:

   ```bash
   pip install discord.py
   ```
   ```bash
   pip install youtube-dl
   ```
   ```bash
   pip install yt-dlp
   ```
   ```bash
   pip install python-dotenv
   ```
   ```bash
   pip install colorama
   ```
   ```bash
   pip install loguru
   ```
   ```bash
   pip install emoji
   ```

Jeżeli po uruchomieniu bota wyskakuje ci w konsoli, że nie znajduje biblioteki o nazwie [nazwa biblioteki], to znajdź nazwę tej biblioteki w pliku `requirements.txt`, a następnie wpisz komendę w `CMD` `pip install [nazwa biblioteki]`.

## Krok 6: Konfiguracja tokena bota

1. Utwórz plik `token.env` w tym samym folderze, gdzie masz główny plik z kodem bota (discordbot.py).
2. Wklej token bota, który skopiowałeś wcześniej, w następujący sposób:

```
TOKEN=Twój_Token_Bota
```

Zapisz plik.

## Krok 7: Uruchomienie bota

Po skonfigurowaniu tokena bota możesz uruchomić bota, używając poniższego polecenia w `CMD`:

```bash
python discordbot.py
```

Po uruchomieniu bota, zobaczysz komunikat potwierdzający, że bot jest aktywny i połączony z serwerem Discord.

## Uwaga

Jeśli bot nie działa poprawnie, upewnij się, że:
- Wszystkie zależności zostały poprawnie zainstalowane.
- FFMPEG jest zainstalowany i jego ścieżka jest dodana do zmiennych środowiskowych systemu.
- Token bota jest poprawny.

Jeżeli dalej po powyższych krokach nie działa, napisz do mnie (discord: osiol486) albo może chat GPT ci pomoże.

