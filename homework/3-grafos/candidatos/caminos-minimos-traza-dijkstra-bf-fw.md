# Traza de Dijkstra, Bellman-Ford y Floyd-Warshall sobre un mismo grafo

Considere el grafo dirigido con nodos $A, B, C, D$ y los siguientes arcos:

| Arco      | Peso |
|-----------|-----:|
| $A \to B$ | 2    |
| $A \to C$ | 5    |
| $C \to B$ | −4   |
| $B \to D$ | 4    |
| $D \to A$ | 1    |
| $D \to C$ | 2    |

**(a)** Ejecute Dijkstra desde $A$, sin modificar un nodo una vez extraído (rompa empates alfabéticamente). Escriba el orden en que se extraen los nodos y el valor de $d$ después de cada extracción.

**(b)** Ejecute Bellman-Ford desde $A$ relajando los arcos, en cada ronda, en este orden: $B \to D$, $C \to B$, $D \to C$, $D \to A$, $A \to B$, $A \to C$. Escriba $d$ al final de cada ronda. Haga las $n - 1$ rondas y la ronda adicional de verificación de ciclos negativos.

**(c)** Compare los resultados de (a) y (b). ¿Cuál es correcto? ¿En qué paso se equivoca el otro algoritmo, y por qué?

**(d)** Ejecute Floyd-Warshall. Escriba la matriz inicial y la matriz después de cada nodo intermedio $k = A, B, C, D$.

**(e)** ¿Qué relación hay entre la fila $A$ de la matriz final y el resultado de (b)? Si necesitara las distancias entre todos los pares de nodos en un grafo denso con pesos negativos, ¿usaría Floyd-Warshall o correría Bellman-Ford desde cada nodo? Justifique con la complejidad.

## Solución

**(a)** Orden de extracción: $A, B, C, D$.

| Extrae | $d[A]$ | $d[B]$ | $d[C]$ | $d[D]$ |
|--------|------:|------:|------:|------:|
| $A$    | 0 | 2 | 5 | ∞ |
| $B$    | 0 | 2 | 5 | 6 |
| $C$    | 0 | 2 | 5 | 6 |
| $D$    | 0 | 2 | 5 | 6 |

Al extraer $C$, la relajación $C \to B$ daría $5 - 4 = 1 < 2$, pero $B$ ya fue extraído y no se modifica.

**(b)**

| Ronda | $d[A]$ | $d[B]$ | $d[C]$ | $d[D]$ |
|-------|------:|------:|------:|------:|
| 1     | 0 | 2 | 5 | ∞ |
| 2     | 0 | 1 | 5 | 6 |
| 3     | 0 | 1 | 5 | 5 |
| 4 (verificación) | 0 | 1 | 5 | 5 |

La ronda 4 no cambia nada, así que no hay ciclos negativos alcanzables desde $A$. Con este orden de arcos se necesitan las $n - 1 = 3$ rondas completas.

**(c)** Bellman-Ford es correcto: $\delta(A, B) = 1$ por $A \to C \to B$, y $\delta(A, D) = 5$ por $A \to C \to B \to D$. Dijkstra se equivoca al extraer $B$ con $d[B] = 2$: supone que ningún camino que pase por un nodo aún no extraído puede ser más barato, lo cual solo vale con pesos no negativos. El error se propaga a $D$, cuya distancia se calculó a partir del valor equivocado de $B$.

**(d)** Filas = origen, columnas = destino, en orden $A, B, C, D$.

$D^{(0)}$:
```
A [ 0,  2,  5,  ∞]
B [ ∞,  0,  ∞,  4]
C [ ∞, -4,  0,  ∞]
D [ 1,  ∞,  2,  0]
```

$k = A$ (cambia $DB$):
```
A [ 0,  2,  5,  ∞]
B [ ∞,  0,  ∞,  4]
C [ ∞, -4,  0,  ∞]
D [ 1,  3,  2,  0]
```

$k = B$ (cambian $AD$, $CD$):
```
A [ 0,  2,  5,  6]
B [ ∞,  0,  ∞,  4]
C [ ∞, -4,  0,  0]
D [ 1,  3,  2,  0]
```

$k = C$ (cambian $AB$, $AD$, $DB$):
```
A [ 0,  1,  5,  5]
B [ ∞,  0,  ∞,  4]
C [ ∞, -4,  0,  0]
D [ 1, -2,  2,  0]
```

$k = D$ (cambian $BA$, $BC$, $CA$):
```
A [ 0,  1,  5,  5]
B [ 5,  0,  6,  4]
C [ 1, -4,  0,  0]
D [ 1, -2,  2,  0]
```

La diagonal queda en cero, lo que confirma que no hay ciclos negativos.

**(e)** La fila $A$ de la matriz final, $[0, 1, 5, 5]$, coincide con el resultado de Bellman-Ford desde $A$. Floyd-Warshall cuesta $O(n^3)$. Correr Bellman-Ford desde cada nodo cuesta $n \cdot O(nm) = O(n^2 m)$, que en un grafo denso ($m \in \Theta(n^2)$) es $O(n^4)$. Conviene Floyd-Warshall.
