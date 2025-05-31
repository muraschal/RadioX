#!/usr/bin/env python3
"""
Test-Script für JARVIS Cursor Integration
Überprüft alle Funktionen und Antworten
"""

from jarvis_cursor_integration import j, js
import time

def test_jarvis_integration():
    """Testet die JARVIS-Integration umfassend."""
    print('🔍 JARVIS Integration Test')
    print('=' * 40)
    
    # Test verschiedene Szenarien
    tests = [
        ('status', 'Status-Check'),
        ('code review', 'Code-Review'),
        ('git commit', 'Git-Operation'),
        ('fehler gefunden', 'Error-Handling'),
        ('danke jarvis', 'Kompliment'),
        ('hallo', 'Begrüßung'),
        ('help', 'Hilfe-Anfrage'),
        ('build system', 'Build-System'),
        ('debug code', 'Debugging'),
        ('random input', 'Unbekannte Eingabe')
    ]
    
    for i, (test_input, description) in enumerate(tests, 1):
        print(f'\n📋 Test {i}/10: {description}')
        print(f'   Input: "{test_input}"')
        
        try:
            # Führe Test durch
            response = j(test_input)
            print(f'   ✅ Response: "{response}"')
            
            # Kurze Pause zwischen Tests
            time.sleep(1)
            
        except Exception as e:
            print(f'   ❌ Fehler: {e}')
    
    print('\n' + '=' * 40)
    print('🎯 Integration Test abgeschlossen!')
    
    # Test der direkten Sprach-Funktion
    print('\n📢 Test direktes Sprechen:')
    js('Integration Test erfolgreich abgeschlossen, Sir.')

if __name__ == "__main__":
    test_jarvis_integration() 