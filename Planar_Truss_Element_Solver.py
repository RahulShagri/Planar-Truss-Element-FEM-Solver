from dearpygui.core import *
from dearpygui.simple import *
from FCStd_loader import *
from Table_API import *
from matrix_assember_and_solver import *
import webbrowser

element_data = None
node_data = None
no_of_elements = None
no_of_nodes = None
Q_result = None
stress_result = None
strain_result = None
reaction_force_result = None
total_displacement_result = None
new_node_result = np.array([])


def run_checks_and_solve(sender, data):
    global Q_result
    global stress_result
    global strain_result
    global reaction_force_result
    global total_displacement_result

    close_popup("Solve Confirmation Window")

    clear_log(logger="log")
    log_info("---- Solver initiated ----", logger="log")
    log_info("Running data checks...", logger="log")

    flag = 0

    A_val = np.zeros(no_of_elements)
    E_val = np.zeros(no_of_elements)
    Q_val = np.zeros((no_of_nodes, 2))
    F_val = np.zeros((no_of_nodes, 2))

    #------checking material properties--------

    if get_value("same_material"):  #For elements with same material
        try:
            A_val = np.full(no_of_elements, float(get_value("##Material Table_0_1")))
            log_info("Area of cross-section values: OK", logger="log")
        except:
            log_error("Please enter a valid value for Area of cross-section.", logger="log")
            flag += 1

        try:
            E_val = np.full(no_of_elements, float(get_value("##Material Table_0_2")))
            log_info("Young's modulus values: OK", logger="log")
        except:
            log_error("Please enter a valid value for Young's Modulus.", logger="log")
            flag += 1

    else:   #For elements with different material
        try:
            for i in range(no_of_elements):
                A_val[i] = float(get_value(f"##Material Table_{i}_1"))

            log_info("A values: OK", logger="log")
        except:
            log_error("Please enter valid values for Area of cross-section.", logger="log")
            flag += 1

        try:
            for i in range(no_of_elements):
                E_val[i] = float(get_value(f"##Material Table_{i}_2"))

            log_info("E values: OK", logger="log")
        except:
            log_error("Please enter valid values for Young's Modulus.", logger="log")
            flag += 1

    #--------checking displacement constraints---------

    for i in range(no_of_nodes):
        x = get_value(f"##Displacement Table_{i}_{1}")
        if not x:
            Q_val[i][0] = 1

        y = get_value(f"##Displacement Table_{i}_{2}")
        if not y:
            Q_val[i][1] = 1


    if np.all(Q_val == 1):
        log_error("No displacement constraints found. Please select at least one.", logger="log")
        flag += 1

    else:
        log_info("Displacement constraints: OK", logger="log")

    #--------checking forces--------
    try:
        for i in range(no_of_nodes):
            x = get_value(f"##Force Table_{i}_{1}")
            y = get_value(f"##Force Table_{i}_{2}")

            if x == "":
                x = 0

            if y == "":
                y = 0

            F_val[i][0] = float(x)
            F_val[i][1] = float(y)

        if not np.any(F_val):
            log_error("No forces found. Please enter at least one force value.", logger="log")
            flag += 1

        else:
            log_info("Force Values: OK", logger="log")

    except:
        log_error("Please enter valid values for nodal Forces.", logger="log")
        flag += 1

    #----------------------------------

    if flag == 1:
        log_error("--- Solver terminated without a solution because 1 error was found. Please resolve the error. ---", logger="log")
        return 0

    elif flag != 0:
        log_error(f"--- Solver terminated without a solution because {flag} errors were found. Please resolve all errors. ---", logger="log")
        return 0

    else:
        log_info("All values have been checked and are valid.", logger="log")
        log_info("Solving...", logger="log")

        Q_val = Q_val.reshape(no_of_nodes*2)
        F_val = F_val.reshape(no_of_nodes*2)

        no_of_support_reactions = np.count_nonzero(Q_val == 0)

        try:
            Q_result, stress_result, strain_result, reaction_force_result, total_displacement_result = solve(node_data, element_data, A_val, E_val, Q_val, F_val)
            log_info("Solution has been calculated!", logger="log")

            log_info("---- Solver terminated ----", logger="log")

        except Exception as e:
            log_error("An exception has occurred while solving. Please check the values entered and try again.",
                      logger="log")
            log_error("--- Solver terminated without a solution. ---", logger="log")
            log_error(f"Exception statement: {e}", logger="log")
            return 0

        add_deformed_sketch(500)
        set_value("Show deformed structure", True)
        set_value("Amplification", 500)
        configure_item("Show deformed structure", enabled=True, tip="")
        configure_item("Amplification", enabled=True, tip="Set deformed amplification scale.")
        add_results_table()


