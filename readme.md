# Bet with Friends  
**Django REST Framework + React**

Aplikacja umożliwia tworzenie **grup na turnieje piłkarskie** (np. EURO, MŚ), w których użytkownicy mogą typować mecze i rywalizować w rankingach punktowych.  

Użytkownicy zostają dodani do grup jako **członkowie** w tabeli `Member`, a w obrębie grupy mogą mieć rolę **admina**, przyznawaną przez superusera.  

---

## Cel projektu
- Tworzenie prywatnych grup turniejowych  
- Członkostwo użytkowników i adminowanie grupami  
- Bezpieczne typowanie wyników meczów (**zakłady nie są widoczne**)  
- Automatyczne naliczanie punktów po ustawieniu wyniku przez admina grupy lub superusera  
- Punkty są zawsze widoczne dla wszystkich członków grupy  

---

## Stack technologiczny
- **Backend:** Python 3, Django, Django REST Framework, Token Authentication  
- **Frontend:** React  
- **Testy:** Django TestCase, DRF APIRequestFactory  

---

## Role użytkowników i członkostwo

### Superuser
- globalny administrator, pełne uprawnienia  
- może tworzyć grupy i nadawać admina  
- jego uprawnień admina nie można odebrać  

### Admin grupy
- zarządza wydarzeniami i wynikami w swojej grupie  

### Członek grupy
- może dołączać / opuszczać grupę i typować wyniki  
- **zakłady nie są widoczne dla nikogo**  
- punkty są zawsze widoczne dla wszystkich członków grupy  

**Członkostwo realizowane przez tabelę `Member`** – każdy użytkownik może być adminem jednej grupy i zwykłym członkiem innej.

---

## Eventy (mecze turniejowe)
- Każdy event przypisany do jednej grupy  
- Zakłady można składać **przed rozpoczęciem meczu**  
- Wyniki ustawia admin grupy lub superuser  
- Po ustawieniu wyniku punkty są przeliczane i **wszyscy członkowie widzą swoje punkty**  

---

## System punktacji
| Warunek | Punkty |
|------|------|
| Dokładny wynik | 3 |
| Poprawny zwycięzca / remis | 1 |
| Błędny typ | 0 |

---

## Bezpieczeństwo i permissions
- Token-based authentication  
- Custom permissions zależne od roli i członkostwa w grupie  
- Blokada operacji zależnie od czasu meczu  
- Brak możliwości eskalacji uprawnień przez API  

---

## Testy
Testy weryfikują logikę biznesową i uprawnienia:
- Uprawnienia adminów grup i superusera  
- Blokady operacji w zależności od czasu meczu  
- Naliczanie punktów dla zakładów  
- Scenariusze pozytywne i negatywne  

---

## Uruchomienie lokalne
### Sklonuj repozytorium i aktywuj wirtualne środowisko
```bash
git clone <repo>
python -m venv venv
venv\Scripts\activate
```

## Zainstaluj wymagania
```bash
pip install -r requirements.txt
```
## Wykonaj migracje bazy danych
```bash
python manage.py migrate
```

## Uruchom backend
```bash
python manage.py runserver
```

## Dostęp do API
http://127.0.0.1:8000/

