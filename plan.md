# Wybór modeli

### Gotowce
- GPT-03mini
- DeepSeek-R1
- Claud 3.7
- llamaMiniMax

### Do Dotrenowania
- minGPT (od zera)
- llama7B

# Można też popróbować z generacją na podstawie wyglądu planszy


# Jak powinno to wyglądać
- plansz 8x8

## Warianty
<!-- 
### Wariant 1 
- 1 snake, jabłka w tych samych miejscach, ściany na brzegach

### Wariant 2
- 1 snake, jabłka pojawiają się dynamicznie
- ściany na brzegach i w jakichś miejsach planszy?
- globalny stan -> przekazany do prompta po każdym ruchu
- LLM daje odp na ten globalny stan

### Wariant 3
- 2 snake, jabłka pojawiają się dynamicznie
- globalny stan -> przekazany do prompta
- LLMy dają odp na ten globalny stan

- porównujemy który snake zdobędzie najwięcej jabłek
- grę sensowną definiujemy jako niewiele gorszą od prostego agenta LLM -->

### Obecny snake
- 1 wąż
- 16x16 plansza
- jabłka w losowych miejscach
- uderzenie w siebie samego skutkuje końcem gry, wyjście poza planszę również

### Immediate TODO
- napisanie komunikacji międzyprocesowej, tak by LLM mógł grać
- przekonać promptem MiniMax'a do generowania jakiś ruchów, zobaczyć jakie ma scory

# Dodatkowe uwagi


# Cele
- wybór odpowiednich parametrów promptów dla dużych modeli, i odpowiednich parametrów API
- wybór odpowiednich parametrów treningu dla mniejszych modeli (fine tuning albo od zera)
- chcemy wiedzieć co było przyczyną porażki danego snake'a, jaki był win-rate, ile zdobył najwięcej pkt itp.


### Parametry do dostosowywania dla snake'a

- cell size?
- rozmiar planszy?



