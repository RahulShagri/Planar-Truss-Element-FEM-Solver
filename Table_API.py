from dearpygui.core import *
from dearpygui.simple import *


class SmartTable:
    # This is the smart table that will fill widgets for cells based on type
    def __init__(self, name: str, header: List[str] = None):
        self.name = name
        self.header = header
        self.row = 0
        self.column = 0
        self.parent_value = ''

        if header is not None:
            self.add_header(self.header)

    def add_header(self, header: List[str]):
        add_separator()
        with managed_columns(f"{self.name}_head", len(header), border=False, parent=self.parent_value):
            for item in header:
                add_text(item)
            add_separator()
            add_separator()
            add_spacing(count=2)

    def add_row(self, row_content: List[Any]):
        with managed_columns(f"{self.name}_{self.row}", len(row_content), border=False, parent=self.parent_value):
            add_text(f"##{self.name}_{self.row}_{self.column}", default_value=row_content[0])
            self.column = 1

            if row_content[1] == 'C':
                for item in row_content[1:-1]:
                    add_checkbox(f"##{self.name}_{self.row}_{self.column}")
                    self.column += 1
                    add_checkbox(f"##{self.name}_{self.row}_{self.column}")
                    self.column += 1

            elif row_content[1] == "flag_1":
                add_text(f"##{self.name}_{self.row}_{self.column}", default_value=row_content[2])
                self.column += 1
                add_input_text(f"##{self.name}_{self.row}_{self.column}", default_value="")
                self.column += 1

            else:
                for item in row_content[1:]:
                    add_input_text(f"##{self.name}_{self.row}_{self.column}", default_value=item)

                    self.column += 1
        self.column = 0
        self.row += 1
        add_separator()

    def set_parent(self, parent_name):
        self.parent_value = parent_name

    def get_cell_data(self, row: int, col: int) -> Any:
        return get_value(f"##{self.name}_{row}_{col}")