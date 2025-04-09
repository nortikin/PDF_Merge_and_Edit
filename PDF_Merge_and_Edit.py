import PyPDF2
import os
import subprocess
import time
import sys
import webbrowser
import favicon
import tkinter as tk
from tkinter import filedialog
# Progressbar
import threading
import time
from tkinter import Button, Tk, HORIZONTAL, Listbox
from tkinter.ttk import Progressbar
# svg images
import tksvg
# ??? donno what is it
from functools import partial

#import dnd

# Written by Simon Wong
# https://github.com/simonwongwong


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def popup(text):
    textwindow = tk.Tk()
    textwindow.title('Оштбка!')
    textwindow.minsize(width=300, height=50)
    textwindow.resizable(False, False)
    label = tk.Label(textwindow, text=text)
    label.pack()
    label.configure(pady=20)
    textwindow.mainloop()


def finished(file, operation, window):
    stickyFill = tk.N + tk.E + tk.W + tk.S
    finishPrompt = tk.Tk()
    finishPrompt.title(operation + "Сделано!")
    finishPrompt.resizable(False, False)
    tk.Label(finishPrompt, text=operation + "Окончено. Открыть файл?").grid(row=0, column=0, columnspan=2, pady=5, padx=5)
    if 'win' not in os.sys.platform:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: subprocess.call(['evince',file])).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    else:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: os.startfile(file)).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    tk.Button(finishPrompt, text="Досвидулидам!", command=lambda: finishPrompt.destroy()).grid(row=1, column=1, pady=5, padx=5, sticky=stickyFill)
    finishPrompt.mainloop()


def filePicker(entry, window):
    file = filedialog.askopenfilename(title="Выбери PDF", filetypes=(("PDF", "*.pdf"),), initialdir=os.getcwd())

    if entry.get() == "":
        entry.insert(0, file)
    else:
        entry.delete(0, 'end')
        entry.insert(0, file)

    window.lift()

def folderPicker(entry, window):
    folder_path = filedialog.askdirectory()
    #print("Выбрана папка: ",folder_path)
    if entry.get() == "":
        entry.insert(0, folder_path)
    else:
        entry.delete(0, 'end')
        entry.insert(0, folder_path)
    window.lift()

