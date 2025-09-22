import pandas as pd
from hhsqllib.corefunc import corefunc
from hhsqllib.sqlfile import database
from hhsqllib.sqlconnect import get_db
from hhfactor.factor import Factor
from hhfactor.algor.factortreatment import *
from hhfactor.algor.datetreatment import *
from hhportfolio.stats import *

def calcuturnover(dfweight = None):

    dfweightpivot = pd.pivot(dfweight, columns='sid',index='dt', values='weight').fillna(0)
    turnover =  dfweightpivot.diff().abs().sum(axis=1)/2
    turnover.iloc[0] = 100
    turnover_df = turnover.reset_index()
    turnover_df.columns = ['date', 'turnover']
    return turnover_df







def backtest(df = None, ifweight = True, stdate ='20100101' , eddate ='20250701', sourcedb = None, banlancemethod = "o2o", buyfeecost = 0.001, sellfeecost = 0.003):
    '''
    Args:
        df:
        ifweight:
        stdate:
        eddate:
        sourcedb:
        banlancemethod:
        c2c :以次日收盘价买入，卖出，以收盘价计算净值
        o2o，以次日开盘价买入，以开盘价计算净值
        buyfeecost: 买入费率
        sellfeecost: 卖出费率
    Returns:
    '''

    df['dt'] = df['dt'].astype(str)
    df = df[(df['dt']>=stdate)*(df['dt']<=eddate)]
    df['dt'] = pd.to_datetime(df['dt'].astype(str))
    if ifweight:
        df['value'] = 1
        ct = df.groupby('dt')['value'].count().reset_index().rename(columns={'value':'ct'})
        df = df.merge(ct, on='dt', how='left')
        df['weight'] = 100/df['ct']
    turnover_df =  calcuturnover(dfweight = df.copy())

    df.set_index(['dt', 'sid'], inplace=True)
    datelist = list(df.index.levels[0])
    dtend = df.index.levels[0][-1]


    dtdaily = Daily(-1)

    sellret = pd.Series()
    buycost = pd.Series()
    sellcost = pd.Series()

    for i,dt in enumerate(df.index.levels[0]):
        print(i,dt)
        if dt != dtend:
            stdate = datelist[i]
            eddate = datelist[i+1]
            dfportfolio0 = df.loc[stdate]
            stocklist = dfportfolio0.index
            dfstockeod = corefunc.get_stockeodprice(stdate,eddate,stocklist=stocklist, sourcedb=sourcedb )
            stocklist = list(set(list(dfstockeod['sid'].drop_duplicates())) & set(stocklist) )
            if banlancemethod == 'o2o':
                nextday = dtdaily.next(stdate)
                dfopen = pd.pivot(dfstockeod, columns='sid', index='dt', values='S_DQ_ADJOPEN').loc[nextday:,stocklist]
                dfclose = pd.pivot(dfstockeod, columns='sid', index='dt', values='S_DQ_ADJCLOSE').loc[nextday:, stocklist]
                weights = dfportfolio0.weight.loc[stocklist]
                pctx = dfclose.pct_change()
                pctx = pctx.iloc[:-2]
                dfclosepct = dfclose.iloc[0]/ dfopen.iloc[0] -1
                pctx.dropna(inplace=True, how='all')
                pctx = pctx._append(dfclosepct)

                dfclosepctlast = dfopen.iloc[-1] / dfclose.iloc[-2] - 1
                dfclosepctlast.name = dfopen.iloc[-1].name
                pctx = pctx._append(dfclosepctlast)
                pctx.sort_index(inplace=True)
            if banlancemethod == 'c2c':
                dfclose = pd.pivot(dfstockeod, columns='sid', index='dt', values='S_DQ_ADJCLOSE').loc[nextday:,
                          stocklist]
                pctx = dfclose.pct_change()
                pctx.dropna(inplace=True)
                pctx = pctx._append(dfclosepct, how='all')


            retq = pctx @ weights
            sellret = sellret._append(retq)


            if i==0:
                buildcost = 100 * buyfeecost
                dt0 = step_trade_dt(stdate.strftime("%Y%m%d"), step=1)
                buildcostdict = pd.Series(buildcost,[dt0])
                buycost = buycost._append(buildcostdict)
            else:
                dt0 = step_trade_dt(stdate.strftime("%Y%m%d"), step=1)
                dfportfolio0old = df.loc[datelist[i-1]]
                newbuild = dfportfolio0['weight'].to_frame('newweight').merge( dfportfolio0old['weight'].to_frame('oldweight'), left_index=True, right_index=True,how='outer')
                buildcost =  buyfeecost * newbuild[newbuild['oldweight'].isna()]['newweight'].sum()
                buildcostdict = pd.Series(buildcost, [dt0])
                sellfee =  sellfeecost * newbuild[newbuild['newweight'].isna()]['oldweight'].sum()
                sellcostdict = pd.Series(sellfee, [stdate.strftime("%Y%m%d")])
                buycost = buycost._append(buildcostdict)
                sellcost = sellcost._append(sellcostdict)

        if dt == dtend:
            today = datetime.today().strftime('%Y%m%d')
            stdate = datelist[-1]
            eddate = today
            dfportfolio0old = df.loc[datelist[-1]]
            stocklist = dfportfolio0old.index
            weights = dfportfolio0old.hold
            dfstockeod = corefunc.get_stockeodprice(stdate, eddate, stocklist=stocklist, sourcedb=sourcedb)
            if len(dfstockeod) == 0:
                continue
            if len(dfopen) == 1:
                continue
            dfopen = pd.pivot(dfstockeod, columns='sid', index='dt', values='S_DQ_ADJOPEN').loc[:, stocklist]
            dfclose = pd.pivot(dfstockeod, columns='sid', index='dt', values='S_DQ_ADJCLOSE').loc[:, stocklist]
            pctx = dfclose.pct_change()
            dfclosepct = dfclose.iloc[0] / dfopen.iloc[0] - 1
            pctx.dropna(inplace=True)
            pctx = pctx._append(dfclosepct)
            retq = pctx @ weights
            sellret = sellret._append(retq)

    if banlancemethod == "o2o":
        sellret = sellret.groupby(level=0).sum()


    return buycost, sellret, sellcost, turnover_df




