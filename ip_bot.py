#To work, you will need a BOT TOKEN, you can get it in https://t.me/BotFather
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

import stealth_requests
from ipwhois import IPWhois
from fake_useragent import UserAgent

TOKEN = "your token"

dp = Dispatcher()
ua = UserAgent()
headers = {'User-Agent': ua.random}

def format_ip_info(ip):
    url = f'https://ipapi.co/{ip}/json/'
    try:
        info = stealth_requests.get(url, headers=headers).json()
        if 'error' in info:
            return f"Error: {info['reason']}"

        keys_order = [
            'ip',
            'city',
            'region',
            'region_code',
            'country_name',
            'country_code',
            'country_capital',
            'country_tld',
            'continent_code',
            'in_eu',
            'postal',
            'latitude',
            'longitude',
            'timezone',
            'utc_offset',
            'country_calling_code',
            'currency',
            'currency_name',
            'languages',
            'country_area',
            'country_population'
        ]

        output_lines = []
        for key in keys_order:
            value = info.get(key, 'N/A')
            output_lines.append(f"{key.replace('_', ' ').title()}: {value}")

        return '\n'.join(output_lines)

    except Exception as e:
        return f"An error occurred while fetching IP info: {str(e)}"

def format_whois_info(ip):
    try:
        obj = IPWhois(ip)
        results = obj.lookup_rdap()

        output_lines = []
        output_lines.append(f"Query: {results.get('query', 'None')}")
        output_lines.append(f"ASN Registry: {results.get('asn_registry', 'None')}")
        output_lines.append(f"ASN: {results.get('asn', 'None')}")
        output_lines.append(f"ASN CIDR: {results.get('asn_cidr', 'None')}")
        output_lines.append(f"ASN Country Code: {results.get('asn_country_code', 'None')}")
        output_lines.append(f"ASN Date: {results.get('asn_date', 'None')}")
        output_lines.append(f"ASN Description: {results.get('asn_description', 'None')}")

        network_info = results.get('network', {})
        output_lines.append("Network Information:")
        output_lines.append(f"  Handle: {network_info.get('handle', 'None')}")
        output_lines.append(f"  Status: {network_info.get('status', 'None')}")
        output_lines.append(f"  Start Address: {network_info.get('start_address', 'None')}")
        output_lines.append(f"  End Address: {network_info.get('end_address', 'None')}")
        output_lines.append(f"  CIDR: {network_info.get('cidr', 'None')}")
        output_lines.append(f"  IP Version: {network_info.get('ip_version', 'None')}")
        output_lines.append(f"  Type: {network_info.get('type', 'None')}")
        output_lines.append(f"  Name: {network_info.get('name', 'None')}")
        output_lines.append(f"  Country: {network_info.get('country', 'None')}")

        events = network_info.get('events', [])
        output_lines.append("Events:")
        if events:
            for event in events:
                output_lines.append(f"  Action: {event.get('action', 'None')}, Timestamp: {event.get('timestamp', 'None')}")
        else:
            output_lines.append("  None")

        objects_info = results.get('objects', {})
        output_lines.append("Objects:")
        if objects_info:
            for key, obj in objects_info.items():
                output_lines.append(f"  {key}:")
                output_lines.append(f"    Handle: {obj.get('handle', 'None')}")
                output_lines.append(f"    Status: {obj.get('status', 'None')}")
                output_lines.append(f"    Links: {obj.get('links', 'None')}")
                output_lines.append(f"    Events:")
                for event in obj.get('events', []):
                    output_lines.append(f"      Action: {event.get('action', 'None')}, Timestamp: {event.get('timestamp', 'None')}")
                output_lines.append(f"    Contact Name: {obj.get('contact', {}).get('name', 'None')}")
                output_lines.append(f"    Contact Address: {obj.get('contact', {}).get('address', 'None')}")
        else:
            output_lines.append("  None")

        return '\n'.join(output_lines)

    except Exception as e:
        return f"An error occurred while fetching WHOIS info: {str(e)}"

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Send me an IP address to get information.")

@dp.message()
async def get_ip_info(message: Message) -> None:
    ip = message.text.strip()
    formatted_info = format_ip_info(ip)
    whois_info = format_whois_info(ip)

    response = f"IP:\n{formatted_info}\n\nWHOIS:\n{whois_info}"
    await message.answer(response)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
