import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QFileDialog
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def truncateString(string, maxLen):
	if len(string) > maxLen:
		string = "..." + string[maxLen - 3:]
	return string

#This function creates a hash of the file from the path that is given to it. The function requires two arguments:
#'path' for the file path, and 'hType' for the hash type. It returns the hash as a hexadecimal digest.
def createHashOfFile(path, hType):
	with open(path, 'rb', buffering = 0) as file1:
		return hashlib.file_digest(file1, hType).hexdigest()

#The purpose of this class is to provide the goBack method to all other classes. 	
class BaseClass():

	#This method allows the user to navigate to the previous window. It also closes the instance of the current window, so RAM is not wasted.	
	def goBack(self, window):
		screen = window()
		widgets.addWidget(screen)
		widgets.setCurrentWidget(screen)
		self.close()
		
#This is the class for the main window.
class MainWindow(QDialog):
	def __init__(self):
		super(MainWindow, self).__init__()
		loadUi("main.ui", self)
		self.hashButton.clicked.connect(self.goToCheckOrValidationSelection)
		self.encryptButton.clicked.connect(self.goToEncryptionDecryption)
	
	#This method takes the user to the window in which they can choose whether they want to create or validate a hash.
	def goToCheckOrValidationSelection(self):
		checkOrValidation = HashCheckOrValidationScreen()
		widgets.addWidget(checkOrValidation)
		widgets.setCurrentWidget(checkOrValidation)
		self.close()
	
	#This method takes the user to the window in which they can choose whether they want to	encrypt or decrypt a file.
	def goToEncryptionDecryption(self):
		screen = EncryptionDecryptionScreen()
		widgets.addWidget(screen)
		widgets.setCurrentWidget(screen)
		self.close()
		
#This is the class for the window in which the user can choose whether they want to create or validate a hash.
class HashCheckOrValidationScreen(QMainWindow, BaseClass):
	def __init__(self):
		super(HashCheckOrValidationScreen, self).__init__()
		loadUi("hashing_general.ui", self)
		self.createHashButton.clicked.connect(self.goToHashSelectionScreen)
		self.validateHashButton.clicked.connect(self.goToHashSelectionScreen)
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, MainWindow))
		
	#This method takes the user to the window in which they can choose which hashing algorithm they wish to be used.
	def goToHashSelectionScreen(self):
		hashSelectionScreen = HashSelectionScreen()
		widgets.addWidget(hashSelectionScreen)
		widgets.setCurrentWidget(hashSelectionScreen)
		self.close()
		
#This is the class for the window in which the user can choose whether they want to encrypt or decrypt a file.
class EncryptionDecryptionScreen(QMainWindow, BaseClass):
	def __init__(self):
		super(EncryptionDecryptionScreen, self).__init__()
		loadUi("encrypting_decrypting_general.ui", self)
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, MainWindow))
		self.encryptButton.clicked.connect(self.goToEncrypt)
		self.decryptButton.clicked.connect(self.goToDecrypt)
		
	#This method takes the user to the window in which they can encrypt a file.
	def goToEncrypt(self):
		screen = EncryptionScreen()
		widgets.addWidget(screen)
		widgets.setCurrentWidget(screen)
		self.close()
		
	#This method takes the user to the window in which they can decrypt a file.
	def goToDecrypt(self):
		screen = DecryptionScreen()
		widgets.addWidget(screen)
		widgets.setCurrentWidget(screen)
		self.close()
	
