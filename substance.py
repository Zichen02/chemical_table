class substance:
    # 性质列表作为类属性，可用于查询和验证
    PROPERTY_LIST = ["MolecularWeight", "MeltingPoint", "BoilingPoint", "Solubility", "Density"]

    def __init__(self, name="", molecular_weight=None, cas_number=None, melting_point=None, boiling_point=None, solubility=None, density=None, other_info=None):
        self.name = name
        self.cas_number = cas_number
        self.melting_point = melting_point
        self.boiling_point = boiling_point
        self.solubility = solubility
        self.molecular_weight = molecular_weight
        self.density = density
        self.other_info = other_info if other_info is not None else {}

    def store_to_txt(self, filename):
        """
        将物质的属性存储到一个文本文件中
        """
        with open(filename, 'w') as file:
            file.write(f"Name: {self.name}\n")
            file.write(f"CAS Number: {self.cas_number}\n")
            file.write(f"Melting Point: {self.melting_point}\n")
            file.write(f"Boiling Point: {self.boiling_point}\n")
            file.write(f"Solubility: {self.solubility}\n")
            file.write(f"Molecular Weight: {self.molecular_weight}\n")
            file.write(f"Density: {self.density}\n")
            if self.other_info:
                file.write("Other Info:\n")
                for key, value in self.other_info.items():
                    file.write(f"  {key}: {value}\n")

    @classmethod
    def read_from_txt(cls, filename):
        """
        从文本文件读取物质信息创建 Substance 实例
        """
        name = ""
        cas_number = ""
        melting_point = None
        boiling_point = None
        solubility = None
        molecular_weight = None
        density = None
        other_info = {}
        reading_other_info = False
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("Name:"):
                    name = line.split(":")[1].strip()
                elif line.startswith("CAS Number:"):
                    cas_number = line.split(":")[1].strip()
                elif line.startswith("Melting Point:"):
                    melting_point = line.split(":")[1].strip()
                elif line.startswith("Boiling Point:"):
                    boiling_point = line.split(":")[1].strip()
                elif line.startswith("Solubility:"):
                    solubility = line.split(":")[1].strip()
                elif line.startswith("Molecular Weight:"):
                    molecular_weight = line.split(":")[1].strip()
                elif line.startswith("Density:"):
                    density = line.split(":")[1].strip()
                elif line.startswith("Other Info:"):
                    reading_other_info = True
                elif reading_other_info:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        other_info[key] = value
        return cls(name, cas_number, melting_point, boiling_point, solubility, molecular_weight, density, other_info)

    def to_dict(self):
        """
        将物质的所有信息输出为字典
        """
        substance_dict = {
            "Name": self.name,
            "CAS Number": self.cas_number,
            "Melting Point": self.melting_point,
            "Boiling Point": self.boiling_point,
            "Solubility": self.solubility,
            "Molecular Weight": self.molecular_weight,
            "Density": self.density
        }
        substance_dict.update(self.other_info)
        return substance_dict
