from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math

class MACD_BBW(bt.Strategy):
    params = (
        ('BBW_short', 10),
        ('BBW_long', 50),
        ('volume_short', 10),
        ('volume_long', 50),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Define indicators
        self.bb = btind.BollingerBands(self.dataclose, period = 20, devfactor = 2)
        self.bbw = (self.bb.lines.top - self.bb.lines.bot) / self.bb.lines.mid
        self.bbw_short = btind.MovingAverageSimple(self.bbw, period = self.params.BBW_short)
        self.bbw_long = btind.MovingAverageSimple(self.bbw, period = self.params.BBW_long)
        self.macd = btind.MACD(self.dataclose, period_me1=12, period_me2=26, period_signal=9)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None            

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades
            if self.macd.macd[0] > 0 and self.bbw_short[0] > self.bbw_long[0]:
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                self.order = self.buy(size=1)
        else:
            # We are in the market, look for a signal to CLOSE trades
            if self.macd.macd[0] < 0 and self.bbw_short[0] > self.bbw_long[0]:
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                self.order = self.sell(size=1)

class SimpleRSI(bt.Strategy):
    params = (
        ('printlog', False),
        ('period', 14),
        ('upperband', 60.0),
        ('lowerband', 40.0),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a RSI indicator
        self.rsi = btind.RelativeStrengthIndex(period=self.params.period, upperband=self.params.upperband, lowerband=self.params.lowerband)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check for open orders
        if self.order:
            return

        # Check if we are not in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.rsi[0] > 60:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
        else:
            if  self.rsi[0] < 40:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()