def calcureturn(buycost= None,sellret= None,sellcost= None,name = None,sourcedb=None,benchmark = 'H00985.CSI'):

    dyt = Daily(-1)
    resdf = sellret.to_frame("净值收益")
    resdf = resdf.join(buycost.to_frame("买入费用")).join(sellcost.to_frame("卖出费用"))
    resdf['扣费收益'] = resdf['净值收益'] - resdf['买入费用'].fillna(0)  -resdf['卖出费用'] .fillna(0)
    resdf['扣费收益累加'] = resdf['扣费收益'].cumsum()
    resdf['扣费收益累乘'] =( 0.01*resdf['扣费收益'] + 1).cumprod()
    resdf['回撤'] = (resdf['扣费收益累乘'].cummax()-resdf['扣费收益累乘'] )/resdf['扣费收益累乘'].cummax()
    portfolio = resdf[['扣费收益']].reset_index()
    portfolio.rename(columns={'index':'dt'}, inplace=True)
    indexeod = corefunc.get_index_eod(indexs=[benchmark],sourcedb=sourcedb)

    indexeod['indexpct'] =100* indexeod['close'].pct_change()
    portfolio = portfolio.merge(indexeod, on='dt', how='left')
    portfolio['超额收益'] = portfolio['扣费收益'] - portfolio['indexpct']
    portfolio['dt_datetime'] = pd.to_datetime(portfolio['dt'], format='%Y%m%d')
    portfolio['dt_month'] = portfolio['dt_datetime'].dt.month
    portfolio['dt_year'] = portfolio['dt_datetime'].dt.year
    portfolio["YM"] = portfolio['dt_datetime'].apply(lambda x:x.strftime('%Y%m'))
    portfolio = portfolio.merge(portfolio.groupby("YM").first()[['dt']].reset_index().rename(columns={'dt':'当月第一个交易日'}))


    resdict = {
        "年化收益": 100*annual_return( 0.01*resdf['扣费收益']),
        "年化波动": 100*annual_volatility( 0.01*resdf['扣费收益']),
        "夏普比例":sharpe_ratio( 0.01*resdf['扣费收益'], risk_free=0),
        "最大回撤":100*max_drawdown(0.01*resdf['扣费收益'])
    }


    portfolio['距离第一个交易日的天数'] = portfolio.apply(lambda x: len(dyt.get(x['当月第一个交易日'],x['dt'])),axis=1)
    portfolio['超额收益累加'] = portfolio['超额收益'].cumsum()
    portfolio['扣费收益累加']= portfolio['扣费收益'].cumsum()


    # 扣费后表现情况
    resdict = pd.Series(resdict)
    #月度收益
    monthlyreturn= portfolio.groupby(['dt_month'])['超额收益'].mean()

    portfolio['dt_day'] = portfolio['dt_datetime'].dt.day
    #日度收益
    dailyreturn = portfolio.groupby(['距离第一个交易日的天数'])['超额收益'].mean()
    #年度收益
    yearreturn = portfolio.groupby(['dt_year'])['超额收益'].mean()


    with pd.ExcelWriter(name) as writer:
        portfolio.to_excel(writer, sheet_name='收益')
        resdict.to_excel(writer, sheet_name='组合表现')
        dailyreturn.to_excel(writer, sheet_name='日度收益')
        monthlyreturn.to_excel(writer, sheet_name='月度收益')
        yearreturn.to_excel(writer, sheet_name='年度收益')
        resdf.to_excel(writer, sheet_name='收益累乘')




if __name__ == '__main__':
    db = database(file=r'sqldatabase.yaml')
    sourcedb = get_db(db.sourcedatabase_wind, schem='dbo')