#This is the class for the window in which the user can encrypt a file.	
class EncryptionScreen(QMainWindow, BaseClass):
	def __init__(self):
		super(EncryptionScreen, self).__init__()
		loadUi("select_encrypt.ui", self)
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, EncryptionDecryptionScreen))
		self.selectFileButton.clicked.connect(self.selectFile)
		self.encryptButton.clicked.connect(self.encrypt)
		self.path = ""
	
	#This method allows the user to open a file explorer in order for them to choose a file which they wish to encrypt.	
	def selectFile(self):
		try:
			self.path = ""
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			f = QFileDialog.getOpenFileName(self)
			
			filename = f[0]
			if filename:
				self.path = filename
				filename = truncateString(filename, 40)
				self.selected_file_name.setText(filename.strip())
				self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
		except FileNotFoundError:
			print("File not found.")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			
		except:
			print("An error occurred.")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
	
	#This method encrypts the chosen file. A random 256-bit key is generated, and AES and it's GCM mode are used.		
	def encrypt(self):
		if self.path:
			try:
				with open(self.path, "rb") as file:
					plaintext = file.read()
					
				key = get_random_bytes(32)
				cipher = AES.new(key, AES.MODE_GCM)
				ciphertext, tag = cipher.encrypt_and_digest(plaintext)
				
				with open(self.path, "wb") as file:
					file.write(tag)
					file.write(cipher.nonce)
					file.write(ciphertext)
					
				
				screen = EncryptionSuccessScreen(key.hex())
				widgets.addWidget(screen)
				widgets.setCurrentWidget(screen)
				self.close()
				
			except ValueError:
				screen = FailureScreen("encryption1")
				widgets.addWidget(screen)
				widgets.setCurrentWidget(screen)
				self.close()
			except:
				screen = FailureScreen("encryption2")
				widgets.addWidget(screen)
				widgets.setCurrentWidget(screen)
				self.close()
		
#This is the class for the window in which the user is informed of the successful encrypting of their chosen file. 
#In this window, they are also provided the key which was used in the encryption process.		
class EncryptionSuccessScreen(QMainWindow, BaseClass):
	def __init__(self, key):
		super(EncryptionSuccessScreen, self).__init__()
		loadUi("success_encrypt.ui", self)
		self.key = key
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, EncryptionDecryptionScreen))
		self.textBrowser.setText(key)

#This is the class for the window in which the user can decrypt a file that they know the key for. 
#Of course, the decryption process only works for the specific encryption type used in this program. 	
class DecryptionScreen(QMainWindow, BaseClass):
	def __init__(self):
		super(DecryptionScreen, self).__init__()
		loadUi("select_decrypt.ui", self)
		self.lineEdit.setPlaceholderText("Copy the key here...")
		self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, EncryptionDecryptionScreen))
		self.selectFileButton.clicked.connect(self.selectFile)
		self.decryptButton.clicked.connect(self.decrypt)
		
		self.path = ""

	#This method allows the user to open a file explorer in order for them to choose a file which they wish to decrypt.
	def selectFile(self):
		try:
			self.path = ""
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			f = QFileDialog.getOpenFileName(self)
			print(f[0])
			filename = f[0]
			if filename:
				self.path = filename
				filename = truncateString(filename, 40)
				self.selected_file_name.setText(filename.strip())
				self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
		except FileNotFoundError:
			print("File not found.")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			
		except:
			print("An error occurred.")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
	
	#This method decrypts the chosen file using the user-provided hexadecimal key.		
	def decrypt(self):
		if self.path and self.lineEdit.text():
			try:
				with open(self.path, "rb") as file:
					tag = file.read(16)
					nonce = file.read(16)
					ciphertext = file.read()
					
				key = self.lineEdit.text().strip()
				key = bytes.fromhex(key)
				cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
				
				plaintext = cipher.decrypt_and_verify(ciphertext, tag)
				
				with open(self.path, "w") as file:
					file.write(plaintext.decode())
					
				screen = DecryptionSuccessScreen()
				widgets.addWidget(screen)
				widgets.setCurrentWidget(screen)
				self.close()
				
			except ValueError:
				screen = FailureScreen("decryption1")
				widgets.addWidget(screen)
				widgets.setCurrentWidget(screen)
				self.close()
			
			except:
				screen = FailureScreen("decryption2")
				widgets.addWidget(screen)
				widgets.setCurrentWidget(screen)
				self.close()
	