def reset_data(sender, data):

    global element_data
    global node_data
    global no_of_elements
    global no_of_nodes
    global Q_result
    global stress_result
    global strain_result
    global reaction_force_result
    global total_displacement_result
    global new_node_result

    close_popup("Reset Confirmation Window")

    clear_log(logger="log")
    log("Welcome to the 2D Truss Element FEM Solver!", logger="log")

    set_value("folder_path", "")
    set_value("file_path", "")
    configure_item("Import sketch", enabled=False)

    delete_item("3. Material Properties")
    with window("3. Material Properties", x_pos=10, y_pos=245, no_resize=True, no_move=True, no_collapse=True,
                no_close=True, width=450, height=187):
        add_spacing(count=2)
        add_checkbox("same_material", label=" All elements have the same material")
        set_value("same_material", True)
        add_spacing(count=2)
        material_table = SmartTable("Material Table")
        material_table.add_header(["", "Area of cross-section (A)", "Young's modulus (E)"])

    delete_item("4. Boundary Conditions")
    with window("4. Boundary Conditions", x_pos=10, y_pos=442, no_resize=True, no_move=True, no_collapse=True,
                no_close=True, width=450, height=187):
        add_tab_bar("BC Data")

    delete_item("Results")
    add_tab("Results", parent="ResultAndDiagram")

    configure_item("Solve!", enabled=False)
    configure_item("Reset", enabled=False)
    configure_item("Diagram Tools", enabled=False)
    set_value("Show element numbers", True)
    set_value("Show node numbers", True)
    set_value("Show original structure", True)
    set_value("Show deformed structure", True)
    set_value("Amplification", 500)
    configure_item("Show deformed structure", enabled=False, tip="No solution has been calculated yet.")
    configure_item("Amplification", enabled=False, tip="No solution has been calculated yet.")

    clear_plot("Sketch_diagram")

    element_data = None
    node_data = None
    no_of_elements = None
    no_of_nodes = None
    Q_result = None
    stress_result = None
    strain_result = None
    reaction_force_result = None
    total_displacement_result = None
    new_node_result = np.array([])


def load_FCStd(path, file_name):
    global element_data
    global node_data
    global no_of_elements
    global no_of_nodes

    element_data = None
    node_data = None

    folder_path = get_value("folder_path")
    print(f"FreeCAD path is: {folder_path} and the file path is {path}")
    flag, node_data, element_data = FCStd_loader(folder_path, path, file_name)

    if flag == 0 and node_data.all != None and element_data.all != None:
        log_info("FreeCAD has been found and the sketch file has been read successfully.", logger="log")

    elif flag == 1:
        log_error("FreeCAD not found! Please check the folder path.", logger="log")
        return 0

    elif flag == 2:
        log_error("FreeCAD sketch is invalid! Please check the path and the file.", logger="log")
        return 0

    no_of_elements = np.shape(element_data)[0]
    no_of_nodes = np.shape(node_data)[0]

    clear_plot("Sketch_diagram")
    add_original_sketch()
    update_element_annotations(True)
    update_node_annotations(True)

    add_material_table()
    add_displacement_constraint_table()
    add_force_table()

    configure_item("Solve!", enabled=True)
    configure_item("Reset", enabled=True)
    set_value("Show element numbers", True)
    set_value("Show node numbers", True)
    configure_item("Diagram Tools", enabled=True)

