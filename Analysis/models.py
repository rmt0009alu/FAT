from django.db import models

# Create your models here.
class StockData(models.Model):
    Date = models.DateTimeField()
    Open = models.FloatField()
    High = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    Volume = models.IntegerField()
    Dividends = models.FloatField()
    Stock_Splits = models.FloatField()
    Ticker = models.CharField(max_length=10)
    Previous_Close = models.FloatField()
    Percent_Variance = models.FloatField()
    MM20 = models.FloatField()
    MM50 = models.FloatField()
    MM200 = models.FloatField()

    # class Meta:
    #     abstract = True

# class ACS_MC(StockData):
#     pass

# class ACX_MC(StockData):
#     pass

# class AENA_MC(StockData):
#     pass

# class AMS_MC(StockData):
#     pass

# class ANA_MC(StockData):
#     pass

# class ANE_MC(StockData):
#     pass

# class BBVA_MC(StockData):
#     pass

# class BKT_MC(StockData):
#     pass

# class CABK_MC(StockData):
#     pass

# class CLNX_MC(StockData):
#     pass

# class COL_MC(StockData):
#     pass

# class ELE_MC(StockData):
#     pass

# class ENG_MC(StockData):
#     pass

# class FDR_MC(StockData):
#     pass

# class FER_MC(StockData):
#     pass

# class GRF_MC(StockData):
#     pass

# class IAG_MC(StockData):
#     pass

# class IBE_MC(StockData):
#     pass

# class IDR_MC(StockData):
#     pass

# class ITX_MC(StockData):
#     pass

# class LOG_MC(StockData):
#     pass

# class MAP_MC(StockData):
#     pass

# class MEL_MC(StockData):
#     pass

# class MRL_MC(StockData):
#     pass

# class MTS_MC(StockData):
#     pass

# class NTGY_MC(StockData):
#     pass

# class RED_MC(StockData):
#     pass

# class REP_MC(StockData):
#     pass

# class ROVI_MC(StockData):
#     pass

# class SAB_MC(StockData):
#     pass

# class SAN_MC(StockData):
#     pass

# class SCYR_MC(StockData):
#     pass

# class SLR_MC(StockData):
#     pass

# class TEF_MC(StockData):
#     pass

# class UNI_MC(StockData):
#     pass