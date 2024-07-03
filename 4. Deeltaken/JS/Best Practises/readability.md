---
title: JavaScript Code Readability
tags:
  - JS/Best-practises
  - page
difficulty: 2
---

# Code Readability and Formatting
**Code readability** en **code formatting** zijn cruciaal voor het schrijven van duidelijke en onderhoudbare code. Goed leesbare code vergemakkelijkt samenwerking, vermindert de kans op fouten, en maakt toekomstige aanpassingen eenvoudiger.

## Waarom Code Readability Belangrijk is
1. **Onderhoudbaarheid**: Duidelijk leesbare code is eenvoudiger te onderhouden en aan te passen.
2. **Samenwerking**: Het vergemakkelijkt samenwerking binnen teams, doordat de intentie van de code sneller begrepen wordt.
3. **Debugging**: Fouten zijn gemakkelijker te vinden en op te lossen in goed gestructureerde code.
4. **Consistentie**: Consistente code stijlen verbeteren de uniformiteit in een codebase, wat de leesbaarheid verhoogt.

### Basisprincipes

1. Consistente Indentatie
Gebruik consistente inspringing om de structuur van je code weer te geven. Standaarden zijn meestal 2 of 4 spaties per niveau, afhankelijk van de voorkeuren of de richtlijnen van het project.

```javascript
if (condition) {
    // Goed ingesprongen
    doSomething();
} else {
    // Consistente inspringing
    doSomethingElse();
}
```

2. Zinvolle Namen
Gebruik beschrijvende namen voor variabelen, functies, en klassen. Vermijd afkortingen en gebruik volledige woorden.

```javascript
// Slecht
const x = 42;

// Goed
const aantalProducten = 42;
```

3. Duidelijke Structuur
Structureer je code logisch en hou aan functionele groeperingen. Gebruik functies om complexe taken op te splitsen in kleinere, begrijpelijke delen.

```javascript
function berekenPrijs(producten) {
    let totaal = 0;
    for (let product of producten) {
        totaal += product.prijs;
    }
    return totaal;
}
```

4. Consistentie in Stijl
Gebruik consistente stijlregels, zoals de positie van accolades, spaties rondom operators, en puntkomma's. Dit verhoogt de leesbaarheid en voorkomt verwarring.

```javascript
// Slecht
if(condition){
doSomething();}

// Goed
if (condition) {
    doSomething();
}
```

5. Vermijd Magic Numbers
Gebruik geen harde getallen in je code zonder uitleg. Definieer ze als constante met een beschrijvende naam.

```javascript
// Slecht
let radius = 10 * 3.14159;

// Goed
let radius = 10 * Math.PI;
```

## Code Formatting Tools
Er zijn verschillende tools beschikbaar om te helpen bij het consistent formatteren van je code:
- [Prettier](https://prettier.io/): Een code formatter die code automatisch consistent maakt volgens de stijlregels.
- [ESLint](https://eslint.org/): Een linter die helpt bij het vinden en oplossen van problemen in je JavaScript-code.
- [EditorConfig](https://editorconfig.org/): Een tool die je helpt bij het onderhouden van consistente codestijlen tussen verschillende editors en IDE's.

## Aanvullende bronnen
Hieronder enkele guides van AirBnB en Google:

- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
