
---
title: "Modèle PGG en Python"
author: [Joël Da Costa Oliveira, Robin Wengi, Fredéric Tauxe]
date: "2019-09-12"
keywords: [Markdown, Example]
...





# Table des matières
- 1 [Introduction](#Intro)

- 2 [Les hypothèses utilisées](#hypo)

    - 2.1 [Taux de chute](#lapse)
    - 2.2 [Courbe de rendement](#rdt)
    - 2.3 [Coûts](#exp)
    - 2.4 [Sinistralité](#sin)
    
- 3 [Les scénarios](#scenario)

    * 3.1 [Scénario 0](#scenario0)
    * 3.2 [Scénario 1](#scenario1)
    * 3.3 [Scénario 2](#scenario2)
    * 3.4 [Scénario 3](#scenario3)
    * 3.5 [Scénario 4](#scenario4)

- 4 [Calcul des variables utilisée](#var)

    * 4.1 [Inforce](#Force3)

    * 4.2 [Sinistralité par produit](#nbm)
    
    * 4.3 [Sinistralité des complémentaires](#sincompl)
    
    * 4.4 [Nombre de rachat](#nblapse)
    
    * 4.5 [Nombre de réduction](#nbred)
    
    * 4.6 [Reserves et valeur de rachat](#resVR)
        + 4.6.1 [Force 3](#mod1)
        + 4.6.2 [Epargne plus](#mod2)
        + 4.6.3 [Império Prévoyance](#mod3)
        + 4.6.4 [Prévoyance à capital décroissant](#mod4)
        + 4.6.5 [Epargne Investissement](#mod6)
        + 4.6.6 [Epargne Investissement?](#mod7)
        + 4.6.7 [Nouvelle Génération](#mod10)
        + 4.6.8 [Sérénité](#mod11)
        + 4.6.9 [Epargne Retraite libre](#mod28)
        + 4.6.10 [Epargne Jeune libre](#mod29)
        + 4.6.11 [Epargne Retraite employés](#mod30)
        + 4.6.12 [Epargne Jeune liée](#mod31)
        + 4.6.13 [Epargne Sécurité](#mod32)
        + 4.6.14 [Epargne Projet ancient](#mod33)
        + 4.6.15 [Epargne Projet](#mod36)
    
    * 4.6 [Commissions par produit](#commprod)
    
   
- 5 [Calcul du BEL](#bel)
    * 5.1 [Primes](#p)
    * 5.2 [Sinistres et annulations](#sinistres)
    * 5.3 [Commissions](#com)
    * 5.4 [Coûts](#coûts)
    * 5.5 [Résultat](#rés)

\newpage.

# Introduction <a name="Intro"></a>

L'objectif de cette documentation est d'expliquer le fonctionnement du modèle de calcul de la provision global de gestion.

\newpage.

# Les hypothèses utilisées <a name="Hypo"></a>

Explication brève des hypothèses, résumé la façon dont ces hypothèses sont calculées sans entrer dans les détails.

## Taux de chute <a name="lapse"></a>

Hypothèses lapse ici

## Courbe de rendement <a name="rdt"></a>

Courbe de rendement ici 

## Coûts <a name="exp"></a>

Modèle de frais, coût par produit, inflation des coûts

## Sinistralité <a name="sin"></a>

Sinistralité utilisées ici





# Scénarios <a name="scenario"></a>

Explication brève des scénarios, expliquer la façon dont les hypothèses sont stressée dans le modèle.


## Scénario 0 Best Estimate <a name="scenario0"></a>

Pas grand chose à dire, modèle de base


## Scénario 1 Best Estimate + marge <a name="scenario1"></a>

Explication de la marge ajouté au scénario BE 


## Scénario 2 Biométrie et frais <a name="scenario2"></a>

Explication du stress des hypothèse pour ce scénario


## Scénario 3 Rendement et longévité <a name="scenario3"></a>

Explication du stress des hypothèse pour ce scénario


## Scénario 4 Annulation +24.75% <a name="scenario4"></a>

Expliquer comment l'annulation est impacté dans le modèle


## Scénario 5 Annulation -24.75% <a name="scenario5"></a>

Expliquer comment l'annulation est impacté dans le modèle


# Calcul des variables utilisée <a name="var"></a>

Les diverses variables utilisée pour calculer le "Best estimated liabilities" varient en fonction du produit. En effet, le calcul des probabilités que la police soit toujours en vigueur va dépendre si il y a possibilité de réduction pour le produit en question.

La sinistralité va également dépendre si celle-ci est calculée avec un taux de sinistre sur primes ou alors simplement avec les probabilités de décès (pour les assurances temporaires décès).

En ce qui concerne les reserves ainsi que les valeur de rachat, ces valeurs seront calculées en fonction de chaque produit.











## Equation de test <a name="subparagraph1"></a>

![equation](https://latex.codecogs.com/gif.latex?\sum&space;{x_{i}}^{})

# WOW Magnifique

## Mon image <a name="chevre"></a>

![maxresdefault](https://user-images.githubusercontent.com/52786448/64136301-f521f800-cdf0-11e9-83ab-a1714ed7487b.jpg)


# Titre 1

## Titre 2

### Titre 3

#### Titre 4
Texte du titre 4

Ici j'ajoute une table

|   | hh |    |   |   |
|---|----|---:|---|---|
|   |    |    | h |   |
|   |    | ff |   |   |
|   |    |    |   |   |

Et une équation
Thèse
 
 J'ajoute ça sur bracket
 
![Monéeuqation](https://latex.codecogs.com/gif.latex?\sum_{1}^{44}\alpha&space;^{j})



# Titre new
* une puce
* une autre
    * une sous puce
    
1. Numérotation
2. Numéro2
3. Etc...

> Je cite un texte ici
>
Citation du futur

>> Réponse à cette citation

Rendez-vous sur le [Site du Zéro](http://www.siteduzero.com) pour tout apprendre à partir de Zéro !

# Les images de frankenstein
 ![Nomdemonimage](https://i2.wp.com/l-express.ca/wp-content/uploads/2018/01/Frankenstein-9-janvier.jpg?w=300&ssl=1)
 

