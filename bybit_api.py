"""
📊 Bybit API Integration
التكامل مع منصة Bybit للحصول على الأسعار وتنفيذ الصفقات
"""
import ccxt
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from config import BYBIT_TESTNET, BYBIT_MAINNET, TRADING_CONFIG

logger = logging.getLogger(__name__)


class BybitAPI:
    """إدارة Bybit API"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 testnet: bool = False):
        """تهيئة Bybit API"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.exchange = None
        self.price_cache = {}
        
        if api_key and api_secret:
            self._init_exchange()
    
    def _init_exchange(self):
        """تهيئة CCXT Exchange"""
        try:
            config = {
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
            }
            
            if self.testnet:
                config['urls'] = {
                    'api': BYBIT_TESTNET['base_url']
                }
            
            self.exchange = ccxt.bybit(config)
            logger.info("✅ Bybit API initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Bybit API: {e}")
            raise
    
    # ==================== الأسعار والسوق ====================
    
    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """الحصول على سعر زوج معين"""
        try:
            # استخدام CCXT
            if self.exchange:
                ticker = await asyncio.to_thread(
                    self.exchange.fetch_ticker, symbol
                )
            else:
                # استخدام API عام بدون مفاتيح
                exchange = ccxt.bybit({'enableRateLimit': True})
                ticker = await asyncio.to_thread(
                    exchange.fetch_ticker, symbol
                )
            
            # تخزين في الـ cache
            self.price_cache[symbol] = {
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['quoteVolume'],
                'change': ticker['percentage'],
                'timestamp': datetime.now()
            }
            
            return self.price_cache[symbol]
        except Exception as e:
            logger.error(f"❌ Error fetching ticker for {symbol}: {e}")
            return None
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """الحصول على السعر الحالي فقط"""
        ticker = await self.get_ticker(symbol)
        return ticker['price'] if ticker else None
    
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        """الحصول على أسعار عدة أزواج"""
        results = {}
        tasks = [self.get_ticker(symbol) for symbol in symbols]
        tickers = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, ticker in zip(symbols, tickers):
            if not isinstance(ticker, Exception) and ticker:
                results[symbol] = ticker
        
        return results
    
    async def get_all_symbols(self, market_type: str = 'spot') -> List[str]:
        """الحصول على جميع الأزواج المتاحة"""
        try:
            exchange = ccxt.bybit({'enableRateLimit': True})
            markets = await asyncio.to_thread(exchange.load_markets)
            
            symbols = []
            for symbol, market in markets.items():
                if market_type == 'spot' and market['spot']:
                    symbols.append(symbol)
                elif market_type == 'future' and (market['future'] or market['swap']):
                    symbols.append(symbol)
            
            return sorted(symbols)
        except Exception as e:
            logger.error(f"❌ Error fetching symbols: {e}")
            return []
    
    async def search_symbols(self, query: str, limit: int = 10) -> List[str]:
        """البحث عن أزواج معينة"""
        all_symbols = await self.get_all_symbols()
        query = query.upper()
        
        # بحث دقيق
        matches = [s for s in all_symbols if query in s]
        return matches[:limit]
    
    # ==================== الصفقات - Spot ====================
    
    async def create_spot_order(self, symbol: str, side: str, 
                               quantity: float, price: float = None) -> Optional[Dict]:
        """إنشاء أمر Spot"""
        if not self.exchange:
            logger.error("❌ Exchange not initialized")
            return None
        
        try:
            order_type = 'market' if price is None else 'limit'
            
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=price
            )
            
            logger.info(f"✅ Spot order created: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"❌ Error creating spot order: {e}")
            return None
    
    async def close_spot_position(self, symbol: str, side: str, 
                                 quantity: float) -> Optional[Dict]:
        """إغلاق صفقة Spot"""
        # عكس الاتجاه للإغلاق
        close_side = 'sell' if side == 'buy' else 'buy'
        return await self.create_spot_order(symbol, close_side, quantity)
    
    # ==================== الصفقات - Futures ====================
    
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية"""
        if not self.exchange:
            return False
        
        try:
            await asyncio.to_thread(
                self.exchange.set_leverage,
                leverage=leverage,
                symbol=symbol
            )
            logger.info(f"✅ Leverage set to {leverage}x for {symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ Error setting leverage: {e}")
            return False
    
    async def create_futures_order(self, symbol: str, side: str, 
                                  quantity: float, leverage: int = 1,
                                  stop_loss: float = None,
                                  take_profit: float = None,
                                  price: float = None) -> Optional[Dict]:
        """إنشاء أمر Futures"""
        if not self.exchange:
            logger.error("❌ Exchange not initialized")
            return None
        
        try:
            # تعيين الرافعة
            await self.set_leverage(symbol, leverage)
            
            # إنشاء الأمر
            order_type = 'market' if price is None else 'limit'
            params = {'leverage': leverage}
            
            # إضافة Stop Loss و Take Profit
            if stop_loss:
                params['stopLoss'] = {'triggerPrice': stop_loss}
            if take_profit:
                params['takeProfit'] = {'triggerPrice': take_profit}
            
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=price,
                params=params
            )
            
            logger.info(f"✅ Futures order created: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"❌ Error creating futures order: {e}")
            return None
    
    async def close_futures_position(self, symbol: str, side: str,
                                    quantity: float = None) -> Optional[Dict]:
        """إغلاق صفقة Futures"""
        if not self.exchange:
            return None
        
        try:
            # إغلاق السوق
            close_side = 'sell' if side == 'buy' else 'buy'
            
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol=symbol,
                type='market',
                side=close_side,
                amount=quantity,
                params={'reduce_only': True}
            )
            
            logger.info(f"✅ Futures position closed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"❌ Error closing futures position: {e}")
            return None
    
    # ==================== إدارة المخاطر ====================
    
    async def set_stop_loss(self, symbol: str, order_id: str, 
                           stop_price: float) -> bool:
        """تعيين Stop Loss"""
        if not self.exchange:
            return False
        
        try:
            await asyncio.to_thread(
                self.exchange.create_order,
                symbol=symbol,
                type='stop_market',
                side='sell',
                amount=0,  # سيتم تحديده من الصفقة
                params={'stopPrice': stop_price, 'triggerBy': 'LastPrice'}
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error setting stop loss: {e}")
            return False
    
    async def set_take_profit(self, symbol: str, order_id: str, 
                             take_price: float) -> bool:
        """تعيين Take Profit"""
        if not self.exchange:
            return False
        
        try:
            await asyncio.to_thread(
                self.exchange.create_order,
                symbol=symbol,
                type='take_profit_market',
                side='sell',
                amount=0,
                params={'stopPrice': take_price, 'triggerBy': 'LastPrice'}
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error setting take profit: {e}")
            return False
    
    # ==================== معلومات الحساب ====================
    
    async def get_balance(self) -> Optional[Dict]:
        """الحصول على رصيد الحساب"""
        if not self.exchange:
            return None
        
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            return balance
        except Exception as e:
            logger.error(f"❌ Error fetching balance: {e}")
            return None
    
    async def get_positions(self) -> List[Dict]:
        """الحصول على الصفقات المفتوحة"""
        if not self.exchange:
            return []
        
        try:
            positions = await asyncio.to_thread(
                self.exchange.fetch_positions
            )
            # تصفية الصفقات المفتوحة فقط
            return [p for p in positions if float(p.get('contracts', 0)) > 0]
        except Exception as e:
            logger.error(f"❌ Error fetching positions: {e}")
            return []
    
    async def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """الحصول على حالة أمر"""
        if not self.exchange:
            return None
        
        try:
            order = await asyncio.to_thread(
                self.exchange.fetch_order,
                id=order_id,
                symbol=symbol
            )
            return order
        except Exception as e:
            logger.error(f"❌ Error fetching order status: {e}")
            return None
    
    # ==================== حسابات ====================
    
    def calculate_position_size(self, balance: float, risk_percent: float,
                               entry_price: float, stop_loss: float,
                               leverage: int = 1) -> float:
        """حساب حجم الصفقة بناءً على المخاطرة"""
        risk_amount = balance * (risk_percent / 100)
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0
        
        position_size = (risk_amount / price_diff) * leverage
        return round(position_size, 8)
    
    def calculate_profit_loss(self, entry_price: float, current_price: float,
                             quantity: float, side: str, leverage: int = 1) -> Tuple[float, float]:
        """حساب الربح/الخسارة"""
        if side == 'buy':
            pnl = (current_price - entry_price) * quantity * leverage
            pnl_percent = ((current_price - entry_price) / entry_price) * 100 * leverage
        else:  # sell
            pnl = (entry_price - current_price) * quantity * leverage
            pnl_percent = ((entry_price - current_price) / entry_price) * 100 * leverage
        
        return round(pnl, 2), round(pnl_percent, 2)
    
    def calculate_liquidation_price(self, entry_price: float, leverage: int,
                                   side: str) -> float:
        """حساب سعر التصفية"""
        if side == 'buy':
            liq_price = entry_price * (1 - 1/leverage * 0.9)
        else:  # sell
            liq_price = entry_price * (1 + 1/leverage * 0.9)
        
        return round(liq_price, 8)


# إنشاء instance عام للأسعار العامة
public_api = BybitAPI()