# noinspection PyTypeChecker
def update_diagram(sender, data):

    close_popup("Diagram Tools Window")

    if get_value("Show original structure"):
        if get_value("Show deformed structure"):
            clear_plot("Sketch_diagram")
            add_original_sketch()

            if new_node_result.size != 0:
                add_deformed_sketch(get_value("Amplification"))
        if not get_value("Show deformed structure"):
            clear_plot("Sketch_diagram")
            add_original_sketch()

    if not get_value("Show original structure"):
        if get_value("Show deformed structure"):
            clear_plot("Sketch_diagram")
            if new_node_result.size != 0:
                add_deformed_sketch(get_value("Amplification"))

        if not get_value("Show deformed structure"):
            clear_plot("Sketch_diagram")

    if get_value("Show element numbers"):
        update_element_annotations(True)
    if not get_value("Show element numbers"):
        update_element_annotations(False)

    if get_value("Show node numbers"):
        update_node_annotations(True)
    if not get_value("Show node numbers"):
        update_node_annotations(False)


def update_element_annotations(choice):
    if choice == True:
        element_number = 1

        for points in element_data:
            start_point_x = node_data[points[0] - 1][0]
            start_point_y = node_data[points[0] - 1][1]

            end_point_x = node_data[points[1] - 1][0]
            end_point_y = node_data[points[1] - 1][1]

            mid_point_x = (start_point_x + end_point_x) / 2
            mid_point_y = (start_point_y + end_point_y) / 2
            add_annotation("Sketch_diagram", text=f"Element {element_number}", x=mid_point_x, y=mid_point_y, xoffset=0, yoffset=-1, tag=f"Element {element_number}")

            element_number += 1

    else:
        for i in range(no_of_elements):
            delete_annotation("Sketch_diagram", f"Element {i+1}")

def update_node_annotations(choice):
    if choice == True:
        node_number = 1

        for node in node_data:
            add_annotation("Sketch_diagram", text=f"Node {node_number}", x=node[0], y=node[1], xoffset=-1, yoffset=1, tag=f"Node {node_number}")
            node_number += 1

    else:
        for i in range(no_of_nodes):
            delete_annotation("Sketch_diagram", f"Node {i+1}")

# noinspection PyTypeChecker
def add_original_sketch():

    element_number = 1

    for points in element_data:
        start_point_x = node_data[points[0]-1][0]
        start_point_y = node_data[points[0]-1][1]

        end_point_x = node_data[points[1]-1][0]
        end_point_y = node_data[points[1]-1][1]

        add_line_series("Sketch_diagram", f"##element{element_number}", [start_point_x, end_point_x], [start_point_y, end_point_y], weight=2, color=[255, 0, 0, 255])
        mid_point_x = (start_point_x+end_point_x)/2
        mid_point_y = (start_point_y+end_point_y)/2

        element_number += 1

    del element_number

    node_number = 1

    for node in node_data:
        add_scatter_series("Sketch_diagram", f"##node{node_number}", [node[0]], [node[1]], outline=[255, 0, 0, 255])
        node_number += 1

def add_deformed_sketch(scale):

    global new_node_result
    global node_data

    node_data = node_data.reshape(no_of_nodes*2)
    new_node_result = np.array([])

    for i in range(0, no_of_nodes*2, 2):
        new_node_result = np.append(new_node_result, node_data[i] + Q_result[i][0]*scale)
        new_node_result = np.append(new_node_result, node_data[i+1] + Q_result[i+1][0]*scale)

    node_data = node_data.reshape((no_of_nodes, 2))
    new_node_result = new_node_result.reshape((no_of_nodes, 2))

    element_number = 1

    for points in element_data:
        start_point_x = new_node_result[points[0] - 1][0]
        start_point_y = new_node_result[points[0] - 1][1]

        end_point_x = new_node_result[points[1] - 1][0]
        end_point_y = new_node_result[points[1] - 1][1]

        add_line_series("Sketch_diagram", f"##dispalced_element{element_number}", [start_point_x, end_point_x],
                        [start_point_y, end_point_y], weight=2, color=[0, 191, 255, 255])

        element_number += 1

    del element_number

    node_number = 1

    for node in new_node_result:
        add_scatter_series("Sketch_diagram", f"##displaced_node{node_number}", [node[0]], [node[1]], outline=[0, 191, 255, 255])
        node_number += 1


