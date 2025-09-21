# from PyQt6.QtWidgets import QApplication
# from PyQt6.QtGui import QClipboard
#
#
# def copy_to_clipboard(text: str):
#     clipboard = QApplication.clipboard()
#     clipboard.setText(text)
def copy_to_clipboard(text: str):
    try:
        import pyperclip

        pyperclip.copy(text)
    except:
        print("Error: failed to copy to clipboard")
        pass
