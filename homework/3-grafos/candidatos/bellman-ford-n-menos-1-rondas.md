# Por qué Bellman-Ford necesita solo n − 1 rondas

Sea $G = (V, E, w)$ un grafo dirigido ponderado con $n = |V|$ nodos, posiblemente con pesos negativos, y sea $s \in V$ la fuente. En cada ronda, Bellman-Ford relaja todos los arcos de $E$ una vez, en un orden fijo.

**(a)** Suponga que $G$ no tiene ciclos de peso negativo alcanzables desde $s$. Demuestre que después de $n - 1$ rondas, $d[v]$ es el costo del camino más corto de $s$ a $v$ para todo $v \in V$.

*Ayuda:* demuestre primero que, después de la ronda $i$, $d[v]$ es a lo sumo el costo del camino más corto de $s$ a $v$ que use como máximo $i$ arcos.

**(b)** Explique por qué, si en una $n$-ésima ronda alguna distancia todavía disminuye, $G$ tiene un ciclo de peso negativo alcanzable desde $s$.

## Solución

**(a)** Por inducción sobre $i$. Para $i = 0$, solo $s$ se alcanza con cero arcos y $d[s] = 0$. Supóngase cierto para $i - 1$, y sea $P$ un camino más corto de $s$ a $v$ con a lo sumo $i$ arcos, cuyo último arco es $(u, v)$. El prefijo de $P$ hasta $u$ usa a lo sumo $i - 1$ arcos, así que al terminar la ronda $i - 1$ se tiene $d[u] \le w(P) - w(u, v)$. Durante la ronda $i$ se relaja $(u, v)$, con lo que $d[v] \le d[u] + w(u, v) \le w(P)$. Además, $d[v]$ nunca baja del costo real del camino más corto, porque cada valor de $d[v]$ es el costo de algún camino.

Sin ciclos negativos, todo camino más corto se puede tomar simple: quitar un ciclo de peso no negativo no lo encarece. Un camino simple visita a lo sumo $n$ nodos, es decir, usa a lo sumo $n - 1$ arcos. Por la afirmación anterior con $i = n - 1$, $d[v]$ es el costo del camino más corto.

**(b)** Por (a), si no hubiera ciclos negativos alcanzables, después de $n - 1$ rondas cada $d[v]$ ya sería el costo mínimo, y ninguna relajación posterior podría bajarlo más. Si en la ronda $n$ alguna distancia baja, el grafo no cumple la hipótesis de (a): hay un ciclo negativo alcanzable desde $s$.
