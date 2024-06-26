# entrées: 
# sommets -> Liste des sommets [(sommet_i, position_x_i, position_y_i)]
# all_arrete -> Liste de toutes les arrêtes [(sommet_i, sommet_j)]
# all_arrete_poid -> Dictionnaire de toutes les arrêtes et leur poid: {(sommet_i, sommet_j): poid}
# sortie : on renvoie une liste de sommets représentants un cycle sous format [(sommet_i, position_x_i, position_y_i)]
def get_chemin_pulp(sommets, all_arrete, all_arrete_poid):
    # Liste de tous les sommets
    all_sommets = [i for i in range(len(sommets))]

    # Variables de décision
    x = pulp.LpVariable.dicts('x', all_arrete, cat=pulp.LpBinary)
    u = pulp.LpVariable.dicts('u', all_sommets, lowBound=1, upBound=len(all_sommets), cat=pulp.LpInteger)

    # Création du modèle
    model = pulp.LpProblem("TSP", pulp.LpMinimize)

    # Fonction objectif (on multiplie les arrêtes par leur poid)
    model += pulp.lpSum(x[i, j]*all_arrete_poid[i, j] for (i, j) in all_arrete)



    # Contraintes de degré
    for sommet in all_sommets:
        # il faut que le degré sortant de l'arrête soit exactement 1
        model += pulp.lpSum(x[i, k] for (i, k) in all_arrete if i==sommet) == 1
        # il faut que le degré entrant de l'arrête soit exactement 1
        model += pulp.lpSum(x[i, k] for (k, i) in all_arrete if k==sommet) == 1

    # Elimination des SubTours
    n = len(all_sommets)
    for (i, j) in all_arrete:
        # Eviter de définir une contrainte pour le sommet de départ
        if i != 0 and j != 0:
            # grâce a cette contrainte, on supprime les Sub tour
            model += u[i] - u[j] + n * x[i, j] <= n - 1, f"SEC_{i}_{j}"

    # Fixer le point de départ
    model += u[0] == 1, "Start"

    # Résolution du modèle
    solver = pulp.PULP_CBC_CMD(msg=0)
    model.solve(solver)

    # Affichage des résultats
    print("Status:", pulp.LpStatus[model.status])
    print("Objective:", pulp.value(model.objective))

    # On stocke toutes les arrêtes choisies
    result = {}
    for (i, j) in all_arrete:
        if pulp.value(x[i, j]) == 1:
            result[i] = (i, j)

    # On renvoies la liste des arrêtes sous format : [(sommet_i, position_x_i, position_y_i)]
    final_result = []
    next_visited = 0
    (i, j) = (0, 0)
    for t in range (len(result)+1):
        #print("next visited = ", next_visited)
        (i, j) = result[next_visited]
        final_result.append((i+1, sommets[i][1], sommets[i][2]))
        next_visited = j
    return final_result




# entrées: 
# sommets -> Liste des sommets [(sommet_i, position_x_i, position_y_i)]
# all_arrete -> Liste de toutes les arrêtes [(sommet_i, sommet_j)]
# all_arrete_poid -> Dictionnaire de toutes les arrêtes et leur poid: {(sommet_i, sommet_j): poid}
# sortie : on renvoie une liste de sommets représentants un cycle sous format [(sommet_i, position_x_i, position_y_i)]
def get_chemin_gurobi(sommets, all_arrete, all_arrete_poid):

    # Liste de tous les sommets
    all_sommets = [i for i in range(len(sommets))]
    
    # Variables de décision
    model = gp.Model("TSP")
    x = model.addVars(all_arrete, vtype=GRB.BINARY, name="x")
    u = model.addVars(all_sommets, lb=1, ub=len(all_sommets), vtype=GRB.INTEGER, name='u')

    # Fonction objectif (on multiplie les arrêtes par leur poid)
    model.setObjective(gp.quicksum(x[i, j]*all_arrete_poid[i, j] for (i, j) in all_arrete), GRB.MINIMIZE)

    # Contraintes de degré
    for sommet in all_sommets:
        # il faut que le degré sortant de l'arrête soit exactement 1
        model.addConstr(gp.quicksum(x[i, k] for (i, k) in all_arrete if i==sommet) == 1)
        # il faut que le degré entrant de l'arrête soit exactement 1
        model.addConstr(gp.quicksum(x[i, k] for (k, i) in all_arrete if k==sommet) == 1)

    # Elimination des SubTours
    n = len(all_sommets)
    for (i, j) in all_arrete:
        # Eviter de définir une contrainte pour le sommet de départ
        if i != 0 and j != 0:  
            model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1, f"SEC_{i}_{j}")
    model.addConstr(u[0] == 1, "Start")
    model.optimize()

    # Affichage des résultats
    print("Status:", model.Status)
    print("Objective:", model.ObjVal)

    # On stocke toutes les arrêtes choisies
    result = {}
    for (i, j) in all_arrete:
        if x[i, j].X > 0.5:
            result[i] = (i, j)

    # On renvoies la liste des arrêtes sous format : [(sommet_i, position_x_i, position_y_i)]
    #print("result = ", result)
    final_result = []
    next_visited = 0
    (i, j) = (0, 0)
    for t in range (len(result)+1):
        print("next visited = ", next_visited)
        (i, j) = result[next_visited]
        final_result.append((i+1, sommets[i][1], sommets[i][2]))
        next_visited = j
    #print("final_result = ", final_result)
    return final_result


# entrée: 
# all_cities -> tous les sommets
def create_connexe_graph(all_cities):
    # Liste de positions correspondant aux sommets
    points = []
    for i in all_cities:
        points.append((i[1], i[2]))

    # triangulation de Delaunay
    tri = Delaunay(points)
    G = nx.Graph()
    
    # Ajouter des sommets
    for i, point in enumerate(points):
        G.add_node(i, pos=(point[0], point[1]))

    # Ajouter des arêtes basées sur la triangulation
    for simplex in tri.simplices:
        for i in range(3):
            for j in range(i+1, 3):
                G.add_edge(simplex[i], simplex[j])

    # Dessiner le graphe
    #node_pos = nx.get_node_attributes(G, 'pos')
    # plt.figure(figsize=(8, 6))
    # nx.draw(G, pos=node_pos, with_labels=True, node_size=500, node_color="skyblue", font_size=15, font_weight="bold")
    # plt.show()
    
    # Renvoies du résultat
    result = []
    for i in G.edges():
        result.append(i)
        result.append((i[1], i[0]))
    print(result)
    return result



# entrée: 
# cities -> Liste des villes (ou sommets)
# data -> instance d'une classe 
# choice_solver -> string pour savoir quel solveur utiliser (PULP, GUROBIPY)
# sortie: Pas de retour
def start_getting_best_chemin(cities, data, choice_solve="GUROBIPY"):
    all_edges = []
    weighed_edges = {}
    # on créée un graphe connexe planaire
    all_edges = create_connexe_graph(cities, weighed_edges)

    # création des arrêtes pondérées
    for (i, j) in all_edges:
        weighed_edges[(i, j)] = data.calculateDistance(i, j) 

    if choice_solve == "GUROBIPY":
        best_chemin = get_chemin_gurobi(cities, all_edges, weighed_edges)
    else:
        best_chemin = get_chemin_pulp(cities, all_edges, weighed_edges)
    print("best chemin = ", best_chemin)
    display_sol(best_chemin, cities)
    return best_chemin


data = Cities()
start_getting_best_chemin(data.cities, data, "GUROBIPY")
