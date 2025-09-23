<p align="center">
  <img src="asset/flow_logo_small.png" alt="logo"/>
</p>

## Informations
Application pour permettre l'ex�cution de task ou de workflow bas� sur des scripts Python.
Un task repr�sente un ensemble de fonction.
Un flow repr�sente un ensemble de fonction o� la sortie de la fonction A devient les param�tres de la fonction suivante.


### Pr�requis
- Python 3
<br>

## Installation
```console
pip install zpp_flow
```
<br>

## Utilisation

### config

La commande permet de lister les param�tres de configuration. 
Il est possible de les �diter en rajoutant le nom du param�tre et sa valeur � la commande

```console
flow config PARAM_NAME VALUE
```

### run

La commande permet d'ex�cuter une task ou un flow. Pour cela, il suffit de renseigner le nom de la task.

```console
flow run TASK_NAME
```

En param�tre suppl�mentaire, il est possible d'utiliser:
<br>
**--task** pour filtrer sur les task
<br>
**--flow** pour filtrer sur les flow
<br>
**--debug** pour afficher la totalit� des retour de code
<br>
**--repeat** INT pour r�peter les actions � intervalles r�guli�res. Par d�faut l'intervalle est en seconde mais il est possible d'utiliser des cl�s de temps (m: minutes, h: heures, d: jours)
<br>
**--starter** HH:MM:SS pour d�marrer la task � un moment pr�cis (les secondes ne sont pas obligatoires)
<br>


### list

La commande permet d'afficher la liste des task et flow disponibles.

```console
flow list
```

### info

La commande permet d'afficher les d�tails sur une task ou un flow sp�cifique.

```console
flow info TASK_NAME
```

### details

La commande permet d'afficher les d�tails pour l'ensemble des task et flow disponibles.

```console
flow details
```

### fabric

La commande permet d'ouvrir le r�pertoire de script

```console
flow fabric
```

### tree:

La commande permet d'afficher l'arborescence du r�pertoire de script

```console
flow tree
```

### pull:

La commande permet de r�cup�rer un fichier depuis le r�pertoire de script

```console
flow pull FILE_NAME
```

Il est possible de rajouter l'option **--output** pour pr�ciser le chemin de sortie

### push:

La commande permet d'envoyer un fichier dans le r�pertoire de script

```console
flow push FILE_NAME
```

Il est possible de rajouter l'option **--folder** pour pr�ciser le r�pertoire de destination

### pop:

La commande permet de supprimer un script du r�pertoire de script

```console
flow pop FILE_NAME
```
<br>

## Cr�ation de script

Pour �tre pris en compte par l'application, les scripts doivent une certaine syntaxe.
Chaque fonction est ind�pendante de base et doit avoir un d�corateur @zpp_flow.task ou @zpp_flow.flow
Le d�corateur peut contenir plusieurs param�tres comme **name** pour d�finir le nom de la task ou **order** pour d�finir l'ordre d'ex�cution.

```python
import zpp_flow

@zpp_flow.task
def hello_world():
	print("Bonjour je suis une task")
```

Dans une fonction, il est possible de d�finir des arguments qui pourront �tre utilis�s dans le reste du flow

```python
from zpp_flow.core.runner import set_persist

set_persist(argument, value)
```