from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math

class MAcrossover(bt.Strategy):
    params = (
        ('pfast', 20),
        ('pslow', 50),
    )
    
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
            
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Instantiate moving averages
        self.slow_sma = btind.MovingAverageSimple(self.datas[0], 
                        period=self.params.pslow)
        self.fast_sma = btind.MovingAverageSimple(self.datas[0], 
                        period=self.params.pfast)
        self.crossover = btind.CrossOver(self.fast_sma, self.slow_sma)
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
		    return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            if order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            
            self.bar_executed = len(self)

	elif order.status in [order.Canceled, order.Margin, order.Rejected]:
		self.log('Order Canceled/Margin/Rejected')
    
    # Reset orders
	self.order = None

    def next(self):
    	# Check for open orders
    	if self.order:
    		return
    
    	# Check if we are in the market
    	if not self.position:
    		# We are not in the market, look for a signal to OPEN trades
    			
    		#If the 20 SMA is above the 50 SMA
    		if self.crossover > 0:
    			self.log(f'BUY CREATE {self.dataclose[0]:2f}')
    			# Keep track of the created order to avoid a 2nd order
    			self.order = self.buy()
    		#Otherwise if the 20 SMA is below the 50 SMA   
    		elif self.crossover < 0:
    			self.log(f'SELL CREATE {self.dataclose[0]:2f}')
    			# Keep track of the created order to avoid a 2nd order
    			self.order = self.sell()
    	else:
    		# We are already in the market, look for a signal to CLOSE trades
    		if len(self) >= (self.bar_executed + 5):
    			self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
    			self.order = self.close()


class SimpleRSI(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a RSI indicator
        self.rsi = bt.indicators.RelativeStrengthIndex(self.datas[0])

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

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.rsi[0] < 40:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.rsi[0] > 60:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

