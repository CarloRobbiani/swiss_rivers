

# This is not Torch-dataset stuff. it is data reading / data as code

class Hydro2MeteoMapper:

    '''
    copied from report:
    use "[A-z -]+ ([0-9]+).*([A-Z]{3}).*" on regexr.com
    1) removed some line breaks
    2) removed ALT/DIS/DRA but not those on Altdorf!
    3) format using self.h2m['$1'] = '$2'\n    
    4) added Station 2113?
    '''

    def meteo(self, hydro_station:str) -> str:
        return self.h2m[hydro_station]
    
    def stations(self) -> list[str]:
        return list(self.h2m.keys())
    
    def meteo_stations(self) -> set[str]:
        result = list(set(self.h2m.values()))
        return sorted(result)        

    def __init__(self):
        super().__init__()
        self.h2m = dict()
        self.h2m['2009'] = 'AIG'
        self.h2m['2016'] = 'BUS'
        self.h2m['2018'] = 'BUS'
        self.h2m['2019'] = 'MER'
        self.h2m['2029'] = 'BER'
        self.h2m['2030'] = 'INT'
        self.h2m['2033'] = 'CHU' # T_2033 starts at 01.01.2002
        self.h2m['2034'] = 'PAY'
        self.h2m['2044'] = 'SHA'
        self.h2m['2056'] = 'ALT'
        self.h2m['2068'] = 'MAG'
        self.h2m['2070'] = 'LAG'
        self.h2m['2084'] = 'ALT'
        self.h2m['2085'] = 'BER'
        self.h2m['2091'] = 'BAS'
        self.h2m['2104'] = 'GLA'
        self.h2m['2106'] = 'BAS'
        self.h2m['2109'] = 'INT'
        self.h2m['2112'] = 'STG' # T_2112 starts at 01.01.2006
        self.h2m['2113'] = 'BUS' # T_2113 no flow!
        self.h2m['2126'] = 'TAE' # T_2126 starts at 01.01.2002
        self.h2m['2130'] = 'RUE'
        self.h2m['2135'] = 'BER'
        self.h2m['2139'] = 'VAD'
        self.h2m['2143'] = 'KLO'
        self.h2m['2150'] = 'RAG'
        self.h2m['2152'] = 'LUZ'
        self.h2m['2159'] = 'BER'
        self.h2m['2161'] = 'GRC'
        self.h2m['2167'] = 'LUG'
        self.h2m['2170'] = 'GVE'
        self.h2m['2174'] = 'GVE'
        self.h2m['2176'] = 'SMA'
        self.h2m['2179'] = 'BER'
        self.h2m['2181'] = 'GUT'
        self.h2m['2210'] = 'FAH'
        self.h2m['2232'] = 'ABO'
        self.h2m['2243'] = 'REH'
        self.h2m['2256'] = 'SAM'
        self.h2m['2265'] = 'SCU'
        self.h2m['2269'] = 'GRC'
        self.h2m['2276'] = 'ALT'
        self.h2m['2282'] = 'NAP'
        self.h2m['2288'] = 'SHA'
        #self.h2m['2290'] = 'BRL' # BRL missing
        self.h2m['2307'] = 'CHA'
        self.h2m['2308'] = 'GUT'
        self.h2m['2327'] = 'DAV'
        self.h2m['2343'] = 'WYN'
        self.h2m['2347'] = 'GRO'
        self.h2m['2351'] = 'VIS'
        self.h2m['2366'] = 'BEH'
        self.h2m['2369'] = 'PAY'
        self.h2m['2372'] = 'GLA'
        self.h2m['2374'] = 'EBK'
        self.h2m['2386'] = 'TAE'
        self.h2m['2392'] = 'SHA' # 2392 no flow!
        self.h2m['2410'] = 'VAD'
        self.h2m['2414'] = 'EBK'
        self.h2m['2415'] = 'KLO'
        self.h2m['2432'] = 'PUY'
        self.h2m['2433'] = 'CGI'
        self.h2m['2434'] = 'WYN'
        self.h2m['2457'] = 'INT'
        self.h2m['2462'] = 'SAM'
        self.h2m['2467'] = 'BER'
        self.h2m['2473'] = 'VAD'
        self.h2m['2481'] = 'LUZ'
        self.h2m['2485'] = 'FAH'
        self.h2m['2493'] = 'CGI'
        self.h2m['2499'] = 'ALT'
        self.h2m['2500'] = 'BER'
        self.h2m['2604'] = 'EIN'
        self.h2m['2606'] = 'GVE'
        self.h2m['2608'] = 'LUZ'
        self.h2m['2609'] = 'EIN'
        self.h2m['2612'] = 'OTL'
        self.h2m['2613'] = 'BAS'
        self.h2m['2617'] = 'SMM'
        self.h2m['2623'] = 'ULR' # T_2623 no flow!
        self.h2m['2634'] = 'LUZ'
        self.h2m['2635'] = 'EIN'

class Hydro2MeteoMapper1to1(Hydro2MeteoMapper):

    '''
    This meteo mapper deltes all dublications. s.t. there is a 1-1 map between meteo and water.
    '''

    def __init__(self):
        super().__init__()
        one2one_h2m = dict()

        for station in self.stations():
            meteo = self.h2m[station]
            if meteo not in set(one2one_h2m.values()):
                one2one_h2m[station] = meteo
        
        self.h2m = one2one_h2m


class Hydro2MeteoMapperBernOnly(Hydro2MeteoMapper1to1):

    '''
    This meteo mapper is even worse. It uses a single meteo station for Switzerland ()
    '''

    def __init__(self):
        super().__init__()
    
    def meteo(self, station):
        return 'BER' # return bern only!


if __name__ == '__main__':
    #h2m = Hydro2MeteoMapper()
    #h2m = Hydro2MeteoMapper1to1()
    h2m = Hydro2MeteoMapperBernOnly()
    hydro_stations = set(h2m.h2m.keys())
    print(hydro_stations)
    print(len(hydro_stations))
    meteo_stations = set(h2m.h2m.values())
    print(meteo_stations)
    print(len(meteo_stations))
    print('get for 2623 (Wallis):', h2m.meteo('2623'))
