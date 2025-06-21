import telebot
import requests
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"), parse_mode=None)
API_KEY = os.getenv("API_KEY")
API_KEY_CRYPTO = os.getenv("API_KEY_CRYPTO")

@bot.message_handler(commands=['start'])
def start_function(message):
    bot.reply_to(message, "Привет, я бот-конвертер валют!\n"
                         "Чтобы начать конвертацию, используй команду:\n"
                         "/convertCrypto|/convertMoney <сумма> <из_валюты> <в_валюту>\n"
                         "Например: /convertCrypto|/convertMoney 100 USD RUB")

@bot.message_handler(commands=['help'])
def start_function(message):
    bot.reply_to(message, "Вот список моих команд:\n/convertCrypto|/convertMoney <число> <с_какой_валюты> <в_какую_валюту> - Конвертация валюты\n"
                          "/help - вывести список команд\n/button - Отобразить меню кнопок")

def get_crypto_rate(crypto1_value, crypto1, crypto2):
    api_url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={crypto1}{crypto2}"
    try:
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY_CRYPTO})
        response.raise_for_status()
        data = response.json()
        
        if "price" in data:
            price = float(data["price"])
            return crypto1_value * price, price
    except:
        pass
    
    api_url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={crypto2}{crypto1}"
    try:
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY_CRYPTO})
        response.raise_for_status()
        data = response.json()
        
        if "price" in data:
            inverse_price = float(data["price"])
            price = 1 / inverse_price
            return crypto1_value * price, price
    except:
        pass
    
    print(f"Не удалось получить курс для пары {crypto1}/{crypto2}")
    return None, None

@bot.message_handler(commands=['convertCrypto'])
def convertCrypto(message):
    try:
        args = message.text.split()[1:]

        if len(args) != 3:
            bot.reply_to(message, "Пожалуйста, используйте формат: /convertCrypto|/convertMoney <Сумма> <первая_валюта> <вторая_валюта>")
            return

        amount = float(args[0])
        from_value = args[1].upper()
        to_value = args[2].upper()

        rate, price_per_unit = get_crypto_rate(amount, from_value, to_value)

        if rate is not None:
            bot.reply_to(message, f"Результат конвертации: {amount} {from_value} = {rate:.8f} {to_value}\n"
                                  f"Курс: 1 {from_value} = {price_per_unit:.8f} {to_value}")
        else:
            bot.reply_to(message, "Не удалось получить курс валют. Попробуйте позже или проверьте название валюты.")
            
    except ValueError:
        bot.reply_to(message, "Ошибка: Неверный формат числа.")

    except Exception as e:
        bot.reply_to(message, f"Произошла неизвестная ошибка: {str(e)}")

def get_exchange_rate(from_currency, to_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get('result') == 'success':
            return data['conversion_rates'].get(to_currency)
        else:
            print(f"Ошибка API: {data.get('error-type', 'unknown error')}")
            return None

    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

@bot.message_handler(commands=['convertMoney'])
def convertMoney(message):
    try:
        args = message.text.split()[1:]

        if len(args) != 3:
            bot.reply_to(message, "Пожалуйста, используйте формат: /convertCrypto|/convertMoney <Сумма> <первая_валюта> <вторая_валюта>")
            return

        amount = float(args[0])
        from_value = args[1].upper()
        to_value = args[2].upper()

        rate = get_exchange_rate(from_value, to_value)
        if rate is not None:
            result = amount * rate
            bot.reply_to(message, 
                        f"Результат конвертации:\n"
                        f"{amount} {from_value} = {result:.2f} {to_value}\n"
                        f"Курс: 1 {from_value} = {rate:.4f} {to_value}")
        else:
            bot.reply_to(message, "Не удалось получить курс валют. Попробуйте позже или проверьте название валюты.")

    except ValueError:
        bot.reply_to(message, "Неправильный формат суммы. Используйте числа, например: 100")
    except IndexError:
        bot.reply_to(message, "Неправильный формат, вот пример команды: /convertCrypto|/convertMoney 100 USD RUB")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['button'])
