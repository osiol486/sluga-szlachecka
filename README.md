# Instrukcja instalacji bota SŁUGA SZLACHECKA

**1. Informuję, że instrukcja dotyczy instalacji na systemie Windows.**

**2. Czemu instrukcja instalacji bota, a nie link do zaproszenia go?** Bota stworzyłem 4fun za pomocą chatu GPT, nie mam wiecznie włączonego komputera, aby bot działał, a discorda tak właściwie nie używam już praktycznie, więc tym bardziej bot jest przez większość czasu wyłączony.

## Spis folderów i plików:

**Folder główny:**

1. `Discordbot.py` - główny plik uruchamiający bota.
2. `libopus-0.dll` - plik potrzebny do odtwarzania muzyki.
3. `logger_config.py` - tworzy logi do poszczególnych akcji z konsoli; przechowuje logi w utworzonym folderze "logs" w poszczególnych plikach .log
4. `requirements.txt` - plik z wszystkimi bibilotekami, które są używane w bocie, również te importowane ręcznie. Patrz punkt 4 na samym końcu.
5. `token.env` - patrz pkt 7

**Folder cogs:**

1. `antispam.py` - wykrywa to, gdy dany użytkownik spamuje komendami i następnie blokuje użytkownikowi możliwość korzystania z komend na jakiś czas.
2. `information.py` - znajdują się tam komendy informacyjne, np. help, komendy, ping.
3. `moderation.py` - znajdują się tam podstawowe komendy moderacyjne, np. mute, ban, kick, purge.
4. `music.py` - znajdują się tam komendy muzyczne, np. play, queue, loopqueue, seek, nowplaying.
5. `utility.py` -znajdują się tam komendy narzędziowe, np. userinfo, serverinfo, avatar.

**Folder logs**

Ten folder tworzy się po uruchomieniu bota. W 3 plikach zapisuje różne logi. 

**Folder cache**

Po uruchomieniu bota i skorzystaniu z komendy muzycznej `!play` bot zacznie zapisywać grane utwory w pliku, który utworzy w folderze cache. Jest to tak zrobione, aby zoptymalizować proces włączania muzyki i aby bot się nie zawieszał aż tak (normalnie bot by musiał szukać za każdym razem danego utworu na youtube, a tak to szuka w pliku `music_cache.json` jeżeli został już dany utwór użyty wcześniej).

**Folder ffmpeg** 

Abyś nie musiał pobierać ręcznie ffmpeg, który służy do obsługi bota w zakresie muzyki, umieściłem ten folder również do pobrania na gotowo. Dzięki ffmpeg bot z muzyką waży do niecałych 300MB. Bez tego folderu by wszystko ważyło parę-parenaście MB.

**Folder utils**

1. `utils.py` - przydatne funkcje parsujące różne dane, np. nie trzeba pisać "60" (sekund) tylko można napisać w komendzie "1m" (minuta).
2. `constants.py` - przechowuje stałe zmienne, czyli np. chcemy używać danego koloru zawsze, to ma być ten konkretny zielony. No to ustawiamy tam jaki to jest zielony, a następnie używamy zielonego w różnych plikach bez koniecznosci wklejania z osobna kodu HEX.

## Wymagania wstępne
Aby uruchomić bota muzycznego Discord, potrzebujesz kilku narzędzi i środowisk:

- polecam Visual Studio Code do edytowania kodu oraz do uruchamiania bota, ale nie jest to konieczne.
- Python 3.8 lub nowszy
- FFMPEG (do obsługi dźwięku)
- Libopus.dll (też do obsługi dźwięku)
- Token bota Discord (wygenerowany na stronie Discord Developer Portal)

## Krok 1: Zainstaluj Pythona

1. Przejdź na stronę [Python.org](https://www.python.org/downloads/) i pobierz najnowszą wersję Pythona.
2. Podczas instalacji zaznacz opcję "Add Python to PATH", aby móc korzystać z polecenia `python` w wierszu poleceń.
3. Jeśli korzystasz z Visual Studio Code, zaleca się pobranie Pythona z Microsoft Store, aby lepiej zintegrować środowisko programistyczne.

## Krok 2: Stwórz aplikację bota na stronie Discord Developer Portal

1. Przejdź na [Discord Developer Portal](https://discord.com/developers/applications).
2. Kliknij przycisk "New Application", aby stworzyć nową aplikację.
3. Wprowadź nazwę bota i kliknij "Create".
4. Przejdź do zakładki "Bot" i kliknij "Add Bot", aby dodać bota do swojej aplikacji.
5. Skopiuj token bota – będzie potrzebny do skonfigurowania bota.
6. Przejdź do zakładki "OAuth2" > "URL Generator". Zaznacz uprawnienia bota, takie jak `bot` oraz `administrator` (chyba że chcesz botowi nadać konkretne permisje, a nie od razu admina, to wybierz sobie jakieś poszczególne permisje, które musi posiadać bot), a następnie wygeneruj i skopiuj link do zaproszenia bota na swój serwer.
7. Otwórz wygenerowany link i zaproś bota na swój serwer Discord.

## Krok 3: Pobranie plików bota

Aby pobrać kod źródłowy bota, możesz skorzystać z opcji pobrania pliku .zip z repozytorium.
1. Przejdź na [stronę repozytorium bota na GitHubie](https://github.com/osiol486/discordbot/).
2. kliknij przycisk **Code** (Zielony przycisk na stronie repozytorium).
3. Wybierz **Download ZIP**.
4. Rozpakuj pobrany plik `.zip` w miejscu, w którym chcesz przechowywać pliki bota.

## Krok 4: Zainstaluj wymagane biblioteki

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

## Krok 5 Konfiguracja FFmpeg

Dodaj FFmpeg do zmiennych środowiskowych:
	•	Kliknij prawym przyciskiem myszy ikonę Ten komputer (lub Mój komputer) na pulpicie i wybierz Właściwości.
	•	Kliknij Zaawansowane ustawienia systemu (z lewej strony).
	•	W oknie Właściwości systemu wybierz zakładkę Zaawansowane i kliknij przycisk Zmienne środowiskowe.
	•	W sekcji Zmienne systemowe znajdź zmienną o nazwie Path i kliknij przycisk Edytuj.
	•	W oknie edycji zmiennych kliknij Nowy, a następnie wklej wcześniej skopiowaną ścieżkę (C:\ffmpeg\bin).
	•	Kliknij OK we wszystkich oknach, aby zatwierdzić zmiany.

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

