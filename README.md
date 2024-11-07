# Instrukcja instalacji bota

**1. Informuję, że instrukcja dotyczy instalacji na systemie Windows.**

**2. Czemu instrukcja instalacji bota, a nie link do zaproszenia go? Bota stworzyłem 4fun za pomocą chatu GPT, nie mam wiecznie włączonego komputera, aby bot działał, a discorda tak właściwie nie używam już praktycznie, więc tym bardziej bot jest przez większość czasu wyłączony.**

## Wymagania wstępne
Aby uruchomić bota muzycznego Discord, potrzebujesz kilku narzędzi i środowisk:

- Python 3.8 lub nowszy
- FFMPEG (do obsługi dźwięku)
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
5. Co więcej w pliku music.py (folder cogs) musisz zmienić ścieżkę do FFMPEG. Musisz tam podać ścieżkę do pliku ffmpeg.exe. Jest to plik w folderze bin.

## Krok 3: Stwórz aplikację bota na stronie Discord Developer Portal

1. Przejdź na [Discord Developer Portal](https://discord.com/developers/applications).
2. Kliknij przycisk "New Application", aby stworzyć nową aplikację.
3. Wprowadź nazwę bota i kliknij "Create".
4. Przejdź do zakładki "Bot" i kliknij "Add Bot", aby dodać bota do swojej aplikacji.
5. Skopiuj token bota – będzie potrzebny do skonfigurowania bota.
6. Przejdź do zakładki "OAuth2" > "URL Generator". Zaznacz uprawnienia bota, takie jak `bot` oraz `administrator`, a następnie wygeneruj i skopiuj link do zaproszenia bota na swój serwer.
7. Otwórz wygenerowany link i zaproś bota na swój serwer Discord.

## Krok 4: Klonowanie repozytorium

Aby pobrać kod źródłowy bota, musisz go sklonować (pobrać na swój komputer). W tym celu:

1. Otwórz wiersz poleceń (`CMD`) lub terminal, np. w systemie Windows możesz nacisnąć klawisz Windows, wpisać "cmd" i uruchomić Wiersz polecenia.
2. Przejdź do folderu, w którym chcesz umieścić kod bota, używając polecenia `cd` (np. `cd C:\TwojeProjekty`).
3. Następnie wpisz poniższe polecenie, aby sklonować repozytorium:

   ```bash
   git clone https://github.com/nazwauzytkownika/nazwarepozytorium.git
   ```

4. Przejdź do katalogu z botem:

   ```bash
   cd nazwarepozytorium
   ```

## Krok 5: Zainstaluj wymagane biblioteki

Aby uruchomić bota, musisz zainstalować kilka bibliotek Pythona. W terminalu, w katalogu projektu, wpisz poniższe polecenia:

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

## Krok 6: Instalacja `libopus` (do obsługi dźwięku)

Biblioteka `libopus` jest wymagana przez `discord.py` do odtwarzania dźwięku na serwerach Discord. Jest to kodek audio, który umożliwia przesyłanie dźwięku wysokiej jakości z niskim opóźnieniem. Jeśli biblioteka `libopus` nie jest zainstalowana lub poprawnie skonfigurowana, bot może nie być w stanie odtwarzać dźwięku.

1. Pobierz plik `libopus-0.dll` ze strony [DLL-files.com](https://www.dll-files.com/libopus-0.dll.html).
2. Rozpakuj pobrany plik, jeśli jest spakowany.
3. Umieść plik `libopus-0.dll` w tym samym folderze, w którym znajduje się Twój plik `discordbot.py`.

**Uwaga:** Umieszczenie `libopus-0.dll` w folderze z botem pozwala `discord.py` na znalezienie biblioteki bez konieczności dodatkowej konfiguracji.

## Krok 7: Konfiguracja tokena bota

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

