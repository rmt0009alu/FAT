import yfinance as yf


def get_fundamental_info(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)

        # fundamental_info = stock.financials [igual a 'stock.get_income_stmt()']
        # -----------------------------------
        #
        #                                                         2023-09-30      2022-09-30      2021-09-30      2020-09-30
        # Tax Effect Of Unusual Items                                    0.0             0.0             0.0             0.0
        # Tax Rate For Calcs                                        0.147192        0.162045        0.133023        0.144282
        # Normalized EBITDA                                   125820000000.0  130541000000.0  120233000000.0   77344000000.0
        # Net Income From Continuing Operation Net Minori...   96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Reconciled Depreciation                              11519000000.0   11104000000.0   11284000000.0   11056000000.0
        # Reconciled Cost Of Revenue                          214137000000.0  223546000000.0  212981000000.0  169559000000.0
        # EBITDA                                              125820000000.0  130541000000.0  120233000000.0   77344000000.0
        # EBIT                                                114301000000.0  119437000000.0  108949000000.0   66288000000.0
        # Net Interest Income                                            NaN    -106000000.0     198000000.0     890000000.0
        # Interest Expense                                               NaN    2931000000.0    2645000000.0    2873000000.0
        # Interest Income                                                NaN    2825000000.0    2843000000.0    3763000000.0
        # Normalized Income                                    96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Net Income From Continuing And Discontinued Ope...   96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Total Expenses                                      268984000000.0  274891000000.0  256868000000.0  208227000000.0
        # Total Operating Income As Reported                  114301000000.0  119437000000.0  108949000000.0   66288000000.0
        # Diluted Average Shares                               15812547000.0   16325819000.0   16864919000.0   17528214000.0
        # Basic Average Shares                                 15744231000.0   16215963000.0   16701272000.0   17352119000.0
        # Diluted EPS                                                   6.13            6.11            5.61            3.28
        # Basic EPS                                                     6.16            6.15            5.67            3.31
        # Diluted NI Availto Com Stockholders                  96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Net Income Common Stockholders                       96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Net Income                                           96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Net Income Including Noncontrolling Interests        96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Net Income Continuous Operations                     96995000000.0   99803000000.0   94680000000.0   57411000000.0
        # Tax Provision                                        16741000000.0   19300000000.0   14527000000.0    9680000000.0
        # Pretax Income                                       113736000000.0  119103000000.0  109207000000.0   67091000000.0
        # Other Income Expense                                  -565000000.0    -334000000.0     258000000.0     803000000.0
        # Other Non Operating Income Expenses                   -565000000.0    -334000000.0     258000000.0     803000000.0
        # Net Non Operating Interest Income Expense                      NaN    -106000000.0     198000000.0     890000000.0
        # Interest Expense Non Operating                                 NaN    2931000000.0    2645000000.0    2873000000.0
        # Interest Income Non Operating                                  NaN    2825000000.0    2843000000.0    3763000000.0
        # Operating Income                                    114301000000.0  119437000000.0  108949000000.0   66288000000.0
        # Operating Expense                                    54847000000.0   51345000000.0   43887000000.0   38668000000.0
        # Research And Development                             29915000000.0   26251000000.0   21914000000.0   18752000000.0
        # Selling General And Administration                   24932000000.0   25094000000.0   21973000000.0   19916000000.0
        # Gross Profit                                        169148000000.0  170782000000.0  152836000000.0  104956000000.0
        # Cost Of Revenue                                     214137000000.0  223546000000.0  212981000000.0  169559000000.0
        # Total Revenue                                       383285000000.0  394328000000.0  365817000000.0  274515000000.0
        # Operating Revenue                                   383285000000.0  394328000000.0  365817000000.0  274515000000.0

        # fundamental_info = stock.get_actions() [igual a 'stock.actions']
        # --------------------------------------
        #
        # Dividends  Stock Splits
        # Date
        # 1987-05-11 00:00:00-04:00   0.000536           0.0
        # 1987-06-16 00:00:00-04:00   0.000000           2.0
        # 1987-08-10 00:00:00-04:00   0.000536           0.0
        # 1987-11-17 00:00:00-05:00   0.000714           0.0
        # 1988-02-12 00:00:00-05:00   0.000714           0.0
        # ...                              ...           ...
        # 2022-11-04 00:00:00-04:00   0.230000           0.0
        # 2023-02-10 00:00:00-05:00   0.230000           0.0
        # 2023-05-12 00:00:00-04:00   0.240000           0.0
        # 2023-08-11 00:00:00-04:00   0.240000           0.0
        # 2023-11-10 00:00:00-05:00   0.240000           0.0

        # fundamental_info = stock.fast_info
        # ----------------------------------
        #
        # lazy-loading dict with keys = ['currency', 'dayHigh', 'dayLow', 'exchange', 'fiftyDayAverage', 'lastPrice', 'lastVolume', 'marketCap', 'open', 'previousClose', 'quoteType', 'regularMarketPreviousClose', 'shares', 'tenDayAverageVolume', 'threeMonthAverageVolume', 'timezone', 'twoHundredDayAverage', 'yearChange', 'yearHigh', 'yearLow']
        #
        # print(fundamental_info['currency'])
        # print(fundamental_info['yearChange'])
        # print(fundamental_info['yearHigh'])
        # print(fundamental_info['yearLow'])
        # print(fundamental_info['quoteType'])
        # USD
        # 0.39208606356050935
        # 199.6199951171875  
        # 128.1199951171875
        # EQUITY

        # fundamental_info = stock.balance_sheet [igual a 'stock.balancesheet']
        # --------------------------------------
        # assets
        #                                                         2023-09-30      2022-09-30      2021-09-30      2020-09-30
        # Treasury Shares Number                                         0.0             NaN             NaN             NaN
        # Ordinary Shares Number                               15550061000.0   15943425000.0   16426786000.0   16976763000.0
        # Share Issued                                         15550061000.0   15943425000.0   16426786000.0   16976763000.0
        # Net Debt                                             81123000000.0   96423000000.0   89779000000.0   74420000000.0
        # Total Debt                                          111088000000.0  120069000000.0  124719000000.0  112436000000.0
        # Tangible Book Value                                  62146000000.0   50672000000.0   63090000000.0   65339000000.0
        # Invested Capital                                    173234000000.0  170741000000.0  187809000000.0  177775000000.0
        # Working Capital                                      -1742000000.0  -18577000000.0    9355000000.0   38321000000.0
        # Net Tangible Assets                                  62146000000.0   50672000000.0   63090000000.0   65339000000.0
        # Common Stock Equity                                  62146000000.0   50672000000.0   63090000000.0   65339000000.0
        # Total Capitalization                                157427000000.0  149631000000.0  172196000000.0  164006000000.0
        # Total Equity Gross Minority Interest                 62146000000.0   50672000000.0   63090000000.0   65339000000.0
        # Stockholders Equity                                  62146000000.0   50672000000.0   63090000000.0   65339000000.0
        # Gains Losses Not Affecting Retained Earnings        -11452000000.0  -11109000000.0     163000000.0    -406000000.0
        # Other Equity Adjustments                            -11452000000.0             NaN             NaN             NaN
        # Retained Earnings                                     -214000000.0   -3068000000.0    5562000000.0   14966000000.0
        # Capital Stock                                        73812000000.0   64849000000.0   57365000000.0   50779000000.0
        # Common Stock                                         73812000000.0   64849000000.0   57365000000.0   50779000000.0
        # Total Liabilities Net Minority Interest             290437000000.0  302083000000.0  287912000000.0  258549000000.0
        # Total Non Current Liabilities Net Minority Inte...  145129000000.0  148101000000.0  162431000000.0  153157000000.0
        # Other Non Current Liabilities                        49848000000.0   49142000000.0   53325000000.0   54490000000.0
        # Tradeand Other Payables Non Current                            NaN   16657000000.0   24689000000.0   28170000000.0
        # Long Term Debt And Capital Lease Obligation          95281000000.0   98959000000.0  109106000000.0   98667000000.0
        # Long Term Debt                                       95281000000.0   98959000000.0  109106000000.0   98667000000.0
        # Current Liabilities                                 145308000000.0  153982000000.0  125481000000.0  105392000000.0
        # Other Current Liabilities                            58829000000.0   60845000000.0   47493000000.0   42684000000.0
        # Current Deferred Liabilities                          8061000000.0    7912000000.0    7612000000.0    6643000000.0
        # Current Deferred Revenue                              8061000000.0    7912000000.0    7612000000.0    6643000000.0
        # Current Debt And Capital Lease Obligation            15807000000.0   21110000000.0   15613000000.0   13769000000.0
        # Current Debt                                         15807000000.0   21110000000.0   15613000000.0   13769000000.0
        # Other Current Borrowings                              9822000000.0   11128000000.0    9613000000.0    8773000000.0
        # Commercial Paper                                      5985000000.0    9982000000.0    6000000000.0    4996000000.0
        # Payables And Accrued Expenses                        62611000000.0   64115000000.0   54763000000.0   42296000000.0
        # Payables                                             62611000000.0   64115000000.0   54763000000.0   42296000000.0
        # Accounts Payable                                     62611000000.0   64115000000.0   54763000000.0   42296000000.0
        # Total Assets                                        352583000000.0  352755000000.0  351002000000.0  323888000000.0
        # Total Non Current Assets                            209017000000.0  217350000000.0  216166000000.0  180175000000.0
        # Other Non Current Assets                             64758000000.0   54428000000.0   48849000000.0   42522000000.0
        # Investments And Advances                            100544000000.0  120805000000.0  127877000000.0  100887000000.0
        # Other Investments                                              NaN  120805000000.0  127877000000.0  100887000000.0
        # Investmentin Financial Assets                       100544000000.0  120805000000.0  127877000000.0  100887000000.0
        # Available For Sale Securities                       100544000000.0  120805000000.0  127877000000.0  100887000000.0
        # Net PPE                                              43715000000.0   42117000000.0   39440000000.0   36766000000.0
        # Accumulated Depreciation                                       NaN  -72340000000.0  -70283000000.0  -66760000000.0
        # Gross PPE                                                      NaN  114457000000.0  109723000000.0  103526000000.0
        # Leases                                                         NaN   11271000000.0   11023000000.0   10283000000.0
        # Machinery Furniture Equipment                                  NaN   81060000000.0   78659000000.0   75291000000.0
        # Land And Improvements                                          NaN   22126000000.0   20041000000.0   17952000000.0
        # Properties                                                     NaN             0.0             0.0             0.0
        # Current Assets                                      143566000000.0  135405000000.0  134836000000.0  143713000000.0
        # Other Current Assets                                 14695000000.0   21223000000.0   14111000000.0   11264000000.0
        # Inventory                                             6331000000.0    4946000000.0    6580000000.0    4061000000.0
        # Receivables                                          60985000000.0   60932000000.0   51506000000.0   37445000000.0
        # Other Receivables                                    31477000000.0   32748000000.0   25228000000.0   21325000000.0
        # Accounts Receivable                                  29508000000.0   28184000000.0   26278000000.0   16120000000.0
        # Cash Cash Equivalents And Short Term Investments     61555000000.0   48304000000.0   62639000000.0   90943000000.0
        # Other Short Term Investments                         31590000000.0   24658000000.0   27699000000.0   52927000000.0
        # Cash And Cash Equivalents                            29965000000.0   23646000000.0   34940000000.0   38016000000.0
        # Cash Equivalents                                               NaN    5100000000.0   17635000000.0   20243000000.0
        # Cash Financial                                                 NaN   18546000000.0   17305000000.0   17773000000.0

        # fundamental_info = stock.cash_flow [igual a 'stock.cashflow']
        # ----------------------------------
        #
        #                                                     2023-09-30      2022-09-30      2021-09-30      2020-09-30
        # Free Cash Flow                                   99584000000.0  111443000000.0   92953000000.0   73365000000.0
        # Repurchase Of Capital Stock                     -77550000000.0  -89402000000.0  -85971000000.0  -72358000000.0
        # Repayment Of Debt                               -11151000000.0   -9543000000.0   -8750000000.0  -13592000000.0
        # Issuance Of Debt                                  5228000000.0    9420000000.0   20393000000.0   16091000000.0
        # Issuance Of Capital Stock                                  NaN             NaN    1105000000.0     880000000.0
        # Capital Expenditure                             -10959000000.0  -10708000000.0  -11085000000.0   -7309000000.0
        # Interest Paid Supplemental Data                   3803000000.0    2865000000.0    2687000000.0    3002000000.0
        # Income Tax Paid Supplemental Data                18679000000.0   19573000000.0   25385000000.0    9501000000.0
        # End Cash Position                                30737000000.0   24977000000.0   35929000000.0   39789000000.0
        # Beginning Cash Position                          24977000000.0   35929000000.0   39789000000.0   50224000000.0
        # Changes In Cash                                   5760000000.0  -10952000000.0   -3860000000.0  -10435000000.0
        # Financing Cash Flow                            -108488000000.0 -110749000000.0  -93353000000.0  -86820000000.0
        # Cash Flow From Continuing Financing Activities -108488000000.0 -110749000000.0  -93353000000.0  -86820000000.0
        # Net Other Financing Charges                      -6012000000.0   -6383000000.0   -6685000000.0   -3760000000.0
        # Cash Dividends Paid                             -15025000000.0  -14841000000.0  -14467000000.0  -14081000000.0
        # Common Stock Dividend Paid                      -15025000000.0  -14841000000.0  -14467000000.0  -14081000000.0
        # Net Common Stock Issuance                       -77550000000.0  -89402000000.0  -84866000000.0  -71478000000.0
        # Common Stock Payments                           -77550000000.0  -89402000000.0  -85971000000.0  -72358000000.0
        # Common Stock Issuance                                      NaN             NaN    1105000000.0     880000000.0
        # Net Issuance Payments Of Debt                    -9901000000.0    -123000000.0   12665000000.0    2499000000.0
        # Net Short Term Debt Issuance                     -3978000000.0    3955000000.0    1022000000.0    -963000000.0
        # Short Term Debt Payments                                   NaN             NaN             NaN    -963000000.0
        # Short Term Debt Issuance                                   NaN    3955000000.0             NaN             NaN
        # Net Long Term Debt Issuance                      -5923000000.0   -4078000000.0   11643000000.0    3462000000.0
        # Long Term Debt Payments                         -11151000000.0   -9543000000.0   -8750000000.0  -12629000000.0
        # Long Term Debt Issuance                           5228000000.0    5465000000.0   20393000000.0   16091000000.0
        # Investing Cash Flow                               3705000000.0  -22354000000.0  -14545000000.0   -4289000000.0
        # Cash Flow From Continuing Investing Activities    3705000000.0  -22354000000.0  -14545000000.0   -4289000000.0
        # Net Other Investing Changes                      -1337000000.0   -1780000000.0    -352000000.0    -791000000.0
        # Net Investment Purchase And Sale                 16001000000.0   -9560000000.0   -3075000000.0    5335000000.0
        # Sale Of Investment                               45514000000.0   67363000000.0  106483000000.0  120483000000.0
        # Purchase Of Investment                          -29513000000.0  -76923000000.0 -109558000000.0 -115148000000.0
        # Net Business Purchase And Sale                             NaN    -306000000.0     -33000000.0   -1524000000.0
        # Purchase Of Business                                       NaN    -306000000.0     -33000000.0   -1524000000.0
        # Net PPE Purchase And Sale                       -10959000000.0  -10708000000.0  -11085000000.0   -7309000000.0
        # Purchase Of PPE                                 -10959000000.0  -10708000000.0  -11085000000.0   -7309000000.0
        # Operating Cash Flow                             110543000000.0  122151000000.0  104038000000.0   80674000000.0
        # Cash Flow From Continuing Operating Activities  110543000000.0  122151000000.0  104038000000.0   80674000000.0
        # Change In Working Capital                        -6577000000.0    1200000000.0   -4911000000.0    5690000000.0
        # Change In Other Working Capital                            NaN     478000000.0    1676000000.0    2081000000.0
        # Change In Other Current Liabilities               3031000000.0    5632000000.0    5799000000.0    8916000000.0
        # Change In Other Current Assets                   -5684000000.0   -6499000000.0   -8042000000.0   -9588000000.0
        # Change In Payables And Accrued Expense           -1889000000.0    9448000000.0   12326000000.0   -4062000000.0
        # Change In Payable                                -1889000000.0    9448000000.0   12326000000.0   -4062000000.0
        # Change In Account Payable                        -1889000000.0    9448000000.0   12326000000.0   -4062000000.0
        # Change In Inventory                              -1618000000.0    1484000000.0   -2642000000.0    -127000000.0
        # Change In Receivables                             -417000000.0   -9343000000.0  -14028000000.0    8470000000.0
        # Changes In Account Receivables                   -1688000000.0   -1823000000.0  -10125000000.0    6917000000.0
        # Other Non Cash Items                             -2227000000.0     111000000.0    -147000000.0     -97000000.0
        # Stock Based Compensation                         10833000000.0    9038000000.0    7906000000.0    6829000000.0
        # Deferred Tax                                               NaN     895000000.0   -4774000000.0    -215000000.0
        # Deferred Income Tax                                        NaN     895000000.0   -4774000000.0    -215000000.0
        # Depreciation Amortization Depletion              11519000000.0   11104000000.0   11284000000.0   11056000000.0
        # Depreciation And Amortization                    11519000000.0   11104000000.0   11284000000.0   11056000000.0
        # Net Income From Continuing Operations            96995000000.0   99803000000.0   94680000000.0   57411000000.0

        # fundamental_info = stock.get_news() -> Puede funcionar con las que tienen 'link'
        # -----------------------------------
        #
        #         [{'uuid': '4205eaa9-f620-3a0b-a81a-0e82c7c9fd0b', 'title': 'Magnificent Seven Stocks To Buy And Watch: Nvidia Rallies To Record High', 'publisher': "Investor's Business Daily", 'link': 'https://finance.yahoo.com/m/4205eaa9-f620-3a0b-a81a-0e82c7c9fd0b/magnificent-seven-stocks-to.html', 'providerPublishTime': 1704742902, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/IVY_jviTG_ue49k31izfew--~B/aD02MDA7dz0xMDY1O2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/ibd.com/f287385a5f84c1d1e13191d4ae92d9fb', 'width': 1065, 'height': 600, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/EDUpiEmpjj.CUhr9H67TBQ--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/ibd.com/f287385a5f84c1d1e13191d4ae92d9fb', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['NVDA', 'AAPL', 'TSLA', 'META', 'MSFT']}, {'uuid': '5f90cca0-59e7-33aa-9819-fbc6c33715a3', 'title': 'Barclays sheds 5,000 jobs amid cost-cutting drive', 'publisher': 'The Telegraph', 'link': 'https://finance.yahoo.com/m/5f90cca0-59e7-33aa-9819-fbc6c33715a3/barclays-sheds-5%2C000-jobs.html', 'providerPublishTime': 1704741522, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/PrzncJ3d8MrU4NF5LRHelw--~B/aD0xNTQ2O3c9MjQ3NDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/the_telegraph_258/4fd4a5f10a516b4f5ca835607952f0f2', 'width': 2474, 'height': 1546, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/Y86XxUgdVty2_U3FALgO5Q--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/the_telegraph_258/4fd4a5f10a516b4f5ca835607952f0f2', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['^FTSE', 'BA', 'ALK', 'AAPL', 'JNJ', 'DRXGY', 'BCS', 'COMP', '^HSI', '^GSPC', '^YH102', '^DJI']}, {'uuid': 'bdd6cbc9-1a89-3b77-b5d4-8fe896138e64', 'title': "Apple's Vision Pro headset launches next month as company seeks to expand mixed-reality market", 'publisher': 'Associated Press Finance', 'link': 'https://finance.yahoo.com/news/apples-vision-pro-headset-launches-190538968.html', 'providerPublishTime': 1704740738, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/CIoWshePjBdOSZPtiUNCZg--~B/aD0yMjYwO3c9MzM4OTthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap_finance_articles_694/0834cdf10f1e2797efc6e3bde15db0a4', 'width': 3389, 'height': 2260, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/tQJYZ8B85yjerFQv7_yzoA--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/ap_finance_articles_694/0834cdf10f1e2797efc6e3bde15db0a4', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['AAPL']}, {'uuid': '85d3c15a-426c-3bac-b64f-88585d8b157f', 'title': 'These Stocks Are Moving the Most Today: Boeing, Spirit AeroSystems, American, Nvidia, Apple, Axonics, Ambrx, and More', 'publisher': 'Barrons.com', 'link': 'https://finance.yahoo.com/m/85d3c15a-426c-3bac-b64f-88585d8b157f/these-stocks-are-moving-the.html', 'providerPublishTime': 1704737220, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/aSrFnVJINdtJfREZKcOLGA--~B/aD02NDA7dz0xMjgwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/Barrons.com/55a5b0ed3b2e21bbdb1d08f3b8987a6d', 'width': 1280, 'height': 640, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/y4iXeCbOmqWRDC9TJEq.zw--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/Barrons.com/55a5b0ed3b2e21bbdb1d08f3b8987a6d', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['TSLA', 'HARP', 'AAPL']}, {'uuid': 
        # '65b53896-faf4-3a06-9d0d-a63cf3c83192', 'title': 'Best Dow Jones Stocks To Buy And Watch In January 2024: Apple Rebounds, Boeing Dives', 'publisher': "Investor's Business Daily", 'link': 'https://finance.yahoo.com/m/65b53896-faf4-3a06-9d0d-a63cf3c83192/best-dow-jones-stocks-to-buy.html', 'providerPublishTime': 1704737073, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/JPX5jeyihDRi4N6ueuYJVQ--~B/aD01NjM7dz0xMDAwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/ibd.com/ed4e9880b0c3e9257977ca3554a6c383', 'width': 1000, 'height': 563, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/.0m6SEAzHJOxc1V1Vw8fuA--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/ibd.com/ed4e9880b0c3e9257977ca3554a6c383', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['^DJI', 'MSFT', 'AAPL']}, {'uuid': '12ffd68e-f03e-44e9-a704-8e11332affce', 'title': 'Why 2024 could be the year of media dealmaking', 'publisher': 'Yahoo Finance', 'link': 'https://finance.yahoo.com/news/why-2024-could-be-the-year-of-media-dealmaking-125059041.html', 'providerPublishTime': 
        # 1704737028, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/R83kYXzzlY0lHr7PRsDjdQ--~B/aD0yODQ4O3c9NDI4ODthcHBpZD15dGFjaHlvbg--/https://s.yimg.com/os/creatr-uploaded-images/2023-12/a521d910-9ea7-11ee-bbfc-58008a14aee1', 'width': 4288, 'height': 2848, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/QjGWbnhiPT.RLdBRvYkugA--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://s.yimg.com/os/creatr-uploaded-images/2023-12/a521d910-9ea7-11ee-bbfc-58008a14aee1', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['PARA', 'PARAA', 'PARAP', 'NFLX', 'WBD', 'DIS', 'CMCSA', 'AAPL', 'ATUS', 'AMZN']}, {'uuid': 
        # 'b90479d1-1439-3f28-8310-c20b149de300', 'title': 'Apple disputes EU rules labelling its 5 App Stores as one service', 'publisher': 'Reuters', 'link': 'https://finance.yahoo.com/news/apple-disputes-eu-rules-labelling-175204780.html', 'providerPublishTime': 1704736324, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/xCUxnHuLVXuHXa_LRL.BhQ--~B/aD01MzM7dz04MDA7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/reuters-finance.com/192b551dc2b37d7ae092678af895977a', 'width': 800, 'height': 533, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/bLSebvcezYoPBd8BOgNWJw--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/reuters-finance.com/192b551dc2b37d7ae092678af895977a', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['AAPL']}, {'uuid': 'ba525301-03e1-305a-856c-d961034c9b96', 'title': 'Navigating Market Uncertainty: Intrinsic Value of Apple Inc', 'publisher': 'GuruFocus.com', 'link': 'https://finance.yahoo.com/news/navigating-market-uncertainty-intrinsic-value-170154334.html', 'providerPublishTime': 1704733314, 'type': 'STORY', 'thumbnail': {'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/.2jI7yhsqUKdeQ_kZJrS4g--~B/aD00MDA7dz00MDA7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/us.finance.gurufocus/24bb4e9d1cf942a6190fe9707aa59d3c', 'width': 400, 'height': 400, 'tag': 'original'}, {'url': 'https://s.yimg.com/uu/api/res/1.2/rS1PyaUsN1UUVEF6R8Jldg--~B/Zmk9ZmlsbDtoPTE0MDtweW9mZj0wO3c9MTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/us.finance.gurufocus/24bb4e9d1cf942a6190fe9707aa59d3c', 'width': 140, 'height': 140, 'tag': '140x140'}]}, 'relatedTickers': ['AAPL']}]

        # fundamental_info = stock.get_major_holders()
        # --------------------------------------------
        #
        #         0                                      1
        # 0   0.07%        % of Shares Held by All Insider
        # 1  61.50%       % of Shares Held by Institutions
        # 2  61.54%        % of Float Held by Institutions
        # 3    5867  Number of Institutions Holding Shares

        # fundamental_info = stock.get_institutional_holders()
        # ----------------------------------------------------
        #
        #                               Holder      Shares Date Reported   % Out         Value
        # 0                 Vanguard Group Inc  1299997133    2023-09-29  0.0836  240739965900
        # 1                     Blackrock Inc.  1031407553    2023-09-29  0.0663  191001205184
        # 2            Berkshire Hathaway, Inc   915560382    2023-09-29  0.0589  169548047105
        # 3           State Street Corporation   569291690    2023-09-29  0.0366  105424280222
        # 4                           FMR, LLC   298321726    2023-09-29  0.0192   55244708100
        # 5      Geode Capital Management, LLC   296103070    2023-09-29  0.0190   54833846295
        # 6      Price (T.Rowe) Associates Inc   216307878    2023-09-29  0.0139   40056973859
        # 7                     Morgan Stanley   206732960    2023-09-29  0.0133   38283842692
        # 8         Northern Trust Corporation   168874976    2023-09-29  0.0109   31273112018
        # 9  Norges Bank Investment Management   167374278    2022-12-30  0.0108   30995205262

        # fundamental_info = stock.get_mutualfund_holders()
        # -------------------------------------------------
        #
        #                                               Holder     Shares Date Reported   % Out        Value
        # 0             Vanguard Total Stock Market Index Fund  462496298    2023-09-29  0.0297  85614814202
        # 1                            Vanguard 500 Index Fund  353157634    2023-09-29  0.0227  65374631861
        # 2                            Fidelity 500 Index Fund  170161953    2023-10-30  0.0109  31499460759
        # 3                             SPDR S&P 500 ETF Trust  163961069    2023-09-29  0.0105  30351586638
        # 4                           iShares Core S&P 500 ETF  138678373    2023-09-29  0.0089  25671390645
        # 5                         Vanguard Growth Index Fund  128896004    2023-09-29  0.0083  23860531384
        # 6        Invesco ETF Tr-Invesco QQQ Tr, Series 1 ETF  124636013    2023-09-29  0.0080  23071944882
        # 7  Vanguard Institutional Index Fund-Institutiona...   98610773    2023-09-29  0.0063  18254293159
        # 8         Vanguard Information Technology Index Fund   76972129    2023-08-30  0.0049  14248664371
        # 9                 Select Sector SPDR Fund-Technology   64668259    2023-09-29  0.0042  11971038477

        # fundamental_info = stock.option_chain()
        # ---------------------------------------
        #
        # info que no entiendo

        # fundamental_info = stock.options
        # --------------------------------
        #
        # ('2024-01-12', '2024-01-19', '2024-01-26', '2024-02-02', '2024-02-09', '2024-02-16', '2024-02-23', '2024-03-15', '2024-04-19', '2024-05-17', '2024-06-21', '2024-07-19', '2024-08-16', '2024-09-20', '2024-12-20', '2025-01-17', '2025-06-20', '2025-09-19', '2025-12-19', '2026-01-16', '2026-06-18')
        
        # fundamental_info = stock.get_shares_full()
        # ------------------------------------------
        #
        # 2022-07-29 00:00:00-04:00    16243000320
        # 2022-07-30 00:00:00-04:00    16185199616
        # 2022-08-01 00:00:00-04:00    16070800384
        # 2022-09-02 00:00:00-04:00    16070800384
        # 2022-09-15 00:00:00-04:00    15918600192
        #                                 ...     
        # 2023-12-26 00:00:00-05:00    15552799744
        # 2024-01-03 00:00:00-05:00    15552799744
        # 2024-01-04 00:00:00-05:00    15552799744
        # 2024-01-05 00:00:00-05:00    15552799744
        # 2024-01-05 00:00:00-05:00    15752800256

        # fundamental_info = stock.quarterly_income_stmt [igual a 'stock.quarterly_incomestmt' y 'stock.quarterly_financials']
        # ----------------------------------------------
        #
        #                                                        2023-09-30     2023-06-30     2023-03-31      2022-12-31
        # Tax Effect Of Unusual Items                                   0.0            0.0            0.0             0.0
        # Tax Rate For Calcs                                       0.149715       0.125456       0.148756        0.157904
        # Normalized EBITDA                                   29622000000.0  26050000000.0  31216000000.0   38932000000.0
        # Net Income From Continuing Operation Net Minori...  22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Reconciled Depreciation                              2653000000.0   3052000000.0   2898000000.0    2916000000.0
        # Reconciled Cost Of Revenue                          49071000000.0  45384000000.0  52860000000.0   66822000000.0
        # EBITDA                                              29622000000.0  26050000000.0  31216000000.0   38932000000.0
        # EBIT                                                26969000000.0  22998000000.0  28318000000.0   36016000000.0
        # Net Interest Income                                           NaN    -18000000.0    -12000000.0    -135000000.0
        # Interest Expense                                              NaN    998000000.0    930000000.0    1003000000.0
        # Interest Income                                               NaN    980000000.0    918000000.0     868000000.0
        # Normalized Income                                   22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Net Income From Continuing And Discontinued Ope...  22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Total Expenses                                      62529000000.0  58799000000.0  66518000000.0   81138000000.0
        # Total Operating Income As Reported                  26969000000.0  22998000000.0  28318000000.0   36016000000.0
        # Diluted Average Shares                              15672400000.0  15775021000.0  15847050000.0   15955718000.0
        # Basic Average Shares                                15599434000.0  15697614000.0  15787154000.0   15892723000.0
        # Diluted EPS                                                  1.46           1.26           1.52            1.88
        # Basic EPS                                                    1.47           1.27           1.53            1.89
        # Diluted NI Availto Com Stockholders                 22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Net Income Common Stockholders                      22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Net Income                                          22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Net Income Including Noncontrolling Interests       22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Net Income Continuous Operations                    22956000000.0  19881000000.0  24160000000.0   29998000000.0
        # Tax Provision                                        4042000000.0   2852000000.0   4222000000.0    5625000000.0
        # Pretax Income                                       26998000000.0  22733000000.0  28382000000.0   35623000000.0
        # Other Income Expense                                   29000000.0   -265000000.0     64000000.0    -393000000.0
        # Other Non Operating Income Expenses                    29000000.0   -265000000.0     64000000.0    -393000000.0
        # Net Non Operating Interest Income Expense                     NaN    -18000000.0    -12000000.0    -135000000.0
        # Interest Expense Non Operating                                NaN    998000000.0    930000000.0    1003000000.0
        # Interest Income Non Operating                                 NaN    980000000.0    918000000.0     868000000.0
        # Operating Income                                    26969000000.0  22998000000.0  28318000000.0   36016000000.0
        # Operating Expense                                   13458000000.0  13415000000.0  13658000000.0   14316000000.0
        # Research And Development                             7307000000.0   7442000000.0   7457000000.0    7709000000.0
        # Selling General And Administration                   6151000000.0   5973000000.0   6201000000.0    6607000000.0
        # Gross Profit                                        40427000000.0  36413000000.0  41976000000.0   50332000000.0
        # Cost Of Revenue                                     49071000000.0  45384000000.0  52860000000.0   66822000000.0
        # Total Revenue                                       89498000000.0  81797000000.0  94836000000.0  117154000000.0
        # Operating Revenue                                   89498000000.0  81797000000.0  94836000000.0  117154000000.0


        # fundamental_info = stock.quarterly_balance_sheet [igual a 'stock.quarterly_balancesheet']
        # ------------------------------------------------
        #
        #                                                         2023-09-30      2023-06-30      2023-03-31      2022-12-31
        # Treasury Shares Number                                         0.0             NaN             NaN             NaN
        # Ordinary Shares Number                               15550061000.0   15647868000.0   15723406000.0   15842407000.0
        # Share Issued                                         15550061000.0   15647868000.0   15723406000.0   15842407000.0
        # Net Debt                                             81123000000.0   80872000000.0   84928000000.0   90575000000.0
        # Total Debt                                          111088000000.0  109280000000.0  109615000000.0  111110000000.0
        # Tangible Book Value                                  62146000000.0   60274000000.0   62158000000.0   56727000000.0
        # Invested Capital                                    173234000000.0  169554000000.0  171773000000.0  167837000000.0
        # Working Capital                                      -1742000000.0   -2304000000.0   -7162000000.0   -8509000000.0
        # Net Tangible Assets                                  62146000000.0   60274000000.0   62158000000.0   56727000000.0
        # Common Stock Equity                                  62146000000.0   60274000000.0   62158000000.0   56727000000.0
        # Total Capitalization                                157427000000.0  158345000000.0  159199000000.0  156354000000.0
        # Total Equity Gross Minority Interest                 62146000000.0   60274000000.0   62158000000.0   56727000000.0
        # Stockholders Equity                                  62146000000.0   60274000000.0   62158000000.0   56727000000.0
        # Gains Losses Not Affecting Retained Earnings        -11452000000.0  -11801000000.0  -11746000000.0  -12912000000.0
        # Other Equity Adjustments                            -11452000000.0  -11801000000.0  -11746000000.0             NaN
        # Retained Earnings                                     -214000000.0    1408000000.0    4336000000.0    3240000000.0
        # Capital Stock                                        73812000000.0   70667000000.0   69568000000.0   66399000000.0
        # Common Stock                                         73812000000.0   70667000000.0   69568000000.0   66399000000.0
        # Total Liabilities Net Minority Interest             290437000000.0  274764000000.0  270002000000.0  290020000000.0
        # Total Non Current Liabilities Net Minority Inte...  145129000000.0  149801000000.0  149927000000.0  152734000000.0
        # Other Non Current Liabilities                        49848000000.0   51730000000.0   52886000000.0   53107000000.0
        # Long Term Debt And Capital Lease Obligation          95281000000.0   98071000000.0   97041000000.0   99627000000.0
        # Long Term Debt                                       95281000000.0   98071000000.0   97041000000.0   99627000000.0
        # Current Liabilities                                 145308000000.0  124963000000.0  120075000000.0  137286000000.0
        # Other Current Liabilities                            58829000000.0   58897000000.0   56425000000.0   59893000000.0
        # Current Deferred Liabilities                          8061000000.0    8158000000.0    8131000000.0    7992000000.0
        # Current Deferred Revenue                              8061000000.0    8158000000.0    8131000000.0    7992000000.0
        # Current Debt And Capital Lease Obligation            15807000000.0   11209000000.0   12574000000.0   11483000000.0
        # Current Debt                                         15807000000.0   11209000000.0   12574000000.0   11483000000.0
        # Other Current Borrowings                              9822000000.0    7216000000.0   10578000000.0    9740000000.0
        # Commercial Paper                                      5985000000.0    3993000000.0    1996000000.0    1743000000.0
        # Payables And Accrued Expenses                        62611000000.0   46699000000.0   42945000000.0   57918000000.0
        # Payables                                             62611000000.0   46699000000.0   42945000000.0   57918000000.0
        # Accounts Payable                                     62611000000.0   46699000000.0   42945000000.0   57918000000.0
        # Total Assets                                        352583000000.0  335038000000.0  332160000000.0  346747000000.0
        # Total Non Current Assets                            209017000000.0  212379000000.0  219247000000.0  217970000000.0
        # Other Non Current Assets                             64758000000.0   64768000000.0   65388000000.0   60924000000.0
        # Investments And Advances                            100544000000.0  104061000000.0  110461000000.0  114095000000.0
        # Other Investments                                              NaN             NaN             NaN  114095000000.0
        # Investmentin Financial Assets                       100544000000.0  104061000000.0  110461000000.0             NaN
        # Available For Sale Securities                       100544000000.0  104061000000.0  110461000000.0             NaN
        # Net PPE                                              43715000000.0   43550000000.0   43398000000.0   42951000000.0
        # Accumulated Depreciation                                       NaN  -70787000000.0  -69668000000.0  -68044000000.0
        # Gross PPE                                                      NaN  114337000000.0  113066000000.0  110995000000.0
        # Current Assets                                      143566000000.0  122659000000.0  112913000000.0  128777000000.0
        # Other Current Assets                                 14695000000.0   13640000000.0   13660000000.0   16422000000.0
        # Inventory                                             6331000000.0    7351000000.0    7482000000.0    6820000000.0
        # Finished Goods                                                 NaN    3563000000.0    4103000000.0    4307000000.0
        # Raw Materials                                                  NaN    3788000000.0    3379000000.0    2513000000.0
        # Receivables                                          60985000000.0   39186000000.0   35899000000.0   54180000000.0
        # Other Receivables                                    31477000000.0   19637000000.0   17963000000.0   30428000000.0
        # Accounts Receivable                                  29508000000.0   19549000000.0   17936000000.0   23752000000.0
        # Cash Cash Equivalents And Short Term Investments     61555000000.0   62482000000.0   55872000000.0   51355000000.0
        # Other Short Term Investments                         31590000000.0   34074000000.0   31185000000.0   30820000000.0
        # Cash And Cash Equivalents                            29965000000.0   28408000000.0   24687000000.0   20535000000.0
        # Cash Equivalents                                               NaN    3071000000.0    4637000000.0    2627000000.0
        # Cash Financial                                                 NaN   25337000000.0   20050000000.0   17908000000.0

        # fundamental_info = stock.quarterly_cash_flow [igual a 'stock.quarterly_cashflow']
        # --------------------------------------------
        #
        #                                                    2023-09-30     2023-06-30     2023-03-31     2022-12-31
        # Free Cash Flow                                  19435000000.0  24287000000.0  25644000000.0  30218000000.0
        # Repurchase Of Capital Stock                    -21003000000.0 -17478000000.0 -19594000000.0 -19475000000.0
        # Repayment Of Debt                                         0.0  -7500000000.0   5964000000.0  -9615000000.0
        # Issuance Of Debt                                          0.0            NaN            NaN            NaN
        # Capital Expenditure                             -2163000000.0  -2093000000.0  -2916000000.0  -3787000000.0
        # Interest Paid Supplemental Data                  1213000000.0    717000000.0   1170000000.0    703000000.0
        # Income Tax Paid Supplemental Data               11659000000.0   2126000000.0   4066000000.0    828000000.0
        # End Cash Position                               30737000000.0  29898000000.0  27129000000.0  21974000000.0
        # Beginning Cash Position                         29898000000.0  27129000000.0  21974000000.0  24977000000.0
        # Changes In Cash                                   839000000.0   2769000000.0   5155000000.0  -3003000000.0
        # Financing Cash Flow                            -23153000000.0 -24048000000.0 -25724000000.0 -35563000000.0
        # Cash Flow From Continuing Financing Activities -23153000000.0 -24048000000.0 -25724000000.0 -35563000000.0
        # Net Other Financing Charges                      -385000000.0  -2438000000.0   -484000000.0  -2705000000.0
        # Cash Dividends Paid                             -3758000000.0  -3849000000.0  -3650000000.0  -3768000000.0
        # Common Stock Dividend Paid                      -3758000000.0  -3849000000.0  -3650000000.0  -3768000000.0
        # Net Common Stock Issuance                      -21003000000.0 -17478000000.0 -19594000000.0 -19475000000.0
        # Common Stock Payments                          -21003000000.0 -17478000000.0 -19594000000.0 -19475000000.0
        # Net Issuance Payments Of Debt                    1993000000.0   -283000000.0  -1996000000.0  -9615000000.0
        # Net Short Term Debt Issuance                     1993000000.0   1989000000.0    254000000.0  -8214000000.0
        # Short Term Debt Payments                                  NaN            NaN            NaN  -8214000000.0
        # Net Long Term Debt Issuance                               0.0  -2272000000.0  -2250000000.0  -1401000000.0
        # Long Term Debt Payments                                   0.0  -7500000000.0  -2250000000.0  -1401000000.0
        # Long Term Debt Issuance                                   0.0            NaN            NaN            NaN
        # Investing Cash Flow                              2394000000.0    437000000.0   2319000000.0  -1445000000.0
        # Cash Flow From Continuing Investing Activities   2394000000.0    437000000.0   2319000000.0  -1445000000.0
        # Net Other Investing Changes                      -584000000.0   -506000000.0   -106000000.0   -141000000.0
        # Net Investment Purchase And Sale                 5141000000.0   3036000000.0   5341000000.0   2483000000.0
        # Sale Of Investment                              13698000000.0  12795000000.0  11385000000.0   7636000000.0
        # Purchase Of Investment                          -8557000000.0  -9759000000.0  -6044000000.0  -5153000000.0
        # Net PPE Purchase And Sale                       -2163000000.0  -2093000000.0  -2916000000.0  -3787000000.0
        # Purchase Of PPE                                 -2163000000.0  -2093000000.0  -2916000000.0  -3787000000.0
        # Operating Cash Flow                             21598000000.0  26380000000.0  28560000000.0  34005000000.0
        # Cash Flow From Continuing Operating Activities  21598000000.0  26380000000.0  28560000000.0  34005000000.0
        # Change In Working Capital                       -6060000000.0    749000000.0    231000000.0  -1497000000.0
        # Change In Other Working Capital                           NaN            NaN            NaN    131000000.0
        # Change In Other Current Liabilities                45000000.0   1229000000.0  -2001000000.0   3758000000.0
        # Change In Other Current Assets                   -821000000.0   -771000000.0      7000000.0  -4099000000.0
        # Change In Payables And Accrued Expense          14901000000.0   3974000000.0 -14689000000.0  -6075000000.0
        # Change In Payable                               14901000000.0   3974000000.0 -14689000000.0  -6075000000.0
        # Change In Account Payable                       14901000000.0   3974000000.0 -14689000000.0  -6075000000.0
        # Change In Inventory                               952000000.0    -22000000.0   -741000000.0  -1807000000.0
        # Change In Receivables                          -21137000000.0  -3661000000.0  17786000000.0   6595000000.0
        # Changes In Account Receivables                  -9297000000.0  -1987000000.0   5321000000.0   4275000000.0
        # Other Non Cash Items                             -576000000.0     81000000.0  -1415000000.0   -317000000.0
        # Stock Based Compensation                         2625000000.0   2617000000.0   2686000000.0   2905000000.0
        # Depreciation Amortization Depletion              2653000000.0   3052000000.0   2898000000.0   2916000000.0
        # Depreciation And Amortization                    2653000000.0   3052000000.0   2898000000.0   2916000000.0
        # Net Income From Continuing Operations           22956000000.0  19881000000.0  24160000000.0  29998000000.0

        fundamental_info = stock.quarterly_financials

        fundamental_info = yf.get_indicators(stock)
        return fundamental_info
    except Exception as e:
        return f"Error fetching fundamental info: {e}"




# Example usage
ticker_symbol = "AAPL"  # Replace with the stock symbol you're interested in
fundamental_info = get_fundamental_info(ticker_symbol)

if isinstance(fundamental_info, dict):
    for key, value in fundamental_info.items():
        print(f"{key}: {value}")
else:
    print(fundamental_info) 