# Класс для списка, без него не решается
class Drag_and_Drop_Listbox(tk.Listbox):
    """ A tk listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.MULTIPLE
        kw['activestyle'] = 'none'
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.getState, add='+')
        self.bind('<Button-1>', self.setCurrent, add='+')
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None
        self.curState = None
    def setCurrent(self, event):
        ''' gets the current index of the clicked item in the listbox '''
        self.curIndex = self.nearest(event.y)
    def getState(self, event):
        ''' checks if the clicked item in listbox is selected '''
        i = self.nearest(event.y)
        self.curState = self.selection_includes(i)
    def shiftSelection(self, event):
        ''' shifts item up or down in listbox '''
        i = self.nearest(event.y)
        if self.curState == 1:
            self.selection_set(self.curIndex)
        else:
            self.selection_clear(self.curIndex)
        if i < self.curIndex:
            # Moves up
            x = self.get(i)
            selected = self.selection_includes(i)
            self.delete(i)
            self.insert(i+1, x)
            if selected:
                self.selection_set(i+1)
            self.curIndex = i
        elif i > self.curIndex:
            # Moves down
            x = self.get(i)
            selected = self.selection_includes(i)
            self.delete(i)
            self.insert(i-1, x)
            if selected:
                self.selection_set(i-1)
            self.curIndex = i
def example():
    root = tk.Tk()
    listbox = Drag_and_Drop_Listbox(root)
    for i,name in enumerate(['name'+str(i) for i in range(10)]):
        listbox.insert(tk.END, name)
        if i % 2 == 0:
            listbox.selection_set(i)
    listbox.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

# Класс для шкалы прогресса, без класса не решается
class MonApp(Tk):
    def __init__(self):
        super().__init__()
        self.btn = Button(self, text='Traitement', command=self.traitement)
        self.btn.grid(row=0, column=0)
        self.progress = Progressbar(self, orient=HORIZONTAL, length=100, mode='indeterminate')
    def traitement(self):
        def real_traitement():
            self.progress.grid(row=1,column=0)
            self.progress.start()
            time.sleep(5)
            self.progress.stop()
            self.progress.grid_forget()
            self.btn['state']='normal'
        self.btn['state']='disabled'
        threading.Thread(target=real_traitement).start()

def mergePages():
    import tempfile

    class PDFManager:
        def __init__(self):
            self.pdf_files = {}  # {filename: (filepath, file_handle, PdfReader instance)}
            self.current_pdf = None

        def add_pdf(self, filepath):
            try:
                file_handle = open(filepath, 'rb')
                reader = PyPDF2.PdfReader(file_handle)
                self.pdf_files[filepath] = (filepath, file_handle, reader)
                return True
            except Exception as e:
                popup(f"Ошибка загрузки файла: {str(e)}")
                return False

        def get_pages(self, filepath):
            if filepath in self.pdf_files:
                return self.pdf_files[filepath][2].pages
            return []

        def set_current_pdf(self, filepath):
            if filepath in self.pdf_files:
                self.current_pdf = filepath

        def get_current_pages(self):
            if self.current_pdf:
                # Переоткрываем файл если он был закрыт
                filepath, file_handle, reader = self.pdf_files[self.current_pdf]
                if file_handle.closed:
                    file_handle = open(filepath, 'rb')
                    reader = PyPDF2.PdfReader(file_handle)
                    self.pdf_files[self.current_pdf] = (filepath, file_handle, reader)
                return reader.pages
            return []

        def close_all(self):
            for filepath, file_handle, _ in self.pdf_files.values():
                if not file_handle.closed:
                    file_handle.close()
            self.pdf_files.clear()

    def open_pdf_page(pdf_path, page_num):
        temp_pdf = PyPDF2.PdfWriter()
        pages = pdf_manager.get_pages(pdf_path)
        if page_num < len(pages):
            temp_pdf.add_page(pages[page_num])

        temp_path = os.path.join(tempfile.gettempdir(), f"temp_page_{page_num}.pdf")
        with open(temp_path, 'wb') as f:
            temp_pdf.write(f)

        if 'win' in os.sys.platform:
            os.startfile(temp_path)
        else:
            subprocess.call(['xdg-open', temp_path])

    def update_left_listbox():
        left_listbox.delete(0, tk.END)
        for filepath in pdf_manager.pdf_files:
            left_listbox.insert(tk.END, os.path.basename(filepath))

    def update_middle_listbox():
        middle_listbox.delete(0, tk.END)
        try:
            pages = pdf_manager.get_current_pages()
            for i in range(len(pages)):
                middle_listbox.insert(tk.END, f"Page {i+1}")
        except Exception as e:
            popup(f"Ошибка загрузки страниц: {str(e)}")
            middle_listbox.delete(0, tk.END)

    def on_left_select(event):
        selection = left_listbox.curselection()
        if selection:
            filepath = list(pdf_manager.pdf_files.keys())[selection[0]]
            pdf_manager.set_current_pdf(filepath)
            update_middle_listbox()

    def move_to_right():
        selection = middle_listbox.curselection()
        if not selection or not pdf_manager.current_pdf:
            return

        for idx in selection:
            page_num = int(middle_listbox.get(idx).split()[1]) - 1
            right_listbox.insert(tk.END, (pdf_manager.current_pdf, page_num))

    def remove_from_right():
        selection = right_listbox.curselection()
        for idx in reversed(selection):
            right_listbox.delete(idx)

    def move_up_right():
        selection = right_listbox.curselection()
        if not selection:
            return

        for pos in selection:
            if pos == 0:
                continue
            text = right_listbox.get(pos)
            right_listbox.delete(pos)
            right_listbox.insert(pos-1, text)
            right_listbox.selection_set(pos-1)

    def move_down_right():
        selection = right_listbox.curselection()
        if not selection:
            return

        for pos in reversed(selection):
            if pos == right_listbox.size()-1:
                continue
            text = right_listbox.get(pos)
            right_listbox.delete(pos)
            right_listbox.insert(pos+1, text)
            right_listbox.selection_set(pos+1)

    def merge_pdfs():
        if right_listbox.size() == 0:
            popup("Нет страниц для сшивания!")
            return

        output_file = filedialog.asksaveasfilename(
            title="Сохранить объединённый PDF",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"),)
        )

        if not output_file:
            return

        # Создаем новое окно для прогресс-бара
        progress_window = tk.Toplevel(merge_window)
        progress_window.title("Сшивание PDF")
        progress_window.geometry("300x100")

        progress = Progressbar(progress_window, orient=tk.HORIZONTAL, length=280, mode='determinate')
        progress.pack(pady=20)

        label = tk.Label(progress_window, text="Идет процесс сшивания...")
        label.pack()

        def do_merge():
            try:
                merger = PyPDF2.PdfMerger()
                total_pages = right_listbox.size()

                for i in range(total_pages):
                    pdf_path, page_num = right_listbox.get(i)
                    # Всегда получаем свежий reader для файла
                    file_handle = open(pdf_path, 'rb')
                    reader = PyPDF2.PdfReader(file_handle)
                    if page_num < len(reader.pages):
                        merger.append(fileobj=file_handle, pages=(page_num, page_num+1))
                    file_handle.close()

                    progress['value'] = (i + 1) / total_pages * 100
                    progress_window.update()

                with open(output_file, 'wb') as f:
                    merger.write(f)

                progress_window.destroy()
                finished(output_file, "Сшивание", merge_window)
            except Exception as e:
                progress_window.destroy()
                popup(f"Ошибка: {str(e)}")

        # Запускаем сшивание в отдельном потоке
        threading.Thread(target=do_merge).start()

    def add_pdfs():
        files = filedialog.askopenfilenames(
            title="Выберите PDF файлы",
            filetypes=(("PDF files", "*.pdf"),),
            initialdir=os.getcwd()
        )

        for file in files:
            if file not in pdf_manager.pdf_files:
                if pdf_manager.add_pdf(file):
                    update_left_listbox()

    def clear_all():
        pdf_manager.close_all()
        pdf_manager.current_pdf = None
        left_listbox.delete(0, tk.END)
        middle_listbox.delete(0, tk.END)
        right_listbox.delete(0, tk.END)

    # Initialize PDF manager
    pdf_manager = PDFManager()

    # Create main window
    merge_window = tk.Tk()
    merge_window.title("PDF сшить страницы")
    merge_window.geometry("1200x600")
    merge_window.minsize(800, 400)

    # Configure grid weights
    for i in range(3):
        merge_window.columnconfigure(i, weight=1)
    merge_window.rowconfigure(1, weight=1)

    # Icons
    add_icon = "📄"
    open_icon = "👁"
    move_icon = "➡"
    remove_icon = "❌"
    merge_icon = "🔗"
    clear_icon = "🧹"
    up_icon = "⬆"
    down_icon = "⬇"

    # Left frame - PDF files list
    left_frame = tk.LabelFrame(merge_window, text="PDF файлы", padx=5, pady=5)
    left_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(0, weight=1)

    left_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE)
    left_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
    left_listbox.bind('<<ListboxSelect>>', on_left_select)

    left_buttons = tk.Frame(left_frame)
    left_buttons.grid(row=1, column=0, sticky=tk.EW, pady=5)

    tk.Button(left_buttons, text=add_icon + " Добавить", command=add_pdfs).pack(side=tk.LEFT, padx=2)
    tk.Button(left_buttons, text=clear_icon + " Очистить", command=clear_all).pack(side=tk.LEFT, padx=2)

    # Middle frame - Pages of selected PDF
    middle_frame = tk.LabelFrame(merge_window, text="Страницы выбранного PDF", padx=5, pady=5)
    middle_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)
    middle_frame.columnconfigure(0, weight=1)
    middle_frame.rowconfigure(0, weight=1)

    middle_listbox = tk.Listbox(middle_frame, selectmode=tk.EXTENDED)
    middle_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

    middle_buttons = tk.Frame(middle_frame)
    middle_buttons.grid(row=1, column=0, sticky=tk.EW, pady=5)

    tk.Button(middle_buttons, text=open_icon + " Просмотреть",
              command=lambda: (
                  open_pdf_page(
                      pdf_manager.current_pdf,
                      int(middle_listbox.get(middle_listbox.curselection()[0]).split()[1]) - 1
                  ) if pdf_manager.current_pdf and middle_listbox.curselection() else None
              )).pack(side=tk.LEFT, padx=2)

    # Right frame - Pages to merge
    right_frame = tk.LabelFrame(merge_window, text="Страницы для сшивания", padx=5, pady=5)
    right_frame.grid(row=1, column=2, sticky=tk.NSEW, padx=5, pady=5)
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(0, weight=1)

    right_listbox = tk.Listbox(right_frame)
    right_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

    right_buttons = tk.Frame(right_frame)
    right_buttons.grid(row=1, column=0, sticky=tk.EW, pady=5)

    tk.Button(right_buttons, text=move_icon + " Добавить", command=move_to_right).pack(side=tk.LEFT, padx=2)
    tk.Button(right_buttons, text=remove_icon + " Удалить", command=remove_from_right).pack(side=tk.LEFT, padx=2)
    tk.Button(right_buttons, text=up_icon + " Вверх", command=move_up_right).pack(side=tk.LEFT, padx=2)
    tk.Button(right_buttons, text=down_icon + " Вниз", command=move_down_right).pack(side=tk.LEFT, padx=2)

    # Control buttons at the bottom
    control_frame = tk.Frame(merge_window)
    control_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)

    tk.Button(control_frame, text=merge_icon + " Сшить", command=merge_pdfs).pack(side=tk.RIGHT, padx=5)
    tk.Button(control_frame, text="Отмена", command=lambda: [pdf_manager.close_all(), merge_window.destroy()]).pack(side=tk.RIGHT, padx=5)

    merge_window.mainloop()


def updatePages():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    updaterWindow = tk.Tk()
    updaterWindow.title("PDF обновить страницу")
    updaterWindow.resizable(False, False)

    tk.Label(updaterWindow, text="Обновит одну страницу PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(updaterWindow, text="Выбери PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(updaterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(updaterWindow, text="Выбрать...", command=lambda entry=updateFile, window=updaterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(updaterWindow, text="Страница для обновления:").grid(row=2, column=0, padx=10, pady=3)
    pageToUpdate = tk.Entry(updaterWindow)
    pageToUpdate.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(updaterWindow, text="Выбери PDF с новой страницей:").grid(row=3, column=0, padx=10, pady=3)
    updatedPage = tk.Entry(updaterWindow)
    updatedPage.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(updaterWindow, text="Выбрать...", command=lambda entry=updatedPage, window=updaterWindow: filePicker(entry, window)).grid(row=3, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(updaterWindow, text="Номер страницы:").grid(row=4, column=0, padx=10, pady=3)
    pageWithUpdate = tk.Entry(updaterWindow)
    pageWithUpdate.grid(row=4, column=1, sticky=stickyFill, pady=5, padx=5)
    pageWithUpdate.insert(0, "1")

    tk.Button(updaterWindow, text="Обновить!", command=lambda: updaterWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    updaterWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToUpdate = int(pageToUpdate.get())
    filename = filename[:-4] + '-upd'+str(pageToUpdate)+'.pdf'
    updatedPage = checkExist(updatedPage.get())
    pageWithUpdate = int(pageWithUpdate.get())

    if pageToUpdate == 0 or pageWithUpdate == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    updatedPagePDF = PyPDF2.PdfReader(updatedPage)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        updatedPDF.insert_page(updatedPagePDF.pages[pageWithUpdate - 1], pageToUpdate - 1)
    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    outputFile = open(filename, 'wb')

    pdfOut = PyPDF2.PdfWriter()

    for i in range(len(updatedPDF.pages)):
        if i != pageToUpdate:
            pdfOut.add_page(updatedPDF.pages[i])

    pdfOut.write(outputFile)
    outputFile.close()

    updaterWindow.destroy()
    finished(filename, "Обновление страницы", updaterWindow)

def movePages():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    moveWindow = tk.Tk()
    moveWindow.title("PDF переместить страницу")
    moveWindow.resizable(False, False)

    tk.Label(moveWindow, text="Переместить страницу PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(moveWindow, text="Начальный PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(moveWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(moveWindow, text="Выбрать...", command=lambda entry=updateFile, window=moveWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(moveWindow, text="Номер страницы для перемещения:").grid(row=2, column=0, padx=10, pady=3)
    pageBefore = tk.Entry(moveWindow)
    pageBefore.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(moveWindow, text="Номер страницы, перед которым вставить:").grid(row=4, column=0, padx=10, pady=3)
    pageAfter = tk.Entry(moveWindow)
    pageAfter.grid(row=4, column=1, sticky=stickyFill, pady=5, padx=5)
    pageAfter.insert(0, "1")

    tk.Button(moveWindow, text="Переместить!", command=lambda: moveWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    moveWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageBefore = int(pageBefore.get())
    filename = filename[:-4] + '-mov-'+str(pageBefore)+'.pdf'
    pageAfter = int(pageAfter.get())

    if pageBefore == 0 or pageAfter == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    updatedPDF = PyPDF2.PdfWriter()
    try:
        page_was_deleted = False
        for i in range(len(originalPDF.pages)):
            #updatedPDF.insert_page(originalPDF.pages[pageBefore - 1], pageAfter - 1)
            if i == pageBefore-1:
                # 1 - удаление страницы
                page_was_deleted = True
                continue
            elif i == pageAfter-1 and page_was_deleted:
                # 2 - добавление страницы после удалённой
                page_was_deleted = False
                updatedPDF.add_page(originalPDF.pages[i])
                updatedPDF.add_page(originalPDF.pages[pageBefore-1])
            elif i == pageAfter-1:
                # 3 - добавление страницы до удаления либо отработан 2
                updatedPDF.add_page(originalPDF.pages[pageBefore-1])
                updatedPDF.add_page(originalPDF.pages[i])
            else:
                # ряовое включение страницы
                updatedPDF.add_page(originalPDF.pages[i])

    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    #pdfOut = PyPDF2.PdfWriter()
    outputFile = open(filename, 'wb')
    updatedPDF.write(outputFile)
    outputFile.close()

    moveWindow.destroy()
    finished(filename, "Перемещение страницы", moveWindow)

def getPage():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    getWindow = tk.Tk()
    getWindow.title("PDF Сохранить страницу")
    getWindow.resizable(False, False)

    tk.Label(getWindow, text="Сохранить страницу из PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(getWindow, text="Начальный PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(getWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(getWindow, text="Выбрать...", command=lambda entry=updateFile, window=getWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(getWindow, text="Номер страницы:").grid(row=2, column=0, padx=10, pady=3)
    pageToget = tk.Entry(getWindow)
    pageToget.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Button(getWindow, text="Сохранить!", command=lambda: getWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    getWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToget = int(pageToget.get())
    filename = filename[:-4] + '-saved-'+str(pageToget)+'.pdf'
    originalPDF = PyPDF2.PdfReader(updateFile)
    if pageToget <1:
        pageToget = 1
    outputFile = open(filename, 'wb')
    pdfOut = PyPDF2.PdfWriter()
    pdfOut.add_page(originalPDF.pages[pageToget-1])
    pdfOut.write(outputFile)
    outputFile.close()

    getWindow.destroy()
    finished(filename, "Сохранение страницы", getWindow)

def insertPages():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    inserterWindow = tk.Tk()
    inserterWindow.title("PDF вставить страницу")
    inserterWindow.resizable(False, False)

    tk.Label(inserterWindow, text="Вставить страницу внутрь PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(inserterWindow, text="Начальный PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(inserterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(inserterWindow, text="Выбрать...", command=lambda entry=updateFile, window=inserterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(inserterWindow, text="Номер будущей страницы:").grid(row=2, column=0, padx=10, pady=3)
    pageToInsert = tk.Entry(inserterWindow)
    pageToInsert.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(inserterWindow, text="PDF с новой страницей:").grid(row=3, column=0, padx=10, pady=3)
    fileWithInsert = tk.Entry(inserterWindow)
    fileWithInsert.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(inserterWindow, text="Выбрать...", command=lambda entry=fileWithInsert, window=inserterWindow: filePicker(entry, window)).grid(row=3, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(inserterWindow, text="Номер заимствованной страницы для вставки:").grid(row=4, column=0, padx=10, pady=3)
    pageWithInsert = tk.Entry(inserterWindow)
    pageWithInsert.grid(row=4, column=1, sticky=stickyFill, pady=5, padx=5)
    pageWithInsert.insert(0, "1")

    tk.Button(inserterWindow, text="Вставить!", command=lambda: inserterWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    inserterWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToInsert = int(pageToInsert.get())
    filename = filename[:-4] + '-ins-'+str(pageToInsert)+'.pdf'
    fileWithInsert = checkExist(fileWithInsert.get())
    pageWithInsert = int(pageWithInsert.get())

    if pageToInsert == 0 or pageWithInsert == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    PDFwithInsert = PyPDF2.PdfReader(fileWithInsert)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        updatedPDF.insert_page(PDFwithInsert.pages[pageWithInsert - 1], pageToInsert - 1)
    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    outputFile = open(filename, 'wb')

    pdfOut = PyPDF2.PdfWriter()

    for i in range(len(updatedPDF.pages)):
        pdfOut.add_page(updatedPDF.pages[i])

    pdfOut.write(outputFile)
    outputFile.close()
    inserterWindow.destroy()
    finished(filename, "Вставка страницы", inserterWindow)

def deletePages():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    deleterWindow = tk.Tk()
    deleterWindow.title("Удалить страницы из PDF")
    deleterWindow.resizable(False, False)
    '''
    вариант 4
    вместо диапазона парсить re строку типа 1,3,5-15, 23
    интерпретировать в 1,3,5,6,7,8,9,10,11,12,13,14,15,23
    автосортировка после распознавания, set() для исключения повторов
    пройтись с конца 23...1 для удаления листов
    имя включает начальную строку пользователя без пробелов
    '''

    tk.Label(deleterWindow, text="Удаляет диапазон страниц из PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(deleterWindow, text="PDF для редактирования:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(deleterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(deleterWindow, text="Выбрать...", command=lambda entry=updateFile, window=deleterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(deleterWindow, text="Первая страница:").grid(row=2, column=0, padx=10, pady=3)
    pageFromDelete = tk.Entry(deleterWindow)
    pageFromDelete.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(deleterWindow, text="Последняя страница:").grid(row=3, column=0, padx=10, pady=3)
    pageToDelete = tk.Entry(deleterWindow)
    pageToDelete.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Button(deleterWindow, text="Удалить!", command=lambda: deleterWindow.quit()).grid(row=4, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    deleterWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToDelete = int(pageToDelete.get())
    pageFromDelete = int(pageFromDelete.get())
    filename = f'{filename[:-4]}-del-{pageFromDelete}-{pageToDelete}.pdf'

    if pageToDelete == 0 or pageToDelete < pageFromDelete:
        popup("Число не верно, должно быть больше 0 и не в обратном порядке")

    originalPDF = PyPDF2.PdfReader(updateFile)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        for i in range(pageToDelete,pageFromDelete-1,-1):
            updatedPDF.pages[i - 1]
    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    outputFile = open(filename, 'wb')

    pdfOut = PyPDF2.PdfWriter()

    for i in range(len(updatedPDF.pages)):
        if i > pageToDelete - 1 or i < pageFromDelete - 1:
            pdfOut.add_page(updatedPDF.pages[i])

    pdfOut.write(outputFile)
    outputFile.close()

    deleterWindow.destroy()
    finished(filename, "Удаление страницы", deleterWindow)

def optimizePDF():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    optimizerWindow = tk.Tk()
    optimizerWindow.title("Оптимизировать PDF, уменьшить объём.")
    optimizerWindow.resizable(False, False)

    tk.Label(optimizerWindow, text="Оптимизирует PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(optimizerWindow, text="Исходный PDF:").grid(row=1, column=0, padx=10, pady=3)
    optimizerFile = tk.Entry(optimizerWindow)
    optimizerFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(optimizerWindow, text="Выбрать...", command=lambda entry=optimizerFile, window=optimizerWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Button(optimizerWindow, text="Оптимизировать!", command=lambda: optimizerWindow.quit()).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    optimizerWindow.mainloop()

    filename_ = optimizerFile.get()
    filename = f'{filename_[:-4]}-opt.pdf'
    optimizerFile = checkExist(optimizerFile.get())
    originalPDF = PyPDF2.PdfReader(optimizerFile)
    outputFile = open(filename, 'wb')
    pdfOut = PyPDF2.PdfWriter()

    for page in originalPDF.pages:
        page.compress_content_streams()  # This is CPU intensive!
        pdfOut.add_page(page)
    pdfOut.write(outputFile)
    outputFile.close()
    optimizerWindow.destroy()
    finished(filename, "Оптимизатор PDF ", optimizerWindow)

def checkExist(fileName):
    try:
        openedFile = open(fileName, 'rb')
        print("Найден файл ",fileName)
        if fileName.endswith('pdf'):
            return openedFile
    except FileNotFoundError:
        popup(f'{fileName} не найден либо неисправен. Обратитесь к разработчику по ссылке «Описание проекта»')

def boomPages():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    boomerWindow = tk.Tk()
    boomerWindow.title("Взорвать PDF на мелкие листы в папку.")
    boomerWindow.resizable(False, False)

    tk.Label(boomerWindow, text="Разделяет страницы PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(boomerWindow, text="PDF для редактирования:").grid(row=1, column=0, padx=10, pady=3)
    boomFile = tk.Entry(boomerWindow)
    boomFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(boomerWindow, text="Выбрать...", command=lambda entry=boomFile, window=boomerWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Button(boomerWindow, text="Разделить!", command=lambda: boomerWindow.quit()).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    boomerWindow.mainloop()

    filename_ = boomFile.get()
    boomFile = checkExist(boomFile.get())
    originalPDF = PyPDF2.PdfReader(boomFile)
    directory, name_ = os.path.split(filename_)
    newdir = os.path.join(directory,'_separated')
    os.mkdir(newdir)
    if not boomFile:
        finished(filename_, "Разделение страницы", boomerWindow)
    for i in range(len(originalPDF.pages)):
        k = "%03d" % (i+1,)
        print(newdir,name_[:-4],k,'.pdf',end='\r')
        filename = os.path.join(newdir,f'{name_[:-4]}-sep-{str(k)}.pdf')
        outputFile = open(filename, 'wb')
        pdfOut = PyPDF2.PdfWriter()
        pdfOut.add_page(originalPDF.pages[i])
        pdfOut.write(outputFile)
        outputFile.close()

    boomerWindow.destroy()
    finished(filename_, "Разделение страницы", boomerWindow)

def instructions():
    webbrowser.open("https://github.com/nortikin/PDF_Merge_and_Edit", new=2, autoraise=True)

# Обновленные кнопки в главном окне с иконками
def create_main_window():
    selector = tk.Tk()
    selector.configure(padx=10, pady=10)
    selector.title("PDF Редактор")
    icon = tk.PhotoImage(data=favicon.icon)
    selector.tk.call('wm', 'iconphoto', selector._w, icon)
    selector.resizable(False, False)

    stickyFill = tk.N + tk.E + tk.W + tk.S

    # Иконки для кнопок
    split_icon = "✂️"
    merge_icon = "📚"
    update_icon = "🔄"
    insert_icon = "⏏️"
    extract_icon = "📄"
    move_icon = "↔️"
    delete_icon = "❌"
    optimize_icon = "⚡"
    github_icon = "🐙"

    # body of GUI
    tk.Label(selector, text="Работа с PDF v 1.0.0").grid(row=1, column=1, pady=5, padx=5)

    tk.Button(selector, text=f"{split_icon} Разбить PDF файл в папку        ", command=boomPages).grid(row=2, column=0, columnspan=2, rowspan=2, sticky=stickyFill, pady=10, padx=5)
    tk.Button(selector, text=f"{merge_icon} Сшить PDF файл из папки       ", command=mergePages).grid(row=4, column=0, columnspan=2, rowspan=2, sticky=stickyFill, pady=10, padx=5)
    tk.Button(selector, text=f"{github_icon} Описание проекта в github       ", command=instructions).grid(row=6, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{update_icon} Обновить страницу в PDF        ", command=updatePages).grid(row=6, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{insert_icon} Втиснуть страницу в PDF           ", command=insertPages, padx=20).grid(row=7, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{extract_icon} Сохранить страницу из PDF      ", command=getPage, padx=20).grid(row=8, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{move_icon} Переместить страницу PDF       ", command=movePages).grid(row=9, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{delete_icon} Удалить страницы в PDF            ", command=deletePages).grid(row=10, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{optimize_icon} Оптимизировать PDF файл         ", command=optimizePDF).grid(row=11, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
    #tk.Button(selector, text=f"{github_icon} Описание проекта в github       ", command=instructions).grid(row=12, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)

    selector.protocol("WM_DELETE_WINDOW", sys.exit)
    selector.mainloop()

# Замените вызов selector = tk.Tk() на:
if __name__ == "__main__":
    create_main_window()
