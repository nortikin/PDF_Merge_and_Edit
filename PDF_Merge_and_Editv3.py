import PyPDF2
import os
import subprocess
import time
import sys
import webbrowser
import favicon
import tkinter as tk
from tkinter import filedialog
from functools import partial

# Written by Simon Wong
# https://github.com/simonwongwong


def popup(text):
    textwindow = tk.Tk()
    textwindow.title('Оштбка!')
    textwindow.minsize(width=300, height=50)
    label = tk.Label(textwindow, text=text)
    label.pack()
    label.configure(pady=20)
    textwindow.mainloop()


def finished(file, operation, window):
    finishPrompt = tk.Tk()
    finishPrompt.title(operation + " сделано!")
    tk.Label(finishPrompt, text=operation + " кончено. Открыть файл?").grid(row=0, column=0, columnspan=2, pady=5, padx=5)
    if 'win' not in os.sys.platform:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: subprocess.call(['evince',file])).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    else:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: os.startfile(file)).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    tk.Button(finishPrompt, text="До свидания", command=lambda: finishPrompt.destroy()).grid(row=1, column=1, pady=5, padx=5, sticky=stickyFill)
    finishPrompt.mainloop()


def filePicker(entry, window):
    file = filedialog.askopenfilename(title="Выбери PDF", filetypes=(("PDF", "*.pdf"),), initialdir=os.getcwd())

    if entry.get() == "":
        entry.insert(0, file)
    else:
        entry.delete(0, 'end')
        entry.insert(0, file)

    window.lift()


def merge(entry, window):

    mergeWindow = tk.Tk()
    mergeWindow.title("PDF merger")

    tk.Label(mergeWindow, text="Создаст новый PDF из набора файлов").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    entry = int(entry.get())
    for i in range(int(entry+1)):
        tk.Label(mergeWindow, text=f"Выбери {i+1}-й PDF:").grid(row=i+1, column=0, padx=10, pady=3)
        locals()[f'collaps_{i}'] = tk.Entry(mergeWindow)
        locals()[f'collaps_{i}'].grid(row=i+1, column=1, sticky=stickyFill, pady=5, padx=5)
        tk.Button(mergeWindow, text="Выбрать...", command=lambda entry=locals()[f'collaps_{i}'], window=mergeWindow: filePicker(entry, window)).grid(row=i+1, column=2, pady=5, padx=5, sticky=stickyFill)



    tk.Label(mergeWindow, text="Имя сшитого файла:").grid(row=i+1, column=0)
    mergedFile = tk.Entry(mergeWindow)
    mergedFile.grid(row=i+1, column=1, padx=5, pady=5, sticky=stickyFill)
    tk.Button(mergeWindow, text="Искать...", command=lambda entry=mergedFile, window=mergeWindow: filePicker(entry, window)).grid(row=i+1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Button(mergeWindow, text="Сшить!", command=lambda: mergeWindow.quit()).grid(row=i+2, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    mergeWindow.mainloop()

    files_ = []
    for i in range(int(entry)):
        try:
            files_.append(checkExist(locals()[f'collaps_{i}'].get()))
        except:
            pass
    print(f'files are {files_}')

    mergedFile = mergedFile.get()
    mergedBook = PyPDF2.PdfMerger()
    for f in files_:
        mergedBook.append(f.name)


    fullbook = open(mergedFile + '.pdf', 'wb')
    mergedBook.write(fullbook)
    mergedBook.close()
    fullbook.close()
    mergeWindow.destroy()
    finished(mergedFile + ".pdf", "Merge", mergeWindow)


def pageUpdate():
    updaterWindow = tk.Tk()
    updaterWindow.title("Обновить страницу PDF")

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
    filename = filename[:-4] + '-upd'+pageToUpdate+'.pdf'
    updatedPage = checkExist(updatedPage.get())
    pageWithUpdate = int(pageWithUpdate.get())

    if pageToUpdate == 0 or pageWithUpdate == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    updatedPagePDF = PyPDF2.PdfReader(updatedPage)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        updatedPDF.insertPage(updatedPagePDF.pages[pageWithUpdate - 1], pageToUpdate - 1)
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


def insertPage():
    inserterWindow = tk.Tk()
    inserterWindow.title("PDF вставка страницы")

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
    filename = filename[:-4] + '-ins-'+pageToInsert+'.pdf'
    fileWithInsert = checkExist(fileWithInsert.get())
    pageWithInsert = int(pageWithInsert.get())

    if pageToInsert == 0 or pageWithInsert == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    PDFwithInsert = PyPDF2.PdfReader(fileWithInsert)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        updatedPDF.insertPage(PDFwithInsert.pages[pageWithInsert - 1], pageToInsert - 1)
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
    deleterWindow = tk.Tk()
    deleterWindow.title("Удалить страницы из PDF")

    tk.Label(deleterWindow, text="Удаляет диапазон страниц из PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(deleterWindow, text="PDF для редактирования:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(deleterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(deleterWindow, text="Выбрать...", command=lambda entry=updateFile, window=deleterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(deleterWindow, text="Первая страница:").grid(row=2, column=0, padx=10, pady=3)
    pageFromDelete = tk.Entry(deleterWindow)
    pageFromDelete.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(deleterWindow, text="последняя страница:").grid(row=3, column=0, padx=10, pady=3)
    pageToDelete = tk.Entry(deleterWindow)
    pageToDelete.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Button(deleterWindow, text="Удаоить!", command=lambda: deleterWindow.quit()).grid(row=4, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

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


def checkExist(fileName):
    try:
        openedFile = open(fileName, 'rb')
        return openedFile
    except FileNotFoundError:
        popup('"' + fileName + '"' + " не найден. Пжлст, перезапустите программу.")


def instructions():
    webbrowser.open("https://github.com/simonwongwong/PDF_Merge_and_Edit", new=2, autoraise=True)


selector = tk.Tk()
selector.configure(padx=10, pady=10)
selector.title("PDF Редактор")
icon = tk.PhotoImage(data=favicon.icon)
selector.tk.call('wm', 'iconphoto', selector._w, icon)

stickyFill = tk.N + tk.E + tk.W + tk.S

# body of GUI
tk.Label(selector, text="Возможности:").grid(row=0, column=1, columnspan=2, pady=5, padx=5)
nfiles = tk.IntVar()
entry_ = tk.Entry(selector, text=nfiles)
entry_.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
nfiles.set(2)
tk.Button(selector, text="Сшить PDFs", command=lambda entry=entry_, window=selector: merge(entry, window)).grid(row=1, column=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Обновить страницу", command=pageUpdate).grid(row=2, column=1, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Всунуть страницу в PDF", command=insertPage, padx=20).grid(row=3, column=1, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Удалить диапазон страниц", command=deletePages).grid(row=4, column=1, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Руководство", command=instructions).grid(row=5, column=1, columnspan=2, sticky=stickyFill, pady=3, padx=5)


selector.protocol("WM_DELETE_WINDOW", sys.exit)
selector.mainloop()
