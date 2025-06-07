#!/bin/bash
# 🎙️ RadioX Show History Aliases
# Füge diese zu deiner ~/.bashrc oder ~/.zshrc hinzu

# Basis-Pfad
RADIOX_PATH="D:/DEV/muraschal/RadioX/backend"

# 🎯 Show-Befehle
alias show-latest="cd $RADIOX_PATH && python cli/cli_show_history.py latest"
alias show-script="cd $RADIOX_PATH && python cli/cli_show_history.py latest --script"
alias show-list="cd $RADIOX_PATH && python cli/cli_show_history.py list"
alias show-last5="cd $RADIOX_PATH && python cli/cli_show_history.py list 5"

# 🎭 Funktionen für spezifische Shows
show-get() {
    if [ -z "$1" ]; then
        echo "❌ Session ID erforderlich: show-get <session_id>"
        return 1
    fi
    cd $RADIOX_PATH && python cli/cli_show_history.py show "$1"
}

show-read() {
    if [ -z "$1" ]; then
        echo "❌ Session ID erforderlich: show-read <session_id>"
        return 1
    fi
    cd $RADIOX_PATH && python cli/cli_show_history.py script "$1"
}

# 🚀 RadioX Master Befehle
alias radiox-generate="cd $RADIOX_PATH && python production/radiox_master.py --action generate_broadcast"
alias radiox-status="cd $RADIOX_PATH && python production/radiox_master.py --action system_status"
alias radiox-test="cd $RADIOX_PATH && python cli/cli_master.py test"

# 📊 Schema Befehle
alias schema-info="cd $RADIOX_PATH && python cli/cli_schema.py info"
alias schema-test="cd $RADIOX_PATH && python cli/cli_schema.py test"

echo "🎙️ RadioX Show Aliases geladen!"
echo ""
echo "📋 VERFÜGBARE BEFEHLE:"
echo "  show-latest     - Letzte Show anzeigen"
echo "  show-script     - Letztes Script anzeigen"
echo "  show-list       - Liste aller Shows"
echo "  show-last5      - Letzte 5 Shows"
echo "  show-get <id>   - Spezifische Show"
echo "  show-read <id>  - Script einer Show"
echo ""
echo "🚀 RADIOX BEFEHLE:"
echo "  radiox-generate - Neue Show generieren"
echo "  radiox-status   - System-Status"
echo "  radiox-test     - System testen"
echo ""
echo "🗄️ SCHEMA BEFEHLE:"
echo "  schema-info     - Schema-Informationen"
echo "  schema-test     - Schema testen" 