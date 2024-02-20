from django.test import SimpleTestCase
from util.tickers.Tickers_BDs import tickers_dj30, tickers_ibex35, tickers_ftse100, tickers_indices, tickers_adaptados_ibex35, tickers_adaptados_dj30, tickers_adaptados_ftse100, tickers_adaptados_indices, ruta_bd_dj30, ruta_bd_ibex35, ruta_bd_ftse100, nombre_bd_dj30, nombre_bd_ibex35, nombre_bd_ftse100, obtener_nombre_bd, tickers_disponibles, tickers_adaptados_disponibles
from log.logger.logger import get_logger_configurado


# Idea original de NuclearPeon:
# https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
            
            log = get_logger_configurado('Tickers')
            log.info("")
            log.info("----------------------------------")
            log.info("TESTS TICKERS")
            log.info("----------------------------------")

            cls.setUpBool = True

        return cls._instance


class TestTickers(SimpleTestCase):
    
    def setUp(self):
        Singleton()
        self.log = get_logger_configurado('Tickers')

    def test_tickers_dj30(self):
        tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','^DJI']                           
        self.assertEquals(tickers, tickers_dj30(), " - [NO OK] Tickers dj30")
        self.log.info(" - [OK] Tickers dj30")
        

    def test_tickers_ibex35(self):
        tickers = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
            'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
            'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
            'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
            'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
            'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
            'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
            'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
            'SLR.MC', 'TEF.MC', 'UNI.MC', '^IBEX']                        
        self.assertEquals(tickers, tickers_ibex35(), " - [NO OK] Tickers ibex35")
        self.log.info(" - [OK] Tickers ibex35")


    def test_tickers_ftse100(self):
        tickers = ['III.L', 'ADM.L', 'AAF.L', 'AAL.L', 'ANTO.L', 
               'AHT.L', 'ABF.L', 'AZN.L', 'AUTO.L', 'AV.L', 
               'BME.L', 'BA.L', 'BARC.L', 'BDEV.L', 'BEZ.L', 
               'BKG.L', 'BP.L', 'BATS.L', 'BT-A.L', 'BNZL.L', 
               'BRBY.L', 'CNA.L', 'CCH.L', 'CPG.L', 'CTEC.L', 
               'CRDA.L', 'DCC.L', 'DGE.L', 'DPLM.L', 'EDV.L', 
               'ENT.L', 'EXPN.L', 'FCIT.L', 'FLTR.L', 'FRAS.L', 
               'FRES.L', 'GLEN.L', 'GSK.L', 'HLN.L', 'HLMA.L', 
               'HIK.L', 'HWDN.L', 'HSBA.L', 'IMI.L', 'IMB.L', 
               'INF.L', 'IHG.L', 'ICP.L', 'ITRK.L', 'IAG.L', 
               'JD.L', 'KGF.L', 'LAND.L', 'LGEN.L', 'LLOY.L', 
               'LSEG.L', 'MNG.L', 'MKS.L', 'MRO.L', 'MNDI.L', 
               'NG.L', 'NWG.L', 'NXT.L', 'OCDO.L', 'PSON.L', 
               'PSH.L', 'PSN.L', 'PHNX.L', 'PRU.L', 'RKT.L', 
               'REL.L', 'RTO.L', 'RMV.L', 'RIO.L', 'RR.L', 
               'RS1.L', 'SGE.L', 'SBRY.L', 'SDR.L', 'SMT.L', 
               'SGRO.L', 'SVT.L', 'SHEL.L', 'SN.L', 'SMDS.L', 
               'SMIN.L', 'SKG.L', 'SPX.L', 'SSE.L', 'STJ.L', 
               'STAN.L', 'TW.L', 'TSCO.L', 'ULVR.L', 'UTG.L', 
               'UU.L', 'VOD.L', 'WEIR.L', 'WTB.L', 'WPP.L', '^FTSE']
        self.assertEquals(tickers, tickers_ftse100(), " - [NO OK] Tickers ftse100")
        self.log.info(" - [OK] Tickers ftse100")


    def test_tickers_índices(self):
        índices = ['^DJI', '^IBEX', '^FTSE']
        self.assertEquals(índices, tickers_indices(), " - [NO OK] Tickers índices")
        self.log.info(" - [OK] Tickers índices")

    
    def test_tickers_adaptados_dj30(self):
        tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','DJI']  
        self.assertEquals(tickers, tickers_adaptados_dj30(), " - [NO OK] Tickers adaptados dj30")
        self.log.info(" - [OK] Tickers adaptados dj30")


    def test_tickers_adaptados_ibex35(self):
        tickers = ['ACS_MC', 'ACX_MC', 'AENA_MC', 'AMS_MC', 
            'ANA_MC', 'ANE_MC', 'BBVA_MC', 'BKT_MC', 
            'CABK_MC', 'CLNX_MC', 'COL_MC', 'ELE_MC', 
            'ENG_MC', 'FDR_MC', 'FER_MC', 'GRF_MC', 
            'IAG_MC', 'IBE_MC', 'IDR_MC', 'ITX_MC', 
            'LOG_MC', 'MAP_MC', 'MEL_MC', 'MRL_MC', 
            'MTS_MC', 'NTGY_MC', 'RED_MC', 'REP_MC', 
            'ROVI_MC', 'SAB_MC', 'SAN_MC', 'SCYR_MC', 
            'SLR_MC', 'TEF_MC', 'UNI_MC', 'IBEX']
        self.assertEquals(tickers, tickers_adaptados_ibex35(), " - [NO OK] Tickers adaptados ibex35")
        self.log.info(" - [OK] Tickers adaptados ibex35")


    def test_tickers_adaptados_ftse100(self):
        tickers = ['III_L', 'ADM_L', 'AAF_L', 'AAL_L', 'ANTO_L', 
               'AHT_L', 'ABF_L', 'AZN_L', 'AUTO_L', 'AV_L', 
               'BME_L', 'BA_L', 'BARC_L', 'BDEV_L', 'BEZ_L', 
               'BKG_L', 'BP_L', 'BATS_L', 'BT-A_L', 'BNZL_L', 
               'BRBY_L', 'CNA_L', 'CCH_L', 'CPG_L', 'CTEC_L', 
               'CRDA_L', 'DCC_L', 'DGE_L', 'DPLM_L', 'EDV_L', 
               'ENT_L', 'EXPN_L', 'FCIT_L', 'FLTR_L', 'FRAS_L', 
               'FRES_L', 'GLEN_L', 'GSK_L', 'HLN_L', 'HLMA_L', 
               'HIK_L', 'HWDN_L', 'HSBA_L', 'IMI_L', 'IMB_L', 
               'INF_L', 'IHG_L', 'ICP_L', 'ITRK_L', 'IAG_L', 
               'JD_L', 'KGF_L', 'LAND_L', 'LGEN_L', 'LLOY_L', 
               'LSEG_L', 'MNG_L', 'MKS_L', 'MRO_L', 'MNDI_L', 
               'NG_L', 'NWG_L', 'NXT_L', 'OCDO_L', 'PSON_L', 
               'PSH_L', 'PSN_L', 'PHNX_L', 'PRU_L', 'RKT_L', 
               'REL_L', 'RTO_L', 'RMV_L', 'RIO_L', 'RR_L', 
               'RS1_L', 'SGE_L', 'SBRY_L', 'SDR_L', 'SMT_L', 
               'SGRO_L', 'SVT_L', 'SHEL_L', 'SN_L', 'SMDS_L', 
               'SMIN_L', 'SKG_L', 'SPX_L', 'SSE_L', 'STJ_L', 
               'STAN_L', 'TW_L', 'TSCO_L', 'ULVR_L', 'UTG_L', 
               'UU_L', 'VOD_L', 'WEIR_L', 'WTB_L', 'WPP_L', 'FTSE']
        self.assertEquals(tickers, tickers_adaptados_ftse100(), " - [NO OK] Tickers ftse100")
        self.log.info(" - [OK] Tickers ftse100")

    
    def test_tickers_adaptados_indices(self):
        índices = ['DJI', 'IBEX', 'FTSE']
        self.assertEquals(índices, tickers_adaptados_indices())
        self.log.info(" - [OK] Tickers adaptados índices")

    
    def test_ruta_bd_dj30(self):
        self.assertEquals('databases/dj30.sqlite3', ruta_bd_dj30(), " - [NO OK] Ruta bd dj30")
        self.log.info(" - [OK] Ruta bd dj30")
    
    
    def test_ruta_bd_ibex35(self):
        self.assertEquals('databases/ibex35.sqlite3', ruta_bd_ibex35(), " - [NO OK] Ruta bd ibex35")
        self.log.info(" - [OK] Ruta bd ibex35")

    
    def test_ruta_bd_ftse100(self):
        self.assertEquals('databases/ftse100.sqlite3', ruta_bd_ftse100(), " - [NO OK] Ruta bd ftse100")
        self.log.info(" - [OK] Ruta bd ftse100")


    def test_nombre_bd_dj30(self):
        self.assertEquals('dj30', nombre_bd_dj30(), " - [NO OK] Nombre bd dj30")
        self.log.info(" - [OK] Nombre bd dj30")

    
    def test_nombre_bd_ibex35(self):
        self.assertEquals('ibex35', nombre_bd_ibex35(), " - [NO OK] Nombre bd ibex35")
        self.log.info(" - [OK] Nombre bd ibex35")


    def test_nombre_bd_ftse100(self):
        self.assertEquals('ftse100', nombre_bd_ftse100(), " - [NO OK] Nombre bd ftse100")
        self.log.info(" - [OK] Nombre bd ftse100")

    
    def test_obtener_nombre_bd_de_ticker(self):
        for _ in tickers_dj30():
            self.assertEquals(obtener_nombre_bd(_), nombre_bd_dj30(), " - [NO OK] Obtener nombre de bd en dj30")
        for _ in tickers_adaptados_dj30():
            self.assertEquals(obtener_nombre_bd(_), nombre_bd_dj30(), " - [NO OK] Obtener nombre de bd en dj30")
        self.log.info(" - [OK] Obtener nombre de bd en dj30")

        for _ in tickers_ibex35():
            self.assertEquals(obtener_nombre_bd(_), nombre_bd_ibex35(), " - [NO OK] Obtener nombre de bd en ibex35")
        for _ in tickers_adaptados_ibex35():
            self.assertEquals(obtener_nombre_bd(_), nombre_bd_ibex35(), " - [NO OK] Obtener nombre de bd en ibex35")
        self.log.info(" - [OK] Obtener nombre de bd en ibex35")

        for _ in tickers_ftse100():
            self.assertEquals(obtener_nombre_bd(_), nombre_bd_ftse100(), " - [NO OK] Obtener nombre de bd en ftse100")
        for _ in tickers_adaptados_ftse100():
            self.assertEquals(obtener_nombre_bd(_), nombre_bd_ftse100(), " - [NO OK] Obtener nombre de bd en ftse100")
        self.log.info(" - [OK] Obtener nombre de bd en ftse100")

        self.assertEquals(obtener_nombre_bd('testTicker'), None, " - [NO OK] Obtener None con nombre falso")
        self.log.info(" - [OK] Obtener None con nombre falso")


    def test_tickers_disponibles(self):
        tickers_1 = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','^DJI']  
        tickers_2 = ['ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 
            'ANA.MC', 'ANE.MC', 'BBVA.MC', 'BKT.MC', 
            'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
            'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 
            'IAG.MC', 'IBE.MC', 'IDR.MC', 'ITX.MC', 
            'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC', 
            'MTS.MC', 'NTGY.MC', 'RED.MC', 'REP.MC', 
            'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 
            'SLR.MC', 'TEF.MC', 'UNI.MC', '^IBEX']     
        tickers_3 = ['III.L', 'ADM.L', 'AAF.L', 'AAL.L', 'ANTO.L', 
               'AHT.L', 'ABF.L', 'AZN.L', 'AUTO.L', 'AV.L', 
               'BME.L', 'BA.L', 'BARC.L', 'BDEV.L', 'BEZ.L', 
               'BKG.L', 'BP.L', 'BATS.L', 'BT-A.L', 'BNZL.L', 
               'BRBY.L', 'CNA.L', 'CCH.L', 'CPG.L', 'CTEC.L', 
               'CRDA.L', 'DCC.L', 'DGE.L', 'DPLM.L', 'EDV.L', 
               'ENT.L', 'EXPN.L', 'FCIT.L', 'FLTR.L', 'FRAS.L', 
               'FRES.L', 'GLEN.L', 'GSK.L', 'HLN.L', 'HLMA.L', 
               'HIK.L', 'HWDN.L', 'HSBA.L', 'IMI.L', 'IMB.L', 
               'INF.L', 'IHG.L', 'ICP.L', 'ITRK.L', 'IAG.L', 
               'JD.L', 'KGF.L', 'LAND.L', 'LGEN.L', 'LLOY.L', 
               'LSEG.L', 'MNG.L', 'MKS.L', 'MRO.L', 'MNDI.L', 
               'NG.L', 'NWG.L', 'NXT.L', 'OCDO.L', 'PSON.L', 
               'PSH.L', 'PSN.L', 'PHNX.L', 'PRU.L', 'RKT.L', 
               'REL.L', 'RTO.L', 'RMV.L', 'RIO.L', 'RR.L', 
               'RS1.L', 'SGE.L', 'SBRY.L', 'SDR.L', 'SMT.L', 
               'SGRO.L', 'SVT.L', 'SHEL.L', 'SN.L', 'SMDS.L', 
               'SMIN.L', 'SKG.L', 'SPX.L', 'SSE.L', 'STJ.L', 
               'STAN.L', 'TW.L', 'TSCO.L', 'ULVR.L', 'UTG.L', 
               'UU.L', 'VOD.L', 'WEIR.L', 'WTB.L', 'WPP.L', '^FTSE']
        self.assertEquals(tickers_1 + tickers_2 + tickers_3, tickers_disponibles(), " - [NO OK] Obtener tickers disponibles")
        self.log.info(" - [OK] Obtener tickers disponibles")

    
    def test_tickers_adaptados_disponibles(self):
        tickers_1 = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 
            'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 
            'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 
            'UNH', 'V', 'VZ', 'WBA', 'WMT','DJI']  
        tickers_2 = ['ACS_MC', 'ACX_MC', 'AENA_MC', 'AMS_MC', 
            'ANA_MC', 'ANE_MC', 'BBVA_MC', 'BKT_MC', 
            'CABK_MC', 'CLNX_MC', 'COL_MC', 'ELE_MC', 
            'ENG_MC', 'FDR_MC', 'FER_MC', 'GRF_MC', 
            'IAG_MC', 'IBE_MC', 'IDR_MC', 'ITX_MC', 
            'LOG_MC', 'MAP_MC', 'MEL_MC', 'MRL_MC', 
            'MTS_MC', 'NTGY_MC', 'RED_MC', 'REP_MC', 
            'ROVI_MC', 'SAB_MC', 'SAN_MC', 'SCYR_MC', 
            'SLR_MC', 'TEF_MC', 'UNI_MC', 'IBEX']     
        tickers_3 = ['III_L', 'ADM_L', 'AAF_L', 'AAL_L', 'ANTO_L', 
               'AHT_L', 'ABF_L', 'AZN_L', 'AUTO_L', 'AV_L', 
               'BME_L', 'BA_L', 'BARC_L', 'BDEV_L', 'BEZ_L', 
               'BKG_L', 'BP_L', 'BATS_L', 'BT-A_L', 'BNZL_L', 
               'BRBY_L', 'CNA_L', 'CCH_L', 'CPG_L', 'CTEC_L', 
               'CRDA_L', 'DCC_L', 'DGE_L', 'DPLM_L', 'EDV_L', 
               'ENT_L', 'EXPN_L', 'FCIT_L', 'FLTR_L', 'FRAS_L', 
               'FRES_L', 'GLEN_L', 'GSK_L', 'HLN_L', 'HLMA_L', 
               'HIK_L', 'HWDN_L', 'HSBA_L', 'IMI_L', 'IMB_L', 
               'INF_L', 'IHG_L', 'ICP_L', 'ITRK_L', 'IAG_L', 
               'JD_L', 'KGF_L', 'LAND_L', 'LGEN_L', 'LLOY_L', 
               'LSEG_L', 'MNG_L', 'MKS_L', 'MRO_L', 'MNDI_L', 
               'NG_L', 'NWG_L', 'NXT_L', 'OCDO_L', 'PSON_L', 
               'PSH_L', 'PSN_L', 'PHNX_L', 'PRU_L', 'RKT_L', 
               'REL_L', 'RTO_L', 'RMV_L', 'RIO_L', 'RR_L', 
               'RS1_L', 'SGE_L', 'SBRY_L', 'SDR_L', 'SMT_L', 
               'SGRO_L', 'SVT_L', 'SHEL_L', 'SN_L', 'SMDS_L', 
               'SMIN_L', 'SKG_L', 'SPX_L', 'SSE_L', 'STJ_L', 
               'STAN_L', 'TW_L', 'TSCO_L', 'ULVR_L', 'UTG_L', 
               'UU_L', 'VOD_L', 'WEIR_L', 'WTB_L', 'WPP_L', 'FTSE']
        self.assertEquals(tickers_1 + tickers_2 + tickers_3, tickers_adaptados_disponibles(), " - [NO OK] Obtener tickers disponibles")
        self.log.info(" - [OK] Obtener tickers disponibles")
