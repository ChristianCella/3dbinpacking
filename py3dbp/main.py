from .constants import RotationType, Axis
from .auxiliary_methods import intersect, set_to_decimal
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]


class Item:
    def __init__(self, name, width, height, depth, weight):
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        self.rotation_type = 0
        self.position = START_POSITION
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.weight,
            self.position, self.rotation_type, self.get_volume()
        )

    def get_volume(self):
        return set_to_decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def get_dimension(self):
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension
    
    def get_vertices(self):
        x, y, z = self.position
        if self.rotation_type == RotationType.RT_WHD:
            l, h, p = self.width, self.height, self.depth
        elif self.rotation_type == RotationType.RT_HWD:           
            l, h, p  = self.height, self.width, self.depth
        
        return [
            (float(x),     float(y),     float(z)),
            (float(x + l), float(y),     float(z)),
            (float(x + l), float(y + h), float(z)),
            (float(x),     float(y + h), float(z)),
            (float(x),     float(y),     float(z + p)),
            (float(x + l), float(y),     float(z + p)),
            (float(x + l), float(y + h), float(z + p)),
            (float(x),     float(y + h), float(z + p))
        ]
    
    def get_center(self):
        x,y,z =self.position
        if self.rotation_type == RotationType.RT_WHD:
            l, h, p = self.width, self.height, self.depth
        elif self.rotation_type == RotationType.RT_HWD:           
            l, h, p = self.height, self.width, self.depth
        return[
            int(x+l/2), int(y+h/2), int(z+p/2)
        ]


class Bin:
    def __init__(self, name, width, height, depth, max_weight):
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.max_weight = max_weight
        self.items = []
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def set_offset (self, x_pos, y_pos, z_pos):
        self.offset=[x_pos, y_pos, z_pos]

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.max_weight,
            self.get_volume()
        )

    def get_volume(self):
        return set_to_decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def get_total_weight(self):
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return set_to_decimal(total_weight, self.number_of_decimals)

    def put_item(self, item, pivot):
        fit = False
        valid_item_position = item.position
        item.position = pivot

        for i in range(0, len(RotationType.ALL)):
            item.rotation_type = i
            dimension = item.get_dimension()
            if (
                self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                if self.get_total_weight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                self.items.append(item)

            if not fit:
                item.position = valid_item_position

            return fit

        if not fit:
            item.position = valid_item_position

        return fit
    
    def get_vertices(self):
        x, y, z = self.position
        l, h, p = self.width, self.height, self.depth
        return [
            (float(x),     float(y),     float(z)),
            (float(x + l), float(y),     float(z)),
            (float(x + l), float(y + h), float(z)),
            (float(x),     float(y + h), float(z)),
            (float(x),     float(y),     float(z + p)),
            (float(x + l), float(y),     float(z + p)),
            (float(x + l), float(y + h), float(z + p)),
            (float(x),     float(y + h), float(z + p))
        ]
    def get_center(self):
        x,y,z =self.position
        l, h, p = self.width, self.height, self.depth
        return[
            float(x+l/2), float(y+h/2), float(z+p/2)
        ]
    
    def get_offset(self):
        return [
            self.offset[0], self.offset[1], self.offset[2]
        ]
    
    


class Packer:
    def __init__(self):
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0

    def add_bin(self, bin):
        return self.bins.append(bin)

    def add_item(self, item):
        self.total_items = len(self.items) + 1

        return self.items.append(item)

    def pack_to_bin(self, bin, item):
        fitted = False

        # if the bin is empty, put the item at [0, 0, 0]; if it fits, it stays; otherwise it is put to unfitted items
        if not bin.items:
            response = bin.put_item(item, START_POSITION)

            if not response:
                bin.unfitted_items.append(item)

            return

        # With this loop you are trying to place the item next to each already fitted item:
            # If an orientation fits, it is added
            # If it doesn't fit, it is added to unfitted items
        for axis in range(0, 3):
            items_in_bin = bin.items

            for ib in items_in_bin:
                pivot = [0, 0, 0]
                w, h, d = ib.get_dimension()
                if axis == Axis.WIDTH:
                    pivot = [
                        ib.position[0] + w,
                        ib.position[1],
                        ib.position[2]
                    ]
                elif axis == Axis.HEIGHT:
                    pivot = [
                        ib.position[0],
                        ib.position[1] + h,
                        ib.position[2]
                    ]
                elif axis == Axis.DEPTH:
                    pivot = [
                        ib.position[0],
                        ib.position[1],
                        ib.position[2] + d
                    ]

                if bin.put_item(item, pivot):
                    fitted = True
                    break
            if fitted:
                break

        if not fitted:
            bin.unfitted_items.append(item)

    def pack(
        self, bigger_first=False, distribute_items=False,
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS
    ):
        for bin in self.bins:
            bin.format_numbers(number_of_decimals)

        for item in self.items:
            item.format_numbers(number_of_decimals)

        # Bins and items are sorted by volume
        self.bins.sort(
            key=lambda bin: bin.get_volume(), reverse=bigger_first
        )
        self.items.sort(
            key=lambda item: item.get_volume(), reverse=bigger_first
        )

        # Try to pack all the items into the bins
        for bin in self.bins:
            for item in self.items:
                self.pack_to_bin(bin, item)

            if distribute_items:
                for item in bin.items:
                    self.items.remove(item)

class Scene:
    
    def __init__(self):
        """
        Inizializza una scena 3D vuota.
        """
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

    def add_object_to_scene(self, item, red):
        """
        Aggiunge un cubo alla scena.
        :param cubo: Oggetto Cubo da disegnare
        """
        vertici = item.get_vertices()
        # Definizione delle facce del cubo
        facce = [
            [vertici[0], vertici[1], vertici[2], vertici[3]],  # Base inferiore
            [vertici[4], vertici[5], vertici[6], vertici[7]],  # Base superiore
            [vertici[0], vertici[1], vertici[5], vertici[4]],  # Lato frontale
            [vertici[2], vertici[3], vertici[7], vertici[6]],  # Lato posteriore
            [vertici[0], vertici[3], vertici[7], vertici[4]],  # Lato sinistro
            [vertici[1], vertici[2], vertici[6], vertici[5]]   # Lato destro
        ]

        # Aggiunta delle facce al grafico
        if red == True:
            self.ax.add_collection3d(Poly3DCollection(facce, facecolors='red', linewidths=1, edgecolors='r', alpha=0.6))

        else:
            self.ax.add_collection3d(Poly3DCollection(facce, facecolors='cyan', linewidths=1, edgecolors='r', alpha=0.6))
   

    def show_scene(self):
        """
        Mostra la scena 3D con tutti i cubi aggiunti.
        """
        self.ax.set_xlabel('Asse X')
        self.ax.set_ylabel('Asse Y')
        self.ax.set_zlabel('Asse Z')
        plt.show()