#This is the class for the window in which the user is informed of the successful derypting of their chosen file.			
class DecryptionSuccessScreen(QMainWindow, BaseClass):
	def __init__(self):
		super(DecryptionSuccessScreen, self).__init__()
		loadUi("success_decrypt.ui", self)
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, EncryptionDecryptionScreen))

		
#This is the class for the window in which the user is informed of a failure that happened during the encryption or decryption process.	
class FailureScreen(QMainWindow, BaseClass):
	def __init__(self, failure):
		super(FailureScreen, self).__init__()
		self.failure = failure
		loadUi("failure.ui", self)
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, MainWindow))
		
		if self.failure == "decryption1":
			self.text.setText("Decryption was unsuccessful. This might be because the key was incorrect or the encrypted data was modified.")
			self.text.setAlignment(QtCore.Qt.AlignCenter)
		elif self.failure == "decryption2":
			self.text.setText("An unspecified error occurred. Decryption was unsuccessful.")
			self.text.setAlignment(QtCore.Qt.AlignCenter)
		elif self.failure == "encryption1":
			self.text.setText("Encryption was unsuccessful.")
			self.text.setAlignment(QtCore.Qt.AlignCenter)
		elif self.failure == "encryption2":
			self.text.setText("An unspecified error occurred. Encryption was unsuccessful.")
			self.text.setAlignment(QtCore.Qt.AlignCenter)
		


#This is the class for the window in which the user can choose which hashing algorithm they wish to be used.
class HashSelectionScreen(QMainWindow, BaseClass):
	#hType = QtCore.pyqtSignal(str)
	def	__init__(self, backFrom = "None"):
		super(HashSelectionScreen, self).__init__()
		loadUi("hash_type.ui", self)
		self.backFrom = backFrom
		
		self.toolButton.clicked.connect(lambda: BaseClass.goBack(self, HashCheckOrValidationScreen))

		#This ensures that the correct window will be shown if the "go back" button is pressed inside a HashScreen
		#or HashValidationScreen window, and then a new hashing algorithm chosen.
		if self.sender().text() == "Create a hash" or self.backFrom == "Creating":
			self.sha256Button.clicked.connect(self.goToHashScreen)
			self.sha512Button.clicked.connect(self.goToHashScreen)
			self.md5Button.clicked.connect(self.goToHashScreen)
		else:
			self.sha256Button.clicked.connect(self.goToValidateScreen)
			self.sha512Button.clicked.connect(self.goToValidateScreen)
			self.md5Button.clicked.connect(self.goToValidateScreen)
		
	#This method takes the user to the window in which they can create a hash of a file.
	def goToHashScreen(self):
		hashScreen = HashScreen()
		widgets.addWidget(hashScreen)
		widgets.setCurrentWidget(hashScreen)
		#self.hType.emit(hTypeIs)
		self.close()
		
	#This method takes the user to the window in which they can validate a file against a hash.
	def goToValidateScreen(self):
		validateScreen = HashValidationScreen()
		widgets.addWidget(validateScreen)
		widgets.setCurrentWidget(validateScreen)
		self.close()

		
#This is the class for the window in which the user can create a hash of a file.
class HashScreen(QMainWindow):
	def __init__(self):
		super(HashScreen, self).__init__()
		loadUi("hash_generation.ui", self)
		
		self.hType = self.sender().text()
		self.filename = ""
		self.selectFileButton.clicked.connect(self.selectFile)
		self.toolButton.clicked.connect(self.goBack)
		self.hashButton.clicked.connect(self.createHash)
	
	#This method allows the user to open a file explorer in order for them to choose a file which they wish to create a hash of.
	def selectFile(self, hType):
		try:
			self.filename = ""
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			f = QFileDialog.getOpenFileName(self)
			print(f[0])
			filename = f[0]
			if filename:
				self.filename = filename
				filename = truncateString(filename, 40)
				self.selected_file_name.setText(filename.strip())
				self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
		except FileNotFoundError:
			print("File not found.")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			self.label1.setText("")
			self.label.setText("")
			
		except:
			print("An error occurred.")
			self.label1.setText("")
			self.label.setText("")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
	
	#This method creates a hash of the chosen type of the chosen file.		
	def createHash(self):
		if self.filename or not self.filename:
			try:
				self.label1.setStyleSheet("QTextBrowser { color: black; }")
				hash1 = createHashOfFile(self.filename, self.hType.lower())
				self.label1.setText(f'The {self.hType} hash for the file {self.filename} is:')
				self.label.setText(hash1)
				self.label1.setAlignment(QtCore.Qt.AlignCenter)
				self.label.setAlignment(QtCore.Qt.AlignCenter)
			except:
				self.label1.setText("An error occurred.")
				self.label1.setAlignment(QtCore.Qt.AlignCenter)
				self.label.setText("")
				self.label1.setStyleSheet("QTextBrowser { color: red; }")
		else:
			self.label.setText("")
			self.label1.setText("Please select a file first.")
			self.label1.setAlignment(QtCore.Qt.AlignCenter)
			self.label1.setStyleSheet("QTextBrowser { color: red; }")
			
	#This method allows the user to go back to the previous window. It seemed that HashSelectionScreen wasn't callable 
	#using the goBack method of the parent class, so this class has its own version of the method.		
	def goBack(self):
		hashSelectionScreen = HashSelectionScreen("Creating")
		widgets.addWidget(hashSelectionScreen)
		widgets.setCurrentWidget(hashSelectionScreen)
		self.close()
	