def add_results_table():

    if does_item_exist("Results"):
        delete_item("Results")

    add_tab("Results", parent="ResultAndDiagram")


    max_displacement = np.max(total_displacement_result)
    min_displacement = np.min(total_displacement_result)

    tensile_stress = stress_result[stress_result >= 0]
    max_tensile_stress = np.max(tensile_stress)
    min_tensile_stress = np.min(tensile_stress)

    compressive_stress = np.absolute(stress_result[stress_result <=0 ])
    max_compressive_stress = np.max(compressive_stress)
    min_compressive_stress = np.min(compressive_stress)

    max_strain = np.max(strain_result)
    min_strain = np.min(strain_result)

    reaction_forces = np.array([])

    for i in range(0, no_of_nodes*2, 2):
        x_reaction = 0
        y_reaction = 0
        if reaction_force_result[i] == "No support reaction":
            pass
        else:
            x_reaction = float(reaction_force_result[i])
        if reaction_force_result[i+1] == "No support reaction":
            pass
        else:
            y_reaction =float(reaction_force_result[i+1])

        reaction_forces = np.append(reaction_forces, (x_reaction + y_reaction))

    reaction_forces = np.absolute(reaction_forces)
    max_reaction = np.max(reaction_forces)
    min_reaction = np.min(reaction_forces)

    add_spacing(count=2)
    add_table("Maximum and Minimum Results Table", ["Variable", "Maximum Value", "Minimum Value"], width=880, height=125, parent="Results")

    add_row("Maximum and Minimum Results Table", ["Net Nodal Displacement", f"{max_displacement:0.5}", f"{min_displacement:0.5}"])
    add_row("Maximum and Minimum Results Table", ["Element Tensile Stress", f"{max_tensile_stress:0.5}", f"{min_tensile_stress:0.5}"])
    add_row("Maximum and Minimum Results Table", ["Element Compressive Stress", f"{max_compressive_stress:0.5}", f"{min_compressive_stress:0.5}"])
    add_row("Maximum and Minimum Results Table", ["Element Strain", f"{max_strain:0.5}", f"{min_strain:0.5}"])
    add_row("Maximum and Minimum Results Table", ["Resultant Reaction Force", f"{max_reaction:0.5}", f"{min_reaction:0.5}"])


    add_table("Displacement and reactions Table", ["Node No.", "X-Axis Displacement", "Y-Axis Displacement", "X-Axis Reaction Force", "Y-Axis Reaction Force"], width=880, height=155, parent="Results")
    node = 1

    for i in range(0, no_of_nodes*2, 2):

        x_reaction = reaction_force_result[i][0]
        try:
            x_reaction = float(x_reaction)
            x_reaction = f"{x_reaction:0.5}"
        except:
            pass

        y_reaction = reaction_force_result[i+1][0]
        try:
            y_reaction = float(y_reaction)
            y_reaction = f"{y_reaction:0.5}"
        except:
            pass

        add_row("Displacement and reactions Table", [str(node), f"{Q_result[i][0]:0.5}", f"{Q_result[i + 1][0]:0.5}", x_reaction, y_reaction])

        node += 1

    del node

    add_table("Stress and Strain Table", ["Element No.", "Stress", "Strain"], width=880, height=155, parent="Results")
    for i in range(no_of_elements):
        add_row("Stress and Strain Table", [str(i+1), f"{stress_result[i][0]:0.5}", f"{strain_result[i][0]:0.5}"])


def update_material_table(sender, data):
    if get_value("same_material"):
        for i in range(no_of_elements):
            configure_item(f"##Material Table_{i+1}_1", enabled=False, tip="Same material as the first element.")
            configure_item(f"##Material Table_{i+1}_2", enabled=False, tip="Same material as the first element.")

    else:
        for i in range(no_of_elements):
            configure_item(f"##Material Table_{i+1}_1", enabled=True, tip="")
            configure_item(f"##Material Table_{i+1}_2", enabled=True, tip="")

def add_material_table():
    delete_item("3. Material Properties")

    with window("3. Material Properties", x_pos=10, y_pos=245, no_resize=True, no_move=True, no_collapse=True,
                no_close=True, width=450, height=187):
        material_table = SmartTable("Material Table")
        material_table.set_parent("3. Material Properties")
        add_spacing(count=2)
        add_checkbox("same_material", label=" All elements have the same material", callback=update_material_table)
        set_value("same_material", False)
        add_spacing(count=2)
        material_table.add_header(["Element No.", "Area of cross-section (A)", "Young's modulus (E)"])
        for i in range(no_of_elements):
            material_table.add_row([f"{i+1}", "", ""])

