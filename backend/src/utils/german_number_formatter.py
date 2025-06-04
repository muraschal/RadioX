#!/usr/bin/env python3

"""
Deutsche Zahlen-Formatierung für optimale ElevenLabs Aussprache
Basiert auf ElevenLabs Best Practices für deutsche TTS
"""

import re
from typing import Dict, List


class GermanNumberFormatter:
    """Formatiert Zahlen für optimale deutsche Aussprache in ElevenLabs"""
    
    def __init__(self):
        # Grundzahlen 0-19
        self.basic_numbers = {
            0: "null", 1: "eins", 2: "zwei", 3: "drei", 4: "vier", 5: "fünf",
            6: "sechs", 7: "sieben", 8: "acht", 9: "neun", 10: "zehn",
            11: "elf", 12: "zwölf", 13: "dreizehn", 14: "vierzehn", 15: "fünfzehn",
            16: "sechzehn", 17: "siebzehn", 18: "achtzehn", 19: "neunzehn"
        }
        
        # Zehnerzahlen
        self.tens = {
            20: "zwanzig", 30: "dreißig", 40: "vierzig", 50: "fünfzig",
            60: "sechzig", 70: "siebzig", 80: "achtzig", 90: "neunzig"
        }
        
        # Große Zahlen
        self.large_numbers = {
            100: "hundert", 1000: "tausend", 1000000: "Million", 1000000000: "Milliarde"
        }
        
        # Ordinalzahlen
        self.ordinals = {
            1: "erste", 2: "zweite", 3: "dritte", 4: "vierte", 5: "fünfte",
            6: "sechste", 7: "siebte", 8: "achte", 9: "neunte", 10: "zehnte",
            11: "elfte", 12: "zwölfte", 13: "dreizehnte", 14: "vierzehnte", 15: "fünfzehnte",
            16: "sechzehnte", 17: "siebzehnte", 18: "achtzehnte", 19: "neunzehnte", 20: "zwanzigste"
        }
        
        # Währungen
        self.currencies = {
            "$": "Dollar", "€": "Euro", "CHF": "Schweizer Franken", "£": "Pfund"
        }
        
        # Prozent und Einheiten
        self.units = {
            "%": "Prozent", "°C": "Grad Celsius", "km": "Kilometer", 
            "m": "Meter", "kg": "Kilogramm", "g": "Gramm"
        }
    
    def number_to_german_words(self, num: int) -> str:
        """Konvertiert eine Zahl in deutsche Wörter"""
        
        if num == 0:
            return "null"
        
        if num < 0:
            return f"minus {self.number_to_german_words(-num)}"
        
        if num < 20:
            return self.basic_numbers[num]
        
        if num < 100:
            tens_digit = (num // 10) * 10
            ones_digit = num % 10
            if ones_digit == 0:
                return self.tens[tens_digit]
            else:
                return f"{self.basic_numbers[ones_digit]}und{self.tens[tens_digit]}"
        
        if num < 1000:
            hundreds = num // 100
            remainder = num % 100
            result = ""
            if hundreds == 1:
                result = "einhundert"
            else:
                result = f"{self.basic_numbers[hundreds]}hundert"
            
            if remainder > 0:
                result += self.number_to_german_words(remainder)
            return result
        
        if num < 1000000:
            thousands = num // 1000
            remainder = num % 1000
            result = ""
            if thousands == 1:
                result = "eintausend"
            else:
                result = f"{self.number_to_german_words(thousands)}tausend"
            
            if remainder > 0:
                result += self.number_to_german_words(remainder)
            return result
        
        # Millionen und größer
        if num < 1000000000:
            millions = num // 1000000
            remainder = num % 1000000
            result = f"{self.number_to_german_words(millions)} "
            result += "Million" if millions == 1 else "Millionen"
            
            if remainder > 0:
                result += f" {self.number_to_german_words(remainder)}"
            return result
        
        # Milliarden
        billions = num // 1000000000
        remainder = num % 1000000000
        result = f"{self.number_to_german_words(billions)} "
        result += "Milliarde" if billions == 1 else "Milliarden"
        
        if remainder > 0:
            result += f" {self.number_to_german_words(remainder)}"
        return result
    
    def format_decimal(self, text: str) -> str:
        """Formatiert Dezimalzahlen für deutsche Aussprache"""
        
        # Bitcoin-Preise (z.B. $45,123.67)
        bitcoin_pattern = r'\$([0-9,]+)\.([0-9]+)'
        text = re.sub(bitcoin_pattern, lambda m: self._format_currency_amount(m.group(1), m.group(2), "Dollar"), text)
        
        # Euro-Preise (z.B. €1,234.56)
        euro_pattern = r'€([0-9,]+)\.([0-9]+)'
        text = re.sub(euro_pattern, lambda m: self._format_currency_amount(m.group(1), m.group(2), "Euro"), text)
        
        # Schweizer Franken
        chf_pattern = r'CHF\s*([0-9,]+)\.([0-9]+)'
        text = re.sub(chf_pattern, lambda m: self._format_currency_amount(m.group(1), m.group(2), "Schweizer Franken"), text)
        
        # Prozentangaben (z.B. +2.5%, -1.3%)
        percent_pattern = r'([+-]?)([0-9]+)\.([0-9]+)%'
        text = re.sub(percent_pattern, self._format_percentage, text)
        
        # Temperaturen (z.B. 15.5°C)
        temp_pattern = r'([0-9]+)\.([0-9]+)°C'
        text = re.sub(temp_pattern, self._format_temperature, text)
        
        # Allgemeine Dezimalzahlen (z.B. 3.14)
        decimal_pattern = r'([0-9]+)\.([0-9]+)'
        text = re.sub(decimal_pattern, self._format_general_decimal, text)
        
        return text
    
    def _format_currency_amount(self, whole_part: str, decimal_part: str, currency: str) -> str:
        """Formatiert Währungsbeträge"""
        
        # Entferne Kommas aus der ganzen Zahl
        whole_clean = whole_part.replace(',', '')
        whole_num = int(whole_clean)
        
        # Formatiere die ganze Zahl
        whole_words = self.number_to_german_words(whole_num)
        
        # Formatiere Dezimalstellen
        if len(decimal_part) == 2 and decimal_part != "00":
            decimal_num = int(decimal_part)
            decimal_words = self.number_to_german_words(decimal_num)
            if currency == "Dollar":
                return f"{whole_words} Dollar und {decimal_words} Cent"
            elif currency == "Euro":
                return f"{whole_words} Euro und {decimal_words} Cent"
            else:
                return f"{whole_words} {currency} und {decimal_words} Rappen"
        else:
            return f"{whole_words} {currency}"
    
    def _format_percentage(self, match) -> str:
        """Formatiert Prozentangaben"""
        sign = match.group(1)
        whole = int(match.group(2))
        decimal = match.group(3)
        
        whole_words = self.number_to_german_words(whole)
        
        if decimal and decimal != "0":
            decimal_num = int(decimal)
            decimal_words = self.number_to_german_words(decimal_num)
            result = f"{whole_words} Komma {decimal_words} Prozent"
        else:
            result = f"{whole_words} Prozent"
        
        if sign == "+":
            return f"plus {result}"
        elif sign == "-":
            return f"minus {result}"
        else:
            return result
    
    def _format_temperature(self, match) -> str:
        """Formatiert Temperaturen"""
        whole = int(match.group(1))
        decimal = match.group(2)
        
        whole_words = self.number_to_german_words(whole)
        
        if decimal and decimal != "0":
            decimal_num = int(decimal)
            decimal_words = self.number_to_german_words(decimal_num)
            return f"{whole_words} Komma {decimal_words} Grad Celsius"
        else:
            return f"{whole_words} Grad Celsius"
    
    def _format_general_decimal(self, match) -> str:
        """Formatiert allgemeine Dezimalzahlen"""
        whole = int(match.group(1))
        decimal = match.group(2)
        
        whole_words = self.number_to_german_words(whole)
        decimal_words = " ".join([self.basic_numbers[int(d)] for d in decimal])
        
        return f"{whole_words} Komma {decimal_words}"
    
    def format_integers(self, text: str) -> str:
        """Formatiert ganze Zahlen für deutsche Aussprache"""
        
        # Jahre (z.B. 2024)
        year_pattern = r'\b(19|20)([0-9]{2})\b'
        text = re.sub(year_pattern, self._format_year, text)
        
        # Uhrzeiten (z.B. 7:00, 08:30)
        time_pattern = r'\b([0-9]{1,2}):([0-9]{2})\b'
        text = re.sub(time_pattern, self._format_time, text)
        
        # Große Zahlen mit Kommas (z.B. 1,234,567)
        large_number_pattern = r'\b([0-9]{1,3}(?:,[0-9]{3})+)\b'
        text = re.sub(large_number_pattern, self._format_large_number, text)
        
        # Einfache ganze Zahlen (z.B. 42)
        simple_number_pattern = r'\b([0-9]+)\b'
        text = re.sub(simple_number_pattern, self._format_simple_number, text)
        
        return text
    
    def _format_year(self, match) -> str:
        """Formatiert Jahreszahlen"""
        century = match.group(1)
        year_end = match.group(2)
        
        full_year = int(century + year_end)
        return self.number_to_german_words(full_year)
    
    def _format_time(self, match) -> str:
        """Formatiert Uhrzeiten"""
        hour = int(match.group(1))
        minute = int(match.group(2))
        
        if minute == 0:
            if hour == 0:
                return "Mitternacht"
            elif hour == 12:
                return "Mittag"
            else:
                hour_words = self.number_to_german_words(hour)
                return f"{hour_words} Uhr"
        elif minute == 30:
            if hour == 23:
                return "halb Mitternacht"
            else:
                return f"halb {self.number_to_german_words(hour + 1)}"
        elif minute == 15:
            hour_words = self.number_to_german_words(hour)
            return f"Viertel nach {hour_words}"
        elif minute == 45:
            if hour == 23:
                return "Viertel vor Mitternacht"
            else:
                return f"Viertel vor {self.number_to_german_words(hour + 1)}"
        else:
            hour_words = self.number_to_german_words(hour)
            minute_words = self.number_to_german_words(minute)
            return f"{hour_words} Uhr {minute_words}"
    
    def _format_large_number(self, match) -> str:
        """Formatiert große Zahlen mit Kommas"""
        number_str = match.group(1).replace(',', '')
        number = int(number_str)
        return self.number_to_german_words(number)
    
    def _format_simple_number(self, match) -> str:
        """Formatiert einfache ganze Zahlen"""
        number = int(match.group(1))
        
        # Sehr große Zahlen (über 9999) werden als Ziffernfolge gesprochen
        if number > 9999:
            return " ".join([self.basic_numbers[int(d)] for d in str(number)])
        else:
            return self.number_to_german_words(number)
    
    def format_ordinals(self, text: str) -> str:
        """Formatiert Ordinalzahlen"""
        
        # Ordinalzahlen mit Punkt (z.B. 1., 2., 3.)
        ordinal_pattern = r'\b([0-9]+)\.\b'
        text = re.sub(ordinal_pattern, self._format_ordinal, text)
        
        return text
    
    def _format_ordinal(self, match) -> str:
        """Formatiert eine Ordinalzahl"""
        number = int(match.group(1))
        
        if number in self.ordinals:
            return self.ordinals[number]
        elif number <= 20:
            base = self.number_to_german_words(number)
            return f"{base}te"
        else:
            base = self.number_to_german_words(number)
            return f"{base}ste"
    
    def format_text_for_elevenlabs(self, text: str) -> str:
        """Hauptfunktion: Formatiert Text für optimale deutsche ElevenLabs Aussprache"""
        
        print("🔢 FORMATIERE ZAHLEN FÜR DEUTSCHE AUSSPRACHE")
        print("-" * 40)
        print(f"   📝 Original: {text[:100]}...")
        
        # 1. Formatiere Dezimalzahlen (Währungen, Prozente, etc.)
        text = self.format_decimal(text)
        
        # 2. Formatiere Ordinalzahlen
        text = self.format_ordinals(text)
        
        # 3. Formatiere ganze Zahlen
        text = self.format_integers(text)
        
        # 4. Spezielle Abkürzungen
        text = self.format_abbreviations(text)
        
        print(f"   ✅ Formatiert: {text[:100]}...")
        print(f"   🎙️ Optimiert für ElevenLabs deutsche TTS")
        
        return text
    
    def format_abbreviations(self, text: str) -> str:
        """Formatiert häufige Abkürzungen für deutsche Aussprache"""
        
        abbreviations = {
            "z.B.": "zum Beispiel",
            "d.h.": "das heißt",
            "u.a.": "unter anderem",
            "etc.": "et cetera",
            "bzw.": "beziehungsweise",
            "ca.": "circa",
            "inkl.": "inklusive",
            "exkl.": "exklusive",
            "ggf.": "gegebenenfalls",
            "evtl.": "eventuell",
            "max.": "maximal",
            "min.": "minimal",
            "Nr.": "Nummer",
            "Tel.": "Telefon",
            "Str.": "Straße",
            "Dr.": "Doktor",
            "Prof.": "Professor",
            "CHF": "Schweizer Franken",
            "USD": "US-Dollar",
            "EUR": "Euro",
            "BTC": "Bitcoin",
            "AI": "Künstliche Intelligenz",
            "KI": "Künstliche Intelligenz",
            "CEO": "Chief Executive Officer",
            "CFO": "Chief Financial Officer",
            "CTO": "Chief Technology Officer",
            "API": "Application Programming Interface",
            "URL": "Uniform Resource Locator",
            "HTML": "HyperText Markup Language",
            "CSS": "Cascading Style Sheets",
            "JS": "JavaScript",
            "SQL": "Structured Query Language"
        }
        
        for abbrev, full_form in abbreviations.items():
            # Verwende Wortgrenzen für präzise Ersetzung
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, full_form, text, flags=re.IGNORECASE)
        
        return text


def test_german_number_formatter():
    """Testet den German Number Formatter"""
    
    formatter = GermanNumberFormatter()
    
    test_cases = [
        "Bitcoin steht bei $45,123.67 (+2.5%)",
        "Die Temperatur beträgt 15.5°C",
        "Am 1. Januar 2024 um 7:30 Uhr",
        "Zürich hat ca. 434,335 Einwohner",
        "Das kostet CHF 1,250.00",
        "Die 3. Ausgabe erscheint z.B. am 15.",
        "Dr. Schmidt hat Tel. 044 123 45 67"
    ]
    
    print("🧪 TESTE GERMAN NUMBER FORMATTER")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. TEST:")
        print(f"   Original:   {test_text}")
        formatted = formatter.format_text_for_elevenlabs(test_text)
        print(f"   Formatiert: {formatted}")


if __name__ == "__main__":
    test_german_number_formatter() 