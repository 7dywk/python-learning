from dataclasses import dataclass, field

@dataclass
class Car:
    brand: str
    model: str
    year: int
    is_sedan: bool

my_car = Car("BMW", "m4", 2019, True)


@dataclass
class Garage:
    owner: str
    cars: list[Car] = field(default_factory=list)
    def count_sedans(self):
        sedan_num = 0
        for car in self.cars:
            if car.is_sedan:
                sedan_num += 1
        return sedan_num


my_garage = Garage(owner="Ілля")
my_garage.cars.append(Car(brand="Mazda", model="6", year=2015, is_sedan=True))
my_garage.cars.append(Car(brand="Audi", model="A3", year=2012, is_sedan=False))
print(my_garage.count_sedans())
