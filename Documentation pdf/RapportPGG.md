




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

    * 4.1 [Inforce probability](#inforce)

    * 4.2 [Sinistralité par produit](#nbm)
    
    * 4.3 [Sinistralité des complémentaires](#sincompl)
    
    * 4.4 [Nombre de rachat](#nblapse)
        + 4.4.1 [Produits sans réduction possible](#lapsesansred)
        + 4.4.2 [Produits avec réduction possible](#lapseavecred)
        
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

Sinistralité utilisées ici ainsi que la mortalité d'expérience


\newpage.


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

\newpage.





# Calcul des variables utilisées <a name="var"></a>

Les diverses variables utilisée pour calculer le "Best estimated liabilities" varient en fonction du produit. En effet, le calcul des probabilités que la police soit toujours en vigueur va dépendre si il y a possibilité de réduction pour le produit en question.

La sinistralité va également dépendre si celle-ci est calculée avec un taux de sinistre sur primes ou alors simplement avec les probabilités de décès (pour les assurances temporaires décès).

En ce qui concerne les reserves ainsi que les valeur de rachat, ces valeurs seront calculées en fonction de chaque produit.

## Inforce probability <a name="inforce"></a>

Calcul des inforce probability. Il existe deux calculs pour connaître les inforce probability qui dépend du produits. Il y a donc les produits sans possibilité de réduction, et les produits avec possibilité de réduction.

### Inforce pour les produits sans possibilité de réduction

Ici on insère le calcul 

### Inforce pour les produits avec possibilité de réduction

Ici on insère le calcul 

``` python
class FU(Portfolio):
    mods=[8,9]
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        
on peut insérer du code python avec ce format
```

Exemple d'ajout de calcul Latex :

La fonction $f$ est définie par

\begin{equation}
  f(x) = x-1
\end{equation}

On a alors
\begin{equation}
   f(x) = 0 \iff x = 1
\end{equation}


## Sinistralité par produit  <a name="nbm"></a>

Le calcul de la sinistralité va également dépendre du produit. Tout les sinistres de nos produits (hors rachat) sont calculés avec un taux de sinitralité/primes, à l'exception des produits suivants:

 - Funérailles modalité 8 et 9
 - Autre produits ???
 
 Ces produits ont une sinistralité qui va dépendre des probabilités de décès mais aussi de l'hypothèse de mortalité d'expérience. Pour tout les autres produits, la sinistralité va donc dépendre de l'hypothèse de sinistralité ainsi que du montant des primes.
 
 
 \newpage.
 
## Sinistralité des complémentaires <a name="sincompl"></a>
 
Le taux de sinistralité des complémentaires est défini dans les hypothèses. La sinistralité des complémentaires sera donc déterminée en fonction de ce taux ainsi que de la prime complémentaire en question
 
 \newpage.
 
## Nombre de rachat <a name="nblapse"></a>

Le calcul du nombre de rachat sera différent si un produit permet la réduction ou non.

### Nombre de rachat : Produits sans réduction possible <a name="lapsesansred"></a>
    
Nous avons la probabilité de décès mensuel $qx^m$ qui est défini par

\begin{equation}
  qx^m = 1-(1-qx)^{1/12}
\end{equation}

avec ${\Pi}_{t}$ la probabilité au temps $t$ que la police soit toujours en vigueur au temps $t+1$, $W_{t}$ la probabilité au temps $t$ qu'une police soit annulée au temps $t+1$ ainsi que $W^m_{t}$ la probabilité au temps $t$ que la police soit annulée au temps $t + 1/12$ (au mois prochain).

$W_{t}$ vien des hypothèses de rachat. Nous trouvons la probabilité d'annulation mensuel

\begin{equation}
 W^m_{t} = 1-(1-W_{t})^{1/12} 
\end{equation}



nous avons ensuite le nombre d'annulation $Surr_t$ au temps t

\begin{equation}
  Surr_t = {\Pi}_{t-1} W^m_{t}(1- \frac{qx^m}{2})
\end{equation}


### Nombre de rachat : produit avec réduction possible <a name="lapseavecred"></a>

Lorsque la réduction est possible nous aurons différents états possible :

- Police réduite
- Police en vigueur
- Police annulée

Nous devons donc connaître :

- Le nombre de survivants pour une police non réduite
- Le nombre de nouvelles réductions pour une police en vigueur
- Le nombre total de polices réduites
- Le nombre d'annulation pour une police en vigueur
- Le nombre d'annulation pour une police réduite
- Le nombre de décès pour une police en vigueur
- Le nombre de décès pour une police réduite


Nous avons les variables $qx$, $W_t$, $R_t$ venant des hypothèses, avec $R_t$ la probabilité qu'une police en vigueur soit réduite au temps $t+1$ et $frac$ étant le fractionnement de la police.

Nous trouvons d'abord $R_t^m$ la probabilité mensuelle de réduction

\begin{equation}
  R_t^m = 1-(1-R_t)^{1/frac}
\end{equation}





















    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
   \newpage. 
    
    
# Annexes <a name="annexes"></a>

$qx$ : probabilité de décès annuel pour une personne agée de $x$ années

$W_t$ : probabilité qu'une police en vigueur au temps $t$ soit annulée au temps $t+1$

$frac$ : fractionnement de la police