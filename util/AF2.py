import yfinance as yf

stock = yf.Ticker("AAPL")
balance_sheet = stock.get_balance_sheet()

# Imprime los datos del balance general
balance_sheet = balance_sheet.transpose()

print(balance_sheet['Total Assets'])

print(balance_sheet['NetDebt'])


# DATOS MÁS IMPORTANTES DE UN BALANCE GENERAL https://www.investopedia.com/terms/b/balancesheet.asp
#
# Total Assets: Activos totales: Esta fila proporciona una visión general de los activos totales de la empresa, que representan el valor de sus recursos.
# Net Tangible Assets: Activos netos tangibles: Esta fila indica el patrimonio neto de la empresa después de deducir los activos intangibles, como el fondo de comercio y las patentes.
# Total Liabilities: Obligaciones totales: Esta fila destaca las obligaciones totales de la empresa, que representan sus obligaciones financieras.
# Net Debt: Deuda neta: Esta fila muestra la deuda neta de la empresa, que es su deuda total menos su efectivo y equivalentes de efectivo.
# Invested Capital: Capital invertido: Esta fila mide la capacidad de la empresa para financiar sus operaciones a través de capital propio y deuda.
# Stockholders: Patrimonio de los accionistas: Esta fila representa el interés de propiedad de los accionistas de la empresa.
# Current Assets: Activos corrientes: Esta fila refleja los activos líquidos de la empresa que se pueden convertir en efectivo dentro de un año.
# Non-Current Assets: Activos no corrientes: Esta fila enumera los activos no líquidos de la empresa, que no se pueden convertir en efectivo rápidamente.
# PPE: PP&E: Esta fila indica el valor de los activos físicos a largo plazo de la empresa, como edificios y maquinaria.
# Receivables: Receivables: Esta fila refleja las cantidades adeudadas a la empresa por sus clientes.
# Cash and Cash Equivalents: Efectivo y equivalentes de efectivo: Esta fila representa el efectivo y los activos líquidos fácilmente disponibles de la empresa que pueden utilizarse para cumplir con sus obligaciones a corto plazo.