#This is the class for the window in which the user can validate a file against a hash.		
class HashValidationScreen(QMainWindow):
	def __init__(self):
		super(HashValidationScreen, self).__init__()
		loadUi("hash_validation.ui", self)
		self.lineEdit.setPlaceholderText("Copy the hash here...")
		self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
		self.hashOfFile = ""
		self.label1.setText("")
		
		
		hType = self.sender().text()
		
		self.selectFileButton.clicked.connect(lambda: self.selectFile(hType))
		self.validateButton.clicked.connect(self.validate)
		self.toolButton.clicked.connect(self.goBack)
	
	#This method creates a hash of the chosen type of the file provided by the user, and compares that to the hash provided by the user.	
	def validate(self):
		try:
			self.label1.setStyleSheet("QLabel { color: black; }")
			
			if self.hashOfFile and self.lineEdit.text():
				if self.hashOfFile.strip() == self.lineEdit.text().strip():
					self.label1.setText("The hashes are a match!")
					self.label1.setAlignment(QtCore.Qt.AlignCenter)
					self.label1.setStyleSheet("QLabel { color: green; }")
				else:
					self.label1.setText("The hashes are not a match!")
					self.label1.setAlignment(QtCore.Qt.AlignCenter)
					self.label1.setStyleSheet("QLabel { color: red; }")
			else:
				self.label1.setText("Please select a file and input a hash.")
				self.label1.setAlignment(QtCore.Qt.AlignCenter)
				self.label1.setStyleSheet("QLabel { color: red; }")
				
		except:
			self.label1.setText("An error occurred.")
			self.label1.setAlignment(QtCore.Qt.AlignCenter)
			self.label1.setStyleSheet("QTextBrowser { color: red; }")
	
	#This method allows the user to open a file explorer in order for them to choose a file which they wish to create a hash to
	#be compared against the hash provided by them.
	def selectFile(self, hType):
		try:
			f = QFileDialog.getOpenFileName(self)
			print(f[0])
			hash1 = createHashOfFile(f[0], hType.lower())
			self.hashOfFile = hash1
			filename = f[0]
			filename = truncateString(filename, 40)
			self.selected_file_name.setText(filename.strip())
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			print(hash1)
		except FileNotFoundError:
			print("File not found.")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			self.label1.setText("")
			self.hashOfFile = ""
			
		except:
			print("An error occurred.")
			self.label1.setText("")
			self.selected_file_name.setText("No file selected")
			self.selected_file_name.setAlignment(QtCore.Qt.AlignCenter)
			self.hashOfFile = ""
	
	#This method allows the user to go back to the previous window. It seemed that HashSelectionScreen wasn't callable 
	#using the goBack method of the parent class, so this class has its own version of the method.		
	def goBack(self):
		hashSelectionScreen = HashSelectionScreen("Validation")
		widgets.addWidget(hashSelectionScreen)
		widgets.setCurrentWidget(hashSelectionScreen)
		self.close()
		
#The initial setup of the application. The application has a fixed height and width, which can be changed below.		
app = QApplication(sys.argv)
widgets = QtWidgets.QStackedWidget()
main = MainWindow()
widgets.addWidget(main)
widgets.setFixedHeight(400)
widgets.setFixedWidth(500)
widgets.show()

hashType = "None"

#The application will exit after the application window is closed.
sys.exit(app.exec_())