def add_displacement_constraint_table():
    if does_item_exist("Displacement Constraints"):
        delete_item("Displacement Constraints")

    add_tab("Displacement Constraints", parent="BC Data")
    add_spacing(count=2)
    displacement_table = SmartTable("Displacement Table")
    displacement_table.add_header(["Node No.", "X-Axis Movement Fixed", "Y-Axis Movement Fixed"])

    for i in range(no_of_nodes):
        displacement_table.add_row([str(i + 1), "C", ""])

def add_force_table():

    if does_item_exist("Forces"):
        delete_item("Forces")

    add_tab("Forces", parent="BC Data")
    add_spacing(count=2)

    force_table = SmartTable("Force Table")
    force_table.add_header(["Node No.", "X-Axis Force Component", "Y-Axis Force Component"])

    for i in range(no_of_nodes):
        force_table.add_row([str(i + 1), "", ""])

def directory_picker(sender, data):
    select_directory_dialog(callback=apply_selected_directory)

def apply_selected_directory(sender, data):
    directory = data[0]
    folder = data[1]
    set_value("folder_path", directory)
    configure_item("Import sketch", enabled=True, tip="")

def file_picker(sender, data):
    open_file_dialog(callback=apply_selected_file, extensions=".FCStd")

def apply_selected_file(sender, data):
    directory = data[0]
    file = data[1]
    set_value("file_path", f"{directory}\\{file}")
    load_FCStd(f"{directory}\\{file}", file)

def open_github(sender, data):
    webbrowser.open("https://github.com/RahulShagri/2D-Truss-Element-2-DOF-FEM-Solver")

def close_window(sender, data):
    if data == "Solve Window":
        close_popup("Solve Confirmation Window")

    elif data == "Tools Window":
        close_popup("Diagram Tools Window")

    elif data == "Reset Window":
        close_popup("Reset Confirmation Window")

def switch_theme(sender, data):
    if sender == "dark_mode":

        delete_item("dark_mode")
        add_image_button("light_mode", "icons/light_mode.png", width=23, height=23, tip="Light mode", parent="Extras",
                         callback=switch_theme)

        set_theme("Grey")
        set_main_window_title("Planar Truss Element FEM Solver")
        set_main_window_pos(x=0, y=0)
        set_main_window_size(width=1370, height=740)
        set_main_window_resizable(False)

        set_style_window_padding(4.00, 4.00)
        set_style_frame_padding(6.00, 4.00)
        set_style_item_spacing(6.00, 2.00)
        set_style_item_inner_spacing(4.00, 4.00)
        set_style_touch_extra_padding(0.00, 0.00)
        set_style_indent_spacing(21.00)
        set_style_scrollbar_size(12.00)
        set_style_grab_min_size(10.00)
        set_style_window_border_size(0.00)
        set_style_child_border_size(1.00)
        set_style_popup_border_size(1.00)
        set_style_frame_border_size(0.00)
        set_style_tab_border_size(0.00)
        set_style_window_rounding(0.00)
        set_style_child_rounding(0.00)
        set_style_frame_rounding(0.00)
        set_style_popup_rounding(0.00)
        set_style_scrollbar_rounding(0.00)
        set_style_grab_rounding(0.00)
        set_style_tab_rounding(0.00)
        set_style_window_title_align(0.50, 0.50)
        set_style_window_menu_button_position(mvDir_Left)
        set_style_color_button_position(mvDir_Right)
        set_style_button_text_align(0.50, 0.50)
        set_style_selectable_text_align(0.00, 0.00)
        set_style_display_safe_area_padding(3.00, 3.00)
        set_style_global_alpha(1.00)
        set_style_antialiased_lines(True)
        set_style_antialiased_fill(True)
        set_style_curve_tessellation_tolerance(1.25)
        set_style_circle_segment_max_error(1.60)

    else:
        delete_item("light_mode")
        add_image_button("dark_mode", "icons/dark_mode.png", width=23, height=23, tip="Dark mode", parent="Extras",
                         callback=switch_theme)

        set_theme("Light")
        set_main_window_title("Planar Truss Element FEM Solver")
        set_main_window_pos(x=0, y=0)
        set_main_window_size(width=1370, height=740)
        set_main_window_resizable(False)

        set_style_window_padding(4.00, 4.00)
        set_style_frame_padding(6.00, 4.00)
        set_style_item_spacing(6.00, 2.00)
        set_style_item_inner_spacing(4.00, 4.00)
        set_style_touch_extra_padding(0.00, 0.00)
        set_style_indent_spacing(21.00)
        set_style_scrollbar_size(12.00)
        set_style_grab_min_size(10.00)
        set_style_window_border_size(0.00)
        set_style_child_border_size(1.00)
        set_style_popup_border_size(1.00)
        set_style_frame_border_size(0.00)
        set_style_tab_border_size(0.00)
        set_style_window_rounding(0.00)
        set_style_child_rounding(0.00)
        set_style_frame_rounding(0.00)
        set_style_popup_rounding(0.00)
        set_style_scrollbar_rounding(0.00)
        set_style_grab_rounding(0.00)
        set_style_tab_rounding(0.00)
        set_style_window_title_align(0.50, 0.50)
        set_style_window_menu_button_position(mvDir_Left)
        set_style_color_button_position(mvDir_Right)
        set_style_button_text_align(0.50, 0.50)
        set_style_selectable_text_align(0.00, 0.00)
        set_style_display_safe_area_padding(3.00, 3.00)
        set_style_global_alpha(1.00)
        set_style_antialiased_lines(True)
        set_style_antialiased_fill(True)
        set_style_curve_tessellation_tolerance(1.25)
        set_style_circle_segment_max_error(1.60)