def button_message(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Посмотреть список валют")
    item2=types.KeyboardButton("Посмотреть список криптовалют (из-за мало функциональной API можно использовать только указанные пары.)")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id,'Выберите что вам надо', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Посмотреть список валют")
def handle_button(message):
    bot.send_message(message.chat.id, "USD (Доллар США), AED (Дирхам ОАЭ), AFN (Афгани), ALL (Лек), AMD (Драм), ANG (Нидерландский антильский гульден), "
        "AOA (Кванза), ARS (Аргентинское песо), AUD (Австралийский доллар), AWG (Арубанский флорин), AZN (Азербайджанский манат), BAM (Конвертируемая марка), "
        "BBD (Барбадосский доллар), BDT (Така), BGN (Болгарский лев), BHD (Бахрейнский динар), BIF (Бурундийский франк), BMD (Бермудский доллар), BND (Брунейский доллар), "
        "BOB (Боливиано), BRL (Бразильский реал), BSD (Багамский доллар), BTN (Нгултрум), BWP (Пула), BYN (Белорусский рубль), BZD (Белизский доллар), "
        "CAD (Канадский доллар), CDF (Конголезский франк), CHF (Швейцарский франк), CLP (Чилийское песо), CNY (Юань), COP (Колумбийское песо), CRC (Коста-риканский колон), "
        "CUP (Кубинское песо), CVE (Эскудо Кабо-Верде), CZK (Чешская крона), DJF (Джибутийский франк), DKK (Датская крона), DOP (Доминиканское песо), "
        "DZD (Алжирский динар), EGP (Египетский фунт), ERN (Накфа), ETB (Эфиопский быр), EUR (Евро), FJD (Доллар Фиджи), FKP (Фунт Фолклендских островов), "
        "FOK (Фарерская крона), GBP (Фунт стерлингов), GEL (Лари), GGP (Гернсийский фунт), GHS (Седи), GIP (Гибралтарский фунт), GMD (Даласи), GNF (Гвинейский франк), "
        "GTQ (Кетсаль), GYD (Гайанский доллар), HKD (Гонконгский доллар), HNL (Лемпира), HRK (Хорватская куна), HTG (Гурд), HUF (Форинт), IDR (Индонезийская рупия), "
        "ILS (Новый израильский шекель), IMP (Мэнский фунт), INR (Индийская рупия), IQD (Иракский динар), IRR (Иранский риал), ISK (Исландская крона), "
        "JEP (Джерсийский фунт), JMD (Ямайский доллар), JOD (Иорданский динар), JPY (Иена), KES (Кенийский шиллинг), KGS (Сом), KHR (Риель), KID (Доллар Кирибати), "
        "KMF (Коморский франк), KRW (Южнокорейская вона), KWD (Кувейтский динар), KYD (Доллар Каймановых островов), KZT (Тенге), LAK (Кип), LBP (Ливанский фунт), "
        "LKR (Шри-ланкийская рупия), LRD (Либерийский доллар), LSL (Лоти), LYD (Ливийский динар), MAD (Марокканский дирхам), MDL (Молдавский лей), MGA (Малагасийский ариари), "
        "MKD (Македонский денар), MMK (Мьянманский кьят), MNT (Монгольский тугрик), MOP (Патака), MRU (Угия), MUR (Маврикийская рупия), MVR (Руфия), MWK (Малавийская квача), "
        "MXN (Мексиканское песо), MYR (Малайзийский ринггит), MZN (Мозамбикский метикал), NAD (Намибийский доллар), NGN (Найра), NIO (Кордоба), NOK (Норвежская крона), "
        "NPR (Непальская рупия), NZD (Новозеландский доллар), OMR (Оманский риал), PAB (Бальбоа), PEN (Соль), PGK (Кина), PHP (Филиппинское песо), PKR (Пакистанская рупия), "
        "PLN (Польский злотый), PYG (Гуарани), QAR (Катарский риал), RON (Румынский лей), RSD (Сербский динар), RUB (Российский рубль), RWF (Руандийский франк), "
        "SAR (Саудовский риял), SBD (Доллар Соломоновых Островов), SCR (Сейшельская рупия), SDG (Суданский фунт), SEK (Шведская крона), SGD (Сингапурский доллар), "
        "SHP (Фунт Святой Елены), SLE (Сьерра-леонский леоне), SLL (Сьерра-леонский леоне), SOS (Сомалийский шиллинг), SRD (Суринамский доллар), SSP (Южносуданский фунт), "
        "STN (Добра), SYP (Сирийский фунт), SZL (Лилангени), THB (Бат), TJS (Сомони), TMT (Туркменский манат), TND (Тунисский динар), TOP (Паанга), TRY (Турецкая лира), "
        "TTD (Доллар Тринидада и Тобаго), TVD (Доллар Тувалу), TWD (Новый тайваньский доллар), TZS (Танзанийский шиллинг), UAH (Гривна), UGX (Угандийский шиллинг), "
        "UYU (Уругвайское песо), UZS (Узбекский сум), VES (Венесуэльский боливар), VND (Вьетнамский донг), VUV (Вату), WST (Тала), XAF (Франк КФА BEAC), "
        "XCD (Восточно-карибский доллар), XCG (Восточно-карибский гульден), XDR (СДР), XOF (Франк КФА BCEAO), XPF (Тихоокеанский франк), YER (Йеменский риал), "
        "ZAR (Южноафриканский рэнд), ZMW (Замбийская квача), ZWL (Доллар Зимбабве)")

@bot.message_handler(func=lambda message: message.text == "Посмотреть список криптовалют (из-за мало функциональной API можно использовать только указанные пары.)")
def handle_button(message):
    bot.send_message(message.chat.id, "LTC BTC = Litecoin → Bitcoin\nETH BTC = Ethereum → Bitcoin\nXRP BTC = Ripple → Bitcoin\n"
        "BNB BTC = Binance Coin → Bitcoin\nADA BTC = Cardano → Bitcoin\nSOL BTC = Solana → Bitcoin\nDOGE BTC = Dogecoin → Bitcoin\n"
        "DOT BTC = Polkadot → Bitcoin\nSHIB BTC = Shiba Inu → Bitcoin\nMATIC BTC = Polygon → Bitcoin\nТакже можно использовать наоборот, то есть например: 10 DOT BTC и т.д.")

bot.infinity_polling()