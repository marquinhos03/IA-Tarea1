import heapq

class Algoritmo:

    # Usualmente visto con PriorityQueue(), pero aqui se usa HeapQ
    @staticmethod
    def Busqueda_Costo_Uniforme(nodo_inicial, es_meta, expandir):
        frontera = []
        heapq.heappush(frontera, (0, nodo_inicial))

        costos_minimos = {nodo_inicial: 0}
        padres = {nodo_inicial: None}

        nodo_objetivo = None

        while frontera:
            costo_g, nodo_actual = heapq.heappop(frontera)

            if es_meta(nodo_actual):
                nodo_objetivo = nodo_actual
                break

            if costo_g > costos_minimos[nodo_actual]:
                continue

            for (costo_arista, hijo) in expandir(nodo_actual):
                nuevo_costo = costo_g + costo_arista

                if hijo not in costos_minimos or nuevo_costo < costos_minimos[hijo]:
                    costos_minimos[hijo] = nuevo_costo
                    padres[hijo] = nodo_actual
                    heapq.heappush(frontera, (nuevo_costo, hijo))

        if nodo_objetivo:
            camino_encontrado = []
            nodo_paso = nodo_objetivo

            while padres[nodo_paso] is not None:
                camino_encontrado.append(nodo_paso)
                nodo_paso = padres[nodo_paso]

            #camino_encontrado.append(nodo_inicial)

            camino_encontrado.reverse()
            return camino_encontrado

        return []