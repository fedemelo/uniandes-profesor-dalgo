# Por qué funciona Dijkstra

Sea $G = (V, E, w)$ un grafo dirigido con pesos $w(e) \ge 0$ para todo $e \in E$, y sea $s \in V$ la fuente. Dijkstra mantiene un conjunto $S$ de nodos ya extraídos y, en cada paso, extrae el nodo $u \notin S$ con menor $d[u]$, lo agrega a $S$ y relaja los arcos que salen de $u$. Una vez extraído, $d[u]$ no se vuelve a modificar.

Demuestre que, en el momento en que Dijkstra extrae un nodo $u$, $d[u]$ es el costo del camino más corto de $s$ a $u$. Señale con precisión en qué paso de su argumento usa que los pesos son no negativos.

## Solución

Supóngase, hacia una contradicción, que $u$ es el primer nodo extraído con $d[u]$ mayor que el costo $\delta(s, u)$ del camino más corto. Sea $P$ un camino más corto de $s$ a $u$. En el momento de extraer $u$, $P$ empieza en $S$ (pues $s \in S$) y termina fuera, así que tiene un primer nodo $y \notin S$, cuyo predecesor $x$ en $P$ está en $S$.

Cuando se extrajo $x$, $d[x] = \delta(s, x)$ (porque $u$ es el primer nodo mal extraído) y se relajó $(x, y)$, así que $d[y] \le \delta(s, x) + w(x, y) = \delta(s, y)$, es decir, $d[y] = \delta(s, y)$.

Como los pesos son no negativos, el tramo de $P$ que va de $y$ a $u$ cuesta al menos $0$, así que $\delta(s, y) \le \delta(s, u)$. **Este es el paso que usa la hipótesis.** Entonces $d[y] = \delta(s, y) \le \delta(s, u) < d[u]$, pero Dijkstra eligió $u$ y no $y$, así que $d[u] \le d[y]$. Contradicción.

Con un arco negativo en el tramo de $y$ a $u$, puede pasar que $\delta(s, y) > \delta(s, u)$: un nodo se extrae antes de descubrir un camino más barato que pasa por un nodo extraído después.
