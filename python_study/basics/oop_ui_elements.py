class UIElement:
    def __init__(self, name, locator, is_visible=True):
        self.name = name
        self.locator = locator
        self.is_visible = is_visible

    def check_visibility(self):
        if self.is_visible:
            print(f"[{self.name}] видно на сторінці.")
        else:
            print(f"[{self.name}] приховано.")

    def click(self):
        if self.is_visible:
            print(f"[Натиснуто] {self.name}")
        else:
            print(f"[Помилка] Елемент {self.name} невидимий, клік неможливий.")


class Button(UIElement):
    def __init__(self, name, locator, is_visible=True, is_enabled=True):
        super().__init__(name, locator, is_visible)
        self.is_enabled = is_enabled


    def click(self):
        if self.is_visible and self.is_enabled:
            print(f"[Натиснуто кнопку] {self.name}")
        else:
            print(f"[Помилка] Кнопку {self.name} неможливо натиснути!")


class InputField(UIElement):
    def __init__(self, name, locator, is_visible=True):
        super().__init__(name, locator, is_visible)


    def fill(self, text):
        if self.is_visible:
            print(f"[Ввід тексту] У поле {self.name} введено: {text}")
        else:
            print(f"[Помилка] Елемент {self.name} невидимий")


class Astronaut():
    def __init__(self, name):
        self.name = name
        self.oxygen = 100
        self.energy = 100


    def __str__(self):
        return f"Astronaut {self.name} stats: oxygen={self.oxygen}, energy={self.energy}"


    def work(self, hours):
        self.oxygen -= hours * 5
        self.energy -= hours * 10
        print(f"[Work] {self.name} worked {hours} hours.")
        if self.oxygen <= 0 or self.energy <= 0:
            print(f"[Alarm] {self.name} in critical condition!")


    def sleep(self):
        self.energy = 100
        self.oxygen -= 10
        print(f"[Rest] {self.name} had a sleep. Energy renewed")



mark = Astronaut("Марк")

print(mark)

mark.work(5)
print(mark)

mark.sleep()
print(mark)

mark.work(12)