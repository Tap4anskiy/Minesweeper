import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
from datetime import datetime

#Словарь цветов чисел
colors = {
    1: '#15cf6f',
    2: '#30d9b1',
    3: '#f5a4f3',
    4: '#f578aa',
    5: '#1811f2',
    6: '#86e65a',
    7: '#656ee6',
    8: '#f21811'
}

#Дочерний класс Button с добавлением дополнительных атрибутов
class MyButton(tk.Button):

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width = 3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_open = False
        self.is_mine = False;
        self.is_flag = False

    def __repr__(self):
        return f'MyButton {self.x} {self.y} {self.number} {self.is_mine}'

#Класс игры Сапер
class MineSweeper:

    #Атрибуты игры
    window = tk.Tk(); window.title('Сапер')
    ROW = 10
    COLUMNS = 10
    MINES = 10
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True

    #Конструктор класса - создание кнопок и объявление переменных таймера и счетчика флагов
    def __init__(self):
        self.temp = 0
        self.after_id = ''
        self.num_click = 0
        self.time_label = tk.Label(MineSweeper.window, font='Calibri 14', text='00:00')
        self.flags = MineSweeper.MINES
        self.num_flags = tk.Label(MineSweeper.window, font='Calibri 14', text= f'Флагов осталось: {self.flags}')
        self.buttons = []
        for i in range(MineSweeper.ROW+2):
            temp = []
            for j in range(MineSweeper.COLUMNS+2):
                btn = MyButton(MineSweeper.window, x = i, y = j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind('<Button-3>', self.right_click)
                temp.append(btn)
            self.buttons.append(temp)

    #Функция для правой кнопки мыши - флаги
    def right_click(self, event):
        if MineSweeper.IS_GAME_OVER: return None
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            cur_btn['disabledforeground'] = 'red'
            cur_btn.is_flag = True
            self.flags -= 1
            self.num_flags.config(text = f'Флагов осталось: {self.flags}')
        elif cur_btn['text'] == '🚩':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'
            cur_btn.is_flag = False
            self.flags += 1
            self.num_flags.config(text = f'Флагов осталось: {self.flags}')
    
    #Функция для левой кнопки мыши - логика игры
    def click(self, clicked_button:MyButton):

        #проверка конца игры
        if MineSweeper.IS_GAME_OVER:
            return None

        #проверка первого клика по игровому полю - запуск генерации бомб
        if MineSweeper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            self.print_buttons()
            self.tick()

            MineSweeper.IS_FIRST_CLICK = False

        #попадание в мину - конец игры
        if clicked_button.is_mine:
            clicked_button.config(text='💣', background='red', disabledforeground='black')
            clicked_button.is_open = True
            MineSweeper.window.after_cancel(self.after_id)
            MineSweeper.IS_GAME_OVER = True
            showinfo('Game over', 'Вы проиграли!',detail = 'Закройте это окно и нажмите клавишу F5,\nчтобы играть снова')
            for i in range(MineSweeper.ROW+2):
                for j in range(MineSweeper.COLUMNS+2):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '💣'
        
        #попадание в пустую клетку, вывод количества мин рядом с ней
        else:
            if clicked_button.count_bomb:
                color = colors.get(clicked_button.count_bomb, 'black')
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color, background='#e3e6e8')
                clicked_button.is_open = True
                self.num_click += 1
            else:
                self.breadth_first_search(clicked_button)

            

        #деактивация кнопки после ее нажатия
        clicked_button.config(state='disable')
        clicked_button.config(relief=tk.SUNKEN)

        #проверка на победу
        if self.num_click == MineSweeper.ROW*MineSweeper.COLUMNS - MineSweeper.MINES:
            MineSweeper.window.after_cancel(self.after_id)
            showinfo('Win', 'Вы победили!',detail = 'Закройте это окно и нажмите клавишу F5,\nчтобы играть снова')
            MineSweeper.IS_GAME_OVER = True
        

    #алгоритма поиска в ширину для открытия пустых клеток
    def breadth_first_search(self, btn:MyButton):
        queue = [btn] #массив - очередь элементов для проверки
        while queue:

            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')

            #открытие значения кнопки, проверка, флаг ли она
            if cur_btn.count_bomb:
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground=color, background='#e3e6e8')
            else:
                cur_btn.config(text='', disabledforeground=color, background='#e3e6e8')
            if cur_btn.is_flag: self.flags += 1; self.num_flags.config(text = f'Флагов осталось: {self.flags}')
            cur_btn.is_open = True
            cur_btn.config(state='disable')
            cur_btn.config(relief=tk.SUNKEN)
            self.num_click += 1

            #добавление новых элементов в очередь, если количество бомб рядом с элементом = 0
            if cur_btn.count_bomb == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1,0,1]:
                    for dy in [-1,0,1]:

                        next_btn = self.buttons[x+dx][y+dy]
                        if not next_btn.is_open and 1<=next_btn.x<= MineSweeper.ROW and \
                            1<=next_btn.y<=MineSweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

    
    #перезапуск игры с помощью удаление всех элементов с окна и создания их снова
    def reload(self, *args):
        if self.after_id != '': MineSweeper.window.after_cancel(self.after_id)
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False

    #генерация окна настроек
    def create_settings_win(self):

        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Настройки')

        tk.Label(win_settings, text='Количество строк').grid(row = 0, column = 0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row = 0, column=1, padx=20,pady=20)

        tk.Label(win_settings, text='Количество колонок').grid(row = 1, column = 0)
        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row = 1, column=1, padx=20,pady=20)

        tk.Label(win_settings, text='Количество мин').grid(row = 2, column = 0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row = 2, column=1, padx=20,pady=20)

        save_btn = tk.Button(win_settings, text='Применить', 
                  command =lambda:  self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row = 3, column = 0, columnspan=2, padx=20,pady=20)

    #примение новых настроек
    def change_settings(self,row: tk.Entry, column: tk.Entry, mines: tk.Entry):

        #проверка введенных значений
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильное значение')
            return

        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())

        self.reload()

    #таймер
    def tick(self):
        self.after_id = MineSweeper.window.after(1000, self.tick)
        f_temp = datetime.fromtimestamp(self.temp).strftime("%M:%S")
        self.time_label.configure(text=str(f_temp))
        self.temp += 1   

    #генерация всех виджетов окна
    def create_widgets(self):

        #меню
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        #подменю
        settings_menu = tk.Menu(menubar, tearoff = '0')
        settings_menu.add_command(label='Играть', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_settings_win)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Файл', menu=settings_menu)

        #добавление игровых кнопок на экран
        count = 1
        for i in range(1,MineSweeper.ROW+1):
            for j in range(1,MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i,column=j, stick ='NWES')
                count += 1

        
        #конфигурация мест строк и рядов кнопок
        for i in range(1,MineSweeper.ROW+1):
            tk.Grid.rowconfigure(self.window, i, weight = 1)
        
        for i in range(1,MineSweeper.COLUMNS+1):
            tk.Grid.columnconfigure(self.window, i, weight = 1)

        #таймер
        tk.Grid.rowconfigure(self.window, MineSweeper.ROW+1, weight = 2)
        self.time_label.grid(row=MineSweeper.ROW+1,column = 1, columnspan=MineSweeper.COLUMNS//2,padx=10, pady=10, stick ='NWS')

        #счетчик
        self.num_flags.grid(row=MineSweeper.ROW+1,column = MineSweeper.COLUMNS//2+1, columnspan=MineSweeper.COLUMNS//2,padx=10, pady=10, stick ='NWE')

        #бинд кнопки перезапуска игры
        MineSweeper.window.bind('<F5>', self.reload)

        
    #вспомогательная функция для открытия всех кнопок
    def open_all_buttons(self):
        for i in range(MineSweeper.ROW+2):
            for j in range(MineSweeper.COLUMNS+2):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text='💣', background='red', disabledforeground='black')
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, 'black')
                    btn.config(text=btn.count_bomb, fg = color)

    #начало игры
    def start(self):
        
        self.create_widgets()
        #self.open_all_buttons()

        MineSweeper.window.mainloop();

    #вспомогательная функция по выводу значений кнопок в консоль (отладку)
    def print_buttons(self):
        for i in range(1,MineSweeper.ROW+1):
            for j in range(1,MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.is_mine: print('B', end = ' ')
                else: print(btn.count_bomb, end = ' ')
            print()

    #функция расстановки мин
    def insert_mines(self, number:int):
        index_mines = self.get_mines_places(number)
        print(index_mines)
        for i in range(1,MineSweeper.ROW+1):
            for j in range(1,MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    #подсчет мин в соседних клетках
    def count_mines_in_buttons(self):
        for i in range(1,MineSweeper.ROW+1):
            for j in range(1,MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1,0,1]:
                        for col_dx in [-1,0,1]:
                            neighbour = self.buttons[i+row_dx][j+col_dx]
                            if neighbour.is_mine:
                                count_bomb += 1
                    btn.count_bomb = count_bomb

    #генерация номеров клеток бомб
    @staticmethod
    def get_mines_places(exclude_number: int):
        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1))
        print (f'Исключаем кнопку номер {exclude_number}')
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:MineSweeper.MINES]



#Создание экземпляра класса игры и запуск
#-----------------------------
def main():
    game = MineSweeper()
    game.start()
#-----------------------------
main()
#-----------------------------