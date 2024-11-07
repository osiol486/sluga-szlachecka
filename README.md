# Instrukcja instalacji bota

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
2. Wypakuj archiwum i umieść pliki w dogodnej lokalizacji na dysku.
3. Dodaj ścieżkę do katalogu `bin` FFMPEG do zmiennych środowiskowych systemu (dodaj do PATH).

## Krok 3: Stwórz aplikację bota na stronie Discord Developer Portal

1. Przejdź na [Discord Developer Portal](https://discord.com/developers/applications).
2. Kliknij przycisk "New Application", aby stworzyć nową aplikację.
3. Wprowadź nazwę bota i kliknij "Create".
4. Przejdź do zakładki "Bot" i kliknij "Add Bot", aby dodać bota do swojej aplikacji.
5. Skopiuj token bota – będzie potrzebny do skonfigurowania bota.
6. Przejdź do zakładki "OAuth2" > "URL Generator". Zaznacz uprawnienia bota, takie jak `bot` oraz `administrator`, a następnie wygeneruj i skopiuj link do zaproszenia bota na swój serwer.
7. Otwórz wygenerowany link i zaproś bota na swój serwer Discord.

## Krok 4: Klonowanie repozytorium

Aby pobrać kod źródłowy bota, wykonaj poniższe kroki:

```bash
git clone https://github.com/nazwauzytkownika/nazwarepozytorium.git
```

Następnie przejdź do katalogu z botem:

```bash
cd nazwarepozytorium
```

## Krok 5: Zainstaluj wymagane biblioteki

W katalogu projektu znajduje się plik `requirements.txt`, który zawiera listę wymaganych bibliotek do uruchomienia bota. Aby je zainstalować, użyj poniższego polecenia:

```bash
pip install -r requirements.txt
```

## Krok 6: Konfiguracja tokena bota

1. Utwórz plik 'token.env' w tym samym folderze, gdzie masz główny plik z kodem bota (discordbot.py).
2. Wklej token bota, który skopiowałeś wcześniej, w następujący sposób:

```
TOKEN=Twój_Token_Bota
```

Zapisz plik.

## Krok 7: Uruchomienie bota

Po skonfigurowaniu tokena bota możesz uruchomić bota, używając poniższego polecenia w CMD:

```bash
python discordbot.py
```

Po uruchomieniu bota, zobaczysz komunikat potwierdzający, że bot jest aktywny i połączony z serwerem Discord.

## Uwaga

Jeśli bot nie działa poprawnie, upewnij się, że:
- Wszystkie zależności zostały poprawnie zainstalowane.
- FFMPEG jest zainstalowany i jego ścieżka jest dodana do zmiennych środowiskowych systemu.
- Token bota jest poprawny.