with window("Main"):
    set_theme("Light")
    set_main_window_title("Planar Truss Element FEM Solver")
    set_main_window_pos(x=0, y=0)
    set_main_window_size(width=1370, height=740)
    set_main_window_resizable(False)
    add_additional_font("fonts/OpenSans-Regular.ttf", 18)

    set_style_window_padding(4.00, 4.00)
    set_style_frame_padding(6.00, 4.00)
    set_style_item_spacing(6.00, 2.00)
    set_style_item_inner_spacing(4.00, 4.00)
    set_style_touch_extra_padding(0.00, 0.00)
    set_style_indent_spacing(21.00)
    set_style_scrollbar_size(12.00)
    set_style_grab_min_size(10.00)
    set_style_window_border_size(0.00)
    set_style_child_border_size(1.00)
    set_style_popup_border_size(1.00)
    set_style_frame_border_size(0.00)
    set_style_tab_border_size(0.00)
    set_style_window_rounding(0.00)
    set_style_child_rounding(0.00)
    set_style_frame_rounding(0.00)
    set_style_popup_rounding(0.00)
    set_style_scrollbar_rounding(0.00)
    set_style_grab_rounding(0.00)
    set_style_tab_rounding(0.00)
    set_style_window_title_align(0.50, 0.50)
    set_style_window_menu_button_position(mvDir_Left)
    set_style_color_button_position(mvDir_Right)
    set_style_button_text_align(0.50, 0.50)
    set_style_selectable_text_align(0.00, 0.00)
    set_style_display_safe_area_padding(3.00, 3.00)
    set_style_global_alpha(1.00)
    set_style_antialiased_lines(True)
    set_style_antialiased_fill(True)
    set_style_curve_tessellation_tolerance(1.25)
    set_style_circle_segment_max_error(1.60)


with window("1. Set up FreeCAD", x_pos=0, y_pos=0, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=460, height=130):
    add_spacing(count=2)
    add_text("Find the location of the FreeCAD installation folder. Ex. C:\\FreeCAD 0.18")
    add_spacing(count=2)
    add_button("Find FreeCAD", width=452, height=36, callback=directory_picker)
    add_spacing(count=2)
    add_label_text("##folderpath", source="folder_path", color=[255, 0, 0])

with window("2. Import the FreeCAD Sketch", x_pos=0, y_pos=140, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=460, height=98):
    add_spacing(count=2)
    add_button("Import sketch", width=452, height=36, callback=file_picker, enabled=False, tip="First select the FreeCAD folder path.")
    add_spacing(count=2)
    add_label_text("##filepath", source="file_path", color=[255, 0, 0])

