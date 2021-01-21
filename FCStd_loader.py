import sys
import numpy as np

def FCStd_loader(folder_path, file_path, file_name):
    sys.path.append(f"{folder_path}\\bin")
    flag = 0
    try:
        import FreeCAD
        print("FreeCAD loaded successfully.")
    except:
        print("Could not load FreeCAD.")
        flag = 1
        sys.path.remove(f"{folder_path}\\bin")
        return flag, None, None

    else:
        try:
            doc = FreeCAD.open(file_path)
            print("FreeCAD file loaded successfully.")
        except:
            print("Could not load the FreeCAD file.")
            flag = 2
            sys.path.remove(f"{folder_path}\\bin")
            return flag, None, None
        else:
            sketch_obj = doc.Sketch
            sketch_geometry = sketch_obj.Geometry
            elements = len(sketch_geometry)
            element_points = np.array([])
            for element in range(elements):
                start_point = sketch_geometry[element].StartPoint[:-1]
                end_point = sketch_geometry[element].EndPoint[:-1]
                element_points = np.append(element_points, [start_point, end_point])

            element_points = element_points.reshape((elements, 4))
            doc = FreeCAD.closeDocument(file_name[:-6])
            print("FreeCAD file closed successfully after reading.")

            node_values = np.empty((0, 2))
            start_point = [element_points[0][0], element_points[0][1]]
            end_point = [element_points[0][2], element_points[0][3]]
            node_values = np.append(node_values, [start_point], axis=0)
            node_values = np.append(node_values, [end_point], axis=0)

            element_values = np.empty((0, 2))
            element_values = np.append(element_values, [1, 2])

            for point in range(1, elements):
                start_point = [element_points[point][0], element_points[point][1]]
                end_point = [element_points[point][2], element_points[point][3]]

                pos = 0
                node_flag = 0
                while pos < node_values.shape[0]:
                    if start_point == node_values[pos].tolist():
                        element_values = np.append(element_values, pos+1)
                        node_flag = 1
                        break
                    pos += 1

                if node_flag == 0:
                    node_values = np.append(node_values, [start_point], axis=0)
                    element_values = np.append(element_values, pos+1)

                pos = 0
                node_flag = 0
                while pos < node_values.shape[0]:
                    if end_point == node_values[pos].tolist():
                        element_values = np.append(element_values, pos+1)
                        node_flag = 1
                        break
                    pos += 1

                if node_flag == 0:
                    node_values = np.append(node_values, [end_point], axis=0)
                    element_values = np.append(element_values, pos+1)

            element_values = element_values.reshape(elements, 2).astype(int)

            sys.path.remove(f"{folder_path}\\bin")
            return flag, node_values, element_values

#FCStd_loader("E:\\FreeCAD 0.18", "D:\\port_repo\\2D-Truss-Element-2-DOF-FEM-Solver\\truss.FCStd", "truss.FCStd")
