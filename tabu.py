class Tabu():

    def tabu_list(self, cities, data, k):
        vertexs = []
        all_heighed_vertex = {}
        for i in range (len(cities)):
            for j in range (len(cities)):
                if i == j:
                    continue
                all_heighed_vertex[(i, j)] = data.calculateDistance(i+1, j+1)
            vertexs.append(cities[i][0]-1)

        vertexs.append(vertexs[0])
        #print(all_heighed_vertex)
        #print("all vertes = ", vertexs)


        tabous_list = set()
        max_tabou = 2
        current_list = copy.deepcopy(vertexs)
        iterration = 0
        max_iterration = 200

        global_min = self.calcul_cout(vertexs, all_heighed_vertex)
        while iterration < max_iterration:
            #print("current list = ", current_list)
            #print("new global min = ", global_min)
            all_neighbors = self.get_neighbors(current_list, k)
            local_min = float('inf')
            local_neighbor = []
            #print("all neighbor = ", all_neighbors)
            for neighbor in all_neighbors:
                cout = self.calcul_cout(neighbor, all_heighed_vertex)
                # pour la premiere ittération 
                #print("new local min = ", local_min)
                #print("for neighbor = ", neighbor, " cout = ", cout)
                if cout <= local_min:
                    if tuple(neighbor) in tabous_list and local_min >= global_min:
                        continue
                    local_min = cout
                    local_neighbor = neighbor
                    #print("NEW NEIGBOR = ", local_neighbor)
            
            # si le le local min est supérieur au gloabal min, on ne peux plus améliorer le chemin, fin du programmme
            if local_min < global_min:
                if len(tabous_list) >= max_tabou:
                    tabous_list.pop()
                #print("NEW CURRENT LIST = ", local_neighbor)
                tabous_list.add(tuple(current_list))
                current_list = local_neighbor
                global_min = local_min





                # final_result = []
                # for i in current_list:
                #     final_result.append(cities[i])
                # #############################
                # display_sol(final_result, cities)
            else:
                break

            iterration += 1

        #print("final list = ", current_list, " global min = ", global_min)
        final_result = []
        for i in current_list:
            final_result.append(cities[i])
        return final_result, global_min


    def calcul_cout(self, vertexs, weighed_edges):
        cout = 0
        for i in range (len(vertexs)-1):
            cout += weighed_edges[(vertexs[i], vertexs[i+1])]
        return cout

    """
    def get_neighbors(vertexs, k=0):
        all_combi = []
        for i in range (1, len(vertexs)-1):
            for j in range (i, len(vertexs)-1):
                if i == j:
                    continue
                current = copy.deepcopy(vertexs)
                old_i = current[i]
                old_j = current[j]
                current[i] = old_j
                current[j] = old_i
                all_combi.append(current)
        return all_combi
    """

    def get_neighbors(self, lst, k):
        # Fixer le premier et le dernier élément
        first, last = lst[0], lst[-1]
        middle = lst[1:-1]
        
        permutations = []
        
        for _ in range(k):
            # Créer une copie de la liste du milieu
            permuted_middle = middle[:]
            
            # Choisir aléatoirement deux indices différents à permuter
            i, j = random.sample(range(len(permuted_middle)), 2)
            
            # Permuter les éléments
            permuted_middle[i], permuted_middle[j] = permuted_middle[j], permuted_middle[i]
            
            # Reconstituer la liste complète
            new_permutation = [first] + permuted_middle + [last]
            permutations.append(new_permutation)
        
        return permutations




tabu = Tabu()
result = tabu.tabu_list(data.cities, data, 500)
