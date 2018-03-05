# Klasa ARQModel ma na celu wczytanie pliku wejsciowego .wav
# nastepnie wczytanie kolejnych jego bajtow i przedstawienie ich w formie 0 i 1
# zamiast '\xXX' np.: '\xaa' = '10101010'
# model dzieli na paczki po n=1,2,4,8,16,32,64,128 bajtow
# (najczytelniej jest n=8, n=32 powinno byc optymalne do testow)
# model dodaje rowniez bit parzystosci jako n+1 element paczki
# i bajt ktory zawiera informacje o ilosci jedynek w pakiecie
# bajt ilosci jedynek jest w paczce jako n+2 element
# przykladowa paczka dla n=8:
# ['10110101', '10111111', '00000000', '10010001', '10100101', '10010100', '11111111', '10110001', 1, 34]
# indeksy 	[0:n-1] 	to miejsce danych
# indeks 	n 			to bit parzystosci
# indeks 	n + 1 		to ilosc jedynek w pakiecie danych
# rozmiar paczki to n+2
#
# rozmiar pliku wave.wav z gita to dokladnie 6 000 000(+- 1) bajtow!
# wiec mozna dzielic na paczki po 1,2,4,8,16,32,64,128 bajtow (choc 128 jest ryzykowne)



from __future__ import print_function
import wave
import array


class ARQModel:
    bin_file = []  # bajty pliku .wav
    rate = 32000  # rating pliku .wav
    packages = []  # bin_file podzielony na paczki
    bytesinpack = 0  # po ile bajtow dany byly pakowane
    errors = 0

    def __init__(self):  # konstruktor modulu arq, inicjalizuje pola obiektu
        self.rate = 32000
        self.bin_file = []
        self.packages = []
        self.bytesinpack = 0
        errors = 0

    def loadfile(self, filepath):  # wczytanie pliku .wav i przerobienie go na ciag bajtow w postaci 8 bitow
        tmpw = wave.open(filepath, "rb")
        bytes = tmpw.readframes(tmpw.getnframes())
        tmpw.close()
        self.bin_file = [ord(char) for char in bytes]
        self.bin_file = [bin(char)[2:].zfill(8) for char in
                         self.bin_file]  # wynikowa lista bajtow w reprezentacji zer i jedynek

    def converttowave(self, output):  # tworzy plik wav z ciagu bajtow

        self.bin_file = [int(bit, 2) for bit in self.bin_file]  # do integerow
        self.bin_file = array.array('B', self.bin_file).tostring()  # do bajtow w postaci '\xdd'
        self.output_wave(output, self.bin_file)

    def output_wave(self, path, frames):
        output = wave.open(path, 'w')  # tylko do zapisu
        output.setparams(
            (2, 2, self.rate, 0, 'NONE', 'not compressed'))  # 2 kanaly, szerokosc? probki, rating, kompresja
        output.writeframes(frames)
        output.close()

    def packsofn(self, bytesinpack):  # dzielenie zaladowanego pliku na paczki po zadanej ilosci bajtow
        begin = 0
        end = bytesinpack
        self.bytesinpack = bytesinpack
        for i in range(0, (len(self.bin_file) / bytesinpack)):
            pack = self.bin_file[begin:end]
            self.packages.append(pack)
            begin += bytesinpack
            end += bytesinpack

    def addevenbyte(self):  # dodawanie bitu parzystosci i ilosci jedynek do kazdej paczki
        onesinpackage = 0  # dodanie 1 jesli ilosc jedynek w paczce jest parzysta, 0 wpp
        for pack in self.packages:  # dla kazdego pakietu w paczkach
            pack = self.countones(pack)  # dodaj bity kontrolne

    def countones(self, pack):  # liczy i dodaje bity kontrolne
        onesinpackage = 0
        for byte in pack:  # dla kazdego bajtu w pakiecie
            for char in byte:  # dla kazdego bitu w bajcie
                if (char == '1'):  # liczenie jedynek
                    onesinpackage += 1
        if (onesinpackage % 2 == 0):  # okreslenie parzystosci wystapien jedynek
            pack.append(1)
            pack.append(onesinpackage)
        else:
            pack.append(0)
            pack.append(onesinpackage)

        return pack

    def unpack(self):  # rozpakowanie przeslanych paczek
        for pack in self.packages:  # dla kazdego pakietu w otrzymanej paczce
            if(pack != 0):
                self.bin_file.extend(pack)  # wyciag z paczki i dodaj do 'pliku'

    def printnbytes(self, begin, end):  # wypisuje bajty z podanego zakresu
        for i in range(begin, end):
            print(self.bin_file[i], end=" ")

    def receivepacks(self, pack):  # odbiera JEDEN pakiet danych i sprawdza jego poprawnosc
        ack = self.checkPack(pack)
        if (ack == 'ack'):
            self.packages.append(pack)
        return ack

    def checkPack(self, pack):
        onesinpackage = 0
        tocheck = [el for el in pack]  # kopia paczki, dla ulatwienia wykonywania operacji.
        packones = tocheck.pop()  # ilosc jedynek w pakiecie
        packeven = tocheck.pop()  # bit parzystosci
        for byte in tocheck:  # dla kazdego bajtu w pakiecie
            for bit in byte:  # sprawdzanie kazdego bitu w kazdym bajcie
                if (bit == '1'):  # liczenie jedynek
                    onesinpackage += 1

        # sprawdzenie poprawnosci pakietu
        if (onesinpackage == packones):  # porownanie ilosci jedynek w pakiecie
            if (onesinpackage % 2 == 0):  # 1 jesli ilosc wystapien 1 jest parzysta, 0 wpp
                if (1 == packeven):  # jesli wyliczony na nowo bit parzystosci zgadza sie z odebranym, paczka zostala odebrana poprawnie
                     pack.pop()  # usuniecie crc
                     pack.pop()  # usuniecie bitow kontrolnych z pakietu
                     return 'ack'  # odeslij potwierdzenie odebrania
                else:
                    return 'nack'  # pakiet nie byl poprawny
            else:
                 if (0 == packeven):
                     pack.pop()  # usuniecie crc
                     pack.pop()
                     return 'ack'
                 else:
                     return 'nack'
        else:
            return 'nack'