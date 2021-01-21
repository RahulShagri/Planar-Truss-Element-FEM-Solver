import numpy as np
import math


def assemble_stiffness_matrix(element_keys, K, global_mat):
    a = 0
    b = 0
    for i in element_keys:
        b = 0
        for j in element_keys:
            global_mat[i][j] += K[a][b]
            b += 1
        a += 1
    return global_mat


def solve(Node_data, Element_data, A, E, Q, F):
    print("Solver initiated...")

    elements = np.shape(Element_data)[0]
    nodes = np.shape(Node_data)[0]

    #Measuring the cos^2, sine^2, and cos*sin with respect to the X-Axis and the length of each element
    L = np.zeros(elements)
    cos_sin = np.zeros((elements, 3))

    for i in range(elements):
        start_point = Node_data[Element_data[i][0]-1]
        end_point = Node_data[Element_data[i][1]-1]
        L[i] = pow((pow((end_point[0] - start_point[0]), 2) + pow((end_point[1] - start_point[1]), 2)), 0.5)


        cos = (end_point[0] - start_point[0]) / L[i]
        sin = (end_point[1] - start_point[1]) / L[i]
        cos_sin[i][0] = pow(cos, 2)
        cos_sin[i][1] = pow(sin, 2)
        cos_sin[i][2] = cos*sin

    #Assemblying element keys
    temp_node_keys = np.arange(0, nodes*2, 1).reshape(nodes, 2)
    Element_keys = np.array([])
    Element_data = Element_data.reshape(elements*2)
    for point in Element_data:
        Element_keys = np.append(Element_keys, temp_node_keys[point-1])

    Element_keys = Element_keys.reshape(elements, 4).astype(int)
    del temp_node_keys

    # Assembling the global stiffness matrix
    K_temp = np.array([])

    for a, e, l in zip(A, E, L):
        K_temp = np.append(K_temp, (a * e) / l)

    global_K = np.zeros((nodes*2, nodes*2))

    for i in range(elements):
        K_element = np.array([[cos_sin[i][0], cos_sin[i][2], -cos_sin[i][0], -cos_sin[i][2]],
                              [cos_sin[i][2], cos_sin[i][1], -cos_sin[i][2], -cos_sin[i][1]],
                              [-cos_sin[i][0], -cos_sin[i][2], cos_sin[i][0], cos_sin[i][2]],
                              [-cos_sin[i][2], -cos_sin[i][1], cos_sin[i][2], cos_sin[i][1]]])

        K_element = K_temp[i] * K_element

        global_K = assemble_stiffness_matrix(Element_keys[i], K_element, global_K)

        print("\nElement Stiffness matrix: " + str(i + 1))
        print(K_element)

    print("\nGlobal element stiffness matrix is ")
    print(global_K)

    global_Q = Q.reshape(nodes*2, 1).astype(float)
    global_F = F.reshape(nodes*2, 1).astype(float)

    X = np.where(global_Q != 1)
    rows = np.unique(X[0]).astype(int)

    for i in rows:
        for f in range(elements + 1):
            global_F[f] -= global_K[f][i] * float(global_Q[i])

    F_before_elimination = global_F
    global_F = np.delete(global_F, rows, 0)

    print("\nOn applying boundary conditions and using the elimination approach.")

    print("\nThe global force vector after elimination is:")
    print((global_F))

    K_before_elimination = global_K
    global_K = np.delete(global_K, rows, 0)
    global_K = np.delete(global_K, rows, 1)

    print("\nThe global stiffness matrix after elimination is: ")
    print(global_K)

    unknown_disp = np.linalg.lstsq(global_K, global_F)[0]
    print(unknown_disp)

    i = 0

    for row in range(nodes*2):
        if row in rows:
            continue
        else:
            global_Q[row] = unknown_disp[i]
            i += 1

    del i

    print("\n The global displacement vector with all the known and unknown values is:")
    print(global_Q)

    #Calculating stresses and strains in the elements
    stress = np.zeros(elements)
    strain = np.zeros(elements)
    for i in range(elements):
        q = global_Q[np.ix_(Element_keys[i], [0])]
        c_s = np.array([-math.sqrt(cos_sin[i][0]), -math.sqrt(cos_sin[i][1]), math.sqrt(cos_sin[i][0]), math.sqrt(cos_sin[i][1])])
        stress[i] =(E[i] / L[i]) * c_s.dot(q)

        #print(f"for element {i}, q is {[q[0], q[1]]} and {[q[2], q[3]]}")

        #print(Node_data[(Element_keys[i][0] / 2).astype(int)] + np.array([q[0][0], q[1][0]]))

        start_point = Node_data[((Element_keys[i][0]) / 2).astype(int)] + np.array([q[0][0], q[1][0]])
        end_point = Node_data[((Element_keys[i][2]) / 2).astype(int)] + np.array([q[2][0], q[3][0]])

        #print(f"for element {i} start point is {start_point} and end point is {end_point}")

        final_length = pow((pow((end_point[0] - start_point[0]), 2) + pow((end_point[1] - start_point[1]), 2)), 0.5)
        strain[i] = abs(final_length - L[i]) / L[i]


    stress = stress.reshape(elements, 1)
    print("\nThe element stress vector is:")
    print(stress)

    strain = strain.reshape(elements, 1)
    print("\nThe element strain vector is:")
    print(strain)

    #Reaction forces at support reactions
    reaction_force = np.array([])

    for  i in range(nodes*2):
        if Q[i] == 0:
            reaction_force = np.append(reaction_force, K_before_elimination[i].dot(global_Q) - F_before_elimination[i][0])
        else:
            reaction_force = np.append(reaction_force, "No support reaction")


    reaction_force = reaction_force.reshape((nodes*2, 1))
    print("\nThe support reaction forces are:")
    print(reaction_force)

    #Calculating the total displacement and final coordinates (1000 times exaggerated) for each node

    total_nodal_displacement = np.array([])
    new_node_data = np.array([])
    Node_data = Node_data.reshape(nodes*2)

    for i in range(0, nodes*2, 2):
        displacement = math.pow(math.pow(global_Q[i][0], 2) + math.pow(global_Q[i+1][0], 2), 0.5)
        total_nodal_displacement = np.append(total_nodal_displacement, displacement)

    total_nodal_displacement = total_nodal_displacement.reshape((nodes, 1))

    print("\nSolver terminated.")

    return global_Q, stress, strain, reaction_force, total_nodal_displacement

#----test values----
'''Node_data_test = np.array([[0, 0],
                          [750, 0],
                          [750, 1000],
                           [0, 1000]])
Element_data_test = np.array([[1, 2],
                              [2, 3],
                              [3, 4],
                              [4, 2]])
A_test = np.array([1000, 1000, 1000, 1000])         #mm2
E_test = np.array([200e3, 200e3, 200e3, 200e3])     #MPa
Q_test = np.array([0, 0, 1, 0, 1, 1, 0, 0])
F_test = np.array([0, 0, 20e3, 0, 0, 0, 0, 0])      #N'''

'''Node_data_test = np.array([[0., 0.],
                           [5000., 4000.],
                           [5000., 0.],
                           [10000., 0.]])
Element_data_test = np.array([[1, 2],
                              [2, 3],
                              [2, 4],
                              [4, 3],
                              [1, 3]])

A_test = np.array([500., 500., 500., 500., 500.])
E_test = np.array([200000., 200000., 200000., 200000., 200000.])
Q_test = np.array([0., 0., 1., 1., 1., 1., 0., 0.])
F_test = np.array([0., 0., 0., -20000., 0., 0., 0., 0.])'''

#solve(Node_data_test, Element_data_test, A_test, E_test, Q_test, F_test)