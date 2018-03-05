from __future__ import print_function

from arqmodel import ARQModel


class SAWProtocol:
    # potrzebne obiekty do wykonania symulacji!
    sourceARQ = ARQModel()  # zrodlowy dekoder ARQ
    destARQ = ARQModel()  # docelowy dekoder ARQ
    noiseGenerator = None  # generator szumu
    bytes = 0  # ilosc bajtow na pakiet
    errors = 0  # wykryte bledy w transmisji

    def __init__(self, sARQ, dARQ, noiseGen,
                 n):  # konstruktor (siebie, sourceARQ, destARQ, generator szumu ,ilosc bajtow na pakiet):
        self.sourceARQ = sARQ
        self.destARQ = dARQ
        self.noiseGenerator = noiseGen
        self.bytes = n
        self.errors = 0

    def prepareDecoders(self, file):
        print("<ARQ>\t\tPreparing decoders:\n\n\t\t\tSynchronizing...")
        self.synchronize()

        print("\n\t\t\tLoading file...")
        self.loadFile(file)

        print("\n\t\t\tPreparing source ARQ module...")
        self.prepareSourceARQ()

    def synchronize(self):  # synchronizuje moduly arq
        self.destARQ.bytesinpack = bytes
        self.sourceARQ.bytesinpack = bytes

    def loadFile(self, file):  # wczytanie pliku do zrodlowego modulu arq
        self.sourceARQ.loadfile(file)

    def prepareSourceARQ(self):  # przygotowanie zrodlowego modulu arq do transmisji
        print("\n\t\t\t\tCreating packages...")
        self.sourceARQ.packsofn(self.bytes)  # dzielenie pliku na paczki

        print("\n\t\t\t\tAdding secure bytes...")
        self.sourceARQ.addevenbyte()  # dodanie bitow kontrolnych

    def transmit(self):
        print("\n<sourceARQ>\t\tStarting transmition:\n\n\t\t\t\tSending packages...")
        for pack in self.sourceARQ.packages:  # wyciaganie pojedynczych pakietow z pamieci modulu arq
            ack = self.destARQ.receivepacks(self.noiseGenerator.addNoise(pack))  # proba odebrania pakietu
            while (ack == 'nack'):
                ack = self.destARQ.receivepacks(self.noiseGenerator.addNoise(pack))
                self.errors += 1

        print("\n<destARQ>\t\tFinishing transmition:")
        self.afterTransmition()  # zakonczenie transmisji

    def afterTransmition(self):
        print("\n\t\t\t\tUnpacking...")
        self.destARQ.unpack()  # rozpakowanie odebranych pakietow
        print("\n\t\t\t\tExporting to .wav...")
        self.destARQ.converttowave('receivedViaSAWProtocol.wav')

    def getTotalErrors(self):
        return self.noiseGenerator.totalErrors