with window("3. Material Properties", x_pos=0, y_pos=245, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=460, height=187):
    add_spacing(count=2)
    add_checkbox("same_material", label=" All elements have the same material")
    set_value("same_material", True)
    add_spacing(count=2)
    material_table = SmartTable("Material Table")
    material_table.add_header(["", "Area of cross-section (A)", "Young's modulus (E)"])

with window("4. Boundary Conditions", x_pos=0, y_pos=442, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=460, height=187):
    add_tab_bar("BC Data")

with window("Solve", x_pos=0, y_pos=650, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=460, height=46, no_title_bar=True):
    add_button("Solve!", width=223, height=36, enabled=False, tip="Load a FreeCAD sketch first.")
    add_same_line(spacing=10)
    add_button("Reset", width=223, height=36, enabled=False)

    add_popup("Solve!", 'Solve Confirmation Window', modal=True, mousebutton=mvMouseButton_Left)
    add_text("Are you sure you want to solve?")
    add_spacing()
    add_button("Yes##Solve", width=150, callback=run_checks_and_solve)
    add_same_line(spacing=10)
    add_button("No##Solve", width=150, callback=close_window, callback_data="Solve Window")

    add_popup("Reset", 'Reset Confirmation Window', modal=True, mousebutton=mvMouseButton_Left)
    add_text("Are you sure you want to Reset?")
    add_spacing()
    add_button("Yes##Reset", width=150, callback=reset_data)
    add_same_line(spacing=10)
    add_button("No##Reset", width=150, callback=close_window, callback_data="Reset Window")

with window("##Result_and_diagram_Window", x_pos=460, y_pos=0, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=895, height=490, no_title_bar=True):
    add_tab_bar("ResultAndDiagram")
    add_tab("Diagram", parent="ResultAndDiagram")
    add_spacing(count=2)
    add_button("Diagram Tools", width=200, height=30, enabled=False)
    add_same_line(spacing=660)
    add_text("[?]", tip=" - Double left-click to fit the plot automatically.\n - Double right-click to show more settings.")
    add_spacing(count=2)

    add_popup("Diagram Tools", "Diagram Tools Window", modal=True, mousebutton=mvMouseButton_Left)
    add_spacing(count=5)
    add_checkbox("Show element numbers")
    set_value("Show element numbers", True)
    add_spacing(count=2)
    add_checkbox("Show node numbers")
    set_value("Show node numbers", True)
    add_spacing(count=2)
    add_checkbox("Show original structure")
    set_value("Show original structure", True)
    add_spacing(count=2)

    with child("Deformed Sketch Tools", width=300, height=70):

        add_checkbox("Show deformed structure", enabled=False, tip="No solution has been calculated yet.")
        set_value("Show deformed structure", True)
        add_spacing(count=2)
        add_slider_int("Amplification", max_value=1000, min_value=1, tip="No solution has been calculated yet.", default_value=500, enabled=False)

    add_spacing(count=5)

    add_button("OK", width=145, callback=update_diagram)
    add_same_line(spacing=10)
    add_button("Cancel", width=145, callback=close_window, callback_data="Tools Window")

    add_plot("Sketch_diagram", label="", width=890, height=412, x_axis_name="X-Axis", y_axis_name="Y-Axis", parent="Diagram", equal_aspects=True, anti_aliased=True)
    add_tab("Results", parent="ResultAndDiagram")


with window("Logger", x_pos=460, y_pos=486, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=855, height=210):
    add_logger("log", log_level=0, auto_scroll=True)
    clear_log(logger="log")
    log("Welcome to the Planar Truss Element FEM Solver!", logger="log")

with window("Extras", x_pos=1310, y_pos=486, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=43,
            height=80, no_title_bar=True):
    add_image_button("Help", "icons/help.png", width=23, height=23, tip="Get more information on GitHub.", callback=open_github)
    add_spacing()
    add_separator()
    add_spacing()
    add_image_button("dark_mode", "icons/dark_mode.png", width=23, height=23, tip="Dark mode", callback=switch_theme)


start_dearpygui(primary_window="Main")
