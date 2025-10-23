"""
نظام المحفظة المتقدم - يربط جميع الصفقات ويعرض العملات بوضوح
يدعم الحسابات التجريبية والحقيقية مع تحديث فوري
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from database import db_manager
from user_manager import user_manager
from real_account_manager import RealAccountManager

logger = logging.getLogger(__name__)

class AdvancedPortfolioManager:
    """مدير المحفظة المتقدم - يربط جميع الصفقات ويعرض العملات بوضوح"""
    
    def __init__(self):
        self.real_account_manager = RealAccountManager()
        logger.info("🚀 تم تهيئة نظام المحفظة المتقدم")
    
    async def get_comprehensive_portfolio(self, user_id: int) -> Dict[str, Any]:
        """الحصول على المحفظة الشاملة للمستخدم"""
        try:
            logger.info(f"🔍 جاري تحضير المحفظة الشاملة للمستخدم {user_id}")
            
            # الحصول على إعدادات المستخدم
            user_data = user_manager.get_user(user_id)
            if not user_data:
                return {"error": "لم يتم العثور على بيانات المستخدم"}
            
            account_type = user_data.get('account_type', 'demo')
            market_type = user_data.get('market_type', 'spot')
            
            logger.info(f"📊 نوع الحساب: {account_type}, نوع السوق: {market_type}")
            
            if account_type == 'demo':
                return await self._get_demo_portfolio(user_id, market_type)
            else:
                return await self._get_real_portfolio(user_id, market_type)
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على المحفظة الشاملة: {e}")
            return {"error": f"خطأ في تحضير المحفظة: {str(e)}"}
    
    async def _get_demo_portfolio(self, user_id: int, market_type: str) -> Dict[str, Any]:
        """الحصول على المحفظة التجريبية مع ربط كامل بالصفقات"""
        try:
            logger.info(f"🎯 تحضير المحفظة التجريبية للمستخدم {user_id}")
            
            portfolio = {
                "type": "demo",
                "market_type": market_type,
                "spot_currencies": {},
                "futures_positions": {},
                "total_value": 0,
                "last_update": datetime.now().isoformat()
            }
            
            # الحصول على جميع الصفقات من user_positions
            user_positions = user_manager.user_positions.get(user_id, {})
            logger.info(f"🔍 DEBUG: الصفقات الموجودة للمستخدم {user_id}: {len(user_positions)} صفقة")
            
            for position_id, position_info in user_positions.items():
                logger.info(f"🔍 DEBUG: معالجة صفقة {position_id}: {position_info}")
                
                if position_info.get('account_type') != 'demo':
                    logger.info(f"🔍 DEBUG: تخطي صفقة {position_id} - نوع الحساب: {position_info.get('account_type')}")
                    continue
                
                pos_market_type = position_info.get('market_type', 'spot')
                logger.info(f"🔍 DEBUG: معالجة صفقة {position_id} - نوع السوق: {pos_market_type}")
                
                if pos_market_type == 'spot':
                    await self._process_demo_spot_position(portfolio, position_info)
                elif pos_market_type == 'futures':
                    await self._process_demo_futures_position(portfolio, position_info)
            
            # حساب إجمالي قيمة المحفظة
            portfolio["total_value"] = sum(
                currency["total_value"] for currency in portfolio["spot_currencies"].values()
            ) + sum(
                position["total_value"] for position in portfolio["futures_positions"].values()
            )
            
            logger.info(f"✅ تم تحضير المحفظة التجريبية: {len(portfolio['spot_currencies'])} عملات سبوت، {len(portfolio['futures_positions'])} صفقات فيوتشر")
            logger.info(f"🔍 DEBUG: تفاصيل المحفظة النهائية: {portfolio}")
            return portfolio
            
        except Exception as e:
            logger.error(f"❌ خطأ في المحفظة التجريبية: {e}")
            return {"error": f"خطأ في المحفظة التجريبية: {str(e)}"}
    
    async def _process_demo_spot_position(self, portfolio: Dict, position_info: Dict):
        """معالجة صفقة سبوت تجريبية"""
        try:
            symbol = position_info.get('symbol', '')
            base_currency = self._extract_base_currency(symbol)
            logger.info(f"🔍 DEBUG: معالجة صفقة سبوت {symbol} -> العملة الأساسية: {base_currency}")
            
            if not base_currency:
                logger.warning(f"⚠️ DEBUG: لم يتم العثور على العملة الأساسية للرمز {symbol}")
                return
            
            amount = position_info.get('amount', 0)
            entry_price = position_info.get('entry_price', 0)
            current_price = position_info.get('current_price', entry_price)
            
            logger.info(f"🔍 DEBUG: بيانات الصفقة - الكمية: {amount}, سعر الدخول: {entry_price}, السعر الحالي: {current_price}")
            
            if amount <= 0:
                logger.warning(f"⚠️ DEBUG: كمية الصفقة صفر أو سالبة: {amount}")
                return
            
            if base_currency in portfolio["spot_currencies"]:
                # تجميع مع العملة الموجودة
                existing = portfolio["spot_currencies"][base_currency]
                
                # حساب متوسط السعر المرجح
                total_amount = existing["total_amount"] + amount
                weighted_price = ((existing["total_amount"] * existing["average_price"]) + 
                                (amount * entry_price)) / total_amount
                
                existing.update({
                    "total_amount": total_amount,
                    "average_price": weighted_price,
                    "current_price": current_price,
                    "total_value": total_amount * current_price,
                    "profit_loss": (current_price - weighted_price) * total_amount,
                    "profit_percent": ((current_price - weighted_price) / weighted_price * 100) if weighted_price > 0 else 0,
                    "last_update": datetime.now().isoformat()
                })
            else:
                # عملة جديدة
                total_value = amount * current_price
                profit_loss = (current_price - entry_price) * amount
                profit_percent = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                
                portfolio["spot_currencies"][base_currency] = {
                    "symbol": symbol,
                    "total_amount": amount,
                    "average_price": entry_price,
                    "current_price": current_price,
                    "total_value": total_value,
                    "profit_loss": profit_loss,
                    "profit_percent": profit_percent,
                    "last_update": datetime.now().isoformat()
                }
                logger.info(f"✅ DEBUG: تم إضافة عملة جديدة {base_currency} إلى المحفظة")
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة صفقة سبوت: {e}")
    
    async def _process_demo_futures_position(self, portfolio: Dict, position_info: Dict):
        """معالجة صفقة فيوتشر تجريبية"""
        try:
            symbol = position_info.get('symbol', '')
            side = position_info.get('side', 'buy')
            amount = position_info.get('amount', 0)
            entry_price = position_info.get('entry_price', 0)
            current_price = position_info.get('current_price', entry_price)
            
            position_key = f"{symbol}_{side}"
            
            if position_key in portfolio["futures_positions"]:
                # تجميع مع الصفقة الموجودة
                existing = portfolio["futures_positions"][position_key]
                
                # حساب متوسط السعر المرجح
                total_amount = existing["total_amount"] + amount
                weighted_price = ((existing["total_amount"] * existing["average_price"]) + 
                                (amount * entry_price)) / total_amount
                
                existing.update({
                    "total_amount": total_amount,
                    "average_price": weighted_price,
                    "current_price": current_price,
                    "total_value": total_amount * current_price,
                    "profit_loss": (current_price - weighted_price) * total_amount if side == 'buy' else (weighted_price - current_price) * total_amount,
                    "last_update": datetime.now().isoformat()
                })
            else:
                # صفقة جديدة
                total_value = amount * current_price
                profit_loss = (current_price - entry_price) * amount if side == 'buy' else (entry_price - current_price) * amount
                
                portfolio["futures_positions"][position_key] = {
                    "symbol": symbol,
                    "side": side,
                    "total_amount": amount,
                    "average_price": entry_price,
                    "current_price": current_price,
                    "total_value": total_value,
                    "profit_loss": profit_loss,
                    "last_update": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة صفقة فيوتشر: {e}")
    
    async def _get_real_portfolio(self, user_id: int, market_type: str) -> Dict[str, Any]:
        """الحصول على المحفظة الحقيقية من API"""
        try:
            logger.info(f"🎯 تحضير المحفظة الحقيقية للمستخدم {user_id}")
            
            portfolio = {
                "type": "real",
                "market_type": market_type,
                "spot_currencies": {},
                "futures_positions": {},
                "total_value": 0,
                "last_update": datetime.now().isoformat()
            }
            
            # الحصول على مفاتيح API
            user_data = user_manager.get_user(user_id)
            api_key = user_data.get('api_key') if user_data else None
            api_secret = user_data.get('api_secret') if user_data else None
            
            if not api_key or not api_secret:
                portfolio["error"] = "مفاتيح API غير موجودة"
                return portfolio
            
            # الحصول على العملات من API
            if market_type == 'spot':
                await self._fetch_real_spot_currencies(portfolio, api_key, api_secret)
            
            # الحصول على صفقات الفيوتشر من API
            await self._fetch_real_futures_positions(portfolio, api_key, api_secret)
            
            # حساب إجمالي قيمة المحفظة
            portfolio["total_value"] = sum(
                currency["total_value"] for currency in portfolio["spot_currencies"].values()
            ) + sum(
                position["total_value"] for position in portfolio["futures_positions"].values()
            )
            
            logger.info(f"✅ تم تحضير المحفظة الحقيقية: {len(portfolio['spot_currencies'])} عملات سبوت، {len(portfolio['futures_positions'])} صفقات فيوتشر")
            return portfolio
            
        except Exception as e:
            logger.error(f"❌ خطأ في المحفظة الحقيقية: {e}")
            return {"error": f"خطأ في المحفظة الحقيقية: {str(e)}"}
    
    async def _fetch_real_spot_currencies(self, portfolio: Dict, api_key: str, api_secret: str):
        """جلب العملات الحقيقية من API"""
        try:
            # الحصول على الرصيد من Bybit
            balance_data = self.real_account_manager.get_account_balance(api_key, api_secret, 'spot')
            
            if balance_data and 'result' in balance_data:
                for coin_data in balance_data['result']['list']:
                    coin = coin_data['coin']
                    free_amount = float(coin_data['free'])
                    locked_amount = float(coin_data['locked'])
                    total_amount = free_amount + locked_amount
                    
                    if total_amount > 0:
                        # الحصول على السعر الحالي
                        ticker_data = self.real_account_manager.get_ticker_price(f"{coin}USDT")
                        current_price = float(ticker_data['result']['price']) if ticker_data else 0
                        
                        if current_price > 0:
                            portfolio["spot_currencies"][coin] = {
                                "symbol": f"{coin}USDT",
                                "total_amount": total_amount,
                                "free_amount": free_amount,
                                "locked_amount": locked_amount,
                                "current_price": current_price,
                                "total_value": total_amount * current_price,
                                "last_update": datetime.now().isoformat()
                            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب العملات الحقيقية: {e}")
    
    async def _fetch_real_futures_positions(self, portfolio: Dict, api_key: str, api_secret: str):
        """جلب صفقات الفيوتشر الحقيقية من API"""
        try:
            # الحصول على الصفقات المفتوحة من Bybit
            positions_data = self.real_account_manager.get_open_positions(api_key, api_secret)
            
            if positions_data and 'result' in positions_data:
                for position_data in positions_data['result']['list']:
                    symbol = position_data['symbol']
                    side = position_data['side']
                    size = float(position_data['size'])
                    entry_price = float(position_data['entryPrice'])
                    mark_price = float(position_data['markPrice'])
                    unrealized_pnl = float(position_data['unrealisedPnl'])
                    
                    if size > 0:
                        position_key = f"{symbol}_{side}"
                        
                        portfolio["futures_positions"][position_key] = {
                            "symbol": symbol,
                            "side": side,
                            "total_amount": size,
                            "average_price": entry_price,
                            "current_price": mark_price,
                            "total_value": size * mark_price,
                            "profit_loss": unrealized_pnl,
                            "last_update": datetime.now().isoformat()
                        }
                
        except Exception as e:
            logger.error(f"❌ خطأ في جلب صفقات الفيوتشر: {e}")
    
    def _extract_base_currency(self, symbol: str) -> str:
        """استخراج العملة الأساسية من الرمز"""
        if symbol.endswith('USDT'):
            return symbol.replace('USDT', '')
        elif symbol.endswith('BTC'):
            return symbol.replace('BTC', '')
        elif symbol.endswith('ETH'):
            return symbol.replace('ETH', '')
        else:
            return symbol.split('/')[0] if '/' in symbol else symbol
    
    async def format_portfolio_message(self, portfolio: Dict[str, Any]) -> str:
        """تنسيق رسالة المحفظة"""
        try:
            if "error" in portfolio:
                return f"❌ {portfolio['error']}"
            
            portfolio_type = portfolio.get("type", "unknown")
            market_type = portfolio.get("market_type", "spot")
            
            if portfolio_type == "demo":
                return await self._format_demo_portfolio_message(portfolio, market_type)
            else:
                return await self._format_real_portfolio_message(portfolio, market_type)
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق رسالة المحفظة: {e}")
            return f"❌ خطأ في تنسيق المحفظة: {str(e)}"
    
    async def _format_demo_portfolio_message(self, portfolio: Dict, market_type: str) -> str:
        """تنسيق رسالة المحفظة التجريبية"""
        try:
            message = f"💰 المحفظة التجريبية ({market_type.upper()}):\n\n"
            
            # عرض عملات السبوت
            if portfolio["spot_currencies"]:
                message += "🟢 **عملات السبوت:**\n"
                for currency, data in portfolio["spot_currencies"].items():
                    profit_emoji = "📈" if data["profit_loss"] >= 0 else "📉"
                    message += f"{profit_emoji} **{currency}**\n"
                    message += f"   💰 عدد العملات: {data['total_amount']:.6f} {currency}\n"
                    message += f"   💲 متوسط السعر: {data['average_price']:.2f} USDT\n"
                    message += f"   💲 السعر الحالي: {data['current_price']:.2f} USDT\n"
                    message += f"   📊 القيمة الإجمالية: {data['total_value']:.2f} USDT\n"
                    message += f"   ⬆️ الربح/الخسارة: {data['profit_loss']:.2f} USDT ({data['profit_percent']:+.2f}%)\n\n"
            
            # عرض صفقات الفيوتشر
            if portfolio["futures_positions"]:
                message += "⚡ **صفقات الفيوتشر:**\n"
                for position_key, data in portfolio["futures_positions"].items():
                    profit_emoji = "📈" if data["profit_loss"] >= 0 else "📉"
                    side_emoji = "🟢" if data["side"] == "buy" else "🔴"
                    message += f"{profit_emoji} {side_emoji} **{data['symbol']}** ({data['side'].upper()})\n"
                    message += f"   💰 الحجم: {data['total_amount']:.6f}\n"
                    message += f"   💲 متوسط السعر: {data['average_price']:.2f} USDT\n"
                    message += f"   💲 السعر الحالي: {data['current_price']:.2f} USDT\n"
                    message += f"   📊 القيمة الإجمالية: {data['total_value']:.2f} USDT\n"
                    message += f"   ⬆️ الربح/الخسارة: {data['profit_loss']:.2f} USDT\n\n"
            
            if not portfolio["spot_currencies"] and not portfolio["futures_positions"]:
                message += "📭 لا توجد عملات أو صفقات في المحفظة حالياً\n\n"
                message += "💡 قم بشراء عملات في سوق Spot أو فتح صفقات فيوتشر لتظهر هنا"
            else:
                message += f"💎 **إجمالي قيمة المحفظة: {portfolio['total_value']:.2f} USDT**"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق المحفظة التجريبية: {e}")
            return f"❌ خطأ في تنسيق المحفظة التجريبية: {str(e)}"
    
    async def _format_real_portfolio_message(self, portfolio: Dict, market_type: str) -> str:
        """تنسيق رسالة المحفظة الحقيقية"""
        try:
            message = f"💰 المحفظة الحقيقية ({market_type.upper()}):\n\n"
            
            # عرض عملات السبوت
            if portfolio["spot_currencies"]:
                message += "🟢 **عملات السبوت:**\n"
                for currency, data in portfolio["spot_currencies"].items():
                    message += f"💰 **{currency}**\n"
                    message += f"   💰 عدد العملات الإجمالي: {data['total_amount']:.6f} {currency}\n"
                    message += f"   💳 متاح للتداول: {data['free_amount']:.6f} {currency}\n"
                    message += f"   🔒 مقفل في صفقات: {data['locked_amount']:.6f} {currency}\n"
                    message += f"   💲 السعر الحالي: {data['current_price']:.2f} USDT\n"
                    message += f"   📊 القيمة الإجمالية: {data['total_value']:.2f} USDT\n\n"
            
            # عرض صفقات الفيوتشر
            if portfolio["futures_positions"]:
                message += "⚡ **صفقات الفيوتشر:**\n"
                for position_key, data in portfolio["futures_positions"].items():
                    profit_emoji = "📈" if data["profit_loss"] >= 0 else "📉"
                    side_emoji = "🟢" if data["side"] == "buy" else "🔴"
                    message += f"{profit_emoji} {side_emoji} **{data['symbol']}** ({data['side'].upper()})\n"
                    message += f"   💰 الحجم: {data['total_amount']:.6f}\n"
                    message += f"   💲 متوسط السعر: {data['average_price']:.2f} USDT\n"
                    message += f"   💲 السعر الحالي: {data['current_price']:.2f} USDT\n"
                    message += f"   📊 القيمة الإجمالية: {data['total_value']:.2f} USDT\n"
                    message += f"   ⬆️ الربح/الخسارة: {data['profit_loss']:.2f} USDT\n\n"
            
            if not portfolio["spot_currencies"] and not portfolio["futures_positions"]:
                message += "📭 لا توجد عملات أو صفقات في المحفظة حالياً\n\n"
                message += "💡 قم بإيداع عملات في حسابك على المنصة أو فتح صفقات فيوتشر"
            else:
                message += f"💎 **إجمالي قيمة المحفظة: {portfolio['total_value']:.2f} USDT**"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق المحفظة الحقيقية: {e}")
            return f"❌ خطأ في تنسيق المحفظة الحقيقية: {str(e)}"

# إنشاء مثيل عام للمدير
advanced_portfolio_manager = AdvancedPortfolioManager()
