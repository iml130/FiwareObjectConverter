from fiwareobjectconverter.object_fiware_converter import ObjectFiwareConverter

con = ObjectFiwareConverter()
# print(con.obj_to_fiware.__doc__)
# print("\n")
# print(help(con.obj_to_fiware))

class Test:
    def __init__(self):
        self.name = "Aaron"
        self.age = 22
        self.type = "Coder"
        self.id = "1"

x = Test()

con.obj_to_fiware(x, encode=True)
# ObjectFiwareConverter.obj_to_fiware()
